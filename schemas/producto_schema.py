from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator


class IngredienteEnReceta(BaseModel):
    ingrediente_id: int
    ingrediente_nombre: str | None = None
    unidad_medida: str | None = None
    cantidad_necesaria: Decimal

    model_config = {"from_attributes": True}


class ProductoBase(BaseModel):
    nombre: str
    precio: Decimal
    tiempo_desarrollo: int

    @field_validator("precio")
    @classmethod
    def precio_positivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return v

    @field_validator("tiempo_desarrollo")
    @classmethod
    def tiempo_positivo(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El tiempo de desarrollo debe ser mayor a 0.")
        return v


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: str | None = None
    precio: Decimal | None = None
    tiempo_desarrollo: int | None = None


class RecetaUpdate(BaseModel):
    ingredientes: list["RecetaItem"]


class RecetaItem(BaseModel):
    ingrediente_id: int
    cantidad_necesaria: Decimal

    @field_validator("cantidad_necesaria")
    @classmethod
    def cantidad_positiva(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        return v


class ProductoResponse(ProductoBase):
    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_modificacion: datetime

    model_config = {"from_attributes": True}


class ProductoDetalleResponse(ProductoResponse):
    ingredientes: list[IngredienteEnReceta] = []


class ProductoListResponse(BaseModel):
    total: int
    productos: list[ProductoResponse]
