from sqlalchemy import BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ProductCompliance(Base):
    __tablename__ = "product_compliances"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), unique=True, nullable=False)
    approval_number: Mapped[str] = mapped_column(String(100), default="")
    main_ingredients: Mapped[str] = mapped_column(Text, default="")
    efficacy_ingredients: Mapped[str] = mapped_column(Text, default="")
    suitable_population: Mapped[str] = mapped_column(String(500), default="")
    unsuitable_population: Mapped[str] = mapped_column(String(500), default="")
    health_function: Mapped[str] = mapped_column(String(500), default="")
    usage_dosage: Mapped[str] = mapped_column(String(500), default="")
    shelf_life: Mapped[str] = mapped_column(String(100), default="")
    storage_method: Mapped[str] = mapped_column(String(500), default="")
    precautions: Mapped[str] = mapped_column(Text, default="")

    product: Mapped["Product"] = relationship(back_populates="compliance")
