from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.product import Product, ProductStatus
from app.models.audit_log import AuditLog, AuditAction
from app.models.product_version import ProductVersion, ChangeType
from app.utils.exceptions import BadRequestException
from app.services.product_service import build_product_snapshot


def list_review_products(
    db: Session, status: Optional[str] = None, category_id: Optional[int] = None,
    merchant_id: Optional[int] = None, keyword: Optional[str] = None,
    date_from: Optional[str] = None, date_to: Optional[str] = None,
    page: int = 1, page_size: int = 20, sort_by: str = "submit_at"
):
    q = db.query(Product).filter(
        Product.status.in_([ProductStatus.pending_review, ProductStatus.approved, ProductStatus.rejected])
    )
    if status:
        q = q.filter(Product.status == status)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if merchant_id:
        q = q.filter(Product.merchant_id == merchant_id)
    if keyword:
        q = q.filter(Product.name.contains(keyword))
    if date_from:
        q = q.filter(Product.submit_at >= datetime.fromisoformat(date_from))
    if date_to:
        q = q.filter(Product.submit_at <= datetime.fromisoformat(date_to))

    if sort_by == "submit_at":
        q = q.order_by(Product.submit_at.desc())
    else:
        q = q.order_by(Product.updated_at.desc())

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def approve_product(db: Session, product: Product, reviewer_id: int):
    if product.status != ProductStatus.pending_review:
        raise BadRequestException("仅待审核商品可通过")
    product.status = ProductStatus.approved
    product.audit_at = datetime.utcnow()
    product.audit_by = reviewer_id
    product.version += 1
    product.updated_at = datetime.utcnow()

    snapshot = build_product_snapshot(product)
    db.add(AuditLog(product_id=product.id, reviewer_id=reviewer_id, action=AuditAction.approve))
    db.add(ProductVersion(
        product_id=product.id, version=product.version, snapshot_json=snapshot,
        change_type=ChangeType.approve, changed_by=reviewer_id
    ))
    db.commit()
    return product


def reject_product(db: Session, product: Product, reviewer_id: int, reason: str):
    if product.status != ProductStatus.pending_review:
        raise BadRequestException("仅待审核商品可驳回")
    product.status = ProductStatus.rejected
    product.reject_reason = reason
    product.audit_at = datetime.utcnow()
    product.audit_by = reviewer_id
    product.version += 1
    product.updated_at = datetime.utcnow()

    snapshot = build_product_snapshot(product)
    db.add(AuditLog(product_id=product.id, reviewer_id=reviewer_id, action=AuditAction.reject, reason=reason))
    db.add(ProductVersion(
        product_id=product.id, version=product.version, snapshot_json=snapshot,
        change_type=ChangeType.reject, changed_by=reviewer_id, remark=reason
    ))
    db.commit()
    return product


def batch_approve(db: Session, product_ids: List[int], reviewer_id: int):
    products = db.query(Product).filter(
        Product.id.in_(product_ids),
        Product.status == ProductStatus.pending_review
    ).all()
    for p in products:
        approve_product(db, p, reviewer_id)
    return len(products)


def batch_reject(db: Session, product_ids: List[int], reviewer_id: int, reason: str):
    products = db.query(Product).filter(
        Product.id.in_(product_ids),
        Product.status == ProductStatus.pending_review
    ).all()
    for p in products:
        reject_product(db, p, reviewer_id, reason)
    return len(products)
