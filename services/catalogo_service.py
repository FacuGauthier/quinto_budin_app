from sqlalchemy.orm import Session
from sqlalchemy import select
from models.producto import Producto
from models.pedido import Pedido, ESTADO_PENDIENTE, ESTADO_EN_PROCESO
from models.detalle_pedido import DetallePedido
from schemas.producto_schema import ProductoCreate, ProductoUpdate, RecetaUpdate, IngredienteEnReceta
from repositories.producto_repository import producto_repo
from repositories.ingrediente_repository import ingrediente_repo
from core.exceptions import (
    RecursoNoEncontrado, RecursoInactivo, OperacionNoPermitida
)


class CatalogoService:

    def crear_producto(self, db: Session, data: ProductoCreate) -> Producto:
        if producto_repo.existe_con_nombre(db, data.nombre):
            raise OperacionNoPermitida(
                f"Ya existe un producto activo con el nombre '{data.nombre}'."
            )
        return producto_repo.crear(db, data)

    def obtener_producto(self, db: Session, producto_id: int) -> Producto:
        producto = producto_repo.obtener_por_id(db, producto_id)
        if not producto:
            raise RecursoNoEncontrado("Producto", producto_id)
        return producto

    def listar_productos(self, db: Session, solo_activos: bool = True) -> list[Producto]:
        return producto_repo.obtener_todos(db, solo_activos=solo_activos)

    def actualizar_producto(self, db: Session, producto_id: int, data: ProductoUpdate) -> Producto:
        producto = self.obtener_producto(db, producto_id)
        if not producto.activo:
            raise RecursoInactivo("Producto", producto_id)
        if data.nombre and data.nombre != producto.nombre:
            if producto_repo.existe_con_nombre(db, data.nombre, excluir_id=id):
                raise OperacionNoPermitida(
                    f"Ya existe un producto activo con el nombre '{data.nombre}'."
                )
        return producto_repo.actualizar(db, producto, data)

    def desactivar_producto(self, db: Session, producto_id: int) -> Producto:
        producto = self.obtener_producto(db, producto_id)
        if not producto.activo:
            raise RecursoInactivo("Producto", producto_id)

        # Verificar que no esté en pedidos activos
        stmt = (
            select(DetallePedido)
            .join(DetallePedido.pedido)
            .where(
                DetallePedido.producto_id == id,
                Pedido.estado.in_([ESTADO_PENDIENTE, ESTADO_EN_PROCESO]),
            )
        )
        en_uso = db.execute(stmt).scalar_one_or_none()
        if en_uso:
            raise OperacionNoPermitida(
                f"El producto id={id} tiene pedidos activos (PENDIENTE o EN_PROCESO). "
                "No puede desactivarse."
            )
        return producto_repo.desactivar(db, producto)

    def definir_receta(self, db: Session, producto_id: int, data: RecetaUpdate) -> list[IngredienteEnReceta]:
        producto = self.obtener_producto(db, producto_id)
        if not producto.activo:
            raise RecursoInactivo("Producto", producto_id)

        # Validar que todos los ingredientes existan y estén activos
        for item in data.ingredientes:
            ing = ingrediente_repo.obtener_por_id(db, item.ingrediente_id)
            if not ing:
                raise RecursoNoEncontrado("Ingrediente", item.ingrediente_id)
            if not ing.activo:
                raise RecursoInactivo("Ingrediente", item.ingrediente_id)

        producto_repo.actualizar_receta(db, producto_id, data.ingredientes)
        return self.obtener_receta(db, producto_id)

    def obtener_receta(self, db: Session, producto_id: int) -> list[IngredienteEnReceta]:
        pi_list = producto_repo.obtener_ingredientes_de_producto(db, producto_id)
        return [
            IngredienteEnReceta(
                ingrediente_id=pi.ingrediente_id,
                ingrediente_nombre=pi.ingrediente.nombre if pi.ingrediente else None,
                unidad_medida=pi.ingrediente.unidad_medida if pi.ingrediente else None,
                cantidad_necesaria=pi.cantidad_necesaria,
            )
            for pi in pi_list
        ]


catalogo_service = CatalogoService()
