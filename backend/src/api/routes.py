from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from src.services.session_service import create_session, get_session, update_session, list_sessions
from src.services.title_generator import generate_session_title
from src.agents.business_analysis.agent import BusinessAnalysisCrew
from src.agents.financial_analysis.agent import FinancialAnalysisCrew
from src.agents.valuation.agent import ValuationCrew
from src.agents.mda_analysis.agent import MDACrew
from src.agents.competitor_analysis.agent import CompetitorCrew
import shutil
import os
import json

router = APIRouter()
UPLOAD_ROOT = "knowledge"
os.makedirs(UPLOAD_ROOT, exist_ok=True)

@router.get("/sessions")
async def get_all_sessions():
    return list_sessions()

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # 1. Create Session First to get ID
    # Use placeholder path initially
    session = create_session(file_path="", file_name=file.filename)
    
    # 2. Create Session Directory
    session_dir = os.path.join(UPLOAD_ROOT, session.id)
    os.makedirs(session_dir, exist_ok=True)
    
    # 3. Save File
    file_location = os.path.join(session_dir, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # 4. Update Session with Absolute Path
    abs_path = os.path.abspath(file_location)
    
    # Update the single path field used by create_session (which sets file_paths_json)
    # Since create_session is already done, we update via property
    session.file_paths = [abs_path]
    update_session(session)
    
    # Trigger Title Generation
    background_tasks.add_task(generate_session_title, session.id, abs_path)
    
    return {"session_id": session.id, "message": "文件上传成功", "file_path": f"/static/{session.id}/{file.filename}"}

@router.post("/session/{session_id}/upload")
async def add_file_to_session(session_id: str, file: UploadFile = File(...)):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
        
    session_dir = os.path.join(UPLOAD_ROOT, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    file_location = os.path.join(session_dir, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    abs_path = os.path.abspath(file_location)
    
    # Update file paths
    current_paths = session.file_paths
    if abs_path not in current_paths:
        current_paths.append(abs_path)
        session.file_paths = current_paths
        update_session(session)
        
    return {"message": "文件添加成功", "file_paths": session.file_paths}

@router.delete("/session/{session_id}/file")
async def delete_file_from_session(session_id: str, filename: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    # Check if file is in session
    # stored paths are absolute. We check if any path ends with /{filename}
    target_path = None
    new_paths = []
    found = False
    
    for path in session.file_paths:
        if path.endswith(f"/{filename}") or path.endswith(f"\\{filename}"):
            target_path = path
            found = True
        else:
            new_paths.append(path)
            
    if not found:
        raise HTTPException(status_code=404, detail="文件在会话中未找到")
        
    session.file_paths = new_paths
    update_session(session)
    
    # Optionally delete from disk
    if target_path and os.path.exists(target_path):
        try:
            os.remove(target_path)
        except Exception as e:
            print(f"Failed to delete file {target_path}: {e}")
    
    return {"message": "文件删除成功", "file_paths": session.file_paths}

# Helper to convert absolute paths to knowledge-relative paths
def _to_knowledge_relative(file_paths: list[str]) -> list[str]:
    # We want "session_id/filename.pdf" or just "filename.pdf" depending on structure
    # Robust logic: find split point
    rel_paths = []
    
    for p in file_paths:
        # Normalization
        p_str = str(p)
        
        # Try to split by 'knowledge/' or 'uploads/'
        # We take the *last* component to be safe against full path having multiple
        
        if '/knowledge/' in p_str:
            rel = p_str.split('/knowledge/')[-1]
            rel_paths.append(rel)
        elif '/uploads/' in p_str:
            rel = p_str.split('/uploads/')[-1]
            rel_paths.append(rel)
        else:
            # Fallback: if it's already just a filename or relative path
            # check if it exists in UPLOAD_ROOT
            if os.path.exists(os.path.join(UPLOAD_ROOT, p_str)):
                rel_paths.append(p_str)
            else:
                # Just assume it might be relative
                rel_paths.append(p_str)
                
    print(f"DEBUG: Converted paths {file_paths} -> {rel_paths}")
    return rel_paths

def _to_knowledge_relative_single(file_path: str) -> str:
    res = _to_knowledge_relative([file_path])
    return res[0] if res else file_path

# Helper Tasks
# ...
def _run_business_analysis_task(session_id: str, file_paths: list[str]):
    try:
        # Re-fetch session to ensure fresh state or just use ID to update
        session = get_session(session_id)
        if not session:
            return
            
        session.business_status = "RUNNING"
        update_session(session)
        
        # Convert to relative paths for CrewAI
        rel_paths = _to_knowledge_relative(file_paths)
        print(f"DEBUG: Running Business Analysis with paths: {rel_paths}")
        
        crew = BusinessAnalysisCrew(file_paths=rel_paths)
        result = crew.run()
        
        session.business_analysis_result = str(result)
        session.business_status = "COMPLETED"
        update_session(session)
        
    except Exception as e:
        print(f"Error in business analysis task: {e}")
        import traceback
        traceback.print_exc()
        session = get_session(session_id)
        if session:
            session.business_status = "FAILED"
            # Optional: Store error message in result or separate field
            session.business_analysis_result = f"Error: {str(e)}"
            update_session(session)

@router.post("/analyze/{session_id}/business")
async def run_business_analysis(session_id: str, background_tasks: BackgroundTasks):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    # Check if already running? (Optional optimization)
    if session.business_status == "RUNNING":
         return {"status": "RUNNING", "message": "分析正在进行中"}

    background_tasks.add_task(_run_business_analysis_task, session_id, session.file_paths)
    
    return {"status": "PENDING", "message": "商业模式分析已启动"}

def _run_financial_analysis_task(session_id: str, file_path: str):
    try:
        session = get_session(session_id)
        if not session: return
        session.financial_status = "RUNNING"
        update_session(session)
        
        # Relative path
        rel_path = _to_knowledge_relative_single(file_path)
        
        crew = FinancialAnalysisCrew(file_path=rel_path)
        result = crew.run()
        
        session.financial_analysis_result = str(result)
        session.financial_status = "COMPLETED"
        update_session(session)
    except Exception as e:
        print(f"Error in financial task: {e}")
        session = get_session(session_id)
        if session:
            session.financial_status = "FAILED"
            session.financial_analysis_result = f"Error: {e}"
            update_session(session)

@router.post("/analyze/{session_id}/financial")
async def run_financial_analysis(session_id: str, background_tasks: BackgroundTasks):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    if not session.file_paths:
        raise HTTPException(status_code=400, detail="会话中没有文件")
        
    if session.financial_status == "RUNNING":
         return {"status": "RUNNING", "message": "分析正在进行中"}

    background_tasks.add_task(_run_financial_analysis_task, session_id, session.file_paths[0])
    return {"status": "PENDING", "message": "财务分析已启动"}

def _run_mda_analysis_task(session_id: str, file_paths: list[str]):
    try:
        session = get_session(session_id)
        if not session: return
        session.mda_status = "RUNNING"
        update_session(session)
        
        rel_paths = _to_knowledge_relative(file_paths)
        
        crew = MDACrew(file_paths=rel_paths)
        result = crew.run()
        
        session.mda_analysis_result = str(result)
        session.mda_status = "COMPLETED"
        update_session(session)
    except Exception as e:
        print(f"Error in MDA task: {e}")
        session = get_session(session_id)
        if session:
            session.mda_status = "FAILED"
            session.mda_analysis_result = f"Error: {e}"
            update_session(session)

@router.post("/analyze/{session_id}/mda")
async def run_mda_analysis(session_id: str, background_tasks: BackgroundTasks):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session.mda_status == "RUNNING":
         return {"status": "RUNNING", "message": "分析正在进行中"}

    background_tasks.add_task(_run_mda_analysis_task, session_id, session.file_paths)
    return {"status": "PENDING", "message": "MD&A 分析已启动"}

def _run_competitor_analysis_task(session_id: str, file_paths: list[str]):
    try:
        session = get_session(session_id)
        if not session: return
        session.competitor_status = "RUNNING"
        update_session(session)
        
        rel_paths = _to_knowledge_relative(file_paths)
        
        crew = CompetitorCrew(file_paths=rel_paths)
        result = crew.run()
        
        session.competitor_analysis_result = str(result)
        session.competitor_status = "COMPLETED"
        update_session(session)
    except Exception as e:
        print(f"Error in competitor task: {e}")
        session = get_session(session_id)
        if session:
            session.competitor_status = "FAILED"
            session.competitor_analysis_result = f"Error: {e}"
            update_session(session)

@router.post("/analyze/{session_id}/competitor")
async def run_competitor_analysis(session_id: str, background_tasks: BackgroundTasks):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session.competitor_status == "RUNNING":
         return {"status": "RUNNING", "message": "分析正在进行中"}
         
    background_tasks.add_task(_run_competitor_analysis_task, session_id, session.file_paths)
    return {"status": "PENDING", "message": "竞争对手分析已启动"}

def _run_valuation_task(session_id: str, financial_data: dict, moat_rating: str):
    try:
        session = get_session(session_id)
        if not session: return
        session.valuation_status = "RUNNING"
        update_session(session)
        
        crew = ValuationCrew(financial_data=financial_data, moat_rating=moat_rating)
        result = crew.run()
        
        session.valuation_result = str(result)
        session.valuation_status = "COMPLETED"
        update_session(session)
    except Exception as e:
        print(f"Error in valuation task: {e}")
        session = get_session(session_id)
        if session:
            session.valuation_status = "FAILED"
            session.valuation_result = f"Error: {e}"
            update_session(session)

@router.post("/analyze/{session_id}/valuation")
async def run_valuation(session_id: str, background_tasks: BackgroundTasks):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
        
    if session.valuation_status == "RUNNING":
         return {"status": "RUNNING", "message": "分析正在进行中"}
    
    # 模拟数据流
    financial_data = {
        "net_income": 1000000, 
        "depreciation_amortization": 200000, 
        "capex": 150000,
        "growth_rate": 0.05,
        "discount_rate": 0.10,
        "terminal_growth_rate": 0.02,
        "years": 10
    }
    moat_rating = "Narrow"
    
    background_tasks.add_task(_run_valuation_task, session_id, financial_data, moat_rating)
    return {"status": "PENDING", "message": "估值分析已启动"}

@router.get("/session/{session_id}")
async def get_session_status(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    return session

# Export/Import logic
@router.get("/export/{session_id}")
async def export_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    import zipfile
    import io
    from fastapi.responses import StreamingResponse
    import os
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Add Session Data
        session_data = session.model_dump_json()
        zip_file.writestr("session.json", session_data)
        
        # 2. Add Files
        session_dir = os.path.join(UPLOAD_ROOT, session.id)
        for file_path in session.file_paths:
            # File path is absolute path like /Users/.../backend/uploads/{session_id}/filename.pdf
            # Just verify it exists and add it
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                zip_file.write(file_path, arcname=f"files/{filename}")
            else:
                # Fallback: check if it's in the session dir by name (legacy support)
                filename = os.path.basename(file_path)
                fallback_path = os.path.join(session_dir, filename)
                if os.path.exists(fallback_path):
                    zip_file.write(fallback_path, arcname=f"files/{filename}")
                else:
                    print(f"Warning: File not found during export: {file_path}")
    
    zip_buffer.seek(0)
    
    filename = f"value-analyst-{session.company_name or 'session'}-{session_id[:8]}.zip"
    
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip", 
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/import")
async def import_session(file: UploadFile = File(...)):
    import zipfile
    import io
    import json
    import shutil
    import os
    from src.models.session import AnalysisSession
    from src.services.session_service import update_session # Reuse update/save
    
    try:
        content = await file.read()
        zip_buffer = io.BytesIO(content)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            # 1. Read Session Data
            if "session.json" not in zip_ref.namelist():
                raise HTTPException(status_code=400, detail="Invalid backup file: session.json missing")
            
            session_json = zip_ref.read("session.json")
            session_dict = json.loads(session_json)
            session_id = session_dict.get("id")
            if not session_id:
                 raise HTTPException(status_code=400, detail="Invalid session data: missing ID")

            # 2. Restore Files
            session_dir = os.path.join(UPLOAD_ROOT, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            restored_paths = []
            
            for file_info in zip_ref.infolist():
                if file_info.filename.startswith("files/") and not file_info.is_dir():
                    # Extract filename from files/xxx.pdf
                    target_filename = os.path.basename(file_info.filename)
                    if not target_filename: continue
                    
                    target_path = os.path.join(session_dir, target_filename)
                    
                    # Prevent path traversal? basename protects us primarily
                    with open(target_path, "wb") as f:
                        f.write(zip_ref.read(file_info))
                    
                    restored_paths.append(os.path.abspath(target_path))
                        
            # 3. Restore Session to DB
            session_obj = AnalysisSession.model_validate(session_dict)
            
            # Update paths to the current system's absolute paths
            # Note: We overwrite whatever was in the JSON because paths are local-system dependent
            if restored_paths:
                session_obj.file_paths = restored_paths
            
            # Upsert
            existing = get_session(session_obj.id)
            if existing:
                update_session(session_obj)
            else:
                # Add new session explicitly
                # Our service 'update_session' uses session.add/commit which works for new entities with set IDs too
                update_session(session_obj)
                
            return {"session_id": session_obj.id, "message": "导入成功"}
            
    except Exception as e:
        print(f"Import failed: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
