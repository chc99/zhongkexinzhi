from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.services.auth_service import authenticate, create_token
from app.dependencies import get_current_user
from app.utils.response import success

auth_router = APIRouter(tags=["认证"])


@auth_router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, req.username, req.password)
    token = create_token(user.id, user.username, user.role.value)
    return success(LoginResponse(
        token=token, username=user.username, role=user.role.value, user_id=user.id
    ).model_dump())


@auth_router.post("/auth/logout")
def logout(user=Depends(get_current_user)):
    return success(message="已退出")


@auth_router.get("/auth/me")
def me(user=Depends(get_current_user)):
    return success(UserInfo.model_validate(user).model_dump())
