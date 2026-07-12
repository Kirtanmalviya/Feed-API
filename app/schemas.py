from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str

class PostCreate(BaseModel):
    user_id: int
    caption: str

class PostLike(BaseModel):
    user_id: int
    post_id: int

class PostResponse(BaseModel):
    id: int
    user_id: int
    caption: str
    created_at: datetime

    class Config:
        from_attributes = True

class FeedResponse(BaseModel):
    posts: list[PostResponse]
    has_more: bool
    next_before_time: datetime | None = None