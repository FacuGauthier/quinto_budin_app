from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.pedido import Pedido, ESTADO_COMPLETADO
from models.detalle_pedido import DetallePedido
from models.producto import Producto
from models.compra import Compra
from schemas.finanzas_schema import (
    ResumenVentasResponse,
    ProductoMasVendidoResponse,
    CostoComprasResponse,
    GananciasResponse,
)


class FinanzasService:

    def calcular_resumen_ventas(
        self, db: Session, fecha_desde: datetime, fecha_hasta: datetime
    ) -> ResumenVentasResponse:
        stmt = select(
            func.sum(Pedido.precio_total).label("total"),
            func.count(Pedido.id).label("cantidad"),
        ).where(
            Pedido.estado == ESTADO_COMPLETADO,
            Pedido.fecha_pedido >= fecha_desde,
            Pedido.fecha_pedido <= fecha_hasta,
        )
        resultado = db.execute(stmt).one()
        total = resultado.total or Decimal("0")
        cantidad = resultado.cantidad or 0
        ticket_promedio = (total / cantidad) if cantidad > 0 else Decimal("0")

        return ResumenVentasResponse(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            total_ventas=total,
            cantidad_pedidos=cantidad,
            ticket_promedio=ticket_promedio,
        )

    def obtener_productos_mas_vendidos(
        self,
        db: Session,
        fecha_desde: datetime,
        fecha_hasta: datetime,
        limit: int = 10,
    ) -> list[ProductoMasVendidoResponse]:
        stmt = (
            select(
                DetallePedido.producto_id,
                Producto.nombre,
                func.sum(DetallePedido.cantidad).label("cantidad_vendida"),
                func.sum(DetallePedido.subtotal).label("ingresos"),
            )
            .join(DetallePedido.pedido)
            .join(DetallePedido.producto)
            .where(
                Pedido.estado == ESTADO_COMPLETADO,
                Pedido.fecha_pedido >= fecha_desde,
                Pedido.fecha_pedido <= fecha_hasta,
            )
            .group_by(DetallePedido.producto_id, Producto.nombre)
            .order_by(func.sum(DetallePedido.cantidad).desc())
            .limit(limit)
        )
        filas = db.execute(stmt).all()
        return [
            ProductoMasVendidoResponse(
                producto_id=f.producto_id,
                nombre=f.nombre,
                cantidad_vendida=f.cantidad_vendida,
                ingresos_generados=f.ingresos or Decimal("0"),
            )
            for f in filas
        ]

    def calcular_costo_compras(
        self, db: Session, fecha_desde: datetime, fecha_hasta: datetime
    ) -> CostoComprasResponse:
        stmt = select(
            func.sum(Compra.total).label("total"),
            func.count(Compra.id).label("cantidad"),
        ).where(
            Compra.fecha_compra >= fecha_desde,
            Compra.fecha_compra <= fecha_hasta,
        )
        resultado = db.execute(stmt).one()
        return CostoComprasResponse(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            total_compras=resultado.total or Decimal("0"),
            cantidad_compras=resultado.cantidad or 0,
        )

    def calcular_ganancias_estimadas(
        self, db: Session, fecha_desde: datetime, fecha_hasta: datetime
    ) -> GananciasResponse:
        ventas = self.calcular_resumen_ventas(db, fecha_desde, fecha_hasta)
        costos = self.calcular_costo_compras(db, fecha_desde, fecha_hasta)
        return GananciasResponse(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            ingresos=ventas.total_ventas,
            costos=costos.total_compras,
            ganancia_estimada=ventas.total_ventas - costos.total_compras,
        )


finanzas_service = FinanzasService()
