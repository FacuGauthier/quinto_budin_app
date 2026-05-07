from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .detalle_compra import DetalleCompra

class Compra(Base):
    __tablename__ = "compras"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fecha_compra: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False, index=True
    )
    proveedor: Mapped[str | None] = mapped_column(String(150), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    # Relaciones
    detalles: Mapped[list["DetalleCompra"]] = relationship(  # noqa: F821
        back_populates="compra",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Compra id={self.id} fecha={self.fecha_compra} total={self.total}>"
