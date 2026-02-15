from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.issue import Issue
from app.models.project_member import ProjectMember


def get_issue_by_id(db: Session, issue_id: int):
    return db.query(Issue).filter(Issue.id == issue_id).first()


def get_project_membership(db: Session, project_id: int, user_id: int):
    return db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()


def create_comment(db: Session, issue_id: int, author_id: int, body: str):
    comment = Comment(issue_id=issue_id, author_id=author_id, body=body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments_by_issue(db: Session, issue_id: int):
    return db.query(Comment).filter(Comment.issue_id == issue_id).all()
