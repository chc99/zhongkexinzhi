from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ProductDetail(Base):
    __tablename__ = "product_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")

    product: Mapped["Product"] = relationship(back_populates="detail")
