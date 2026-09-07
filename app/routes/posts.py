from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.oauth import get_current_user


router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post("/")
def create_post( # pyright: ignore[reportUnknownParameterType]
    body: schemas.PostCreate, 
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)
):
    
    newpost = models.Posts(
        user_id = current_user.user_id,
        caption = body.caption
    )

    db.add(newpost)
    db.commit()

    return {
        "id": newpost.id,
        "user_id": newpost.user_id,
        "caption": newpost.caption,
        "created_at": newpost.created_at
    } # pyright: ignore[reportUnknownVariableType]

@router.delete("/{post_id}")
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)
):

    post = db.query(models.Posts).filter(models.Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post was not found")
    
    if post.user_id != current_user.user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="only can delte own posts!")
    
    post_media = db.query(
        models.PostMedia
        ).filter(
            models.PostMedia.post_id == post_id
            ).all()
    

    
    post_likes = db.query(
        models.Likes
        ).filter(
            models.Likes.post_id == post_id
            ).all()

    media_paths: list[Path] = [] 

    for media in post_media:
        media_paths.append(Path(media.storage_path))
        db.delete(media)
    
    for like in post_likes:
        db.delete(like)
    
    db.delete(post)
    db.commit()

    for media_path in media_paths:
        if media_path.exists():
            media_path.unlink()
    
    return {"message": "Post deleted successfully"}

@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Posts).filter(models.Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail=f"post with id: {post_id} was not found")
    
    return post

@router.patch("/{post_id}", response_model=schemas.PostResponse)
def update_post( # type: ignore
    body: schemas.PostCreate,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)
):
    
    post = db.query(models.Posts).filter(models.Posts.id == post_id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="post was not found")
    
    if post.user_id != current_user.user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="not allowed to update other's post")
    
    post.caption = body.caption

    db.commit()

    db.refresh(post)

    return {
        "id": post.id,
        "user_id": current_user.user_id,
        "caption": post.caption,
        "created_at": post.created_at,
        "media": post.media
    }  #type: ignore