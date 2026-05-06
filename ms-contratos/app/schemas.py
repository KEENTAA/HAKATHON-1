"""Esquemas Pydantic para el microservicio de Contratos."""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import ContractStatus


class EmployeeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    hire_date: date
    status: str
    current_salary: float


class ContractTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ContractGenerateRequest(BaseModel):
    employee_id: int = Field(..., gt=0, description="ID del funcionario")
    contract_type_id: Optional[int] = Field(None, gt=0, description="Tipo de contrato (opcional)")
    start_date: date = Field(..., description="Fecha de inicio del contrato")
    salary: Decimal = Field(..., gt=0, description="Salario del contrato")
    trial_period_days: int = Field(90, gt=0, description="Días de prueba")
    end_date: Optional[date] = Field(None, description="Fecha de fin opcional")

    @field_validator("trial_period_days")
    @classmethod
    def normalize_trial_days(cls, value: int) -> int:
        return int(value)


class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    contract_type_id: int
    start_date: date
    end_date: Optional[date]
    salary: Decimal
    trial_period_days: int
    status: ContractStatus
    generated_document: str


class ContractGenerateResponse(BaseModel):
    contract: ContractResponse
    employee: EmployeeSummary
    contract_type: ContractTypeResponse
    document: str


class ContractListResponse(BaseModel):
    items: list[ContractResponse]
    total: int


class MessageResponse(BaseModel):
    message: str
