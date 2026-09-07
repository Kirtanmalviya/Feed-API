from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.oauth import get_current_user

MEDIA_DIR = Path("media/post_media")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(
    prefix="/posts",
    tags=["Post Media"]
)

@router.post("/{post_id}/media")
def upload_post_media(
    post_id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)
):

    post = db.query(models.Posts).filter(models.Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post was not found")
    
    if post.user_id != current_user.user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="can post media to own posts!")
    
    allowed_types = ["image/jpeg","image/png","image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="file type must be jpeg or png or webp")
    
    max_size = 2 * 1024 * 1024

    file.file.seek(0,2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > max_size:
        raise HTTPException(status_code=400, detail="file size must be less than 2MB")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename is missing")
    
    
    file_extension = Path(file.filename).suffix

    unique_filename = f"post_{post_id}_{uuid.uuid4()}{file_extension}"

    file_path = MEDIA_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    ob = models.PostMedia(
        post_id=post_id,
        media_type=models.MediaType.IMAGE,
        storage_path=str(file_path),
        status=models.MediaStatus.READY
    )

    db.add(ob)
    db.commit()
    db.refresh(ob)

    return ob