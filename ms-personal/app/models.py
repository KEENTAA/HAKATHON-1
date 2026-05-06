"""Modelos SQLAlchemy para el módulo de Personal."""

from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class EmployeeStatus(str, enum.Enum):
    """Estados posibles de un empleado."""
    ACTIVO = "Activo"
    BAJA = "Baja"
    SUSPENDIDO = "Suspendido"


class Department(Base):
    """Tabla de departamentos/áreas de la empresa."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    employees = relationship("Employee", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"


class Position(Base):
    """Tabla de cargos/posiciones disponibles."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    base_salary = Column(Float, nullable=False)  # Sueldo base sugerido
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    employees = relationship("Employee", back_populates="position")

    def __repr__(self):
        return f"<Position(id={self.id}, name='{self.name}', base_salary={self.base_salary})>"


class Employee(Base):
    """Tabla de funcionarios/empleados - Core del sistema."""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    ci = Column(String(50), unique=True, nullable=False, index=True)  # Documento de Identidad
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    hire_date = Column(Date, nullable=False)  # Fecha de ingreso
    current_salary = Column(Float, nullable=False)  # Salario real pactado
    status = Column(
        Enum(EmployeeStatus),
        default=EmployeeStatus.ACTIVO,
        nullable=False,
        index=True
    )
    
    # Claves foráneas
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False, index=True)
    
    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")

    def __repr__(self):
        return f"<Employee(id={self.id}, ci='{self.ci}', name='{self.first_name} {self.last_name}', status={self.status})>"
