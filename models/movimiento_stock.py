from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ingrediente import Ingrediente

# Tipos de movimiento
TIPO_COMPRA = "COMPRA"
TIPO_CONSUMO = "CONSUMO"
TIPO_AJUSTE = "AJUSTE"


class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("ingredientes.id"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), nullable=False,
        comment="Positivo = entrada, Negativo = salida"
    )
    stock_anterior: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), nullable=False,
        comment="Stock antes de aplicar el movimiento"
    )
    stock_posterior: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), nullable=False,
        comment="Stock después de aplicar el movimiento"
    )
    referencia_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    referencia_tipo: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
        comment="COMPRA o PEDIDO"
    )
    motivo: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Obligatorio para tipo AJUSTE"
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False, index=True
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    # Relaciones
    ingrediente: Mapped["Ingrediente"] = relationship(  # noqa: F821
        back_populates="movimientos"
    )

    def __repr__(self) -> str:
        return (
            f"<MovimientoStock id={self.id} tipo={self.tipo} "
            f"ingrediente={self.ingrediente_id} cantidad={self.cantidad}>"
        )
