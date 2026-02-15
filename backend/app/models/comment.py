from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    issue_id = Column(
        Integer,
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False
    )

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    body = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to Issue
    issue = relationship("Issue", back_populates="comments")
