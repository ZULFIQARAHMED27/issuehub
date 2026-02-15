from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dao import comments_dao


def add_comment(db: Session, issue_id: int, body: str, current_user_id: int):
    issue = comments_dao.get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = comments_dao.get_project_membership(db, issue.project_id, current_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")

    comment = comments_dao.create_comment(
        db, issue_id=issue_id, author_id=current_user_id, body=body
    )
    return {"id": comment.id, "body": comment.body, "author_id": comment.author_id}


def list_comments(db: Session, issue_id: int, current_user_id: int):
    issue = comments_dao.get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = comments_dao.get_project_membership(db, issue.project_id, current_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")

    comments = comments_dao.list_comments_by_issue(db, issue_id)
    return [
        {
            "id": c.id,
            "body": c.body,
            "author_id": c.author_id,
            "created_at": c.created_at
        }
        for c in comments
    ]
