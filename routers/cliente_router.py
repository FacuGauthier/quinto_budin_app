from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.cliente_schema import ClienteCreate, ClienteUpdate, ClienteResponse, ClienteListResponse
from services.cliente_service import cliente_service

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(data: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.crear_cliente(db, data)


@router.get("", response_model=ClienteListResponse)
def listar_clientes(
    solo_activos: bool = True,
    nombre: str | None = None,
    apellido: str | None = None,
    telefono: str | None = None,
    db: Session = Depends(get_db),
):
    clientes = cliente_service.listar_clientes(
        db, solo_activos=solo_activos,
        nombre=nombre, apellido=apellido, telefono=telefono,
    )
    return ClienteListResponse(total=len(clientes), clientes=clientes)


@router.get("/{id}", response_model=ClienteResponse)
def obtener_cliente(id: int, db: Session = Depends(get_db)):
    return cliente_service.obtener_cliente(db, id)


@router.put("/{id}", response_model=ClienteResponse)
def actualizar_cliente(id: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    return cliente_service.actualizar_cliente(db, id, data)


@router.delete("/{id}", response_model=ClienteResponse)
def desactivar_cliente(id: int, db: Session = Depends(get_db)):
    return cliente_service.desactivar_cliente(db, id)
