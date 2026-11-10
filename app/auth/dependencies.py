from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.auth.utils import decode_access_token
from app.users.models import User

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    user = db.execute(select(User).where(User.id == int(user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code = 401,
            detail = "Пользователь не найден"
        )
    return user

def is_moder_or_admin(role: str) -> bool:
    return role in ("moderator", "admin")



def require_moderator_or_admin(user: User = Depends(get_current_user)):
    if not is_moder_or_admin(user.role):
        raise HTTPException(
            status_code=403,
            detail="У вас недостаточно прав для выполнения этих действий"
        )
    return user

def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="У вас недостаточно прав для выполнения этих действий"
        )
    return user

def get_optional_user(credentials: HTTPAuthorizationCredentials | None = Depends(optional_security), db: Session = Depends(get_db)):

    if credentials is None:
        return None

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except HTTPException:
        return None
    user_id = int(payload.get("sub"))
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    return user


def detect_image_type(content: bytes) -> str | None:
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return None
