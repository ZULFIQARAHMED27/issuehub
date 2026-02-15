from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dao import projects_dao
from app.services.common import role_value


def create_project(db: Session, name: str, key: str, description: str | None, creator_user_id: int):
    existing = projects_dao.get_project_by_key(db, key)
    if existing:
        raise HTTPException(status_code=400, detail="Project key already exists")

    project = projects_dao.create_project(db, name=name, key=key, description=description)
    projects_dao.create_project_member(
        db, project_id=project.id, user_id=creator_user_id, role="maintainer"
    )

    return {
        "id": project.id,
        "name": project.name,
        "key": project.key,
        "description": project.description
    }


def list_projects(db: Session, user_id: int):
    memberships = projects_dao.list_memberships_for_user(db, user_id)
    project_ids = [m.project_id for m in memberships]
    projects = projects_dao.list_projects_by_ids(db, project_ids)
    role_by_project_id = {m.project_id: role_value(m.role) for m in memberships}

    return [
        {
            "id": p.id,
            "name": p.name,
            "key": p.key,
            "description": p.description,
            "my_role": role_by_project_id.get(p.id)
        }
        for p in projects
    ]


def add_member_to_project(db: Session, project_id: int, request_user_id: int, email: str, role: str):
    membership = projects_dao.get_membership(db, project_id, request_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    if role_value(membership.role) != "maintainer":
        raise HTTPException(status_code=403, detail="Only maintainer can invite members")

    user = projects_dao.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found")

    existing = projects_dao.get_membership(db, project_id, user.id)
    if existing:
        raise HTTPException(status_code=400, detail="User already a member")

    projects_dao.create_project_member(
        db, project_id=project_id, user_id=user.id, role=role
    )
    return {
        "message": "Member added successfully",
        "user_id": user.id,
        "email": user.email,
        "role": role
    }


def list_project_members(db: Session, project_id: int, request_user_id: int):
    membership = projects_dao.get_membership(db, project_id, request_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")

    members = projects_dao.list_project_members(db, project_id)
    result = []
    for m in members:
        user = projects_dao.get_user_by_id(db, m.user_id)
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": role_value(m.role)
        })
    return result


def delete_project(db: Session, project_id: int, request_user_id: int):
    project = projects_dao.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    membership = projects_dao.get_membership(db, project_id, request_user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    if role_value(membership.role) != "maintainer":
        raise HTTPException(status_code=403, detail="Only maintainer can delete project")

    issue_ids = projects_dao.list_issue_ids_for_project(db, project_id)
    projects_dao.delete_comments_by_issue_ids(db, issue_ids)
    projects_dao.delete_issues_by_project(db, project_id)
    projects_dao.delete_memberships_by_project(db, project_id)
    projects_dao.delete_project(db, project)
    return {"message": "Project deleted successfully"}
