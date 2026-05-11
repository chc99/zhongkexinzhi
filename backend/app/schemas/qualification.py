from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class QualificationCreate(BaseModel):
    qual_type_id: int
    file_url: str
    file_name: str = ""
    expire_date: Optional[date] = None


class QualificationUpdate(BaseModel):
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    expire_date: Optional[date] = None


class QualificationInfo(BaseModel):
    id: int
    qual_type_id: int
    qual_type_name: str = ""
    file_url: str
    file_name: str
    expire_date: Optional[date] = None
    status: str
    remark: str = ""
    created_at: datetime

    class Config:
        from_attributes = True


class QualificationTypeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: str = ""
    is_required: bool = True
    scope: str = "merchant"
    sort_order: int = 0


class QualificationTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    scope: Optional[str] = None
    sort_order: Optional[int] = None


class QualificationTypeInfo(BaseModel):
    id: int
    name: str
    code: str
    description: str
    is_required: bool
    scope: str
    sort_order: int

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_products: int = 0
    pending_products: int = 0
    approved_products: int = 0
    rejected_products: int = 0
    expiring_quals: int = 0
    expired_quals: int = 0
