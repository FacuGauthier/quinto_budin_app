from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.producto_schema import (
    ProductoCreate, ProductoUpdate, ProductoResponse,
    ProductoDetalleResponse, ProductoListResponse, RecetaUpdate, IngredienteEnReceta,
)
from services.catalogo_service import catalogo_service

router = APIRouter(prefix="/productos", tags=["Catálogo"])


@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    return catalogo_service.crear_producto(db, data)


@router.get("", response_model=ProductoListResponse)
def listar_productos(solo_activos: bool = True, db: Session = Depends(get_db)):
    productos = catalogo_service.listar_productos(db, solo_activos=solo_activos)
    return ProductoListResponse(total=len(productos), productos=productos)


@router.get("/{id}", response_model=ProductoDetalleResponse)
def obtener_producto(id: int, db: Session = Depends(get_db)):
    producto = catalogo_service.obtener_producto(db, id)
    receta = catalogo_service.obtener_receta(db, id)
    # Construir respuesta enriquecida
    return ProductoDetalleResponse(
        id=producto.id,
        nombre=producto.nombre,
        precio=producto.precio,
        tiempo_desarrollo=producto.tiempo_desarrollo,
        activo=producto.activo,
        fecha_creacion=producto.fecha_creacion,
        fecha_modificacion=producto.fecha_modificacion,
        ingredientes=receta,
    )


@router.put("/{id}", response_model=ProductoResponse)
def actualizar_producto(id: int, data: ProductoUpdate, db: Session = Depends(get_db)):
    return catalogo_service.actualizar_producto(db, id, data)


@router.delete("/{id}", response_model=ProductoResponse)
def desactivar_producto(id: int, db: Session = Depends(get_db)):
    return catalogo_service.desactivar_producto(db, id)


@router.put("/{id}/receta", response_model=list[IngredienteEnReceta])
def definir_receta(id: int, data: RecetaUpdate, db: Session = Depends(get_db)):
    return catalogo_service.definir_receta(db, id, data)
