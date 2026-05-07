from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.inventario_schema import (
    MovimientoStockResponse,
    HistorialIngredienteResponse,
    AjusteStockCreate,
    ComprasSugeridasResponse,
)
from schemas.ingrediente_schema import StockResponse
from services.stock_service import stock_service
from services.ingrediente_service import ingrediente_service
from repositories.movimiento_stock_repository import movimiento_stock_repo

router = APIRouter(prefix="/inventario", tags=["Inventario"])


@router.get("/stock", response_model=list[StockResponse])
def listar_stock(db: Session = Depends(get_db)):
    ingredientes = ingrediente_service.listar_ingredientes(db, solo_activos=True)
    return [
        StockResponse(
            ingrediente_id=ing.id,
            nombre=ing.nombre,
            stock_actual=ing.stock_actual,
            unidad_medida=ing.unidad_medida,
        )
        for ing in ingredientes
    ]


@router.get("/movimientos", response_model=list[MovimientoStockResponse])
def listar_movimientos(
    tipo: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    db: Session = Depends(get_db),
):
    movimientos = movimiento_stock_repo.obtener_todos(
        db, tipo=tipo, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
    )
    return [
        MovimientoStockResponse(
            id=m.id,
            ingrediente_id=m.ingrediente_id,
            ingrediente_nombre=m.ingrediente.nombre if m.ingrediente else None,
            tipo=m.tipo,
            cantidad=m.cantidad,
            stock_anterior=m.stock_anterior,
            stock_posterior=m.stock_posterior,
            referencia_id=m.referencia_id,
            referencia_tipo=m.referencia_tipo,
            motivo=m.motivo,
            fecha=m.fecha,
        )
        for m in movimientos
    ]


@router.get("/movimientos/ingrediente/{id}", response_model=HistorialIngredienteResponse)
def historial_ingrediente(
    id: int,
    tipo: str | None = None,
    db: Session = Depends(get_db),
):
    ing = ingrediente_service.obtener_ingrediente(db, id)
    movimientos = stock_service.obtener_historial_ingrediente(db, id, tipo=tipo)
    return HistorialIngredienteResponse(
        ingrediente_id=ing.id,
        nombre=ing.nombre,
        unidad_medida=ing.unidad_medida,
        stock_actual=ing.stock_actual,
        movimientos=[
            MovimientoStockResponse(
                id=m.id,
                ingrediente_id=m.ingrediente_id,
                ingrediente_nombre=ing.nombre,
                tipo=m.tipo,
                cantidad=m.cantidad,
                stock_anterior=m.stock_anterior,
                stock_posterior=m.stock_posterior,
                referencia_id=m.referencia_id,
                referencia_tipo=m.referencia_tipo,
                motivo=m.motivo,
                fecha=m.fecha,
            )
            for m in movimientos
        ],
    )


@router.post("/ajuste", response_model=MovimientoStockResponse, status_code=status.HTTP_201_CREATED)
def registrar_ajuste(data: AjusteStockCreate, db: Session = Depends(get_db)):
    movimiento = stock_service.registrar_ajuste_manual(
        db, data.ingrediente_id, data.cantidad, data.motivo
    )
    ing = ingrediente_service.obtener_ingrediente(db, data.ingrediente_id)
    return MovimientoStockResponse(
        id=movimiento.id,
        ingrediente_id=movimiento.ingrediente_id,
        ingrediente_nombre=ing.nombre,
        tipo=movimiento.tipo,
        cantidad=movimiento.cantidad,
        stock_anterior=movimiento.stock_anterior,
        stock_posterior=movimiento.stock_posterior,
        referencia_id=movimiento.referencia_id,
        referencia_tipo=movimiento.referencia_tipo,
        motivo=movimiento.motivo,
        fecha=movimiento.fecha,
    )


@router.get("/compras-sugeridas", response_model=ComprasSugeridasResponse)
def compras_sugeridas(db: Session = Depends(get_db)):
    return stock_service.generar_reporte_compras_sugeridas(db)
