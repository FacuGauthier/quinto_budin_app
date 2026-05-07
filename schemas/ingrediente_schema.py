from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator

UNIDADES_VALIDAS = {"KG", "GR", "L", "ML", "UNIDAD"}


class IngredienteBase(BaseModel):
    nombre: str
    marca: str | None = None
    unidad_medida: str

    @field_validator("unidad_medida")
    @classmethod
    def unidad_valida(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in UNIDADES_VALIDAS:
            raise ValueError(f"Unidad de medida inválida. Opciones: {UNIDADES_VALIDAS}")
        return v


class IngredienteCreate(IngredienteBase):
    stock_inicial: Decimal = Decimal("0")

    @field_validator("stock_inicial")
    @classmethod
    def stock_no_negativo(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("El stock inicial no puede ser negativo.")
        return v


class IngredienteUpdate(BaseModel):
    nombre: str | None = None
    marca: str | None = None
    unidad_medida: str | None = None
    # stock_actual está intencionalmente excluido


class IngredienteResponse(IngredienteBase):
    id: int
    stock_actual: Decimal
    activo: bool
    fecha_creacion: datetime
    fecha_modificacion: datetime

    model_config = {"from_attributes": True}


class StockResponse(BaseModel):
    ingrediente_id: int
    nombre: str
    stock_actual: Decimal
    unidad_medida: str

    model_config = {"from_attributes": True}


class IngredienteListResponse(BaseModel):
    total: int
    ingredientes: list[IngredienteResponse]
