"""Modelos SQLAlchemy para el microservicio de Contratos."""

import enum
from datetime import date

from sqlalchemy import CheckConstraint, Column, Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class EmployeeReference(Base):
    __tablename__ = "employees"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)


class ContractStatus(str, enum.Enum):
    ACTIVO = "Activo"
    VENCIDO = "Vencido"
    REEMPLAZADO = "Reemplazado"


class ContractType(Base):
    __tablename__ = "contract_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)

    contracts = relationship("Contract", back_populates="contract_type")

    def __repr__(self) -> str:
        return f"<ContractType(id={self.id}, name='{self.name}')>"


class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = (
        CheckConstraint("trial_period_days > 0", name="ck_contracts_trial_period_positive"),
        CheckConstraint("salary > 0", name="ck_contracts_salary_positive"),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_contracts_date_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_type_id = Column(Integer, ForeignKey("contract_types.id"), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    salary = Column(Numeric(12, 2), nullable=False)
    trial_period_days = Column(Integer, nullable=False, default=90)
    status = Column(
        Enum(ContractStatus),
        nullable=False,
        default=ContractStatus.ACTIVO,
        index=True,
    )
    generated_document = Column(Text, nullable=False)

    contract_type = relationship("ContractType", back_populates="contracts")

    def __repr__(self) -> str:
        return (
            f"<Contract(id={self.id}, employee_id={self.employee_id}, contract_type_id={self.contract_type_id}, "
            f"salary={self.salary}, status={self.status})>"
        )
