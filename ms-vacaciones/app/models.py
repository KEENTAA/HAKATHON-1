"""Modelos SQLAlchemy para el microservicio de Vacaciones."""

import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class EmployeeReference(Base):
    __tablename__ = "employees"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)


class VacationRequestStatus(str, enum.Enum):
    PENDIENTE = "Pendiente"
    APROBADO = "Aprobado"
    RECHAZADO = "Rechazado"


class VacationBalance(Base):
    __tablename__ = "vacation_balances"

    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True, index=True)
    total_days_earned = Column(Integer, nullable=False, default=0)
    days_used = Column(Integer, nullable=False, default=0)
    last_update = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<VacationBalance(employee_id={self.employee_id}, total_days_earned={self.total_days_earned}, "
            f"days_used={self.days_used})>"
        )


class VacationRequest(Base):
    __tablename__ = "vacation_requests"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_vacation_requests_date_range"),
        CheckConstraint("days_requested > 0", name="ck_vacation_requests_days_requested_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Integer, nullable=False)
    status = Column(
        Enum(VacationRequestStatus),
        nullable=False,
        default=VacationRequestStatus.PENDIENTE,
        index=True,
    )
    notes = Column(Text, nullable=True)
    requested_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<VacationRequest(id={self.id}, employee_id={self.employee_id}, "
            f"days_requested={self.days_requested}, status={self.status})>"
        )
