from datetime import datetime
from sqlalchemy import Integer, String, Enum as SAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.database import Base
from app.models.user import User
import enum


class CategoryStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[CategoryStatus] = mapped_column(SAEnum(CategoryStatus), default=CategoryStatus.active)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    created_by_user: Mapped["User"] = relationship("User")
    parent: Mapped[Optional["Category"]] = relationship("Category", back_populates="children", remote_side=[id])
    children: Mapped[List["Category"]] = relationship("Category", back_populates="parent", remote_side=[parent_id])
