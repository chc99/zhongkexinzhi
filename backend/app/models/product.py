from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, Text, Enum as SAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.database import Base
import enum


class ProductStatus(str, enum.Enum):
    draft = "draft"
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), default="")
    spec: Mapped[str] = mapped_column(String(100), default="")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    main_image: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[ProductStatus] = mapped_column(SAEnum(ProductStatus), default=ProductStatus.draft)
    reject_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submit_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    audit_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    audit_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    compliance: Mapped[Optional["ProductCompliance"]] = relationship(back_populates="product", uselist=False, cascade="all, delete-orphan")
    images: Mapped[List["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    detail: Mapped[Optional["ProductDetail"]] = relationship(back_populates="product", uselist=False, cascade="all, delete-orphan")
    qualifications: Mapped[List["ProductQualification"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    versions: Mapped[List["ProductVersion"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="product", cascade="all, delete-orphan")
