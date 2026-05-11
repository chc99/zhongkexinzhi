from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import require_reviewer
from app.models.user import User
from app.models.product import Product, ProductStatus
from app.schemas.audit import RejectRequest, BatchIdsRequest
from app.schemas.product import ProductListInfo, ProductDetailInfo, ProductImageSchema
from app.services.audit_service import (
    list_review_products, approve_product, reject_product,
    batch_approve, batch_reject
)
from app.services.product_service import get_product
from app.utils.response import success, page_result

reviewer_router = APIRouter(tags=["审核员"])


@reviewer_router.get("/reviewer/products")
def reviewer_product_list(
    status: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    merchant_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("submit_at"),
    db: Session = Depends(get_db),
    user: User = Depends(require_reviewer),
):
    items, total = list_review_products(
        db, status, category_id, merchant_id, keyword,
        date_from, date_to, page, page_size, sort_by
    )
    result = []
    for p in items:
        result.append(ProductListInfo(
            id=p.id, name=p.name, brand=p.brand,
            price=p.price, stock=p.stock, main_image=p.main_image,
            status=p.status.value, submit_at=p.submit_at, created_at=p.created_at,
        ).model_dump())
    return page_result(result, total, page, page_size)


@reviewer_router.get("/reviewer/products/{product_id}")
def reviewer_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_reviewer),
):
    p = get_product(db, product_id)
    compliance = None
    if p.compliance:
        compliance = {
            c.name: getattr(p.compliance, c.name)
            for c in p.compliance.__table__.columns
            if c.name not in ("id", "product_id")
        }
    return success(ProductDetailInfo(
        id=p.id, merchant_id=p.merchant_id, category_id=p.category_id,
        name=p.name, brand=p.brand, spec=p.spec,
        price=p.price, stock=p.stock, main_image=p.main_image,
        status=p.status.value, reject_reason=p.reject_reason,
        submit_at=p.submit_at, audit_at=p.audit_at, audit_by=p.audit_by,
        version=p.version, created_at=p.created_at, updated_at=p.updated_at,
        compliance=compliance,
        images=[ProductImageSchema.model_validate(img) for img in (p.images or [])],
        detail=p.detail.content if p.detail else None,
    ).model_dump())


@reviewer_router.post("/reviewer/products/{product_id}/approve")
def reviewer_product_approve(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_reviewer),
):
    p = get_product(db, product_id)
    approve_product(db, p, user.id)
    return success(message="审核通过")


@reviewer_router.post("/reviewer/products/{product_id}/reject")
def reviewer_product_reject(
    product_id: int, req: RejectRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_reviewer),
):
    p = get_product(db, product_id)
    reject_product(db, p, user.id, req.reason)
    return success(message="已驳回")


@reviewer_router.post("/reviewer/products/batch-approve")
def reviewer_batch_approve(
    req: BatchIdsRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_reviewer),
):
    count = batch_approve(db, req.ids, user.id)
    return success({"count": count})


@reviewer_router.post("/reviewer/products/batch-reject")
def reviewer_batch_reject(
    req: BatchIdsRequest,
    reason: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_reviewer),
):
    count = batch_reject(db, req.ids, user.id, reason)
    return success({"count": count})


@reviewer_router.get("/reviewer/dashboard")
def reviewer_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_reviewer),
):
    pending = db.query(Product).filter(Product.status == ProductStatus.pending_review).count()
    approved_today = db.query(Product).filter(
        Product.status == ProductStatus.approved, Product.audit_by == user.id
    ).count()
    rejected_today = db.query(Product).filter(
        Product.status == ProductStatus.rejected, Product.audit_by == user.id
    ).count()
    return success({
        "pending_count": pending, "approved_today": approved_today, "rejected_today": rejected_today
    })
