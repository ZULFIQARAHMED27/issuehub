from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dao import issues_dao
from app.schemas.issue import IssueCreate, IssueUpdate
from app.services.common import role_value


def create_issue(db: Session, project_id: int, payload: IssueCreate, current_user_id: int):
    membership = issues_dao.get_project_membership(db, project_id, current_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")

    issue = issues_dao.create_issue(
        db,
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        reporter_id=current_user_id,
        assignee_id=payload.assignee_id
    )
    return {
        "id": issue.id,
        "title": issue.title,
        "status": issue.status,
        "priority": issue.priority,
        "reporter_id": issue.reporter_id,
        "assignee_id": issue.assignee_id
    }


def list_issues(
    db: Session,
    project_id: int,
    page: int,
    page_size: int,
    status: str | None,
    priority: str | None,
    assignee: int | None,
    q: str | None,
    sort: str | None,
    current_user_id: int
):
    membership = issues_dao.get_project_membership(db, project_id, current_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")

    issues, total = issues_dao.list_issues(
        db=db,
        project_id=project_id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        assignee_id=assignee,
        q=q,
        sort=sort,
    )

    result = []
    for issue in issues:
        reporter = issues_dao.get_user_by_id(db, issue.reporter_id)
        assignee = issues_dao.get_user_by_id(db, issue.assignee_id) if issue.assignee_id else None
        result.append({
            "id": issue.id,
            "title": issue.title,
            "status": issue.status,
            "priority": issue.priority,
            "reporter_id": issue.reporter_id,
            "reporter_name": reporter.name if reporter else None,
            "assignee_id": issue.assignee_id,
            "assignee_name": assignee.name if assignee else None
        })

    return {"total": total, "page": page, "page_size": page_size, "data": result}


def update_issue(db: Session, issue_id: int, payload: IssueUpdate, current_user_id: int):
    issue = issues_dao.get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = issues_dao.get_project_membership(db, issue.project_id, current_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")

    is_maintainer = role_value(membership.role) == "maintainer"
    is_reporter = issue.reporter_id == current_user_id
    if not is_maintainer and not is_reporter:
        raise HTTPException(status_code=403, detail="Not allowed to update this issue")

    if payload.title is not None:
        issue.title = payload.title
    if payload.description is not None:
        issue.description = payload.description
    if payload.priority is not None:
        issue.priority = payload.priority
    if payload.status is not None:
        if not is_maintainer:
            raise HTTPException(status_code=403, detail="Only maintainer can change status")
        issue.status = payload.status
    if "assignee_id" in payload.model_fields_set:
        if not is_maintainer:
            raise HTTPException(status_code=403, detail="Only maintainer can assign issues")
        issue.assignee_id = payload.assignee_id

    issues_dao.commit_issue(db, issue)
    return {
        "id": issue.id,
        "title": issue.title,
        "status": issue.status,
        "priority": issue.priority,
        "reporter_id": issue.reporter_id,
        "assignee_id": issue.assignee_id
    }


def delete_issue(db: Session, issue_id: int, current_user_id: int):
    issue = issues_dao.get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = issues_dao.get_project_membership(db, issue.project_id, current_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")

    is_maintainer = role_value(membership.role) == "maintainer"
    is_reporter = issue.reporter_id == current_user_id
    if not is_maintainer and not is_reporter:
        raise HTTPException(status_code=403, detail="Not allowed to delete this issue")

    issues_dao.delete_issue(db, issue)
    return {"message": "Issue deleted successfully"}


def get_issue_detail(db: Session, issue_id: int, current_user_id: int):
    issue = issues_dao.get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    membership = issues_dao.get_project_membership(db, issue.project_id, current_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")

    reporter = issues_dao.get_user_by_id(db, issue.reporter_id)
    assignee = issues_dao.get_user_by_id(db, issue.assignee_id) if issue.assignee_id else None
    return {
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status,
        "priority": issue.priority,
        "reporter_id": issue.reporter_id,
        "reporter_name": reporter.name if reporter else None,
        "assignee_id": issue.assignee_id,
        "assignee_name": assignee.name if assignee else None,
        "created_at": issue.created_at,
        "updated_at": issue.updated_at
    }
