from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app import models
from sqlalchemy.orm import Session

from app.oauth import get_current_user

router = APIRouter()


@router.post("/follows/{user2}")
def follow_user(
    user2: int,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)
):
    
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
    
    if current_user.user_id == user2:
        raise HTTPException(
            status_code=400, 
            detail="following self is not allowed"
        )
    
    checkBeforeFollow = db.query(
        models.Follows
        ).filter(
            models.Follows.follower_id == current_user.user_id, 
            models.Follows.following_id == user2
            ).first()
    
    if checkBeforeFollow:
        raise HTTPException(
            status_code=409, 
            detail="cannot follower a user more than 1 time"
        )
    
    ob = models.Follows(
        follower_id=current_user.user_id,
        following_id=user2
    )

    db.add(ob)
    db.commit()

    return {"message": f"{current_user.user_id} follows {user2}"}
