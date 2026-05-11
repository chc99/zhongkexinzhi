from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.models.product import Product, ProductStatus
from app.models.product_compliance import ProductCompliance
from app.models.product_image import ProductImage
from app.models.product_detail import ProductDetail
from app.schemas.product import ProductCreate, ProductUpdate
from app.utils.exceptions import NotFoundException, BadRequestException


def list_products(
    db: Session, merchant_id: int,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1, page_size: int = 20
):
    q = db.query(Product).filter(Product.merchant_id == merchant_id)
    if status:
        q = q.filter(Product.status == status)
    if keyword:
        q = q.filter(Product.name.contains(keyword))
    total = q.count()
    items = q.order_by(Product.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_product(db: Session, product_id: int, merchant_id: Optional[int] = None) -> Product:
    q = db.query(Product).options(
        joinedload(Product.compliance),
        joinedload(Product.images),
        joinedload(Product.detail),
        joinedload(Product.qualifications),
    ).filter(Product.id == product_id)
    if merchant_id:
        q = q.filter(Product.merchant_id == merchant_id)
    product = q.first()
    if not product:
        raise NotFoundException("商品不存在")
    return product


def create_product(db: Session, merchant_id: int, data: ProductCreate) -> Product:
    product = Product(merchant_id=merchant_id, **data.model_dump())
    db.add(product)
    db.flush()
    db.add(ProductCompliance(product_id=product.id))
    db.add(ProductDetail(product_id=product.id))
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    compliance_data = None
    if data.compliance:
        compliance_data = data.compliance
        data = data.model_dump(exclude={"compliance"}, exclude_unset=True)
    else:
        data = data.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(product, field, value)

    if compliance_data:
        comp = db.query(ProductCompliance).filter(ProductCompliance.product_id == product.id).first()
        for field, value in compliance_data.model_dump().items():
            setattr(comp, field, value)

    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product):
    if product.status != ProductStatus.draft:
        raise BadRequestException("仅草稿状态可删除")
    db.delete(product)
    db.commit()


def build_product_snapshot(product: Product) -> dict:
    product_dict = {
        "name": product.name, "brand": product.brand, "spec": product.spec,
        "price": str(product.price), "stock": product.stock, "main_image": product.main_image,
        "category_id": product.category_id,
    }
    if product.compliance:
        product_dict["compliance"] = {
            c.name: getattr(product.compliance, c.name)
            for c in product.compliance.__table__.columns
            if c.name not in ("id", "product_id")
        }
    if product.images:
        product_dict["images"] = [
            {"image_type": img.image_type.value, "file_url": img.file_url, "sort_order": img.sort_order}
            for img in product.images
        ]
    if product.detail:
        product_dict["detail"] = product.detail.content
    return product_dict
