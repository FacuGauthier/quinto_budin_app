from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator

ESTADOS_VALIDOS = {"PENDIENTE", "EN_PROCESO", "COMPLETADO", "CANCELADO"}


class DetallePedidoCreate(BaseModel):
    producto_id: int
    cantidad: int

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        return v


class DetallePedidoResponse(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str | None = None
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class PedidoCreate(BaseModel):
    cliente_id: int
    fecha_entrega: datetime | None = None
    direccion_entrega: str
    detalles: list[DetallePedidoCreate]

    @field_validator("detalles")
    @classmethod
    def al_menos_un_producto(cls, v: list) -> list:
        if not v:
            raise ValueError("El pedido debe tener al menos un producto.")
        return v


class PedidoUpdate(BaseModel):
    direccion_entrega: str | None = None
    fecha_entrega: datetime | None = None


class EstadoUpdate(BaseModel):
    nuevo_estado: str

    @field_validator("nuevo_estado")
    @classmethod
    def estado_valido(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Opciones: {ESTADOS_VALIDOS}")
        return v


class PedidoResponse(BaseModel):
    id: int
    cliente_id: int
    cliente_nombre: str | None = None
    fecha_pedido: datetime
    fecha_entrega: datetime | None
    direccion_entrega: str
    estado: str
    precio_total: Decimal
    fecha_creacion: datetime
    fecha_modificacion: datetime

    model_config = {"from_attributes": True}


class PedidoDetalleResponse(PedidoResponse):
    detalles: list[DetallePedidoResponse] = []


class PedidoListResponse(BaseModel):
    total: int
    pedidos: list[PedidoResponse]
