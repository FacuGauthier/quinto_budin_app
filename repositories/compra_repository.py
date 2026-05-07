from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from models.compra import Compra
from models.detalle_compra import DetalleCompra
from schemas.compra_schema import CompraCreate, DetalleCompraCreate


class CompraRepository:

    def crear(self, db: Session, data: CompraCreate) -> Compra:
        compra = Compra(
            proveedor=data.proveedor,
            observaciones=data.observaciones,
            total=Decimal("0"),
        )
        db.add(compra)
        db.commit()
        db.refresh(compra)
        return compra

    def agregar_detalle(
        self, db: Session, compra_id: int, detalle: DetalleCompraCreate
    ) -> DetalleCompra:
        subtotal = detalle.precio_unitario * detalle.cantidad
        dc = DetalleCompra(
            compra_id=compra_id,
            ingrediente_id=detalle.ingrediente_id,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario,
            subtotal=subtotal,
        )
        db.add(dc)
        db.commit()
        db.refresh(dc)
        return dc

    def obtener_por_id(self, db: Session, compra_id: int) -> Compra | None:
        stmt = (
            select(Compra)
            .where(Compra.id == compra_id)
            .options(
                joinedload(Compra.detalles).joinedload(DetalleCompra.ingrediente)
            )
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    def obtener_todas(self, db: Session) -> list[Compra]:
        stmt = select(Compra).order_by(Compra.fecha_compra.desc())
        return list(db.execute(stmt).scalars().all())

    def calcular_y_actualizar_total(self, db: Session, compra_id: int) -> Decimal:
        stmt = select(func.sum(DetalleCompra.subtotal)).where(
            DetalleCompra.compra_id == compra_id
        )
        total = db.execute(stmt).scalar_one_or_none() or Decimal("0")
        compra = db.get(Compra, compra_id)
        compra.total = total
        db.commit()
        return total


compra_repo = CompraRepository()
