"""Endpoints para gestión de empleados - Core del microservicio."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from app.database import get_db
from app.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeDetailResponse, MessageResponse
)
from app import crud

router = APIRouter(prefix="/employees", tags=["Empleados"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/",
    response_model=List[EmployeeDetailResponse],
    summary="Listar empleados",
    description="Obtiene la lista de todos los empleados de la empresa con filtros opcionales"
)
async def list_employees(
    db: DbDep,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    status: str = Query(None, description="Filtrar por estado (Activo, Baja, Suspendido)"),
    department_id: int = Query(None, gt=0, description="Filtrar por ID de departamento")
):
    """
    Listar todos los empleados.
    
    **Parámetros de query:**
    - **skip**: número de registros a omitir (paginación)
    - **limit**: número máximo de registros a retornar
    - **status**: filtrar por estado del empleado
    - **department_id**: filtrar por departamento
    """
    return await crud.get_employees(db, skip=skip, limit=limit, status=status, department_id=department_id)


@router.get(
    "/count",
    summary="Contar empleados",
    description="Obtiene la cantidad total de empleados con filtros opcionales"
)
async def count_employees(
    db: DbDep,
    status: str = Query(None, description="Filtrar por estado"),
    department_id: int = Query(None, gt=0, description="Filtrar por departamento")
):
    """Obtener el total de empleados."""
    count = await crud.get_employees_count(db, status=status, department_id=department_id)
    return {"total": count}


@router.get(
    "/{employee_id}",
    response_model=EmployeeDetailResponse,
    summary="Obtener empleado",
    description="Obtiene los detalles completos de un empleado específico"
)
async def get_employee(
    db: DbDep,
    employee_id: int = Path(..., gt=0, description="ID del empleado")
):
    """Obtener un empleado específico por su ID."""
    employee = await crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empleado con ID {employee_id} no encontrado"
        )
    return employee


@router.get(
    "/by-ci/{ci}",
    response_model=EmployeeDetailResponse,
    summary="Obtener empleado por CI",
    description="Obtiene un empleado por su cédula de identidad"
)
async def get_employee_by_ci(
    db: DbDep,
    ci: str = Path(..., min_length=5, description="Cédula de identidad")
):
    """Obtener empleado por cédula de identidad."""
    employee = await crud.get_employee_by_ci(db, ci)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empleado con CI '{ci}' no encontrado"
        )
    return employee


@router.post(
    "/",
    response_model=EmployeeDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear empleado",
    description="Crea un nuevo empleado en el sistema"
)
async def create_employee(
    db: DbDep,
    employee: EmployeeCreate
):
    """
    Crear un nuevo empleado.
    
    **Campos requeridos:**
    - **ci**: Cédula de identidad (única)
    - **first_name**: Nombre
    - **last_name**: Apellido
    - **email**: Email (único)
    - **hire_date**: Fecha de ingreso (YYYY-MM-DD)
    - **current_salary**: Salario actual
    - **department_id**: ID del departamento
    - **position_id**: ID de la posición
    
    **Campos opcionales:**
    - **phone**: Teléfono de contacto
    """
    # Verificar que la cédula sea única
    existing_ci = await crud.get_employee_by_ci(db, employee.ci)
    if existing_ci:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un empleado con la CI '{employee.ci}'"
        )
    
    # Verificar que el email sea único
    existing_email = await crud.get_employee_by_email(db, employee.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un empleado con el email '{employee.email}'"
        )
    
    # Verificar que el departamento exista
    department = await crud.get_department(db, employee.department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento con ID {employee.department_id} no encontrado"
        )
    
    # Verificar que la posición exista
    position = await crud.get_position(db, employee.position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Posición con ID {employee.position_id} no encontrada"
        )
    
    return await crud.create_employee(db, employee)


@router.put(
    "/{employee_id}",
    response_model=EmployeeDetailResponse,
    summary="Actualizar empleado",
    description="Actualiza la información de un empleado existente"
)
async def update_employee(
    db: DbDep,
    employee_id: int = Path(..., gt=0, description="ID del empleado"),
    employee: EmployeeUpdate = None
):
    """
    Actualizar un empleado existente.
    
    **Campos que pueden actualizarse:**
    - first_name
    - last_name
    - email
    - phone
    - current_salary
    - department_id
    - position_id
    - status (Activo, Baja, Suspendido)
    """
    db_employee = await crud.get_employee(db, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empleado con ID {employee_id} no encontrado"
        )
    
    # Si se intenta cambiar el email, verificar que sea único
    if employee.email and employee.email != db_employee.email:
        existing_email = await crud.get_employee_by_email(db, employee.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro empleado con el email '{employee.email}'"
            )
    
    # Verificar que el departamento exista si se intenta cambiar
    if employee.department_id and employee.department_id != db_employee.department_id:
        department = await crud.get_department(db, employee.department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departamento con ID {employee.department_id} no encontrado"
            )
    
    # Verificar que la posición exista si se intenta cambiar
    if employee.position_id and employee.position_id != db_employee.position_id:
        position = await crud.get_position(db, employee.position_id)
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Posición con ID {employee.position_id} no encontrada"
            )
    
    return await crud.update_employee(db, employee_id, employee)


@router.delete(
    "/{employee_id}",
    response_model=MessageResponse,
    summary="Eliminar empleado",
    description="Elimina un empleado del sistema de forma física"
)
async def delete_employee(
    db: DbDep,
    employee_id: int = Path(..., gt=0, description="ID del empleado")
):
    """Eliminar un empleado de forma física."""
    db_employee = await crud.delete_employee(db, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empleado con ID {employee_id} no encontrado"
        )
    return {"message": f"Empleado '{db_employee.first_name} {db_employee.last_name}' eliminado exitosamente"}


@router.patch(
    "/{employee_id}/deactivate",
    response_model=EmployeeDetailResponse,
    summary="Dar de baja a empleado",
    description="Cambia el estado del empleado a 'Baja' sin eliminarlo del sistema"
)
async def deactivate_employee(
    db: DbDep,
    employee_id: int = Path(..., gt=0, description="ID del empleado")
):
    """
    Dar de baja a un empleado sin eliminarlo (cambiar estado a Baja).
    Esto es más seguro que eliminar, preservando el historial.
    """
    db_employee = await crud.deactivate_employee(db, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empleado con ID {employee_id} no encontrado"
        )
    return db_employee


@router.get(
    "/department/{department_id}/list",
    response_model=List[EmployeeDetailResponse],
    summary="Listar empleados por departamento",
    description="Obtiene todos los empleados de un departamento específico"
)
async def get_employees_by_department(
    db: DbDep,
    department_id: int = Path(..., gt=0, description="ID del departamento")
):
    """Obtener todos los empleados de un departamento."""
    # Verificar que el departamento exista
    department = await crud.get_department(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento con ID {department_id} no encontrado"
        )
    
    return await crud.get_employees_by_department(db, department_id)
