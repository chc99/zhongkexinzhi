from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import decode_token
from app.models.user import User
from app.utils.exceptions import UnauthorizedException, ForbiddenException


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("认证格式错误")
    token = authorization[7:]
    payload = decode_token(token)
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise UnauthorizedException("用户不存在")
    if user.status.value == "disabled":
        raise UnauthorizedException("账号已被禁用")
    return user


def require_merchant(user: User = Depends(get_current_user)) -> User:
    if user.role.value != "merchant":
        raise ForbiddenException("仅商家可操作")
    return user


def require_reviewer(user: User = Depends(get_current_user)) -> User:
    if user.role.value != "reviewer":
        raise ForbiddenException("仅审核员可操作")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role.value != "admin":
        raise ForbiddenException("仅超管可操作")
    return user
