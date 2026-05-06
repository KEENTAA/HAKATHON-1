"""Endpoints para gestión de departamentos."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from app.database import get_db
from app.schemas import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse, MessageResponse, ErrorResponse
)
from app import crud

router = APIRouter(prefix="/departments", tags=["Departamentos"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/",
    response_model=List[DepartmentResponse],
    summary="Listar departamentos",
    description="Obtiene la lista de todos los departamentos de la empresa con paginación"
)
async def list_departments(
    db: DbDep,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros")
):
    """
    Listar todos los departamentos.
    
    - **skip**: número de registros a omitir (paginación)
    - **limit**: número máximo de registros a retornar
    """
    return await crud.get_departments(db, skip=skip, limit=limit)


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Obtener departamento",
    description="Obtiene los detalles de un departamento específico"
)
async def get_department(
    db: DbDep,
    department_id: int = Path(..., gt=0, description="ID del departamento")
):
    """Obtener un departamento específico por su ID."""
    department = await crud.get_department(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento con ID {department_id} no encontrado"
        )
    return department


@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear departamento",
    description="Crea un nuevo departamento en la empresa"
)
async def create_department(
    db: DbDep,
    department: DepartmentCreate
):
    """
    Crear un nuevo departamento.
    
    - **name**: Nombre único del departamento (requerido)
    - **description**: Descripción del departamento (opcional)
    """
    # Verificar si ya existe un departamento con ese nombre
    existing = await crud.get_department_by_name(db, department.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un departamento con el nombre '{department.name}'"
        )
    
    return await crud.create_department(db, department)


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Actualizar departamento",
    description="Actualiza la información de un departamento existente"
)
async def update_department(
    db: DbDep,
    department_id: int = Path(..., gt=0, description="ID del departamento"),
    department: DepartmentUpdate = None
):
    """Actualizar un departamento existente."""
    db_department = await crud.update_department(db, department_id, department)
    if not db_department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento con ID {department_id} no encontrado"
        )
    return db_department


@router.delete(
    "/{department_id}",
    response_model=MessageResponse,
    summary="Eliminar departamento",
    description="Elimina un departamento de la empresa"
)
async def delete_department(
    db: DbDep,
    department_id: int = Path(..., gt=0, description="ID del departamento")
):
    """Eliminar un departamento."""
    db_department = await crud.delete_department(db, department_id)
    if not db_department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento con ID {department_id} no encontrado"
        )
    return {"message": f"Departamento '{db_department.name}' eliminado exitosamente"}
