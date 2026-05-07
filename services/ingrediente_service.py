from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.ingrediente import Ingrediente
from models.producto_ingrediente import ProductoIngrediente
from models.producto import Producto
from schemas.ingrediente_schema import IngredienteCreate, IngredienteUpdate
from repositories.ingrediente_repository import ingrediente_repo
from repositories.movimiento_stock_repository import movimiento_stock_repo
from models.movimiento_stock import TIPO_AJUSTE
from core.exceptions import RecursoNoEncontrado, RecursoInactivo, OperacionNoPermitida


class IngredienteService:

    def crear_ingrediente(self, db: Session, data: IngredienteCreate) -> Ingrediente:
        if ingrediente_repo.existe_con_nombre(db, data.nombre):
            raise OperacionNoPermitida(
                f"Ya existe un ingrediente con el nombre '{data.nombre}'."
            )
        ingrediente = ingrediente_repo.crear(db, data)

        # Registrar movimiento inicial si el stock > 0
        if data.stock_inicial > 0:
            movimiento_stock_repo.registrar(
                db=db,
                ingrediente_id=ingrediente.id,
                tipo=TIPO_AJUSTE,
                cantidad=data.stock_inicial,
                stock_anterior=Decimal("0"),
                stock_posterior=data.stock_inicial,
                motivo="STOCK INICIAL",
            )
        return ingrediente

    def obtener_ingrediente(self, db: Session, ingrediente_id: int) -> Ingrediente:
        ing = ingrediente_repo.obtener_por_id(db, ingrediente_id)
        if not ing:
            raise RecursoNoEncontrado("Ingrediente", ingrediente_id)
        return ing

    def listar_ingredientes(self, db: Session, solo_activos: bool = True) -> list[Ingrediente]:
        return ingrediente_repo.obtener_todos(db, solo_activos=solo_activos)

    def actualizar_ingrediente(self, db: Session, ingrediente_id: int, data: IngredienteUpdate) -> Ingrediente:
        ing = self.obtener_ingrediente(db, ingrediente_id)
        if not ing.activo:
            raise RecursoInactivo("Ingrediente", ingrediente_id)
        if data.nombre and data.nombre != ing.nombre:
            if ingrediente_repo.existe_con_nombre(db, data.nombre, excluir_id=id):
                raise OperacionNoPermitida(
                    f"Ya existe un ingrediente con el nombre '{data.nombre}'."
                )
        return ingrediente_repo.actualizar(db, ing, data)

    def desactivar_ingrediente(self, db: Session, ingrediente_id: int) -> Ingrediente:
        ing = self.obtener_ingrediente(db, ingrediente_id)
        if not ing.activo:
            raise RecursoInactivo("Ingrediente", ingrediente_id)

        # Verificar que no esté en recetas activas
        stmt = (
            select(ProductoIngrediente)
            .join(ProductoIngrediente.producto)
            .where(
                ProductoIngrediente.ingrediente_id == ingrediente_id,
                Producto.activo == True,  # noqa: E712
            )
        )
        en_receta = db.execute(stmt).scalar_one_or_none()
        if en_receta:
            raise OperacionNoPermitida(
                f"El ingrediente id={id} está en recetas de productos activos. "
                "Quitalo de las recetas antes de desactivarlo."
            )
        return ingrediente_repo.desactivar(db, ing)

    def consultar_stock(self, db: Session, ingrediente_id: int) -> Decimal:
        ing = self.obtener_ingrediente(db, ingrediente_id)
        return ing.stock_actual


ingrediente_service = IngredienteService()
