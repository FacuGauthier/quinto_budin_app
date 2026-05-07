from sqlalchemy.orm import Session
from models.compra import Compra
from schemas.compra_schema import CompraCreate
from repositories.compra_repository import compra_repo
from repositories.ingrediente_repository import ingrediente_repo
from services.stock_service import stock_service
from core.exceptions import RecursoNoEncontrado, RecursoInactivo


class CompraService:

    def registrar_compra(self, db: Session, data: CompraCreate) -> Compra:
        # Validar todos los ingredientes antes de persistir
        for detalle in data.detalles:
            ing = ingrediente_repo.obtener_por_id(db, detalle.ingrediente_id)
            if not ing:
                raise RecursoNoEncontrado("Ingrediente", detalle.ingrediente_id)
            if not ing.activo:
                raise RecursoInactivo("Ingrediente", detalle.ingrediente_id)

        # Crear cabecera
        compra = compra_repo.crear(db, data)

        # Insertar detalles e impactar stock
        for detalle in data.detalles:
            compra_repo.agregar_detalle(db, compra.id, detalle)
            stock_service.actualizar_stock_por_compra(
                db=db,
                ingrediente_id=detalle.ingrediente_id,
                cantidad=detalle.cantidad,
                compra_id=compra.id,
            )

        # Calcular y persistir total
        compra_repo.calcular_y_actualizar_total(db, compra.id)
        return compra_repo.obtener_por_id(db, compra.id)

    def obtener_compra(self, db: Session, compra_id: int) -> Compra:
        compra = compra_repo.obtener_por_id(db, compra_id)
        if not compra:
            raise RecursoNoEncontrado("Compra", compra_id)
        return compra

    def listar_compras(self, db: Session) -> list[Compra]:
        return compra_repo.obtener_todas(db)


compra_service = CompraService()
