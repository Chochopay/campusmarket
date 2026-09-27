from fastapi import APIRouter, Depends
from app.auth.schemas import UserResponse
from app.users.models import User
from app.auth.dependencies import get_current_user



router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user