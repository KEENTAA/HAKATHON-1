"""Endpoints del microservicio de Boletas."""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database import get_db
from app.schemas import (
    MessageResponse,
    PaySlipGenerateRequest,
    PaySlipGenerateResponse,
    PaySlipListResponse,
    PaySlipResponse,
    PaymentConceptResponse,
)
from app import crud

router = APIRouter(prefix="/boletas", tags=["Boletas"])
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/generate",
    response_model=PaySlipGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar boleta",
    description="Genera y persiste una boleta basada en el salario del funcionario y conceptos adicionales",
)
async def generate_pay_slip(
    db: DbDep,
    payload: PaySlipGenerateRequest,
):
    pay_slip, employee, error = await crud.generate_pay_slip(db, payload)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    stored_pay_slip = await crud.get_pay_slip(db, pay_slip.id)
    if not stored_pay_slip:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo recuperar la boleta generada",
        )

    return PaySlipGenerateResponse(
        payslip=PaySlipResponse.model_validate(stored_pay_slip),
        employee=employee,
        document=stored_pay_slip.generated_document,
    )


@router.get(
    "/concepts",
    response_model=list[PaymentConceptResponse],
    summary="Listar conceptos de pago",
    description="Lista los conceptos de pago base disponibles",
)
async def list_concepts(db: DbDep):
    return await crud.list_payment_concepts(db)


@router.get(
    "/{empleado_id}",
    response_model=PaySlipListResponse,
    summary="Boletas por funcionario",
    description="Lista las boletas registradas para un funcionario",
)
async def get_pay_slips_by_employee(
    db: DbDep,
    empleado_id: int = Path(..., gt=0, description="ID del funcionario"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
):
    employee_row = await crud.get_employee_summary(db, empleado_id)
    if not employee_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionario con ID {empleado_id} no encontrado",
        )

    items = await crud.list_pay_slips_by_employee(db, empleado_id, skip=skip, limit=limit)
    total = await crud.count_pay_slips_by_employee(db, empleado_id)
    return PaySlipListResponse(items=items, total=total)


@router.get(
    "/{empleado_id}/slips",
    response_model=PaySlipListResponse,
    summary="Alias de boletas por funcionario",
    description="Mismo resultado que GET /boletas/{empleado_id}",
)
async def get_pay_slips_by_employee_alias(
    db: DbDep,
    empleado_id: int = Path(..., gt=0, description="ID del funcionario"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
):
    employee_row = await crud.get_employee_summary(db, empleado_id)
    if not employee_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionario con ID {empleado_id} no encontrado",
        )

    items = await crud.list_pay_slips_by_employee(db, empleado_id, skip=skip, limit=limit)
    total = await crud.count_pay_slips_by_employee(db, empleado_id)
    return PaySlipListResponse(items=items, total=total)


@router.get(
    "/slips/{slip_id}",
    response_model=PaySlipResponse,
    summary="Obtener boleta",
    description="Devuelve una boleta específica por ID",
)
async def get_pay_slip(
    db: DbDep,
    slip_id: int = Path(..., gt=0, description="ID de la boleta"),
):
    pay_slip = await crud.get_pay_slip(db, slip_id)
    if not pay_slip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Boleta con ID {slip_id} no encontrada",
        )
    return pay_slip


@router.get(
    "/health-check",
    response_model=MessageResponse,
    summary="Health auxiliar",
    description="Endpoint auxiliar de comprobación del router",
)
async def router_health_check():
    return MessageResponse(message="Boletas router activo")
