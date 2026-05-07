from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .producto import Producto
    from .ingrediente import Ingrediente

class ProductoIngrediente(Base):
    __tablename__ = "producto_ingredientes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("ingredientes.id"), nullable=False, index=True
    )
    cantidad_necesaria: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), nullable=False, comment="Cantidad para elaborar UNA unidad del producto"
    )

    # Relaciones
    producto: Mapped["Producto"] = relationship(  # noqa: F821
        back_populates="ingredientes"
    )
    ingrediente: Mapped["Ingrediente"] = relationship(  # noqa: F821
        back_populates="recetas"
    )

    def __repr__(self) -> str:
        return (
            f"<ProductoIngrediente producto={self.producto_id} "
            f"ingrediente={self.ingrediente_id} cantidad={self.cantidad_necesaria}>"
        )
