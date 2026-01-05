from sqlmodel import SQLModel
from src.services.session_service import engine
from src.models.session import AnalysisSession

def reset_db():
    print("Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    print("Creating all tables...")
    SQLModel.metadata.create_all(engine)
    print("Database reset complete.")

if __name__ == "__main__":
    reset_db()
