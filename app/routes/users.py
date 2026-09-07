from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from app.database import get_db
from app import models, schemas
from app.oauth import  get_current_user
from sqlalchemy.orm import Session, selectinload

router = APIRouter(
    prefix="/users",
    tags=["User"]
)

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)): # type: ignore

    user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {
        "id": user.user_id,
        "username": user.username
    } # type: ignore

@router.delete("/", status_code=204)
def delete_account(db: Session = Depends(get_db), current_user: models.Users = Depends(get_current_user)):

    user = db.query(models.Users).filter(models.Users.user_id == current_user.user_id).first()

    UserRelationships = db.query(
        models.Follows
        ).filter(
            or_(
                models.Follows.follower_id == current_user.user_id, 
                models.Follows.following_id == current_user.user_id
                )
                ).all()
    
    likesByUsers = db.query(
        models.Likes
        ).filter(
            models.Likes.user_id == current_user.user_id
            ).all()
    
    postsByUser = db.query(models.Posts).filter(models.Posts.user_id == current_user.user_id).all()
    postIds = set()#type: ignore
    for post in postsByUser:
        postIds.add(post.id) #type: ignore
        db.delete(post)

    postMediaByUser = db.query(models.PostMedia).filter(models.PostMedia.post_id.in_(postIds)).all()

    for postMedia in postMediaByUser:
        db.delete(postMedia)

    
    for UserRelationship in UserRelationships:
        db.delete(UserRelationship)
    
    for likesByUser in likesByUsers:
        db.delete(likesByUser)
    
    db.delete(user)
    db.commit()

@router.get("/{user_id}/posts", response_model=schemas.FeedResponse)
def getUserPosts( # type: ignore
    user_id: int,
    limit: int = 10,
    before_time: datetime | None = None,
    db: Session = Depends(get_db)
):

    User = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if not User:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    postsQuery = db.query(models.Posts).options(
        selectinload(models.Posts.media)
    ).filter(models.Posts.user_id == user_id)

    if before_time:
        postsQuery = postsQuery.filter(models.Posts.created_at < before_time)

    userPosts = postsQuery.order_by(models.Posts.created_at.desc()).limit(limit + 1).all()

    has_more = len(userPosts) > limit
    if has_more:
        userPosts = userPosts[:limit]

    next_before_time = userPosts[-1].created_at if userPosts else None

    return {
        "posts": userPosts,
        "has_more": has_more,
        "next_before_time": next_before_time
    } # type: ignore

@router.get("/{user_id}/followers", response_model=schemas.FollowerListResponse)
def getFollowers( # type: ignore
    user_id: int,
    limit: int = 15,
    before_time: datetime | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(
        models.Users.user_id, models.Users.username, models.Follows.created_at
    ).join(
        models.Follows, models.Follows.follower_id == models.Users.user_id
    ).filter(
        models.Follows.following_id == user_id
    )

    if before_time:
        query = query.filter(
            models.Follows.created_at < before_time
        )

    results = query.order_by(
        models.Follows.created_at.desc()
    ).limit(limit + 1).all()

    has_more = len(results) > limit
    if has_more: 
        results = results[:limit]

    return {
    "followerList": results,
    "has_more": has_more,
    "next_before_time": results[-1].created_at if results else None
} # type: ignore
    











