from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueUpdate
from app.services import issues_service

router = APIRouter()


# ---------------------------------------
# Create Issue
# ---------------------------------------

@router.post("/projects/{project_id}/issues")
def create_issue(
    project_id: int,
    issue: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return issues_service.create_issue(db, project_id, issue, current_user.id)


# ---------------------------------------
# List Issues (with filters + pagination)
# ---------------------------------------

@router.get("/projects/{project_id}/issues")
def list_issues(
    project_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee: Optional[int] = Query(None),
    assignee_id: Optional[int] = Query(None),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return issues_service.list_issues(
        db=db,
        project_id=project_id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        assignee=assignee if assignee is not None else assignee_id,
        q=q,
        sort=sort,
        current_user_id=current_user.id,
    )


# ---------------------------------------
# Update Issue (DOCUMENT-ALIGNED ROLES)
# ---------------------------------------

@router.patch("/issues/{issue_id}")
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return issues_service.update_issue(db, issue_id, issue_update, current_user.id)


# ---------------------------------------
# Delete Issue
# ---------------------------------------

@router.delete("/issues/{issue_id}")
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return issues_service.delete_issue(db, issue_id, current_user.id)


# ---------------------------------------
# Issue Detail
# ---------------------------------------

@router.get("/issues/{issue_id}")
def get_issue_detail(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return issues_service.get_issue_detail(db, issue_id, current_user.id)
