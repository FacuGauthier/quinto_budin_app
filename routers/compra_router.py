from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.compra_schema import (
    CompraCreate, CompraDetalleResponse, CompraListResponse,
    DetalleCompraResponse,
)
from services.compra_service import compra_service

router = APIRouter(prefix="/compras", tags=["Compras"])


def _to_compra_detalle(compra) -> CompraDetalleResponse:
    detalles = [
        DetalleCompraResponse(
            id=d.id,
            ingrediente_id=d.ingrediente_id,
            ingrediente_nombre=d.ingrediente.nombre if d.ingrediente else None,
            unidad_medida=d.ingrediente.unidad_medida if d.ingrediente else None,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            subtotal=d.subtotal,
        )
        for d in compra.detalles
    ]
    return CompraDetalleResponse(
        id=compra.id,
        proveedor=compra.proveedor,
        observaciones=compra.observaciones,
        total=compra.total,
        fecha_compra=compra.fecha_compra,
        fecha_creacion=compra.fecha_creacion,
        detalles=detalles,
    )


@router.post("", response_model=CompraDetalleResponse, status_code=status.HTTP_201_CREATED)
def registrar_compra(data: CompraCreate, db: Session = Depends(get_db)):
    compra = compra_service.registrar_compra(db, data)
    return _to_compra_detalle(compra)


@router.get("", response_model=CompraListResponse)
def listar_compras(db: Session = Depends(get_db)):
    compras = compra_service.listar_compras(db)
    return CompraListResponse(total=len(compras), compras=compras)


@router.get("/{id}", response_model=CompraDetalleResponse)
def obtener_compra(id: int, db: Session = Depends(get_db)):
    compra = compra_service.obtener_compra(db, id)
    return _to_compra_detalle(compra)
