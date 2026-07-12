from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models,schemas
from app.database import engine, get_db
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def helloAPI():
    return {"message": "FeedAPI running!"}

@app.post("/register")
def create_user(
    body: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    ob = models.Users(
        username = body.username
    )

    db.add(ob)
    db.commit()

    return {"message": f"user created your username is : {body.username}"}

@app.post("/{user1}/follows/{user2}")
def follow_user(
    user1: int, 
    user2: int,
    db: Session = Depends(get_db)
):
    
    user_1 = db.query(
        models.Users
        ).filter(
            models.Users.user_id == user1
            ).first()
    
    if not user_1:
        raise HTTPException(
            status_code=404, 
            detail="Follower is Not recogniged by the system"
        )
    
    user_2 = db.query(
        models.Users
        ).filter(
            models.Users.user_id == user2
            ).first()
    
    if not user_2:
        raise HTTPException(
            status_code=404, 
            detail="person you want to follow does not exist in system"
        )
    
    if user1 == user2:
        raise HTTPException(
            status_code=400, 
            detail="following self is not allowed"
        )
    
    checkBeforeFollow = db.query(
        models.Follows
        ).filter(
            models.Follows.follower_id == user1, 
            models.Follows.following_id == user2
            ).first()
    
    if checkBeforeFollow:
        raise HTTPException(
            status_code=409, 
            detail="cannot follower a user more than 1 time"
        )
    
    ob = models.Follows(
        follower_id=user1,
        following_id=user2
    )

    db.add(ob)
    db.commit()

    return {"message": f"{user1} follows {user2}"}

@app.post("/post")
def create_post(
    body: schemas.PostCreate, 
    db: Session = Depends(get_db)
):
    
    user = db.query(
        models.Users
        ).filter(
            models.Users.user_id == body.user_id
            ).first()
    
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User not found!"
        )
    
    newpost = models.Posts(
        user_id = body.user_id,
        caption = body.caption
    )

    db.add(newpost)
    db.commit()

    return {"message": f"Post created by user {body.user_id}"}

@app.post("/like")
def like_a_post(
    body: schemas.PostLike, 
    db: Session = Depends(get_db)
):
    
    post = db.query(
        models.Posts
        ).filter(
            models.Posts.id == body.post_id
            ).first()
    
    if not post:
        raise HTTPException(
            status_code=404, 
            detail="Post not found!"
        )
    
    user = db.query(
        models.Users
        ).filter(
            models.Users.user_id == body.user_id
            ).first()
    
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User not found!"
        )
    
    checkBeforeLike = db.query(
        models.Likes
        ).filter(
            models.Likes.user_id == body.user_id, 
            models.Likes.post_id == body.post_id
            ).first()
    
    if checkBeforeLike:
        raise HTTPException(
            status_code=409, 
            detail="cannot like a post twice!"
        )

    ob = models.Likes(
        user_id = body.user_id,
        post_id = body.post_id
    )
    db.add(ob)
    db.commit()

    return {"message": f"{body.user_id} like post with id: {body.post_id}"}

@app.get(
        "/feed/{user}", 
        response_model=schemas.FeedResponse
)
def load_feed(
    user: int, 
    limit: int = 10,
    before_time: datetime | None = None,
    db: Session = Depends(get_db)
):
    
    query = db.query(
        models.Posts
        ).join(
            models.Follows, 
            models.Follows.follower_id == models.Posts.user_id
            ).filter(
                models.Follows.follower_id == user
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
    }