from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class ProjectRole(str, enum.Enum):
    member = "member"
    maintainer = "maintainer"


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    role = Column(
        Enum(ProjectRole, name="project_role_enum"),
        nullable=False,
        default=ProjectRole.member
    )

    user = relationship("User")
    project = relationship("Project")
