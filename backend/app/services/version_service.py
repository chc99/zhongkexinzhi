from sqlalchemy.orm import Session
from app.models.product_version import ProductVersion, ChangeType
from app.models.product import Product
from app.services.product_service import build_product_snapshot


def save_version(db: Session, product: Product, change_type: ChangeType, changed_by: int, remark: str = ""):
    snapshot = build_product_snapshot(product)
    version = ProductVersion(
        product_id=product.id, version=product.version, snapshot_json=snapshot,
        change_type=change_type, changed_by=changed_by, remark=remark
    )
    db.add(version)
    db.flush()
    return version


def get_versions(db: Session, product_id: int):
    return db.query(ProductVersion).filter(
        ProductVersion.product_id == product_id
    ).order_by(ProductVersion.created_at.desc()).all()
