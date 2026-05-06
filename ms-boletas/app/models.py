"""Modelos SQLAlchemy para el microservicio de Boletas."""

import enum
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class EmployeeReference(Base):
    __tablename__ = "employees"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)


class PaymentConceptType(str, enum.Enum):
    INGRESO = "Ingreso"
    EGRESO = "Egreso"


class PaySlipStatus(str, enum.Enum):
    GENERADA = "Generada"
    ANULADA = "Anulada"


class PaymentConcept(Base):
    __tablename__ = "payment_concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    type = Column(Enum(PaymentConceptType), nullable=False, index=True)

    details = relationship("PaySlipDetail", back_populates="concept")

    def __repr__(self) -> str:
        return f"<PaymentConcept(id={self.id}, name='{self.name}', type={self.type})>"


class PaySlip(Base):
    __tablename__ = "pay_slips"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    period_month = Column(Integer, nullable=False, index=True)
    period_year = Column(Integer, nullable=False, index=True)
    payment_date = Column(Date, nullable=False)
    total_net = Column(Numeric(12, 2), nullable=False)
    status = Column(Enum(PaySlipStatus), nullable=False, default=PaySlipStatus.GENERADA, index=True)
    generated_document = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    details = relationship("PaySlipDetail", back_populates="pay_slip", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (
            f"<PaySlip(id={self.id}, employee_id={self.employee_id}, "
            f"period={self.period_month}/{self.period_year}, total_net={self.total_net})>"
        )


class PaySlipDetail(Base):
    __tablename__ = "pay_slip_details"

    id = Column(Integer, primary_key=True, index=True)
    pay_slip_id = Column(Integer, ForeignKey("pay_slips.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(Integer, ForeignKey("payment_concepts.id"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)

    pay_slip = relationship("PaySlip", back_populates="details")
    concept = relationship("PaymentConcept", back_populates="details")

    def __repr__(self) -> str:
        return f"<PaySlipDetail(id={self.id}, pay_slip_id={self.pay_slip_id}, concept_id={self.concept_id}, amount={self.amount})>"
