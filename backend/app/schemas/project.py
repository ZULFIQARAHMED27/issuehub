from pydantic import BaseModel, EmailStr
from typing import Optional, Literal


class ProjectCreate(BaseModel):
    name: str
    key: str
    description: Optional[str] = None


class AddMemberRequest(BaseModel):
    email: EmailStr
    role: Literal["maintainer", "member"]
