from pydantic import BaseModel, validator
from datetime import date
from typing import Optional


class VacationRequestCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    description: Optional[str] = None

    @validator("end_date")
    def check_dates(cls, end_date, values):
        if "start_date" in values and end_date < values["start_date"]:
            raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        return end_date

# Schema para cambiar el estado (Aprobar/Rechazar)
class VacationRequestStatusUpdate(BaseModel):
    status: str
    
    @validator("status")
    def validate_status(cls, value):
        allowed = ["PENDING", "APPROVED", "REJECTED"]
        if value.upper() not in allowed:
            raise ValueError(f"Estado no válido. Debe ser uno de {allowed}")
        return value.upper()

class VacationRequestResponse(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    total_days: int
    status: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


#SCHEMAS PARA BALANCE DE VACACIONES

class VacationBalanceResponse(BaseModel):
    employee_id: int
    days_earned: int
    days_used: int
    days_expired: int
    days_available: int

    class Config:
        from_attributes = True

#SCHEMAS PARA EMPLEADO

class EmployeeBase(BaseModel):
    full_name: str
    hire_date: date

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        from_attributes = True