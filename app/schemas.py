from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models import MediaType, MediaStatus
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostCreate(BaseModel):
    caption: str

class PostLike(BaseModel):
    post_id: int

class PostMediaResponse(BaseModel):
    id: int
    post_id: int
    media_type: MediaType
    storage_path: str
    status: MediaStatus
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserResponse(BaseModel):
    user_id: int
    username: str

class PostResponse(BaseModel):
    id: int
    user_id: int
    caption: str
    created_at: datetime
    media: list[PostMediaResponse] = []

    model_config = {
        "from_attributes": True
    }

class FeedResponse(BaseModel):
    posts: list[PostResponse]
    has_more: bool
    next_before_time: datetime | None = None

