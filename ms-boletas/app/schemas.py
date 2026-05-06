"""Esquemas Pydantic para el microservicio de Boletas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import PaySlipStatus, PaymentConceptType


class EmployeeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    hire_date: date
    status: str
    current_salary: float


class PaymentConceptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: PaymentConceptType


class PaymentConceptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: PaymentConceptType

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre del concepto no puede estar vacío")
        return value


class PaySlipDetailCreate(BaseModel):
    concept_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)


class PaySlipDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pay_slip_id: int
    concept_id: int
    amount: Decimal
    concept: PaymentConceptResponse


class PaySlipGenerateRequest(BaseModel):
    employee_id: int = Field(..., gt=0)
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2000, le=2100)
    payment_date: date
    details: list[PaySlipDetailCreate] = Field(default_factory=list)
    include_salary_concept: bool = True


class PaySlipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    period_month: int
    period_year: int
    payment_date: date
    total_net: Decimal
    status: PaySlipStatus
    generated_document: str
    created_at: datetime
    updated_at: datetime
    details: list[PaySlipDetailResponse]


class PaySlipGenerateResponse(BaseModel):
    payslip: PaySlipResponse
    employee: EmployeeSummary
    document: str


class PaySlipListResponse(BaseModel):
    items: list[PaySlipResponse]
    total: int


class MessageResponse(BaseModel):
    message: str
