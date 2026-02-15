from sqlalchemy.orm import Session

from app.models.user import User
from app.models.project_member import ProjectMember


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, name: str, email: str, password_hash: str):
    user = User(name=name, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_memberships_for_user(db: Session, user_id: int):
    return db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()
