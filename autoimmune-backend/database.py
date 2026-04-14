from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create SQLite database file
DATABASE_URL = "sqlite:///./immunoai.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# History table
class ReportHistory(Base):
    __tablename__ = "report_history"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    disease = Column(String)
    confidence = Column(Float)
    date = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()