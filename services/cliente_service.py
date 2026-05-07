from sqlalchemy.orm import Session
from models.cliente import Cliente
from schemas.cliente_schema import ClienteCreate, ClienteUpdate
from repositories.cliente_repository import cliente_repo
from core.exceptions import RecursoNoEncontrado, RecursoInactivo, OperacionNoPermitida


class ClienteService:

    def crear_cliente(self, db: Session, data: ClienteCreate) -> Cliente:
        if cliente_repo.existe_con_telefono(db, data.telefono):
            raise OperacionNoPermitida(
                f"Ya existe un cliente activo con el teléfono '{data.telefono}'."
            )
        return cliente_repo.crear(db, data)

    def obtener_cliente(self, db: Session, cliente_id: int) -> Cliente:
        cliente = cliente_repo.obtener_por_id(db, cliente_id)
        if not cliente:
            raise RecursoNoEncontrado("Cliente", cliente_id)
        return cliente

    def listar_clientes(
        self,
        db: Session,
        solo_activos: bool = True,
        nombre: str | None = None,
        apellido: str | None = None,
        telefono: str | None = None,
    ) -> list[Cliente]:
        return cliente_repo.obtener_todos(
            db, solo_activos=solo_activos,
            nombre=nombre, apellido=apellido, telefono=telefono,
        )

    def actualizar_cliente(self, db: Session, cliente_id: int, data: ClienteUpdate) -> Cliente:
        cliente = self.obtener_cliente(db, cliente_id)
        if not cliente.activo:
            raise RecursoInactivo("Cliente", cliente_id)
        if data.telefono and data.telefono != cliente.telefono:
            if cliente_repo.existe_con_telefono(db, data.telefono, excluir_id=id):
                raise OperacionNoPermitida(
                    f"Ya existe un cliente activo con el teléfono '{data.telefono}'."
                )
        return cliente_repo.actualizar(db, cliente, data)

    def desactivar_cliente(self, db: Session, cliente_id: int) -> Cliente:
        cliente = self.obtener_cliente(db, cliente_id)
        if not cliente.activo:
            raise RecursoInactivo("Cliente", cliente_id)
        return cliente_repo.desactivar(db, cliente)


cliente_service = ClienteService()
