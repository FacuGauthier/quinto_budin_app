from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class ResumenVentasResponse(BaseModel):
    fecha_desde: datetime
    fecha_hasta: datetime
    total_ventas: Decimal
    cantidad_pedidos: int
    ticket_promedio: Decimal


class ProductoMasVendidoResponse(BaseModel):
    producto_id: int
    nombre: str
    cantidad_vendida: int
    ingresos_generados: Decimal


class CostoComprasResponse(BaseModel):
    fecha_desde: datetime
    fecha_hasta: datetime
    total_compras: Decimal
    cantidad_compras: int


class GananciasResponse(BaseModel):
    fecha_desde: datetime
    fecha_hasta: datetime
    ingresos: Decimal
    costos: Decimal
    ganancia_estimada: Decimal
