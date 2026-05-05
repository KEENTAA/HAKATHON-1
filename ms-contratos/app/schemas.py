"""
Schemas - Esquemas Pydantic para validación y respuesta de requests
Define DTOs (Data Transfer Objects) para request/response
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models import ContractStatus


# ==================== CONTRACT TYPE SCHEMAS ====================
class ContractTypeBase(BaseModel):
    """Base schema para ContractType"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del tipo de contrato")


class ContractTypeCreate(ContractTypeBase):
    """Schema para crear ContractType"""
    pass


class ContractTypeResponse(ContractTypeBase):
    """Schema para responder con ContractType"""
    id: int

    class Config:
        from_attributes = True


# ==================== CONTRACT SCHEMAS ====================
class ContractBase(BaseModel):
    """Base schema para Contract"""
    employee_id: int = Field(..., gt=0, description="ID del empleado")
    contract_type_id: int = Field(..., gt=0, description="ID del tipo de contrato")
    start_date: date = Field(..., description="Fecha de inicio del contrato")
    end_date: Optional[date] = Field(None, description="Fecha de fin (null si indefinido)")
    salary: float = Field(..., gt=0, description="Salario mensual")
    trial_period_days: int = Field(default=90, ge=0, le=180, description="Días de período de prueba")


class ContractCreate(ContractBase):
    """Schema para crear Contract"""
    pass


class ContractUpdateStatus(BaseModel):
    """Schema para actualizar estado de Contract"""
    status: ContractStatus = Field(..., description="Nuevo estado del contrato")


class ContractResponse(ContractBase):
    """Schema para responder con Contract completo"""
    id: int
    status: ContractStatus
    document_text: str
    created_at: datetime
    contract_type: ContractTypeResponse

    class Config:
        from_attributes = True


class ContractListResponse(BaseModel):
    """Schema para responder lista de contratos"""
    id: int
    employee_id: int
    contract_type: ContractTypeResponse
    start_date: date
    end_date: Optional[date]
    salary: float
    status: ContractStatus
    created_at: datetime

    class Config:
        from_attributes = True
