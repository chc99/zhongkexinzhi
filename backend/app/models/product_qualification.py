from datetime import datetime, date
from sqlalchemy import Integer, String, Date, Enum as SAEnum, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database import Base
import enum


class QualStatus(str, enum.Enum):
    valid = "valid"
    expiring = "expiring"
    expired = "expired"


class ProductQualification(Base):
    __tablename__ = "product_qualifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    qual_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("qualification_types.id"), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), default="")
    expire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[QualStatus] = mapped_column(SAEnum(QualStatus), default=QualStatus.valid)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="qualifications")
