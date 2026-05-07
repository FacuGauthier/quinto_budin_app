from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models.producto import Producto
from models.producto_ingrediente import ProductoIngrediente
from schemas.producto_schema import ProductoCreate, ProductoUpdate, RecetaItem


class ProductoRepository:

    def crear(self, db: Session, data: ProductoCreate) -> Producto:
        producto = Producto(
            nombre=data.nombre,
            precio=data.precio,
            tiempo_desarrollo=data.tiempo_desarrollo,
        )
        db.add(producto)
        db.commit()
        db.refresh(producto)
        return producto

    def obtener_por_id(self, db: Session, producto_id: int) -> Producto | None:
        stmt = (
            select(Producto)
            .where(Producto.id == producto_id)
            .options(
                joinedload(Producto.ingredientes).joinedload(ProductoIngrediente.ingrediente)
            )
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    def obtener_todos(self, db: Session, solo_activos: bool = True) -> list[Producto]:
        stmt = select(Producto)
        if solo_activos:
            stmt = stmt.where(Producto.activo == True)  # noqa: E712
        stmt = stmt.order_by(Producto.nombre)
        return list(db.execute(stmt).scalars().all())

    def actualizar(self, db: Session, producto: Producto, data: ProductoUpdate) -> Producto:
        cambios = data.model_dump(exclude_none=True)
        for campo, valor in cambios.items():
            setattr(producto, campo, valor)
        producto.fecha_modificacion = datetime.now()
        db.commit()
        db.refresh(producto)
        return producto

    def desactivar(self, db: Session, producto: Producto) -> Producto:
        producto.activo = False
        producto.fecha_modificacion = datetime.now()
        db.commit()
        db.refresh(producto)
        return producto

    def actualizar_receta(
        self, db: Session, producto_id: int, items: list[RecetaItem]
    ) -> None:
        # Elimina receta anterior
        stmt = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id
        )
        existentes = list(db.execute(stmt).scalars().all())
        for pi in existentes:
            db.delete(pi)

        # Inserta nueva receta
        for item in items:
            pi = ProductoIngrediente(
                producto_id=producto_id,
                ingrediente_id=item.ingrediente_id,
                cantidad_necesaria=item.cantidad_necesaria,
            )
            db.add(pi)
        db.commit()

    def obtener_ingredientes_de_producto(
        self, db: Session, producto_id: int
    ) -> list[ProductoIngrediente]:
        stmt = (
            select(ProductoIngrediente)
            .where(ProductoIngrediente.producto_id == producto_id)
            .options(joinedload(ProductoIngrediente.ingrediente))
        )
        return list(db.execute(stmt).unique().scalars().all())

    def existe_con_nombre(
        self, db: Session, nombre: str, excluir_id: int | None = None
    ) -> bool:
        stmt = select(Producto).where(
            Producto.nombre == nombre,
            Producto.activo == True,  # noqa: E712
        )
        if excluir_id is not None:
            stmt = stmt.where(Producto.id != excluir_id)
        return db.execute(stmt).scalar_one_or_none() is not None


producto_repo = ProductoRepository()
