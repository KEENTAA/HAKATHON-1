"""Operaciones CRUD para la base de datos."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import joinedload

from app.models import Employee, Department, Position, EmployeeStatus
from app.schemas import (
    EmployeeCreate, EmployeeUpdate,
    DepartmentCreate, DepartmentUpdate,
    PositionCreate, PositionUpdate
)


# ============== DEPARTAMENTOS ==============

async def get_departments(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Obtener lista de departamentos con paginación."""
    result = await db.execute(
        select(Department).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_department(db: AsyncSession, department_id: int):
    """Obtener departamento por ID."""
    result = await db.execute(
        select(Department).where(Department.id == department_id)
    )
    return result.scalar_one_or_none()


async def get_department_by_name(db: AsyncSession, name: str):
    """Obtener departamento por nombre."""
    result = await db.execute(
        select(Department).where(Department.name == name)
    )
    return result.scalar_one_or_none()


async def create_department(db: AsyncSession, department: DepartmentCreate):
    """Crear nuevo departamento."""
    db_department = Department(**department.model_dump())
    db.add(db_department)
    await db.commit()
    await db.refresh(db_department)
    return db_department


async def update_department(db: AsyncSession, department_id: int, department: DepartmentUpdate):
    """Actualizar departamento existente."""
    db_department = await get_department(db, department_id)
    if not db_department:
        return None
    
    update_data = department.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_department, field, value)
    
    await db.commit()
    await db.refresh(db_department)
    return db_department


async def delete_department(db: AsyncSession, department_id: int):
    """Eliminar departamento."""
    db_department = await get_department(db, department_id)
    if not db_department:
        return None
    
    await db.delete(db_department)
    await db.commit()
    return db_department


# ============== POSICIONES ==============

async def get_positions(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Obtener lista de posiciones con paginación."""
    result = await db.execute(
        select(Position).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_position(db: AsyncSession, position_id: int):
    """Obtener posición por ID."""
    result = await db.execute(
        select(Position).where(Position.id == position_id)
    )
    return result.scalar_one_or_none()


async def get_position_by_name(db: AsyncSession, name: str):
    """Obtener posición por nombre."""
    result = await db.execute(
        select(Position).where(Position.name == name)
    )
    return result.scalar_one_or_none()


async def create_position(db: AsyncSession, position: PositionCreate):
    """Crear nueva posición."""
    db_position = Position(**position.model_dump())
    db.add(db_position)
    await db.commit()
    await db.refresh(db_position)
    return db_position


async def update_position(db: AsyncSession, position_id: int, position: PositionUpdate):
    """Actualizar posición existente."""
    db_position = await get_position(db, position_id)
    if not db_position:
        return None
    
    update_data = position.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_position, field, value)
    
    await db.commit()
    await db.refresh(db_position)
    return db_position


async def delete_position(db: AsyncSession, position_id: int):
    """Eliminar posición."""
    db_position = await get_position(db, position_id)
    if not db_position:
        return None
    
    await db.delete(db_position)
    await db.commit()
    return db_position


# ============== EMPLEADOS ==============

async def get_employees(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    department_id: int = None
):
    """Obtener lista de empleados con filtros y paginación."""
    query = select(Employee).options(
        joinedload(Employee.department),
        joinedload(Employee.position)
    )
    
    filters = []
    if status:
        filters.append(Employee.status == status)
    if department_id:
        filters.append(Employee.department_id == department_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.unique().scalars().all()


async def get_employee(db: AsyncSession, employee_id: int):
    """Obtener empleado por ID con relaciones."""
    result = await db.execute(
        select(Employee)
        .where(Employee.id == employee_id)
        .options(
            joinedload(Employee.department),
            joinedload(Employee.position)
        )
    )
    return result.unique().scalar_one_or_none()


async def get_employee_by_ci(db: AsyncSession, ci: str):
    """Obtener empleado por cédula de identidad."""
    result = await db.execute(
        select(Employee)
        .where(Employee.ci == ci.upper())
        .options(
            joinedload(Employee.department),
            joinedload(Employee.position)
        )
    )
    return result.unique().scalar_one_or_none()


async def get_employee_by_email(db: AsyncSession, email: str):
    """Obtener empleado por email."""
    result = await db.execute(
        select(Employee)
        .where(Employee.email == email.lower())
        .options(
            joinedload(Employee.department),
            joinedload(Employee.position)
        )
    )
    return result.unique().scalar_one_or_none()


async def create_employee(db: AsyncSession, employee: EmployeeCreate):
    """Crear nuevo empleado."""
    db_employee = Employee(
        **employee.model_dump(),
        status=EmployeeStatus.ACTIVO
    )
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    
    # Cargar relaciones
    await db.refresh(db_employee)
    return db_employee


async def update_employee(db: AsyncSession, employee_id: int, employee: EmployeeUpdate):
    """Actualizar empleado existente."""
    db_employee = await get_employee(db, employee_id)
    if not db_employee:
        return None
    
    update_data = employee.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "status":
                setattr(db_employee, field, EmployeeStatus(value))
            else:
                setattr(db_employee, field, value)
    
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def delete_employee(db: AsyncSession, employee_id: int):
    """Eliminar empleado de forma física."""
    db_employee = await get_employee(db, employee_id)
    if not db_employee:
        return None
    
    await db.delete(db_employee)
    await db.commit()
    return db_employee


async def deactivate_employee(db: AsyncSession, employee_id: int, reason: str = None):
    """Dar de baja a un empleado (cambiar estado a Baja)."""
    db_employee = await get_employee(db, employee_id)
    if not db_employee:
        return None
    
    db_employee.status = EmployeeStatus.BAJA
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def get_employees_by_department(db: AsyncSession, department_id: int):
    """Obtener todos los empleados de un departamento."""
    result = await db.execute(
        select(Employee)
        .where(Employee.department_id == department_id)
        .options(
            joinedload(Employee.department),
            joinedload(Employee.position)
        )
    )
    return result.unique().scalars().all()


async def get_employees_count(db: AsyncSession, status: str = None, department_id: int = None):
    """Obtener cantidad total de empleados."""
    query = select(Employee)
    
    filters = []
    if status:
        filters.append(Employee.status == status)
    if department_id:
        filters.append(Employee.department_id == department_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    return len(result.scalars().all())
