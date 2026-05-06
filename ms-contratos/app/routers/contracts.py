"""Endpoints del microservicio de Contratos."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database import get_db
from app.models import ContractStatus
from app.schemas import (
    ContractGenerateRequest,
    ContractGenerateResponse,
    ContractListResponse,
    ContractResponse,
    ContractTypeResponse,
    MessageResponse,
)
from app import crud

router = APIRouter(prefix="/contratos", tags=["Contratos"])
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/generate",
    response_model=ContractGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar contrato",
    description="Genera y persiste un contrato básico parametrizable",
)
async def generate_contract(
    db: DbDep,
    payload: ContractGenerateRequest,
):
    contract, employee, contract_type, document, error = await crud.generate_contract(db, payload)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return ContractGenerateResponse(
        contract=ContractResponse.model_validate(contract),
        employee=employee,
        contract_type=contract_type,
        document=document,
    )


@router.get(
    "/types",
    response_model=list[ContractTypeResponse],
    summary="Listar tipos de contrato",
    description="Obtiene los tipos de contrato disponibles",
)
async def list_types(db: DbDep):
    return await crud.list_contract_types(db)


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    summary="Obtener contrato",
    description="Devuelve un contrato por ID",
)
async def get_contract(
    db: DbDep,
    contract_id: int = Path(..., gt=0, description="ID del contrato"),
):
    contract = await crud.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contrato con ID {contract_id} no encontrado",
        )
    return contract


@router.get(
    "/employees/{employee_id}",
    response_model=ContractListResponse,
    summary="Contratos por funcionario",
    description="Lista contratos de un funcionario",
)
async def get_contracts_by_employee(
    db: DbDep,
    employee_id: int = Path(..., gt=0, description="ID del funcionario"),
    status_filter: ContractStatus | None = Query(None, alias="status", description="Filtrar por estado"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
):
    result = await crud.get_employee_summary(db, employee_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionario con ID {employee_id} no encontrado",
        )

    items = await crud.list_contracts_by_employee(db, employee_id)
    if status_filter:
        items = [item for item in items if item.status == status_filter]
    items = items[skip: skip + limit]
    total = await crud.count_contracts_by_employee(db, employee_id)
    if status_filter:
        total = len([item for item in await crud.list_contracts_by_employee(db, employee_id) if item.status == status_filter])
    return ContractListResponse(items=items, total=total)


@router.get(
    "/health-check",
    response_model=MessageResponse,
    summary="Health auxiliar",
    description="Endpoint auxiliar de comprobación del router",
)
async def router_health_check():
    return MessageResponse(message="Contracts router activo")
