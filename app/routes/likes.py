from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.oauth import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Likes"],
)

@router.post("/like")
def like_a_post(
    body: schemas.PostLike, 
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)
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
    
    checkBeforeLike = db.query(
        models.Likes
        ).filter(
            models.Likes.user_id == current_user.user_id, 
            models.Likes.post_id == body.post_id
            ).first()
    
    if checkBeforeLike:
        raise HTTPException(
            status_code=409, 
            detail="cannot like a post twice!"
        )

    ob = models.Likes(
        user_id = current_user.user_id,
        post_id = body.post_id
    )
    db.add(ob)
    db.commit()

    return {"message": f"{current_user.user_id} like post with id: {body.post_id}"}
