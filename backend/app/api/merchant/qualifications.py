from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_merchant
from app.models.user import User
from app.schemas.qualification import QualificationCreate, QualificationUpdate, QualificationInfo
from app.services.qualification_service import (
    list_merchant_qualifications, get_merchant_qualification,
    create_merchant_qualification, update_merchant_qualification, delete_merchant_qualification
)
from app.utils.response import success

merchant_qual_router = APIRouter(tags=["商家-资质"])


@merchant_qual_router.get("/merchant/qualifications")
def merchant_qual_list(db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    quals = list_merchant_qualifications(db, user.id)
    return success([QualificationInfo.model_validate(q).model_dump() for q in quals])


@merchant_qual_router.post("/merchant/qualifications")
def merchant_qual_create(data: QualificationCreate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    q = create_merchant_qualification(db, user.id, data.qual_type_id, data.file_url, data.file_name, data.expire_date)
    return success({"id": q.id})


@merchant_qual_router.put("/merchant/qualifications/{qual_id}")
def merchant_qual_update(qual_id: int, data: QualificationUpdate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    q = get_merchant_qualification(db, qual_id, user.id)
    update_merchant_qualification(db, q, data.file_url, data.file_name, data.expire_date)
    return success(message="更新成功")


@merchant_qual_router.delete("/merchant/qualifications/{qual_id}")
def merchant_qual_delete(qual_id: int, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    q = get_merchant_qualification(db, qual_id, user.id)
    delete_merchant_qualification(db, q)
    return success(message="删除成功")
