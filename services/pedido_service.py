from sqlalchemy.orm import Session
from models.pedido import Pedido, ESTADO_PENDIENTE, ESTADO_EN_PROCESO, ESTADO_COMPLETADO, ESTADO_CANCELADO
from schemas.pedido_schema import PedidoCreate, PedidoUpdate, DetallePedidoCreate
from repositories.pedido_repository import pedido_repo
from repositories.cliente_repository import cliente_repo
from repositories.producto_repository import producto_repo
from services.stock_service import stock_service
from core.exceptions import (
    RecursoNoEncontrado, RecursoInactivo,
    OperacionNoPermitida, TransicionEstadoInvalida,
)

# Mapa de transiciones válidas
TRANSICIONES_VALIDAS: dict[str, set[str]] = {
    ESTADO_PENDIENTE: {ESTADO_EN_PROCESO, ESTADO_CANCELADO},
    ESTADO_EN_PROCESO: {ESTADO_COMPLETADO, ESTADO_CANCELADO},
    ESTADO_COMPLETADO: {ESTADO_CANCELADO},
    ESTADO_CANCELADO: set(),
}


class PedidoService:

    def crear_pedido(self, db: Session, data: PedidoCreate) -> Pedido:
        # Validar cliente
        cliente = cliente_repo.obtener_por_id(db, data.cliente_id)
        if not cliente:
            raise RecursoNoEncontrado("Cliente", data.cliente_id)
        if not cliente.activo:
            raise RecursoInactivo("Cliente", data.cliente_id)

        # Crear cabecera
        pedido = pedido_repo.crear(db, data)

        # Agregar detalles capturando snapshot del precio
        for item in data.detalles:
            producto = producto_repo.obtener_por_id(db, item.producto_id)
            if not producto:
                raise RecursoNoEncontrado("Producto", item.producto_id)
            if not producto.activo:
                raise RecursoInactivo("Producto", item.producto_id)
            pedido_repo.agregar_detalle(db, pedido.id, item, precio_unitario=producto.precio)

        # Calcular precio total
        pedido_repo.actualizar_precio_total(db, pedido.id)
        return pedido_repo.obtener_por_id(db, pedido.id)

    def obtener_pedido(self, db: Session, pedido_id: int) -> Pedido:
        pedido = pedido_repo.obtener_por_id(db, pedido_id)
        if not pedido:
            raise RecursoNoEncontrado("Pedido", pedido_id)
        return pedido

    def listar_pedidos(
        self,
        db: Session,
        estado: str | None = None,
        cliente_id: int | None = None,
    ) -> list[Pedido]:
        return pedido_repo.obtener_todos(db, estado=estado, cliente_id=cliente_id)

    def agregar_producto(
        self, db: Session, pedido_id: int, detalle: DetallePedidoCreate
    ) -> Pedido:
        pedido = self.obtener_pedido(db, pedido_id)
        if pedido.estado != ESTADO_PENDIENTE:
            raise OperacionNoPermitida(
                f"Solo se pueden agregar productos a pedidos en estado PENDIENTE. "
                f"Estado actual: {pedido.estado}."
            )
        producto = producto_repo.obtener_por_id(db, detalle.producto_id)
        if not producto:
            raise RecursoNoEncontrado("Producto", detalle.producto_id)
        if not producto.activo:
            raise RecursoInactivo("Producto", detalle.producto_id)

        pedido_repo.agregar_detalle(db, pedido_id, detalle, precio_unitario=producto.precio)
        pedido_repo.actualizar_precio_total(db, pedido_id)
        return pedido_repo.obtener_por_id(db, pedido_id)

    def cambiar_estado(self, db: Session, pedido_id: int, nuevo_estado: str) -> Pedido:
        pedido = self.obtener_pedido(db, pedido_id)
        estado_actual = pedido.estado

        if nuevo_estado not in TRANSICIONES_VALIDAS.get(estado_actual, set()):
            raise TransicionEstadoInvalida(estado_actual, nuevo_estado)

        if nuevo_estado == ESTADO_COMPLETADO:
            # Validar y consumir stock (lanza StockInsuficiente si no hay)
            stock_service.consumir_stock_pedido(db, pedido_id)

        if nuevo_estado == ESTADO_CANCELADO and estado_actual == ESTADO_COMPLETADO:
            # Revertir el stock consumido
            stock_service.revertir_consumo_pedido(db, pedido_id)

        return pedido_repo.cambiar_estado(db, pedido, nuevo_estado)

    def actualizar_pedido(self, db: Session, pedido_id: int, data: PedidoUpdate) -> Pedido:
        pedido = self.obtener_pedido(db, pedido_id)
        if pedido.estado != ESTADO_PENDIENTE:
            raise OperacionNoPermitida(
                "Solo se pueden editar pedidos en estado PENDIENTE."
            )
        return pedido_repo.actualizar(db, pedido, data)


pedido_service = PedidoService()
