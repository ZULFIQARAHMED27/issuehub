from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, AddMemberRequest
from app.services import projects_service

router = APIRouter()


# -----------------------------
# Create Project
# -----------------------------
@router.post("/")
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return projects_service.create_project(
        db=db,
        name=project.name,
        key=project.key,
        description=project.description,
        creator_user_id=current_user.id,
    )


# -----------------------------
# List Projects (only joined)
# -----------------------------
@router.get("/")
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return projects_service.list_projects(db, current_user.id)


# -----------------------------
# Invite / Add Member by Email
# -----------------------------
@router.post("/{project_id}/members")
def add_member_to_project(
    project_id: int,
    payload: AddMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return projects_service.add_member_to_project(
        db=db,
        project_id=project_id,
        request_user_id=current_user.id,
        email=payload.email,
        role=payload.role
    )


# -----------------------------
# List Project Members
# -----------------------------
@router.get("/{project_id}/members")
def list_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return projects_service.list_project_members(db, project_id, current_user.id)


# -----------------------------
# Delete Project
# -----------------------------
@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return projects_service.delete_project(db, project_id, current_user.id)
