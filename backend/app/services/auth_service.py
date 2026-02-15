from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.dao import auth_dao
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.common import role_value


def signup(db: Session, name: str, email: str, password: str):
    existing = auth_dao.get_user_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    auth_dao.create_user(db, name=name, email=email, password_hash=get_password_hash(password))
    return {"message": "User created successfully"}


def login(db: Session, username: str, password: str):
    user = auth_dao.get_user_by_email(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


def me(db: Session, user_id: int, name: str, email: str):
    memberships = auth_dao.list_memberships_for_user(db, user_id)
    roles = [role_value(m.role) for m in memberships]
    return {
        "id": user_id,
        "name": name,
        "email": email,
        "project_roles": roles
    }
