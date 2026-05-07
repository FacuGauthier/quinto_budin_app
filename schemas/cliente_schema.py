from datetime import datetime
from pydantic import BaseModel, field_validator


class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    telefono: str

    @field_validator("nombre", "apellido")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El campo no puede estar vacío.")
        return v

    @field_validator("telefono")
    @classmethod
    def telefono_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El teléfono no puede estar vacío.")
        return v


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    telefono: str | None = None


class ClienteResponse(ClienteBase):
    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_modificacion: datetime

    model_config = {"from_attributes": True}


class ClienteListResponse(BaseModel):
    total: int
    clientes: list[ClienteResponse]
