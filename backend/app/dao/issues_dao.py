from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.project_member import ProjectMember
from app.models.user import User


def get_project_membership(db: Session, project_id: int, user_id: int):
    return db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()


def create_issue(
    db: Session,
    project_id: int,
    title: str,
    description: str | None,
    priority,
    reporter_id: int,
    assignee_id: int | None
):
    issue = Issue(
        project_id=project_id,
        title=title,
        description=description,
        priority=priority,
        reporter_id=reporter_id,
        assignee_id=assignee_id
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def list_issues(
    db: Session,
    project_id: int,
    page: int,
    page_size: int,
    status: str | None,
    priority: str | None,
    assignee_id: int | None,
    q: str | None,
    sort: str | None
):
    query = db.query(Issue).filter(Issue.project_id == project_id)

    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)
    if q:
        query = query.filter(Issue.title.ilike(f"%{q}%"))

    if sort == "created_at":
        query = query.order_by(Issue.created_at.desc())
    elif sort == "priority":
        query = query.order_by(Issue.priority.asc())
    elif sort == "status":
        query = query.order_by(Issue.status.asc())

    total = query.count()
    issues = query.offset((page - 1) * page_size).limit(page_size).all()
    return issues, total


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_issue_by_id(db: Session, issue_id: int):
    return db.query(Issue).filter(Issue.id == issue_id).first()


def commit_issue(db: Session, issue: Issue):
    db.commit()
    db.refresh(issue)
    return issue


def delete_issue(db: Session, issue: Issue):
    db.delete(issue)
    db.commit()
