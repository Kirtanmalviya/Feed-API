from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from app.database import get_db
from app import models, schemas
from app.oauth import  get_current_user
from sqlalchemy.orm import Session

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

    


