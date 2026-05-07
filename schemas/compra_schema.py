from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator


class DetalleCompraCreate(BaseModel):
    ingrediente_id: int
    cantidad: Decimal
    precio_unitario: Decimal

    @field_validator("cantidad", "precio_unitario")
    @classmethod
    def positivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El valor debe ser mayor a 0.")
        return v


class DetalleCompraResponse(BaseModel):
    id: int
    ingrediente_id: int
    ingrediente_nombre: str | None = None
    unidad_medida: str | None = None
    cantidad: Decimal
    precio_unitario: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class CompraCreate(BaseModel):
    proveedor: str | None = None
    observaciones: str | None = None
    detalles: list[DetalleCompraCreate]

    @field_validator("detalles")
    @classmethod
    def al_menos_un_ingrediente(cls, v: list) -> list:
        if not v:
            raise ValueError("La compra debe tener al menos un ingrediente.")
        return v


class CompraResponse(BaseModel):
    id: int
    proveedor: str | None
    observaciones: str | None
    total: Decimal
    fecha_compra: datetime
    fecha_creacion: datetime

    model_config = {"from_attributes": True}


class CompraDetalleResponse(CompraResponse):
    detalles: list[DetalleCompraResponse] = []


class CompraListResponse(BaseModel):
    total: int
    compras: list[CompraResponse]
