"""Lógica de negocio y acceso a datos para Vacaciones."""

from datetime import date, datetime

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import VacationBalance, VacationRequest, VacationRequestStatus
from app.schemas import (
    EmployeeSummary,
    VacationBalanceResponse,
    VacationEligibilityResponse,
    VacationRequestCreate,
    VacationRequestReview,
)

VACATION_DAYS_PER_YEAR = 15


def is_employee_active(employee_status: str) -> bool:
    return str(employee_status).upper() == "ACTIVO"


async def get_employee_summary(db: AsyncSession, employee_id: int):
    result = await db.execute(
        text(
            """
            SELECT id, first_name, last_name, hire_date, status, current_salary
            FROM employees
            WHERE id = :employee_id
            """
        ),
        {"employee_id": employee_id},
    )
    row = result.mappings().first()
    return row


async def count_days_used(db: AsyncSession, employee_id: int) -> int:
    result = await db.execute(
        select(func.coalesce(func.sum(VacationRequest.days_requested), 0)).where(
            VacationRequest.employee_id == employee_id,
            VacationRequest.status == VacationRequestStatus.APROBADO,
        )
    )
    return int(result.scalar_one())


def calculate_years_completed(hire_date: date, today: date | None = None) -> int:
    today = today or date.today()
    years = today.year - hire_date.year
    if (today.month, today.day) < (hire_date.month, hire_date.day):
        years -= 1
    return max(years, 0)


def calculate_days_earned(hire_date: date, today: date | None = None) -> int:
    return calculate_years_completed(hire_date, today) * VACATION_DAYS_PER_YEAR


def calculate_requested_days(start_date: date, end_date: date) -> int:
    return (end_date - start_date).days + 1


async def sync_balance(db: AsyncSession, employee_id: int):
    employee = await get_employee_summary(db, employee_id)
    if not employee:
        return None, None, None

    total_days_earned = calculate_days_earned(employee["hire_date"])
    days_used = await count_days_used(db, employee_id)

    result = await db.execute(
        select(VacationBalance).where(VacationBalance.employee_id == employee_id)
    )
    balance = result.scalar_one_or_none()

    if balance is None:
        balance = VacationBalance(
            employee_id=employee_id,
            total_days_earned=total_days_earned,
            days_used=days_used,
            last_update=datetime.utcnow(),
        )
        db.add(balance)
    else:
        balance.total_days_earned = total_days_earned
        balance.days_used = days_used
        balance.last_update = datetime.utcnow()

    await db.commit()
    await db.refresh(balance)
    return employee, balance, calculate_years_completed(employee["hire_date"])


async def get_balance(db: AsyncSession, employee_id: int):
    employee, balance, years_completed = await sync_balance(db, employee_id)
    if not employee or not balance:
        return None

    employee_summary = EmployeeSummary.model_validate(dict(employee))
    total_days_earned = balance.total_days_earned
    days_used = balance.days_used
    days_available = max(total_days_earned - days_used, 0)
    eligible = years_completed >= 1 and is_employee_active(employee["status"])

    return VacationBalanceResponse(
        employee_id=employee_id,
        total_days_earned=total_days_earned,
        days_used=days_used,
        employee=employee_summary,
        years_completed=years_completed,
        days_available=days_available,
        eligible=eligible,
        last_update=balance.last_update,
    )


async def get_eligibility(db: AsyncSession, employee_id: int):
    employee, balance, years_completed = await sync_balance(db, employee_id)
    if not employee or not balance:
        return None

    employee_summary = EmployeeSummary.model_validate(dict(employee))
    days_available = max(balance.total_days_earned - balance.days_used, 0)
    eligible = years_completed >= 1 and is_employee_active(employee["status"])
    if not is_employee_active(employee["status"]):
        message = f"El funcionario no está activo actualmente ({employee['status']})."
    elif years_completed < 1:
        message = "El funcionario aún no cumple un año de antigüedad."
    else:
        message = "El funcionario es elegible para solicitar vacaciones."

    return VacationEligibilityResponse(
        employee=employee_summary,
        years_completed=years_completed,
        total_days_earned=balance.total_days_earned,
        days_used=balance.days_used,
        days_available=days_available,
        eligible=eligible,
        message=message,
    )


async def create_vacation_request(db: AsyncSession, payload: VacationRequestCreate):
    employee = await get_employee_summary(db, payload.employee_id)
    if not employee:
        return None, "Funcionario no encontrado"

    if not is_employee_active(employee["status"]):
        return None, f"El funcionario no está activo actualmente ({employee['status']})."

    if payload.end_date < payload.start_date:
        return None, "La fecha de fin no puede ser menor que la fecha de inicio"

    days_requested = calculate_requested_days(payload.start_date, payload.end_date)
    if days_requested <= 0:
        return None, "El rango de fechas debe cubrir al menos un día"

    balance_info = await get_balance(db, payload.employee_id)
    if not balance_info:
        return None, "No fue posible calcular el balance de vacaciones"

    if balance_info.years_completed < 1:
        return None, "El funcionario aún no cumple un año de antigüedad"

    if days_requested > balance_info.days_available:
        return None, "La solicitud excede los días disponibles"

    db_request = VacationRequest(
        employee_id=payload.employee_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days_requested=days_requested,
        status=VacationRequestStatus.PENDIENTE,
        notes=payload.notes,
        requested_at=datetime.utcnow(),
        reviewed_at=None,
    )
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)
    return db_request, None


async def get_vacation_request(db: AsyncSession, request_id: int):
    result = await db.execute(
        select(VacationRequest).where(VacationRequest.id == request_id)
    )
    return result.scalar_one_or_none()


async def list_vacation_requests(
    db: AsyncSession,
    employee_id: int | None = None,
    status: VacationRequestStatus | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(VacationRequest)
    if employee_id:
        query = query.where(VacationRequest.employee_id == employee_id)
    if status:
        query = query.where(VacationRequest.status == status)
    query = query.order_by(VacationRequest.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def count_vacation_requests(
    db: AsyncSession,
    employee_id: int | None = None,
    status: VacationRequestStatus | None = None,
):
    query = select(func.count(VacationRequest.id))
    if employee_id:
        query = query.where(VacationRequest.employee_id == employee_id)
    if status:
        query = query.where(VacationRequest.status == status)
    result = await db.execute(query)
    return int(result.scalar_one())


async def approve_request(db: AsyncSession, request_id: int, review: VacationRequestReview):
    request = await get_vacation_request(db, request_id)
    if not request:
        return None, "Solicitud no encontrada"

    if request.status != VacationRequestStatus.PENDIENTE:
        return None, "Solo se pueden aprobar solicitudes pendientes"

    request.status = VacationRequestStatus.APROBADO
    request.reviewed_at = datetime.utcnow()
    if review.notes:
        request.notes = review.notes
    await db.commit()
    await db.refresh(request)
    await sync_balance(db, request.employee_id)
    return request, None


async def reject_request(db: AsyncSession, request_id: int, review: VacationRequestReview):
    request = await get_vacation_request(db, request_id)
    if not request:
        return None, "Solicitud no encontrada"

    if request.status != VacationRequestStatus.PENDIENTE:
        return None, "Solo se pueden rechazar solicitudes pendientes"

    request.status = VacationRequestStatus.RECHAZADO
    request.reviewed_at = datetime.utcnow()
    if review.notes:
        request.notes = review.notes
    await db.commit()
    await db.refresh(request)
    await sync_balance(db, request.employee_id)
    return request, None
