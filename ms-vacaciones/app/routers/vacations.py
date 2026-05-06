"""Endpoints del microservicio de Vacaciones."""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database import get_db
from app.models import VacationRequestStatus
from app.schemas import (
    MessageResponse,
    VacationBalanceResponse,
    VacationEligibilityResponse,
    VacationRequestCreate,
    VacationRequestListResponse,
    VacationRequestResponse,
    VacationRequestReview,
)
from app import crud

router = APIRouter(prefix="/vacations", tags=["Vacaciones"])
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/employees/{employee_id}/balance",
    response_model=VacationBalanceResponse,
    summary="Consultar balance de vacaciones",
    description="Calcula y retorna los días ganados, usados y disponibles del funcionario",
)
async def get_balance(
    db: DbDep,
    employee_id: int = Path(..., gt=0, description="ID del funcionario"),
):
    balance = await crud.get_balance(db, employee_id)
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionario con ID {employee_id} no encontrado",
        )
    return balance


@router.get(
    "/employees/{employee_id}/eligibility",
    response_model=VacationEligibilityResponse,
    summary="Consultar elegibilidad",
    description="Indica si el funcionario ya puede solicitar vacaciones",
)
async def get_eligibility(
    db: DbDep,
    employee_id: int = Path(..., gt=0, description="ID del funcionario"),
):
    eligibility = await crud.get_eligibility(db, employee_id)
    if not eligibility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionario con ID {employee_id} no encontrado",
        )
    return eligibility


@router.post(
    "/requests",
    response_model=VacationRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar vacaciones",
    description="Crea una nueva solicitud de vacaciones en estado pendiente",
)
async def create_request(
    db: DbDep,
    payload: VacationRequestCreate,
):
    request, error = await crud.create_vacation_request(db, payload)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return request


@router.get(
    "/requests/{request_id}",
    response_model=VacationRequestResponse,
    summary="Obtener solicitud",
    description="Devuelve el detalle de una solicitud específica",
)
async def get_request(
    db: DbDep,
    request_id: int = Path(..., gt=0, description="ID de la solicitud"),
):
    request = await crud.get_vacation_request(db, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitud con ID {request_id} no encontrada",
        )
    return request


@router.get(
    "/requests",
    response_model=VacationRequestListResponse,
    summary="Listar solicitudes",
    description="Lista solicitudes con filtros opcionales por funcionario y estado",
)
async def list_requests(
    db: DbDep,
    employee_id: int | None = Query(None, gt=0, description="Filtrar por funcionario"),
    status_filter: VacationRequestStatus | None = Query(None, alias="status", description="Filtrar por estado"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
):
    items = await crud.list_vacation_requests(db, employee_id=employee_id, status=status_filter, skip=skip, limit=limit)
    total = await crud.count_vacation_requests(db, employee_id=employee_id, status=status_filter)
    return VacationRequestListResponse(items=items, total=total)


@router.post(
    "/requests/{request_id}/approve",
    response_model=VacationRequestResponse,
    summary="Aprobar solicitud",
    description="Marca una solicitud como aprobada y actualiza el balance",
)
async def approve_request(
    db: DbDep,
    request_id: int = Path(..., gt=0, description="ID de la solicitud"),
    review: VacationRequestReview | None = None,
):
    review = review or VacationRequestReview()
    request, error = await crud.approve_request(db, request_id, review)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return request


@router.post(
    "/requests/{request_id}/reject",
    response_model=VacationRequestResponse,
    summary="Rechazar solicitud",
    description="Marca una solicitud como rechazada",
)
async def reject_request(
    db: DbDep,
    request_id: int = Path(..., gt=0, description="ID de la solicitud"),
    review: VacationRequestReview | None = None,
):
    review = review or VacationRequestReview()
    request, error = await crud.reject_request(db, request_id, review)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return request


@router.get(
    "/employees/{employee_id}/requests",
    response_model=VacationRequestListResponse,
    summary="Solicitudes por funcionario",
    description="Lista todas las solicitudes de vacaciones de un funcionario",
)
async def list_requests_by_employee(
    db: DbDep,
    employee_id: int = Path(..., gt=0, description="ID del funcionario"),
    status_filter: VacationRequestStatus | None = Query(None, alias="status", description="Filtrar por estado"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
):
    employee_balance = await crud.get_balance(db, employee_id)
    if not employee_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionario con ID {employee_id} no encontrado",
        )
    items = await crud.list_vacation_requests(db, employee_id=employee_id, status=status_filter, skip=skip, limit=limit)
    total = await crud.count_vacation_requests(db, employee_id=employee_id, status=status_filter)
    return VacationRequestListResponse(items=items, total=total)


@router.get(
    "/health-check",
    response_model=MessageResponse,
    summary="Health auxiliar",
    description="Endpoint auxiliar de comprobación del router",
)
async def router_health_check():
    return MessageResponse(message="Vacations router activo")
