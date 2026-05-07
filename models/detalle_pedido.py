from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pedido import Pedido
    from .producto import Producto

class DetallePedido(Base):
    __tablename__ = "detalles_pedido"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id"), nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False,
        comment="Snapshot del precio en el momento de crear el pedido"
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Relaciones
    pedido: Mapped["Pedido"] = relationship(back_populates="detalles")  # noqa: F821
    producto: Mapped["Producto"] = relationship(  # noqa: F821
        back_populates="detalles_pedido"
    )

    def __repr__(self) -> str:
        return (
            f"<DetallePedido pedido={self.pedido_id} "
            f"producto={self.producto_id} cantidad={self.cantidad}>"
        )
