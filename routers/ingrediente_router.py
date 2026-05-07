from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.ingrediente_schema import (
    IngredienteCreate, IngredienteUpdate,
    IngredienteResponse, IngredienteListResponse, StockResponse,
)
from services.ingrediente_service import ingrediente_service

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])


@router.post("", response_model=IngredienteResponse, status_code=status.HTTP_201_CREATED)
def crear_ingrediente(data: IngredienteCreate, db: Session = Depends(get_db)):
    return ingrediente_service.crear_ingrediente(db, data)


@router.get("", response_model=IngredienteListResponse)
def listar_ingredientes(solo_activos: bool = True, db: Session = Depends(get_db)):
    ingredientes = ingrediente_service.listar_ingredientes(db, solo_activos=solo_activos)
    return IngredienteListResponse(total=len(ingredientes), ingredientes=ingredientes)


@router.get("/{id}", response_model=IngredienteResponse)
def obtener_ingrediente(id: int, db: Session = Depends(get_db)):
    return ingrediente_service.obtener_ingrediente(db, id)


@router.put("/{id}", response_model=IngredienteResponse)
def actualizar_ingrediente(id: int, data: IngredienteUpdate, db: Session = Depends(get_db)):
    return ingrediente_service.actualizar_ingrediente(db, id, data)


@router.delete("/{id}", response_model=IngredienteResponse)
def desactivar_ingrediente(id: int, db: Session = Depends(get_db)):
    return ingrediente_service.desactivar_ingrediente(db, id)


@router.get("/{id}/stock", response_model=StockResponse)
def consultar_stock(id: int, db: Session = Depends(get_db)):
    ing = ingrediente_service.obtener_ingrediente(db, id)
    return StockResponse(
        ingrediente_id=ing.id,
        nombre=ing.nombre,
        stock_actual=ing.stock_actual,
        unidad_medida=ing.unidad_medida,
    )
