from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.auth.schemas import UserResponse, UserCreate, UserLogin, UserLoginResponse
from app.auth.utils import hash_password, verify_password, create_access_token, normalize_username
from app.database import get_db
from app.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    data.username = normalize_username(data.username)
    result = db.execute(select(User).where(User.username==data.username)).scalar_one_or_none()
    if result:
         raise HTTPException(
            status_code=409,
            detail="Такой пользователь уже существует"
        )
    else:
        hashed_password = hash_password(data.password)
        new_user = User(
            username=data.username,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    return new_user


@router.post("/login", response_model=UserLoginResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    data.username = normalize_username(data.username)
    db_user = db.execute(select(User).where(User.username == data.username)).scalar_one_or_none()
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Логин или пароль неверный"
        )
    if not verify_password(data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Логин или пароль неверный"
        )
    subject = {"sub": str(db_user.id)}
    jwt_token = create_access_token(subject)
    return {"jwt_token" : jwt_token}




