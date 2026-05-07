from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cliente import Cliente
    from .detalle_pedido import DetallePedido

# Estados válidos del pedido
ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_EN_PROCESO = "EN_PROCESO"
ESTADO_COMPLETADO = "COMPLETADO"
ESTADO_CANCELADO = "CANCELADO"


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id"), nullable=False, index=True
    )
    fecha_pedido: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    fecha_entrega: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    direccion_entrega: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), default=ESTADO_PENDIENTE, nullable=False, index=True
    )
    precio_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    fecha_modificacion: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relaciones
    cliente: Mapped["Cliente"] = relationship(  # noqa: F821
        back_populates="pedidos"
    )
    detalles: Mapped[list["DetallePedido"]] = relationship(  # noqa: F821
        back_populates="pedido",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Pedido id={self.id} cliente={self.cliente_id} estado={self.estado}>"
