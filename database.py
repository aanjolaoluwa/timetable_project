# database.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./timetables.db"

# Create database engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model representing a single scheduled class session
class TimetableEntry(Base):
    __tablename__ = "timetable_entries"

    id = Column(Integer, primary_key=True, index=True)
    course = Column(String, index=True)
    lecturer = Column(String)
    students = Column(Integer)
    venue = Column(String)
    timeslot = Column(String)
    duration = Column(Integer)
    level = Column(String)

# Initialize database tables
def init_db():
    Base.metadata.create_all(bind=engine)