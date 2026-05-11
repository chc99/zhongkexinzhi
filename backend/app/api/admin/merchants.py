from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User, UserRole, UserStatus
from app.services.auth_service import hash_password
from app.utils.response import success, page_result
from app.utils.exceptions import NotFoundException

admin_merchant_router = APIRouter(tags=["超管-商家"])


@admin_merchant_router.get("/admin/merchants")
def admin_merchant_list(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), user: User = Depends(require_admin)
):
    q = db.query(User).filter(User.role == UserRole.merchant)
    total = q.count()
    items = q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return page_result(
        [{"id": u.id, "username": u.username, "phone": u.phone, "status": u.status.value, "created_at": u.created_at.isoformat()} for u in items],
        total, page, page_size
    )


@admin_merchant_router.put("/admin/merchants/{merchant_id}/status")
def admin_merchant_status(merchant_id: int, status: str = Query(...), db: Session = Depends(get_db), user: User = Depends(require_admin)):
    m = db.query(User).filter(User.id == merchant_id, User.role == UserRole.merchant).first()
    if not m:
        raise NotFoundException("商家不存在")
    m.status = UserStatus(status)
    db.commit()
    return success(message="更新成功")


@admin_merchant_router.get("/admin/reviewers")
def admin_reviewer_list(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), user: User = Depends(require_admin)
):
    q = db.query(User).filter(User.role == UserRole.reviewer)
    total = q.count()
    items = q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return page_result(
        [{"id": u.id, "username": u.username, "phone": u.phone, "status": u.status.value, "created_at": u.created_at.isoformat()} for u in items],
        total, page, page_size
    )


@admin_merchant_router.post("/admin/reviewers")
def admin_reviewer_create(
    username: str = Query(...), password: str = Query(...), phone: str = Query(""),
    db: Session = Depends(get_db), user: User = Depends(require_admin)
):
    exists = db.query(User).filter(User.username == username).first()
    if exists:
        return success(message="用户名已存在")
    reviewer = User(username=username, password_hash=hash_password(password), role=UserRole.reviewer, phone=phone)
    db.add(reviewer)
    db.commit()
    return success({"id": reviewer.id})
