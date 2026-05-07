from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Numeric, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .producto_ingrediente import ProductoIngrediente
    from .detalle_pedido import DetallePedido

class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tiempo_desarrollo: Mapped[int] = mapped_column(Integer, nullable=False, comment="En minutos")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    fecha_modificacion: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relaciones
    ingredientes: Mapped[list["ProductoIngrediente"]] = relationship(  # noqa: F821
        back_populates="producto",
        cascade="all, delete-orphan",
        lazy="select",
    )
    detalles_pedido: Mapped[list["DetallePedido"]] = relationship(  # noqa: F821
        back_populates="producto", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Producto id={self.id} nombre={self.nombre}>"
