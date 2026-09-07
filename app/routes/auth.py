from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models
from app.oauth import get_current_user, hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", response_model=schemas.UserCreateResponse)
def create_user( # pyright: ignore[reportUnknownParameterType]
    body: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    checkBeforeRegisteration = db.query(models.Users).filter(or_(models.Users.email == body.email, models.Users.username == body.username)).first()
    if checkBeforeRegisteration:
        raise HTTPException(status_code=400, detail="username or email is already taken!")
    
    password_hash = hash_password(body.password)

    new_user = models.Users(
        username = body.username,
        email = body.email,
        hashed_password = password_hash
    )

    db.add(new_user)
    db.commit()

    return {
        "id": new_user.user_id,
        "username": new_user.username,
        "email": new_user.email
    } # pyright: ignore[reportUnknownVariableType]


@router.post("/login")
def login_user(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.email == credentials.email).first()
    if not user or not verify_password(credentials.password ,user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    access_token = create_access_token(user.user_id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def get_me(user: models.Users = Depends(get_current_user)):
    return user