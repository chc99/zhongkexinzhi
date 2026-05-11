from sqlalchemy import BigInteger, String, Boolean, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class QualScope(str, enum.Enum):
    merchant = "merchant"
    product = "product"


class QualificationType(Base):
    __tablename__ = "qualification_types"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    scope: Mapped[QualScope] = mapped_column(SAEnum(QualScope), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
