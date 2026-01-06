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
UPLOAD_DIR = "uploads/knowledge"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Ensure "knowledge" symlink exists for CrewAI compatibility
# CrewAI defaults to looking in "knowledge/" directory
if not os.path.exists("knowledge"):
    try:
        os.symlink(UPLOAD_DIR, "knowledge")
    except Exception as e:
        print(f"Failed to create knowledge symlink: {e}")
elif os.path.islink("knowledge"):
    # Check if it points to the right place
    if os.readlink("knowledge") != UPLOAD_DIR:
        try:
            os.unlink("knowledge")
            os.symlink(UPLOAD_DIR, "knowledge")
        except Exception as e:
            print(f"Failed to update knowledge symlink: {e}")


@router.get("/sessions")
async def get_all_sessions():
    return list_sessions()

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # 使用绝对路径进行后端处理
    abs_path = os.path.abspath(file_location)
    session = create_session(file_path=abs_path, file_name=file.filename)
    
    # Trigger Title Generation
    background_tasks.add_task(generate_session_title, session.id, abs_path)
    
    return {"session_id": session.id, "message": "文件上传成功", "file_path": f"/static/{file.filename}"}

@router.post("/session/{session_id}/upload")
async def add_file_to_session(session_id: str, file: UploadFile = File(...)):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
        
    file_location = f"{UPLOAD_DIR}/{file.filename}"
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

# Helper Tasks
def _run_business_analysis_task(session_id: str, file_paths: list[str]):
    try:
        # Re-fetch session to ensure fresh state or just use ID to update
        session = get_session(session_id)
        if not session:
            return
            
        session.business_status = "RUNNING"
        update_session(session)
        
        crew = BusinessAnalysisCrew(file_paths=file_paths)
        result = crew.run()
        
        session.business_analysis_result = str(result)
        session.business_status = "COMPLETED"
        update_session(session)
        
    except Exception as e:
        print(f"Error in business analysis task: {e}")
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
        
        crew = FinancialAnalysisCrew(file_path=file_path)
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
        
        crew = MDACrew(file_paths=file_paths)
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
        
        crew = CompetitorCrew(file_paths=file_paths)
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
        for file_path in session.file_paths:
            # Clean file path to handle /static/ prefix
            # Assuming file_path stored as "/static/filename.pdf"
            filename = os.path.basename(file_path)
            actual_path = os.path.join("uploads", filename)
            
            if os.path.exists(actual_path):
                zip_file.write(actual_path, arcname=f"files/{filename}")
            else:
                print(f"Warning: File not found during export: {actual_path}")
    
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
            
            # 2. Restore Files
            os.makedirs("uploads", exist_ok=True)
            for file_info in zip_ref.infolist():
                if file_info.filename.startswith("files/") and not file_info.is_dir():
                    # Extract filename from files/xxx.pdf
                    target_filename = os.path.basename(file_info.filename)
                    if not target_filename: continue
                    
                    target_path = os.path.join("uploads", target_filename)
                    
                    # Prevent path traversal? basename protects us primarily
                    with open(target_path, "wb") as f:
                        f.write(zip_ref.read(file_info))
                        
            # 3. Restore Session to DB
            session_obj = AnalysisSession.model_validate(session_dict)
            
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
