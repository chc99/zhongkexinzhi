from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import require_merchant
from app.models.user import User
from app.models.product import Product, ProductStatus
from app.models.product_image import ProductImage, ImageType
from app.models.product_version import ChangeType
from app.models.merchant_qualification import MerchantQualification
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductListInfo, ProductDetailInfo,
    ProductSubmitResponse, ProductImageSchema
)
from app.services.product_service import (
    list_products, get_product, create_product, update_product, delete_product
)
from app.services.qualification_service import (
    list_product_qualifications, create_product_qualification,
    get_product_qualification, delete_product_qualification
)
from app.services.version_service import save_version, get_versions
from app.schemas.qualification import QualificationCreate, QualificationInfo
from app.schemas.audit import VersionInfo
from app.utils.response import success, page_result
from app.utils.exceptions import BadRequestException, NotFoundException

# IMPORTANT: This must be named merchant_product_router to match main.py lazy loading
merchant_product_router = APIRouter(tags=["商家-商品"])


# ===== Product CRUD =====

@merchant_product_router.get("/merchant/products")
def merchant_product_list(
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    items, total = list_products(db, user.id, status, keyword, page, page_size)
    result = []
    for p in items:
        result.append(ProductListInfo(
            id=p.id, name=p.name, brand=p.brand,
            price=p.price, stock=p.stock, main_image=p.main_image,
            status=p.status.value, submit_at=p.submit_at,
            created_at=p.created_at,
        ).model_dump())
    return page_result(result, total, page, page_size)


@merchant_product_router.post("/merchant/products")
def merchant_product_create(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    product = create_product(db, user.id, data)
    return success({"id": product.id, "status": product.status.value})


@merchant_product_router.get("/merchant/products/{product_id}")
def merchant_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    p = get_product(db, product_id, user.id)
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


@merchant_product_router.put("/merchant/products/{product_id}")
def merchant_product_update(
    product_id: int, data: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    p = get_product(db, product_id, user.id)
    product = update_product(db, p, data)
    return success({"id": product.id, "status": product.status.value})


@merchant_product_router.delete("/merchant/products/{product_id}")
def merchant_product_delete(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    p = get_product(db, product_id, user.id)
    delete_product(db, p)
    return success(message="删除成功")


# ===== Product Submission =====

@merchant_product_router.post("/merchant/products/{product_id}/submit")
def merchant_product_submit(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    p = get_product(db, product_id, user.id)
    if p.status != ProductStatus.draft and p.status != ProductStatus.rejected:
        raise BadRequestException("仅草稿或驳回状态可提交审核")
    change_type = ChangeType.submit if p.status == ProductStatus.draft else ChangeType.resubmit
    p.status = ProductStatus.pending_review
    p.submit_at = datetime.utcnow()
    p.updated_at = datetime.utcnow()
    save_version(db, p, change_type, user.id)
    db.commit()
    return success(ProductSubmitResponse(id=p.id, status=p.status.value, version=p.version).model_dump())


# ===== Product Images =====

@merchant_product_router.post("/merchant/products/{product_id}/images")
def merchant_product_add_image(
    product_id: int, image: ProductImageSchema,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    get_product(db, product_id, user.id)
    img = ProductImage(
        product_id=product_id, image_type=ImageType(image.image_type),
        file_url=image.file_url, sort_order=image.sort_order
    )
    db.add(img)
    db.commit()
    return success({"id": img.id})


@merchant_product_router.delete("/merchant/products/{product_id}/images/{image_id}")
def merchant_product_delete_image(
    product_id: int, image_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    get_product(db, product_id, user.id)
    img = db.query(ProductImage).filter(
        ProductImage.id == image_id, ProductImage.product_id == product_id
    ).first()
    if not img:
        raise NotFoundException("图片不存在")
    db.delete(img)
    db.commit()
    return success(message="删除成功")


# ===== Version History =====

@merchant_product_router.get("/merchant/products/{product_id}/versions")
def merchant_product_versions(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    get_product(db, product_id, user.id)
    versions = get_versions(db, product_id)
    return success([VersionInfo.model_validate(v).model_dump() for v in versions])


# ===== Product Qualifications =====

@merchant_product_router.get("/merchant/products/{product_id}/qualifications")
def merchant_product_qual_list(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    get_product(db, product_id, user.id)
    quals = list_product_qualifications(db, product_id)
    return success([QualificationInfo.model_validate(q).model_dump() for q in quals])


@merchant_product_router.post("/merchant/products/{product_id}/qualifications")
def merchant_product_qual_create(
    product_id: int, data: QualificationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    get_product(db, product_id, user.id)
    q = create_product_qualification(db, product_id, data.qual_type_id, data.file_url, data.file_name, data.expire_date)
    return success({"id": q.id})


@merchant_product_router.delete("/merchant/products/{product_id}/qualifications/{qual_id}")
def merchant_product_qual_delete(
    product_id: int, qual_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    get_product(db, product_id, user.id)
    q = get_product_qualification(db, qual_id, product_id)
    delete_product_qualification(db, q)
    return success(message="删除成功")


# ===== Dashboard =====

@merchant_product_router.get("/merchant/dashboard")
def merchant_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    total = db.query(Product).filter(Product.merchant_id == user.id).count()
    pending = db.query(Product).filter(
        Product.merchant_id == user.id, Product.status == ProductStatus.pending_review
    ).count()
    approved = db.query(Product).filter(
        Product.merchant_id == user.id, Product.status == ProductStatus.approved
    ).count()
    rejected = db.query(Product).filter(
        Product.merchant_id == user.id, Product.status == ProductStatus.rejected
    ).count()
    expiring = db.query(MerchantQualification).filter(
        MerchantQualification.merchant_id == user.id,
        MerchantQualification.status == "expiring"
    ).count()
    expired = db.query(MerchantQualification).filter(
        MerchantQualification.merchant_id == user.id,
        MerchantQualification.status == "expired"
    ).count()
    return success({
        "total_products": total, "pending_products": pending,
        "approved_products": approved, "rejected_products": rejected,
        "expiring_quals": expiring, "expired_quals": expired,
    })
