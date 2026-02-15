from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.dependencies import get_current_user, get_db
from app.services import auth_service

router = APIRouter()


# ------------------------
# SIGNUP
# ------------------------
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.signup(db, user.name, user.email, user.password)


# ------------------------
# LOGIN
# ------------------------
@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")

    # Supports assignment example contract: JSON {email,password}
    if "application/json" in content_type:
        payload = await request.json()
        try:
            model = UserLogin(**payload)
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid login payload")
        return auth_service.login(db, model.email, model.password)

    # Also supports OAuth2 form (username/password)
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    if not username or not password:
        raise HTTPException(status_code=422, detail="Invalid login payload")
    return auth_service.login(db, username, password)


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return auth_service.me(db, current_user.id, current_user.name, current_user.email)
