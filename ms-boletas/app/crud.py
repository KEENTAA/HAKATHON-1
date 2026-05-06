"""Lógica de negocio y acceso a datos para Boletas."""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import PaySlip, PaySlipDetail, PaySlipStatus, PaymentConcept, PaymentConceptType
from app.schemas import (
    EmployeeSummary,
    PaySlipDetailCreate,
    PaySlipGenerateRequest,
    PaySlipGenerateResponse,
    PaymentConceptCreate,
    PaymentConceptResponse,
)

DEFAULT_PAYMENT_CONCEPTS = [
    ("Sueldo Básico", PaymentConceptType.INGRESO),
    ("Bono Productividad", PaymentConceptType.INGRESO),
    ("Bono Transporte", PaymentConceptType.INGRESO),
    ("Descuento Salud", PaymentConceptType.EGRESO),
    ("AFP", PaymentConceptType.EGRESO),
]

SALARY_CONCEPT_NAME = "Sueldo Básico"


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
    return result.mappings().first()


async def get_payment_concept(db: AsyncSession, concept_id: int):
    result = await db.execute(select(PaymentConcept).where(PaymentConcept.id == concept_id))
    return result.scalar_one_or_none()


async def get_payment_concept_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(PaymentConcept).where(PaymentConcept.name == name))
    return result.scalar_one_or_none()


async def list_payment_concepts(db: AsyncSession):
    result = await db.execute(select(PaymentConcept).order_by(PaymentConcept.id.asc()))
    return result.scalars().all()


async def seed_payment_concepts(db: AsyncSession):
    result = await db.execute(select(PaymentConcept.name))
    existing = {row[0] for row in result.all()}
    inserted = False

    for name, concept_type in DEFAULT_PAYMENT_CONCEPTS:
        if name not in existing:
            db.add(PaymentConcept(name=name, type=concept_type))
            inserted = True

    if inserted:
        await db.commit()


async def get_pay_slip(db: AsyncSession, pay_slip_id: int):
    result = await db.execute(
        select(PaySlip)
        .options(
            selectinload(PaySlip.details).selectinload(PaySlipDetail.concept)
        )
        .where(PaySlip.id == pay_slip_id)
    )
    return result.scalar_one_or_none()


async def list_pay_slips_by_employee(db: AsyncSession, employee_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(PaySlip)
        .options(
            selectinload(PaySlip.details).selectinload(PaySlipDetail.concept)
        )
        .where(PaySlip.employee_id == employee_id)
        .order_by(PaySlip.period_year.desc(), PaySlip.period_month.desc(), PaySlip.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def count_pay_slips_by_employee(db: AsyncSession, employee_id: int):
    result = await db.execute(
        select(func.count(PaySlip.id)).where(PaySlip.employee_id == employee_id)
    )
    return int(result.scalar_one())


async def build_document(employee: EmployeeSummary, pay_slip: PaySlip, details: list[tuple[PaymentConceptResponse, Decimal]]) -> str:
    lines = [
        "BOLETA DE PAGO",
        f"Funcionario: {employee.first_name} {employee.last_name} (ID {employee.id})",
        f"Periodo: {pay_slip.period_month:02d}/{pay_slip.period_year}",
        f"Fecha de pago: {pay_slip.payment_date.isoformat()}",
        "Detalle:",
    ]
    for concept, amount in details:
        lines.append(f"- {concept.name}: {amount}")
    lines.append(f"Total neto: {pay_slip.total_net}")
    lines.append(f"Estado: {pay_slip.status.value}")
    return "\n".join(lines) + "\n"


async def generate_pay_slip(db: AsyncSession, payload: PaySlipGenerateRequest):
    employee_row = await get_employee_summary(db, payload.employee_id)
    if not employee_row:
        return None, None, "Funcionario no encontrado"

    employee = EmployeeSummary.model_validate(dict(employee_row))
    if not is_employee_active(employee.status):
        return None, None, f"El funcionario no está activo actualmente ({employee.status})."

    if not payload.details and not payload.include_salary_concept:
        return None, None, "Debe incluir al menos un concepto o activar el concepto salarial"

    concept_map: list[tuple[PaymentConceptResponse, Decimal]] = []
    total_net = Decimal("0.00")

    if payload.include_salary_concept:
        salary_concept = await get_payment_concept_by_name(db, SALARY_CONCEPT_NAME)
        if not salary_concept:
            return None, None, f"No existe el concepto base '{SALARY_CONCEPT_NAME}'"
        salary_value = Decimal(str(employee.current_salary)).quantize(Decimal("0.01"))
        concept_map.append((PaymentConceptResponse.model_validate(salary_concept), salary_value))
        total_net += salary_value

    for detail in payload.details:
        concept = await get_payment_concept(db, detail.concept_id)
        if not concept:
            return None, None, f"Concepto con ID {detail.concept_id} no encontrado"
        amount = Decimal(str(detail.amount)).quantize(Decimal("0.01"))
        concept_map.append((PaymentConceptResponse.model_validate(concept), amount))
        if concept.type == PaymentConceptType.INGRESO:
            total_net += amount
        else:
            total_net -= amount

    pay_slip = PaySlip(
        employee_id=payload.employee_id,
        period_month=payload.period_month,
        period_year=payload.period_year,
        payment_date=payload.payment_date,
        total_net=total_net,
        status=PaySlipStatus.GENERADA,
        generated_document="",
    )
    db.add(pay_slip)
    await db.flush()

    for concept, amount in concept_map:
        db.add(
            PaySlipDetail(
                pay_slip_id=pay_slip.id,
                concept_id=concept.id,
                amount=amount,
            )
        )

    pay_slip.generated_document = await build_document(employee, pay_slip, concept_map)
    await db.commit()
    await db.refresh(pay_slip)
    return pay_slip, employee, None
