"""Lógica de negocio y acceso a datos para Contratos."""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Contract, ContractStatus, ContractType
from app.schemas import ContractGenerateRequest, ContractGenerateResponse, ContractTypeResponse, EmployeeSummary

DEFAULT_CONTRACT_TYPE = "Indefinido"
DEFAULT_CONTRACT_TYPES = [
    "Indefinido",
    "Consultoría",
    "Plazo Fijo",
]


def build_contract_document(
    employee: EmployeeSummary,
    contract_type: ContractTypeResponse,
    start_date: date,
    salary: Decimal,
    trial_period_days: int,
    end_date: date | None,
) -> str:
    end_date_text = end_date.isoformat() if end_date else "Indefinido"
    return (
        f"CONTRATO DE TRABAJO\n"
        f"Funcionario: {employee.first_name} {employee.last_name} (ID {employee.id})\n"
        f"Fecha de ingreso / inicio: {start_date.isoformat()}\n"
        f"Tipo de contrato: {contract_type.name}\n"
        f"Salario: {salary}\n"
        f"Tiempo de prueba: {trial_period_days} días\n"
        f"Fecha de fin: {end_date_text}\n"
        f"Estado: Activo\n"
    )


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


async def get_contract_type(db: AsyncSession, contract_type_id: int | None):
    if contract_type_id is not None:
        result = await db.execute(
            select(ContractType).where(ContractType.id == contract_type_id)
        )
        return result.scalar_one_or_none()

    result = await db.execute(
        select(ContractType).where(ContractType.name == DEFAULT_CONTRACT_TYPE)
    )
    return result.scalar_one_or_none()


async def list_contract_types(db: AsyncSession):
    result = await db.execute(select(ContractType).order_by(ContractType.id.asc()))
    return result.scalars().all()


async def get_contract(db: AsyncSession, contract_id: int):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    return result.scalar_one_or_none()


async def list_contracts_by_employee(db: AsyncSession, employee_id: int):
    result = await db.execute(
        select(Contract)
        .where(Contract.employee_id == employee_id)
        .order_by(Contract.id.desc())
    )
    return result.scalars().all()


async def count_contracts_by_employee(db: AsyncSession, employee_id: int):
    result = await db.execute(
        select(func.count(Contract.id)).where(Contract.employee_id == employee_id)
    )
    return int(result.scalar_one())


async def generate_contract(db: AsyncSession, payload: ContractGenerateRequest):
    employee_row = await get_employee_summary(db, payload.employee_id)
    if not employee_row:
        return None, None, None, "Funcionario no encontrado"

    employee = EmployeeSummary.model_validate(dict(employee_row))

    contract_type = await get_contract_type(db, payload.contract_type_id)
    if not contract_type:
        return None, None, None, "Tipo de contrato no encontrado"

    if payload.end_date and payload.end_date < payload.start_date:
        return None, None, None, "La fecha de fin no puede ser menor que la fecha de inicio"

    document = build_contract_document(
        employee=employee,
        contract_type=ContractTypeResponse.model_validate(contract_type),
        start_date=payload.start_date,
        salary=payload.salary,
        trial_period_days=payload.trial_period_days,
        end_date=payload.end_date,
    )

    contract = Contract(
        employee_id=payload.employee_id,
        contract_type_id=contract_type.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        salary=payload.salary,
        trial_period_days=payload.trial_period_days,
        status=ContractStatus.ACTIVO,
        generated_document=document,
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)

    return contract, employee, ContractTypeResponse.model_validate(contract_type), document, None


async def seed_contract_types(db: AsyncSession):
    result = await db.execute(select(ContractType.name))
    existing = {row[0] for row in result.all()}
    inserted = False

    for name in DEFAULT_CONTRACT_TYPES:
        if name not in existing:
            db.add(ContractType(name=name))
            inserted = True

    if inserted:
        await db.commit()
