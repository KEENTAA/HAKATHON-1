"""Esquemas Pydantic para el microservicio de Vacaciones."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import VacationRequestStatus


class EmployeeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    hire_date: date
    status: str
    current_salary: float


class VacationBalanceBase(BaseModel):
    employee_id: int = Field(..., gt=0, description="ID del funcionario")
    total_days_earned: int = Field(..., ge=0, description="Días ganados acumulados")
    days_used: int = Field(..., ge=0, description="Días utilizados")


class VacationBalanceResponse(VacationBalanceBase):
    model_config = ConfigDict(from_attributes=True)

    employee: EmployeeSummary
    years_completed: int
    days_available: int
    eligible: bool
    last_update: datetime


class VacationEligibilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee: EmployeeSummary
    years_completed: int
    total_days_earned: int
    days_used: int
    days_available: int
    eligible: bool
    message: str


class VacationRequestCreate(BaseModel):
    employee_id: int = Field(..., gt=0, description="ID del funcionario")
    start_date: date = Field(..., description="Fecha de inicio de vacaciones")
    end_date: date = Field(..., description="Fecha de fin de vacaciones")
    notes: Optional[str] = Field(None, max_length=1000, description="Observaciones opcionales")

    @field_validator("notes")
    @classmethod
    def strip_notes(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if isinstance(value, str) else value


class VacationRequestReview(BaseModel):
    notes: Optional[str] = Field(None, max_length=1000, description="Motivo u observaciones de la revisión")

    @field_validator("notes")
    @classmethod
    def strip_notes(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if isinstance(value, str) else value


class VacationRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    start_date: date
    end_date: date
    days_requested: int
    status: VacationRequestStatus
    notes: Optional[str]
    requested_at: datetime
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class VacationRequestListResponse(BaseModel):
    items: list[VacationRequestResponse]
    total: int


class MessageResponse(BaseModel):
    message: str
