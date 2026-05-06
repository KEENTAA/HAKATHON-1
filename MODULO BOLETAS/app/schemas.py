from datetime import date
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    ci: str = Field(min_length=3, max_length=20)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    hire_date: Optional[date] = None
    status: Literal["Activo", "Baja", "Suspendido"] = "Activo"


class PaymentConceptCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    type: Literal["Ingreso", "Egreso"]


class PaySlipDetailCreate(BaseModel):
    concept_id: int = Field(gt=0)
    amount: Decimal = Field(ge=0)


class PaySlipCreate(BaseModel):
    employee_id: int = Field(gt=0)
    period_month: int = Field(ge=1, le=12)
    period_year: int = Field(ge=2000)
    payment_date: Optional[date] = None
    details: List[PaySlipDetailCreate] = Field(min_length=1)

