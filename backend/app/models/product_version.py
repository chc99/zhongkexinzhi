from datetime import datetime
from sqlalchemy import BigInteger, Integer, JSON, Enum as SAEnum, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ChangeType(str, enum.Enum):
    submit = "submit"
    approve = "approve"
    reject = "reject"
    resubmit = "resubmit"


class ProductVersion(Base):
    __tablename__ = "product_versions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    change_type: Mapped[ChangeType] = mapped_column(SAEnum(ChangeType), nullable=False)
    changed_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="versions")
