from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.pedido_schema import (
    PedidoCreate, PedidoUpdate, EstadoUpdate,
    PedidoResponse, PedidoDetalleResponse, PedidoListResponse,
    DetallePedidoCreate, DetallePedidoResponse,
)
from schemas.inventario_schema import ValidacionStockResponse
from services.pedido_service import pedido_service
from services.stock_service import stock_service

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


def _to_pedido_response(pedido) -> PedidoDetalleResponse:
    """Construye el schema de respuesta enriquecido con datos relacionados."""
    detalles = [
        DetallePedidoResponse(
            id=d.id,
            producto_id=d.producto_id,
            producto_nombre=d.producto.nombre if d.producto else None,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            subtotal=d.subtotal,
        )
        for d in pedido.detalles
    ]
    return PedidoDetalleResponse(
        id=pedido.id,
        cliente_id=pedido.cliente_id,
        cliente_nombre=(
            f"{pedido.cliente.nombre} {pedido.cliente.apellido}"
            if pedido.cliente else None
        ),
        fecha_pedido=pedido.fecha_pedido,
        fecha_entrega=pedido.fecha_entrega,
        direccion_entrega=pedido.direccion_entrega,
        estado=pedido.estado,
        precio_total=pedido.precio_total,
        fecha_creacion=pedido.fecha_creacion,
        fecha_modificacion=pedido.fecha_modificacion,
        detalles=detalles,
    )


@router.post("", response_model=PedidoDetalleResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(data: PedidoCreate, db: Session = Depends(get_db)):
    pedido = pedido_service.crear_pedido(db, data)
    return _to_pedido_response(pedido)


@router.get("", response_model=PedidoListResponse)
def listar_pedidos(
    estado: str | None = None,
    cliente_id: int | None = None,
    db: Session = Depends(get_db),
):
    pedidos = pedido_service.listar_pedidos(db, estado=estado, cliente_id=cliente_id)
    items = [
        PedidoResponse(
            id=p.id,
            cliente_id=p.cliente_id,
            cliente_nombre=(
                f"{p.cliente.nombre} {p.cliente.apellido}" if p.cliente else None
            ),
            fecha_pedido=p.fecha_pedido,
            fecha_entrega=p.fecha_entrega,
            direccion_entrega=p.direccion_entrega,
            estado=p.estado,
            precio_total=p.precio_total,
            fecha_creacion=p.fecha_creacion,
            fecha_modificacion=p.fecha_modificacion,
        )
        for p in pedidos
    ]
    return PedidoListResponse(total=len(items), pedidos=items)


@router.get("/{id}", response_model=PedidoDetalleResponse)
def obtener_pedido(id: int, db: Session = Depends(get_db)):
    pedido = pedido_service.obtener_pedido(db, id)
    return _to_pedido_response(pedido)


@router.put("/{id}", response_model=PedidoDetalleResponse)
def actualizar_pedido(id: int, data: PedidoUpdate, db: Session = Depends(get_db)):
    pedido = pedido_service.actualizar_pedido(db, id, data)
    return _to_pedido_response(pedido)


@router.post("/{id}/productos", response_model=PedidoDetalleResponse)
def agregar_producto(
    id: int, detalle: DetallePedidoCreate, db: Session = Depends(get_db)
):
    pedido = pedido_service.agregar_producto(db, id, detalle)
    return _to_pedido_response(pedido)


@router.patch("/{id}/estado", response_model=PedidoDetalleResponse)
def cambiar_estado(id: int, data: EstadoUpdate, db: Session = Depends(get_db)):
    pedido = pedido_service.cambiar_estado(db, id, data.nuevo_estado)
    return _to_pedido_response(pedido)


@router.get("/{id}/validar-stock", response_model=ValidacionStockResponse)
def validar_stock_pedido(id: int, db: Session = Depends(get_db)):
    # Verificar que el pedido exista
    pedido_service.obtener_pedido(db, id)
    return stock_service.validar_stock_pedido(db, id)
