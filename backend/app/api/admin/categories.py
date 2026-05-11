from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.utils.response import success
from app.utils.exceptions import NotFoundException

admin_category_router = APIRouter(tags=["超管-品类"])


@admin_category_router.post("/admin/categories")
def admin_category_create(data: CategoryCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    cat = Category(
        parent_id=data.parent_id, name=data.name, description=data.description,
        sort_order=data.sort_order, created_by=user.id
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return success({"id": cat.id})


@admin_category_router.put("/admin/categories/{cat_id}")
def admin_category_update(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise NotFoundException("品类不存在")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cat, field, value)
    db.commit()
    return success(message="更新成功")


@admin_category_router.delete("/admin/categories/{cat_id}")
def admin_category_delete(cat_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise NotFoundException("品类不存在")
    children = db.query(Category).filter(Category.parent_id == cat_id).count()
    if children > 0:
        return success(message="请先删除子品类")
    db.delete(cat)
    db.commit()
    return success(message="删除成功")
