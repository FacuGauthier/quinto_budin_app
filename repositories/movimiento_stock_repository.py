from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models.movimiento_stock import MovimientoStock


class MovimientoStockRepository:

    def registrar(
        self,
        db: Session,
        ingrediente_id: int,
        tipo: str,
        cantidad: Decimal,
        stock_anterior: Decimal,
        stock_posterior: Decimal,
        referencia_id: int | None = None,
        referencia_tipo: str | None = None,
        motivo: str | None = None,
    ) -> MovimientoStock:
        movimiento = MovimientoStock(
            ingrediente_id=ingrediente_id,
            tipo=tipo,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_posterior=stock_posterior,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo,
            motivo=motivo,
        )
        db.add(movimiento)
        db.commit()
        db.refresh(movimiento)
        return movimiento

    def obtener_por_ingrediente(
        self,
        db: Session,
        ingrediente_id: int,
        tipo: str | None = None,
    ) -> list[MovimientoStock]:
        stmt = (
            select(MovimientoStock)
            .where(MovimientoStock.ingrediente_id == ingrediente_id)
            .options(joinedload(MovimientoStock.ingrediente))
            .order_by(MovimientoStock.fecha.desc())
        )
        if tipo:
            stmt = stmt.where(MovimientoStock.tipo == tipo)
        return list(db.execute(stmt).unique().scalars().all())

    def obtener_por_pedido(self, db: Session, pedido_id: int) -> list[MovimientoStock]:
        stmt = (
            select(MovimientoStock)
            .where(
                MovimientoStock.referencia_tipo == "PEDIDO",
                MovimientoStock.referencia_id == pedido_id,
            )
            .options(joinedload(MovimientoStock.ingrediente))
        )
        return list(db.execute(stmt).unique().scalars().all())

    def obtener_por_compra(self, db: Session, compra_id: int) -> list[MovimientoStock]:
        stmt = (
            select(MovimientoStock)
            .where(
                MovimientoStock.referencia_tipo == "COMPRA",
                MovimientoStock.referencia_id == compra_id,
            )
            .options(joinedload(MovimientoStock.ingrediente))
        )
        return list(db.execute(stmt).unique().scalars().all())

    def obtener_todos(
        self,
        db: Session,
        tipo: str | None = None,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> list[MovimientoStock]:
        stmt = (
            select(MovimientoStock)
            .options(joinedload(MovimientoStock.ingrediente))
            .order_by(MovimientoStock.fecha.desc())
        )
        if tipo:
            stmt = stmt.where(MovimientoStock.tipo == tipo)
        if fecha_desde:
            stmt = stmt.where(MovimientoStock.fecha >= fecha_desde)
        if fecha_hasta:
            stmt = stmt.where(MovimientoStock.fecha <= fecha_hasta)
        return list(db.execute(stmt).unique().scalars().all())


movimiento_stock_repo = MovimientoStockRepository()
