from sqlalchemy.orm import Session
from app.models.merchant_qualification import MerchantQualification
from app.models.product_qualification import ProductQualification
from app.utils.exceptions import NotFoundException


def list_merchant_qualifications(db: Session, merchant_id: int):
    return db.query(MerchantQualification).filter(
        MerchantQualification.merchant_id == merchant_id
    ).order_by(MerchantQualification.created_at.desc()).all()


def get_merchant_qualification(db: Session, qual_id: int, merchant_id: int):
    q = db.query(MerchantQualification).filter(
        MerchantQualification.id == qual_id,
        MerchantQualification.merchant_id == merchant_id
    ).first()
    if not q:
        raise NotFoundException("资质不存在")
    return q


def create_merchant_qualification(db: Session, merchant_id: int, qual_type_id: int,
                                  file_url: str, file_name: str = "", expire_date=None):
    q = MerchantQualification(
        merchant_id=merchant_id, qual_type_id=qual_type_id,
        file_url=file_url, file_name=file_name, expire_date=expire_date
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def update_merchant_qualification(db: Session, qual: MerchantQualification,
                                  file_url=None, file_name=None, expire_date=None):
    if file_url:
        qual.file_url = file_url
    if file_name:
        qual.file_name = file_name
    qual.expire_date = expire_date
    db.commit()
    return qual


def delete_merchant_qualification(db: Session, qual: MerchantQualification):
    db.delete(qual)
    db.commit()


def list_product_qualifications(db: Session, product_id: int):
    return db.query(ProductQualification).filter(
        ProductQualification.product_id == product_id
    ).order_by(ProductQualification.created_at.desc()).all()


def create_product_qualification(db: Session, product_id: int, qual_type_id: int,
                                 file_url: str, file_name: str = "", expire_date=None):
    q = ProductQualification(
        product_id=product_id, qual_type_id=qual_type_id,
        file_url=file_url, file_name=file_name, expire_date=expire_date
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def get_product_qualification(db: Session, qual_id: int, product_id: int):
    q = db.query(ProductQualification).filter(
        ProductQualification.id == qual_id,
        ProductQualification.product_id == product_id
    ).first()
    if not q:
        raise NotFoundException("资质不存在")
    return q


def delete_product_qualification(db: Session, qual: ProductQualification):
    db.delete(qual)
    db.commit()
