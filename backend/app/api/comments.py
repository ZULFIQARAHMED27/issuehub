from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.comment import CommentCreate
from app.services import comments_service

router = APIRouter()


@router.post("/issues/{issue_id}/comments")
def add_comment(
    issue_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return comments_service.add_comment(db, issue_id, comment.body, current_user.id)


@router.get("/issues/{issue_id}/comments")
def list_comments(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return comments_service.list_comments(db, issue_id, current_user.id)
