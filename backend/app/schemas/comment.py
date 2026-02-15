from pydantic import BaseModel

class CommentCreate(BaseModel):
    body: str
