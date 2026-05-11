from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProductComplianceSchema(BaseModel):
    approval_number: str = ""
    main_ingredients: str = ""
    efficacy_ingredients: str = ""
    suitable_population: str = ""
    unsuitable_population: str = ""
    health_function: str = ""
    usage_dosage: str = ""
    shelf_life: str = ""
    storage_method: str = ""
    precautions: str = ""


class ProductImageSchema(BaseModel):
    id: Optional[int] = None
    image_type: str
    file_url: str
    sort_order: int = 0

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(..., min_length=1, max_length=200)
    brand: str = ""
    spec: str = ""
    price: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    main_image: str = ""


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=200)
    brand: Optional[str] = None
    spec: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    main_image: Optional[str] = None
    compliance: Optional[ProductComplianceSchema] = None


class ProductListInfo(BaseModel):
    id: int
    name: str
    brand: str
    category_name: str = ""
    price: Decimal
    stock: int
    main_image: str
    status: str
    submit_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductDetailInfo(BaseModel):
    id: int
    merchant_id: int
    category_id: int
    name: str
    brand: str
    spec: str
    price: Decimal
    stock: int
    main_image: str
    status: str
    reject_reason: Optional[str] = None
    submit_at: Optional[datetime] = None
    audit_at: Optional[datetime] = None
    audit_by: Optional[int] = None
    version: int
    created_at: datetime
    updated_at: datetime
    compliance: Optional[ProductComplianceSchema] = None
    images: List[ProductImageSchema] = []
    detail: Optional[str] = None

    class Config:
        from_attributes = True


class ProductSubmitResponse(BaseModel):
    id: int
    status: str
    version: int
