from sqlalchemy import Integer, String, Integer, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ImageType(str, enum.Enum):
    main = "main"
    detail = "detail"


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    image_type: Mapped[ImageType] = mapped_column(SAEnum(ImageType), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship(back_populates="images")
