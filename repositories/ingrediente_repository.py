from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.ingrediente import Ingrediente
from schemas.ingrediente_schema import IngredienteCreate, IngredienteUpdate


class IngredienteRepository:

    def crear(self, db: Session, data: IngredienteCreate) -> Ingrediente:
        ingrediente = Ingrediente(
            nombre=data.nombre,
            marca=data.marca,
            unidad_medida=data.unidad_medida,
            stock_actual=data.stock_inicial,
        )
        db.add(ingrediente)
        db.commit()
        db.refresh(ingrediente)
        return ingrediente

    def obtener_por_id(self, db: Session, ingrediente_id: int) -> Ingrediente | None:
        return db.get(Ingrediente, ingrediente_id)

    def obtener_todos(self, db: Session, solo_activos: bool = True) -> list[Ingrediente]:
        stmt = select(Ingrediente)
        if solo_activos:
            stmt = stmt.where(Ingrediente.activo == True)  # noqa: E712
        stmt = stmt.order_by(Ingrediente.nombre)
        return list(db.execute(stmt).scalars().all())

    def actualizar(self, db: Session, ingrediente: Ingrediente, data: IngredienteUpdate) -> Ingrediente:
        # stock_actual está intencionalmente excluido; sólo se modifica por actualizar_stock()
        cambios = data.model_dump(exclude_none=True)
        for campo, valor in cambios.items():
            setattr(ingrediente, campo, valor)
        ingrediente.fecha_modificacion = datetime.now()
        db.commit()
        db.refresh(ingrediente)
        return ingrediente

    def desactivar(self, db: Session, ingrediente: Ingrediente) -> Ingrediente:
        ingrediente.activo = False
        ingrediente.fecha_modificacion = datetime.now()
        db.commit()
        db.refresh(ingrediente)
        return ingrediente

    def actualizar_stock(
        self, db: Session, ingrediente: Ingrediente, nuevo_stock: Decimal
    ) -> Ingrediente:
        """
        Único método que modifica stock_actual.
        Debe ser llamado sólo desde stock_service, después de registrar el movimiento.
        """
        ingrediente.stock_actual = nuevo_stock
        ingrediente.fecha_modificacion = datetime.now()
        db.commit()
        db.refresh(ingrediente)
        return ingrediente

    def obtener_stock_actual(self, db: Session, id: int) -> Decimal | None:
        ingrediente = db.get(Ingrediente, id)
        return ingrediente.stock_actual if ingrediente else None

    def existe_con_nombre(
        self, db: Session, nombre: str, excluir_id: int | None = None
    ) -> bool:
        stmt = select(Ingrediente).where(Ingrediente.nombre == nombre)
        if excluir_id is not None:
            stmt = stmt.where(Ingrediente.id != excluir_id)
        return db.execute(stmt).scalar_one_or_none() is not None


ingrediente_repo = IngredienteRepository()
