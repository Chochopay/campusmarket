from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.schemas import UserResponse, RoleChange
from app.users.models import User
from app.auth.dependencies import get_current_user, require_admin



router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/{user_id}", response_model=UserResponse)
def change_user_role(user_id: int,
                     data: RoleChange,
                     current_user: User = Depends(require_admin),
                     db: Session = Depends(get_db)
                     ):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Такого пользователя не существует"
        )
    if data.role != "admin" and user.role == "admin":
        other_admin = db.execute(select(User).where(User.role == "admin",
                                                    User.id != user_id)).scalars().first()
        if not other_admin:
            raise HTTPException(
                status_code=409,
                detail="Вы не можете понизить единственного админа"
            )
    if data.role == user.role:
        raise HTTPException(
            status_code=409,
            detail="У пользователя уже стоит такая роль"
        )

    user.role = data.role
    db.commit()
    db.refresh(user)
    return user