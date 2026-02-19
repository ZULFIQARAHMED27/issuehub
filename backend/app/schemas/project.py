from pydantic import BaseModel, EmailStr
from pydantic import field_validator
from typing import Optional, Literal
from datetime import date, timedelta

class ProjectCreate(BaseModel):
    name: str
    key: str
    description: Optional[str] = None
    start_date: Optional[date] = None

    @field_validator("start_date")
    @classmethod
    def validate_start_date_window(cls, value: Optional[date]) -> Optional[date]:
        if value is None:
            return value

        max_allowed = date.today() + timedelta(days=30)
        if value > max_allowed:
            raise ValueError("Not allowed to select beyond 30 days from start date")

        return value

class AddMemberRequest(BaseModel):
    email: EmailStr
    role: Literal["maintainer", "member"]
