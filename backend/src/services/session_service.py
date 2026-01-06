from sqlmodel import Session, create_engine, select, SQLModel
from src.core.config import get_settings
from src.models.session import AnalysisSession
import json

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session(session_id: str) -> AnalysisSession | None:
    with Session(engine) as session:
        statement = select(AnalysisSession).where(AnalysisSession.id == session_id)
        results = session.exec(statement)
        return results.first()

def create_session(file_path: str, file_name: str) -> AnalysisSession:
    with Session(engine) as session:
        # 使用列表中的单个文件进行初始化
        analysis_session = AnalysisSession(
            file_name=file_name,
            file_paths_json=json.dumps([file_path])
        )
        session.add(analysis_session)
        session.commit()
        session.refresh(analysis_session)
        return analysis_session

def update_session(analysis_session: AnalysisSession):
    with Session(engine) as session:
        session.merge(analysis_session)
        session.commit()

def list_sessions(limit: int = 20) -> list[AnalysisSession]:
    with Session(engine) as session:
        statement = select(AnalysisSession).order_by(AnalysisSession.created_at.desc()).limit(limit)
        results = session.exec(statement)
        return list(results.all())



