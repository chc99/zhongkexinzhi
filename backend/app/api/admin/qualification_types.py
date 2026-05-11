from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.models.qualification_type import QualificationType
from app.schemas.qualification import QualificationTypeCreate, QualificationTypeUpdate, QualificationTypeInfo
from app.utils.response import success
from app.utils.exceptions import NotFoundException

admin_qual_type_router = APIRouter(tags=["超管-资质类型"])


@admin_qual_type_router.get("/admin/qualification-types")
def admin_qual_type_list(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    items = db.query(QualificationType).order_by(QualificationType.sort_order).all()
    return success([QualificationTypeInfo.model_validate(t).model_dump() for t in items])


@admin_qual_type_router.post("/admin/qualification-types")
def admin_qual_type_create(data: QualificationTypeCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    t = QualificationType(**data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return success({"id": t.id})


@admin_qual_type_router.put("/admin/qualification-types/{type_id}")
def admin_qual_type_update(type_id: int, data: QualificationTypeUpdate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    t = db.query(QualificationType).filter(QualificationType.id == type_id).first()
    if not t:
        raise NotFoundException("资质类型不存在")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(t, field, value)
    db.commit()
    return success(message="更新成功")


@admin_qual_type_router.delete("/admin/qualification-types/{type_id}")
def admin_qual_type_delete(type_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    t = db.query(QualificationType).filter(QualificationType.id == type_id).first()
    if not t:
        raise NotFoundException("资质类型不存在")
    db.delete(t)
    db.commit()
    return success(message="删除成功")
