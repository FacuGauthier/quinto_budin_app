from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator


class MovimientoStockResponse(BaseModel):
    id: int
    ingrediente_id: int
    ingrediente_nombre: str | None = None
    tipo: str
    cantidad: Decimal
    stock_anterior: Decimal
    stock_posterior: Decimal
    referencia_id: int | None
    referencia_tipo: str | None
    motivo: str | None
    fecha: datetime

    model_config = {"from_attributes": True}


class HistorialIngredienteResponse(BaseModel):
    ingrediente_id: int
    nombre: str
    unidad_medida: str
    stock_actual: Decimal
    movimientos: list[MovimientoStockResponse] = []


class IngredienteFaltante(BaseModel):
    ingrediente_id: int
    nombre: str
    unidad_medida: str
    stock_disponible: Decimal
    cantidad_requerida: Decimal
    faltante: Decimal


class ValidacionProductoItem(BaseModel):
    producto_id: int
    producto_nombre: str
    cantidad_pedida: int
    puede_hacerse: bool
    ingredientes_faltantes: list[IngredienteFaltante] = []


class ValidacionStockResponse(BaseModel):
    pedido_id: int
    puede_completarse: bool
    productos: list[ValidacionProductoItem] = []


class ComprasSugeridasItem(BaseModel):
    ingrediente_id: int
    nombre: str
    unidad_medida: str
    stock_actual: Decimal
    cantidad_necesaria_total: Decimal
    cantidad_a_comprar: Decimal


class ComprasSugeridasResponse(BaseModel):
    pedidos_considerados: list[int]
    items: list[ComprasSugeridasItem]


class AjusteStockCreate(BaseModel):
    ingrediente_id: int
    cantidad: Decimal
    motivo: str

    @field_validator("motivo")
    @classmethod
    def motivo_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El motivo del ajuste es obligatorio.")
        return v
