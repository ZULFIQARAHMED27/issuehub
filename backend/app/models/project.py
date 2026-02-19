from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime
from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
