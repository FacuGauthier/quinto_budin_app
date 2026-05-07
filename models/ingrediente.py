from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .producto_ingrediente import ProductoIngrediente
    from .movimiento_stock import MovimientoStock
    from .detalle_compra import DetalleCompra

class Ingrediente(Base):
    __tablename__ = "ingredientes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    marca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unidad_medida: Mapped[str] = mapped_column(String(20), nullable=False)
    stock_actual: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    fecha_modificacion: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relaciones
    recetas: Mapped[list["ProductoIngrediente"]] = relationship(  # noqa: F821
        back_populates="ingrediente", lazy="select"
    )
    movimientos: Mapped[list["MovimientoStock"]] = relationship(  # noqa: F821
        back_populates="ingrediente", lazy="select"
    )
    detalles_compra: Mapped[list["DetalleCompra"]] = relationship(  # noqa: F821
        back_populates="ingrediente", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Ingrediente id={self.id} nombre={self.nombre} stock={self.stock_actual}>"
