from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.movimiento_stock import TIPO_COMPRA, TIPO_CONSUMO, TIPO_AJUSTE, MovimientoStock
from models.producto_ingrediente import ProductoIngrediente
from repositories.ingrediente_repository import ingrediente_repo
from repositories.movimiento_stock_repository import movimiento_stock_repo
from repositories.pedido_repository import pedido_repo
from schemas.inventario_schema import (
    ValidacionStockResponse,
    ValidacionProductoItem,
    IngredienteFaltante,
    ComprasSugeridasResponse,
    ComprasSugeridasItem,
)
from core.exceptions import StockInsuficiente, RecursoNoEncontrado, RecursoInactivo


class StockService:

    def actualizar_stock_por_compra(
        self,
        db: Session,
        ingrediente_id: int,
        cantidad: Decimal,
        compra_id: int,
    ) -> None:
        """
        Registra un movimiento COMPRA y actualiza el stock_actual del ingrediente.
        El registro del movimiento y la actualización ocurren en la misma transacción.
        """
        ing = ingrediente_repo.obtener_por_id(db, ingrediente_id)
        if not ing:
            raise RecursoNoEncontrado("Ingrediente", ingrediente_id)

        stock_anterior = ing.stock_actual
        stock_posterior = stock_anterior + cantidad

        movimiento_stock_repo.registrar(
            db=db,
            ingrediente_id=ingrediente_id,
            tipo=TIPO_COMPRA,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_posterior=stock_posterior,
            referencia_id=compra_id,
            referencia_tipo="COMPRA",
        )
        ingrediente_repo.actualizar_stock(db, ing, stock_posterior)

    def consumir_stock_pedido(self, db: Session, pedido_id: int) -> None:
        """
        Descuenta del stock todos los ingredientes necesarios para completar el pedido.
        Opera sobre cada producto × ingrediente de la receta.
        Si el stock resulta insuficiente para algún ingrediente, lanza StockInsuficiente
        ANTES de modificar nada (validación previa completa).
        """
        detalles = pedido_repo.obtener_detalles(db, pedido_id)

        # Paso 1: Calcular consumo total por ingrediente (puede haber repetidos entre productos)
        consumo_total: dict[int, Decimal] = {}
        for detalle in detalles:
            stmt = (
                select(ProductoIngrediente)
                .where(ProductoIngrediente.producto_id == detalle.producto_id)
                .options(joinedload(ProductoIngrediente.ingrediente))
            )
            pi_list = list(db.execute(stmt).unique().scalars().all())
            for pi in pi_list:
                necesario = pi.cantidad_necesaria * detalle.cantidad
                consumo_total[pi.ingrediente_id] = (
                    consumo_total.get(pi.ingrediente_id, Decimal("0")) + necesario
                )

        # Paso 2: Verificar que haya stock suficiente para TODOS antes de modificar nada
        faltantes = []
        for ing_id, necesario in consumo_total.items():
            ing = ingrediente_repo.obtener_por_id(db, ing_id)
            if ing and ing.stock_actual < necesario:
                faltantes.append({
                    "ingrediente_id": ing_id,
                    "nombre": ing.nombre,
                    "stock_disponible": float(ing.stock_actual),
                    "cantidad_requerida": float(necesario),
                    "faltante": float(necesario - ing.stock_actual),
                })
        if faltantes:
            raise StockInsuficiente(faltantes)

        # Paso 3: Aplicar consumos
        for ing_id, necesario in consumo_total.items():
            ing = ingrediente_repo.obtener_por_id(db, ing_id)
            stock_anterior = ing.stock_actual
            stock_posterior = stock_anterior - necesario
            movimiento_stock_repo.registrar(
                db=db,
                ingrediente_id=ing_id,
                tipo=TIPO_CONSUMO,
                cantidad=-necesario,  # negativo = salida
                stock_anterior=stock_anterior,
                stock_posterior=stock_posterior,
                referencia_id=pedido_id,
                referencia_tipo="PEDIDO",
            )
            ingrediente_repo.actualizar_stock(db, ing, stock_posterior)

    def revertir_consumo_pedido(self, db: Session, pedido_id: int) -> None:
        """
        Revierte los movimientos de CONSUMO de un pedido que fue COMPLETADO y luego CANCELADO.
        Genera movimientos de AJUSTE con referencia al pedido original para trazabilidad.
        """
        movimientos = movimiento_stock_repo.obtener_por_pedido(db, pedido_id)
        consumos = [m for m in movimientos if m.tipo == TIPO_CONSUMO]

        for movimiento in consumos:
            ing = ingrediente_repo.obtener_por_id(db, movimiento.ingrediente_id)
            if not ing:
                continue
            cantidad_revertida = abs(movimiento.cantidad)  # el consumo era negativo
            stock_anterior = ing.stock_actual
            stock_posterior = stock_anterior + cantidad_revertida
            movimiento_stock_repo.registrar(
                db=db,
                ingrediente_id=ing.id,
                tipo=TIPO_AJUSTE,
                cantidad=cantidad_revertida,
                stock_anterior=stock_anterior,
                stock_posterior=stock_posterior,
                referencia_id=pedido_id,
                referencia_tipo="PEDIDO",
                motivo=f"CANCELACION_PEDIDO_{pedido_id}",
            )
            ingrediente_repo.actualizar_stock(db, ing, stock_posterior)

    def registrar_ajuste_manual(
        self,
        db: Session,
        ingrediente_id: int,
        cantidad: Decimal,
        motivo: str,
    ) -> MovimientoStock:
        """
        Permite corregir el stock manualmente por pérdida, merma, error de conteo, etc.
        La cantidad puede ser positiva (aumenta) o negativa (disminuye).
        """
        ing = ingrediente_repo.obtener_por_id(db, ingrediente_id)
        if not ing:
            raise RecursoNoEncontrado("Ingrediente", ingrediente_id)
        if not ing.activo:
            raise RecursoInactivo("Ingrediente", ingrediente_id)

        stock_anterior = ing.stock_actual
        stock_posterior = stock_anterior + cantidad

        if stock_posterior < 0:
            raise StockInsuficiente([{
                "ingrediente_id": ingrediente_id,
                "nombre": ing.nombre,
                "stock_disponible": float(stock_anterior),
                "cantidad_requerida": float(abs(cantidad)),
                "faltante": float(abs(stock_posterior)),
            }])

        movimiento = movimiento_stock_repo.registrar(
            db=db,
            ingrediente_id=ingrediente_id,
            tipo=TIPO_AJUSTE,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_posterior=stock_posterior,
            motivo=motivo,
        )
        ingrediente_repo.actualizar_stock(db, ing, stock_posterior)
        return movimiento

    def validar_stock_pedido(self, db: Session, pedido_id: int) -> ValidacionStockResponse:
        """
        Consulta de solo lectura.
        Evalúa si el stock actual es suficiente para completar cada producto del pedido.
        """
        detalles = pedido_repo.obtener_detalles(db, pedido_id)
        productos_resultado: list[ValidacionProductoItem] = []

        for detalle in detalles:
            faltantes: list[IngredienteFaltante] = []
            stmt = (
                select(ProductoIngrediente)
                .where(ProductoIngrediente.producto_id == detalle.producto_id)
                .options(joinedload(ProductoIngrediente.ingrediente))
            )
            pi_list = list(db.execute(stmt).unique().scalars().all())

            for pi in pi_list:
                requerido = pi.cantidad_necesaria * detalle.cantidad
                disponible = pi.ingrediente.stock_actual
                if disponible < requerido:
                    faltantes.append(IngredienteFaltante(
                        ingrediente_id=pi.ingrediente_id,
                        nombre=pi.ingrediente.nombre,
                        unidad_medida=pi.ingrediente.unidad_medida,
                        stock_disponible=disponible,
                        cantidad_requerida=requerido,
                        faltante=requerido - disponible,
                    ))

            productos_resultado.append(ValidacionProductoItem(
                producto_id=detalle.producto_id,
                producto_nombre=detalle.producto.nombre if detalle.producto else "",
                cantidad_pedida=detalle.cantidad,
                puede_hacerse=len(faltantes) == 0,
                ingredientes_faltantes=faltantes,
            ))

        puede_completarse = all(p.puede_hacerse for p in productos_resultado)
        return ValidacionStockResponse(
            pedido_id=pedido_id,
            puede_completarse=puede_completarse,
            productos=productos_resultado,
        )

    def generar_reporte_compras_sugeridas(self, db: Session) -> ComprasSugeridasResponse:
        """
        Agrupa todos los pedidos PENDIENTES, calcula el total de ingredientes necesarios
        y los compara contra el stock actual para indicar exactamente qué comprar.
        """
        pendientes = pedido_repo.obtener_pedidos_pendientes(db)
        pedido_ids = [p.id for p in pendientes]

        # Acumular necesidades por ingrediente
        necesidades: dict[int, Decimal] = {}
        for pedido in pendientes:
            for detalle in pedido.detalles:
                stmt = (
                    select(ProductoIngrediente)
                    .where(ProductoIngrediente.producto_id == detalle.producto_id)
                    .options(joinedload(ProductoIngrediente.ingrediente))
                )
                pi_list = list(db.execute(stmt).unique().scalars().all())
                for pi in pi_list:
                    total_necesario = pi.cantidad_necesaria * detalle.cantidad
                    necesidades[pi.ingrediente_id] = (
                        necesidades.get(pi.ingrediente_id, Decimal("0")) + total_necesario
                    )

        # Comparar contra stock actual
        items: list[ComprasSugeridasItem] = []
        for ing_id, necesario in necesidades.items():
            ing = ingrediente_repo.obtener_por_id(db, ing_id)
            if not ing:
                continue
            if ing.stock_actual < necesario:
                items.append(ComprasSugeridasItem(
                    ingrediente_id=ing_id,
                    nombre=ing.nombre,
                    unidad_medida=ing.unidad_medida,
                    stock_actual=ing.stock_actual,
                    cantidad_necesaria_total=necesario,
                    cantidad_a_comprar=necesario - ing.stock_actual,
                ))

        return ComprasSugeridasResponse(
            pedidos_considerados=pedido_ids,
            items=items,
        )

    def obtener_historial_ingrediente(
        self, db: Session, ingrediente_id: int, tipo: str | None = None
    ) -> list[MovimientoStock]:
        ing = ingrediente_repo.obtener_por_id(db, ingrediente_id)
        if not ing:
            raise RecursoNoEncontrado("Ingrediente", ingrediente_id)
        return movimiento_stock_repo.obtener_por_ingrediente(db, ingrediente_id, tipo=tipo)


stock_service = StockService()
