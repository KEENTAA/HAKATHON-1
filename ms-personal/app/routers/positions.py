"""Endpoints para gestión de posiciones/cargos."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from app.database import get_db
from app.schemas import (
    PositionCreate, PositionUpdate, PositionResponse, MessageResponse
)
from app import crud

router = APIRouter(prefix="/positions", tags=["Posiciones"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/",
    response_model=List[PositionResponse],
    summary="Listar posiciones",
    description="Obtiene la lista de todas las posiciones/cargos disponibles"
)
async def list_positions(
    db: DbDep,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros")
):
    """
    Listar todas las posiciones.
    
    - **skip**: número de registros a omitir (paginación)
    - **limit**: número máximo de registros a retornar
    """
    return await crud.get_positions(db, skip=skip, limit=limit)


@router.get(
    "/{position_id}",
    response_model=PositionResponse,
    summary="Obtener posición",
    description="Obtiene los detalles de una posición específica"
)
async def get_position(
    db: DbDep,
    position_id: int = Path(..., gt=0, description="ID de la posición")
):
    """Obtener una posición específica por su ID."""
    position = await crud.get_position(db, position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Posición con ID {position_id} no encontrada"
        )
    return position


@router.post(
    "/",
    response_model=PositionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear posición",
    description="Crea una nueva posición/cargo en la empresa"
)
async def create_position(
    db: DbDep,
    position: PositionCreate
):
    """
    Crear una nueva posición.
    
    - **name**: Nombre único del cargo (requerido)
    - **base_salary**: Salario base sugerido para el cargo (requerido, > 0)
    """
    # Verificar si ya existe una posición con ese nombre
    existing = await crud.get_position_by_name(db, position.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una posición con el nombre '{position.name}'"
        )
    
    return await crud.create_position(db, position)


@router.put(
    "/{position_id}",
    response_model=PositionResponse,
    summary="Actualizar posición",
    description="Actualiza la información de una posición existente"
)
async def update_position(
    db: DbDep,
    position_id: int = Path(..., gt=0, description="ID de la posición"),
    position: PositionUpdate = None
):
    """Actualizar una posición existente."""
    db_position = await crud.update_position(db, position_id, position)
    if not db_position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Posición con ID {position_id} no encontrada"
        )
    return db_position


@router.delete(
    "/{position_id}",
    response_model=MessageResponse,
    summary="Eliminar posición",
    description="Elimina una posición de la empresa"
)
async def delete_position(
    db: DbDep,
    position_id: int = Path(..., gt=0, description="ID de la posición")
):
    """Eliminar una posición."""
    db_position = await crud.delete_position(db, position_id)
    if not db_position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Posición con ID {position_id} no encontrada"
        )
    return {"message": f"Posición '{db_position.name}' eliminada exitosamente"}
