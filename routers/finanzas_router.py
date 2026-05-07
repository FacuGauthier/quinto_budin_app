from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.finanzas_schema import (
    ResumenVentasResponse,
    ProductoMasVendidoResponse,
    CostoComprasResponse,
    GananciasResponse,
)
from services.finanzas_service import finanzas_service

router = APIRouter(prefix="/finanzas", tags=["Finanzas"])


@router.get("/ventas", response_model=ResumenVentasResponse)
def resumen_ventas(
    fecha_desde: datetime = Query(..., description="Fecha inicio del período"),
    fecha_hasta: datetime = Query(..., description="Fecha fin del período"),
    db: Session = Depends(get_db),
):
    return finanzas_service.calcular_resumen_ventas(db, fecha_desde, fecha_hasta)


@router.get("/productos-mas-vendidos", response_model=list[ProductoMasVendidoResponse])
def productos_mas_vendidos(
    fecha_desde: datetime = Query(...),
    fecha_hasta: datetime = Query(...),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return finanzas_service.obtener_productos_mas_vendidos(db, fecha_desde, fecha_hasta, limit)


@router.get("/compras", response_model=CostoComprasResponse)
def costo_compras(
    fecha_desde: datetime = Query(...),
    fecha_hasta: datetime = Query(...),
    db: Session = Depends(get_db),
):
    return finanzas_service.calcular_costo_compras(db, fecha_desde, fecha_hasta)


@router.get("/ganancias", response_model=GananciasResponse)
def ganancias(
    fecha_desde: datetime = Query(...),
    fecha_hasta: datetime = Query(...),
    db: Session = Depends(get_db),
):
    return finanzas_service.calcular_ganancias_estimadas(db, fecha_desde, fecha_hasta)
