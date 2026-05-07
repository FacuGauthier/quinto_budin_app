from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.cliente import Cliente
from schemas.cliente_schema import ClienteCreate, ClienteUpdate


class ClienteRepository:

    def crear(self, db: Session, data: ClienteCreate) -> Cliente:
        cliente = Cliente(
            nombre=data.nombre,
            apellido=data.apellido,
            telefono=data.telefono,
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente

    def obtener_por_id(self, db: Session, cliente_id: int) -> Cliente | None:
        return db.get(Cliente, cliente_id)

    def obtener_todos(
        self,
        db: Session,
        solo_activos: bool = True,
        nombre: str | None = None,
        apellido: str | None = None,
        telefono: str | None = None,
    ) -> list[Cliente]:
        stmt = select(Cliente)
        if solo_activos:
            stmt = stmt.where(Cliente.activo == True)  # noqa: E712
        if nombre:
            stmt = stmt.where(Cliente.nombre.ilike(f"%{nombre}%"))
        if apellido:
            stmt = stmt.where(Cliente.apellido.ilike(f"%{apellido}%"))
        if telefono:
            stmt = stmt.where(Cliente.telefono.ilike(f"%{telefono}%"))
        stmt = stmt.order_by(Cliente.apellido, Cliente.nombre)
        return list(db.execute(stmt).scalars().all())

    def actualizar(self, db: Session, cliente: Cliente, data: ClienteUpdate) -> Cliente:
        cambios = data.model_dump(exclude_none=True)
        for campo, valor in cambios.items():
            setattr(cliente, campo, valor)
        cliente.fecha_modificacion = datetime.now()
        db.commit()
        db.refresh(cliente)
        return cliente

    def desactivar(self, db: Session, cliente: Cliente) -> Cliente:
        cliente.activo = False
        cliente.fecha_modificacion = datetime.now()
        db.commit()
        db.refresh(cliente)
        return cliente

    def existe_con_telefono(
        self, db: Session, telefono: str, excluir_id: int | None = None
    ) -> bool:
        stmt = select(Cliente).where(
            Cliente.telefono == telefono,
            Cliente.activo == True,  # noqa: E712
        )
        if excluir_id is not None:
            stmt = stmt.where(Cliente.id != excluir_id)
        resultado = db.execute(stmt).scalar_one_or_none()
        return resultado is not None


cliente_repo = ClienteRepository()
