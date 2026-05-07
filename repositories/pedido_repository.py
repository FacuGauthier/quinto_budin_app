from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from models.pedido import Pedido, ESTADO_PENDIENTE
from models.detalle_pedido import DetallePedido
from models.producto import Producto
from schemas.pedido_schema import PedidoCreate, PedidoUpdate, DetallePedidoCreate


class PedidoRepository:

    def crear(self, db: Session, data: PedidoCreate) -> Pedido:
        pedido = Pedido(
            cliente_id=data.cliente_id,
            fecha_entrega=data.fecha_entrega,
            direccion_entrega=data.direccion_entrega,
            estado=ESTADO_PENDIENTE,
            precio_total=Decimal("0"),
        )
        db.add(pedido)
        db.commit()
        db.refresh(pedido)
        return pedido

    def agregar_detalle(
        self,
        db: Session,
        pedido_id: int,
        detalle: DetallePedidoCreate,
        precio_unitario: Decimal,
    ) -> DetallePedido:
        subtotal = precio_unitario * detalle.cantidad
        dp = DetallePedido(
            pedido_id=pedido_id,
            producto_id=detalle.producto_id,
            cantidad=detalle.cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal,
        )
        db.add(dp)
        db.commit()
        db.refresh(dp)
        return dp

    def obtener_por_id(self, db: Session, pedido_id: int) -> Pedido | None:
        stmt = (
            select(Pedido)
            .where(Pedido.id == pedido_id)
            .options(
                joinedload(Pedido.cliente),
                joinedload(Pedido.detalles).joinedload(DetallePedido.producto),
            )
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    def obtener_todos(
        self,
        db: Session,
        estado: str | None = None,
        cliente_id: int | None = None,
    ) -> list[Pedido]:
        stmt = (
            select(Pedido)
            .options(joinedload(Pedido.cliente))
            .order_by(Pedido.fecha_creacion.desc())
        )
        if estado:
            stmt = stmt.where(Pedido.estado == estado)
        if cliente_id:
            stmt = stmt.where(Pedido.cliente_id == cliente_id)
        return list(db.execute(stmt).unique().scalars().all())

    def cambiar_estado(self, db: Session, pedido: Pedido, nuevo_estado: str) -> Pedido:
        pedido.estado = nuevo_estado
        pedido.fecha_modificacion = datetime.now()
        db.commit()
        db.refresh(pedido)
        return pedido

    def actualizar_precio_total(self, db: Session, pedido_id: int) -> Decimal:
        stmt = select(func.sum(DetallePedido.subtotal)).where(
            DetallePedido.pedido_id == pedido_id
        )
        total = db.execute(stmt).scalar_one_or_none() or Decimal("0")
        pedido = db.get(Pedido, pedido_id)
        pedido.precio_total = total
        db.commit()
        return total

    def actualizar(self, db: Session, pedido: Pedido, data: PedidoUpdate) -> Pedido:
        cambios = data.model_dump(exclude_none=True)
        for campo, valor in cambios.items():
            setattr(pedido, campo, valor)
        pedido.fecha_modificacion = datetime.now()
        db.commit()
        db.refresh(pedido)
        return pedido

    def obtener_pedidos_pendientes(self, db: Session) -> list[Pedido]:
        stmt = (
            select(Pedido)
            .where(Pedido.estado == ESTADO_PENDIENTE)
            .options(
                joinedload(Pedido.detalles).joinedload(DetallePedido.producto)
            )
        )
        return list(db.execute(stmt).unique().scalars().all())

    def obtener_detalles(self, db: Session, pedido_id: int) -> list[DetallePedido]:
        stmt = (
            select(DetallePedido)
            .where(DetallePedido.pedido_id == pedido_id)
            .options(
                joinedload(DetallePedido.producto).joinedload(
                    Producto.ingredientes
                )
            )
        )
        return list(db.execute(stmt).unique().scalars().all())


pedido_repo = PedidoRepository()
