from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.category import Category, CategoryStatus
from app.models.qualification_type import QualificationType
from app.schemas.category import CategoryInfo
from app.utils.response import success

categories_router = APIRouter(tags=["品类字典"])


@categories_router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).filter(
        Category.status == CategoryStatus.active
    ).order_by(Category.sort_order).all()
    result = []
    for cat in categories:
        if cat.parent_id is None:
            result.append(_build_tree(cat, categories))
    return success(result)


def _build_tree(cat: Category, all_cats: list) -> dict:
    children = [_build_tree(c, all_cats) for c in all_cats if c.parent_id == cat.id]
    info = CategoryInfo.model_validate(cat)
    info.children = children
    return info.model_dump()


@categories_router.get("/qualification-types")
def get_qualification_types(scope: Optional[str] = Query(None), db: Session = Depends(get_db)):
    q = db.query(QualificationType)
    if scope:
        q = q.filter(QualificationType.scope == scope)
    items = q.order_by(QualificationType.sort_order).all()
    return success([
        {
            "id": t.id, "name": t.name, "code": t.code,
            "description": t.description or "",
            "is_required": t.is_required, "scope": t.scope.value,
            "sort_order": t.sort_order
        }
        for t in items
    ])
