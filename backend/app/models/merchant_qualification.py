from datetime import datetime, date
from sqlalchemy import Integer, String, Date, Enum as SAEnum, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database import Base
from app.models.product_qualification import QualStatus


class MerchantQualification(Base):
    __tablename__ = "merchant_qualifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    qual_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("qualification_types.id"), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), default="")
    expire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[QualStatus] = mapped_column(SAEnum(QualStatus), default=QualStatus.valid)
    remark: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    merchant: Mapped["User"] = relationship("User", foreign_keys=[merchant_id])
    qual_type: Mapped["QualificationType"] = relationship("QualificationType", foreign_keys=[qual_type_id])
