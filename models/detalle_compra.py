from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .compra import Compra
    from .ingrediente import Ingrediente

class DetalleCompra(Base):
    __tablename__ = "detalles_compra"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    compra_id: Mapped[int] = mapped_column(
        ForeignKey("compras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("ingredientes.id"), nullable=False, index=True
    )
    cantidad: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Relaciones
    compra: Mapped["Compra"] = relationship(back_populates="detalles")  # noqa: F821
    ingrediente: Mapped["Ingrediente"] = relationship(  # noqa: F821
        back_populates="detalles_compra"
    )

    def __repr__(self) -> str:
        return (
            f"<DetalleCompra compra={self.compra_id} "
            f"ingrediente={self.ingrediente_id} cantidad={self.cantidad}>"
        )
