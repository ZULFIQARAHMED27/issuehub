from sqlalchemy.orm import Session
from datetime import date

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.models.issue import Issue
from app.models.comment import Comment


def get_project_by_key(db: Session, key: str):
    return db.query(Project).filter(Project.key == key).first()


def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(
    db: Session,
    name: str,
    key: str,
    description: str | None,
    start_date: date | None,
):
    project = Project(
        name=name,
        key=key,
        description=description,
        start_date=start_date,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_project_member(db: Session, project_id: int, user_id: int, role: str):
    member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    return member


def get_membership(db: Session, project_id: int, user_id: int):
    return db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()


def list_memberships_for_user(db: Session, user_id: int):
    return db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()


def list_projects_by_ids(db: Session, project_ids: list[int]):
    if not project_ids:
        return []
    return db.query(Project).filter(Project.id.in_(project_ids)).all()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def list_project_members(db: Session, project_id: int):
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def list_issue_ids_for_project(db: Session, project_id: int):
    return [issue_id for (issue_id,) in db.query(Issue.id).filter(Issue.project_id == project_id).all()]


def delete_comments_by_issue_ids(db: Session, issue_ids: list[int]):
    if issue_ids:
        db.query(Comment).filter(Comment.issue_id.in_(issue_ids)).delete(synchronize_session=False)


def delete_issues_by_project(db: Session, project_id: int):
    db.query(Issue).filter(Issue.project_id == project_id).delete(synchronize_session=False)


def delete_memberships_by_project(db: Session, project_id: int):
    db.query(ProjectMember).filter(ProjectMember.project_id == project_id).delete(synchronize_session=False)


def delete_project(db: Session, project: Project):
    db.delete(project)
    db.commit()
