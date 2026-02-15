from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine

from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.issues import router as issues_router
from app.api.comments import router as comments_router
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from sqlalchemy.orm import Session
from app.services import auth_service

# -------------------------
# App Initialization
# -------------------------

app = FastAPI(
    title="IssueHub API",
    version="1.0.0",
    description="Issue Tracking System - Powered by MediaMint"
)

# -------------------------
# CORS Configuration
# -------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Structured Error Handling
# -------------------------

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": exc.errors(),
            }
        },
    )

# -------------------------
# API Routers
# -------------------------

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(issues_router, prefix="/api", tags=["Issues"])
app.include_router(comments_router, prefix="/api", tags=["Comments"])


@app.get("/api/me")
def me_alias(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return auth_service.me(db, current_user.id, current_user.name, current_user.email)

# -------------------------
# Database Tables (Dev Only)
# -------------------------

Base.metadata.create_all(bind=engine)

# -------------------------
# Root Health Check
# -------------------------

@app.get("/")
def root():
    return {
        "message": "IssueHub API running",
        "version": "v1"
    }
