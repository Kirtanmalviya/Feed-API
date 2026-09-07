from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app import models, schemas
from datetime import datetime

from app.oauth import get_current_user

router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
)

@router.get(
        "/", 
        response_model=schemas.FeedResponse
)
def load_feed( # pyright: ignore[reportUnknownParameterType]
    limit: int = 10,
    before_time: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)
):
    
    query = db.query(
        models.Posts
        ).options(selectinload(models.Posts.media)
                  ).join(
            models.Follows, 
            models.Follows.following_id == models.Posts.user_id
            ).filter(
                models.Follows.follower_id == current_user.user_id
                )

    if before_time:
        query = query.filter(
            models.Posts.created_at < before_time
        )
    
    posts = query.order_by(
        models.Posts.created_at.desc()
        ).limit(
            limit + 1
                ).all() 
    
    has_more = len(posts) > limit

    if has_more:
        posts = posts[:limit]

    next_before_time = posts[-1].created_at if posts else None
    
    return {
        "posts": posts,
        "has_more": has_more,
        "next_before_time": next_before_time 
    } # pyright: ignore[reportUnknownVariableType]
