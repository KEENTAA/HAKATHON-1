"""Esquemas Pydantic V2 para validación de datos."""

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field
from datetime import date, datetime
from typing import Optional


# ============== DEPARTAMENTOS ==============

class DepartmentBase(BaseModel):
    """Base para operaciones de departamentos."""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del departamento")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del departamento")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre del departamento no puede estar vacío")
        return v.strip()


class DepartmentCreate(DepartmentBase):
    """Schema para crear departamento."""
    pass


class DepartmentUpdate(BaseModel):
    """Schema para actualizar departamento."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class DepartmentResponse(DepartmentBase):
    """Schema de respuesta para departamento."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID único del departamento")
    created_at: datetime
    updated_at: datetime


# ============== POSICIONES ==============

class PositionBase(BaseModel):
    """Base para operaciones de posiciones."""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del cargo")
    base_salary: float = Field(..., gt=0, description="Salario base sugerido para el cargo")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre del cargo no puede estar vacío")
        return v.strip()


class PositionCreate(PositionBase):
    """Schema para crear posición."""
    pass


class PositionUpdate(BaseModel):
    """Schema para actualizar posición."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    base_salary: Optional[float] = Field(None, gt=0)


class PositionResponse(PositionBase):
    """Schema de respuesta para posición."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID único de la posición")
    created_at: datetime
    updated_at: datetime


# ============== EMPLEADOS ==============

class EmployeeBase(BaseModel):
    """Base para operaciones de empleados."""
    ci: str = Field(..., min_length=5, max_length=50, description="Cédula de identidad (única)")
    first_name: str = Field(..., min_length=1, max_length=100, description="Nombre del empleado")
    last_name: str = Field(..., min_length=1, max_length=100, description="Apellido del empleado")
    email: EmailStr = Field(..., description="Email único del empleado")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    hire_date: date = Field(..., description="Fecha de ingreso (YYYY-MM-DD)")
    current_salary: float = Field(..., gt=0, description="Salario actual pactado")
    department_id: int = Field(..., gt=0, description="ID del departamento")
    position_id: int = Field(..., gt=0, description="ID de la posición")

    @field_validator("ci")
    @classmethod
    def ci_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La cédula de identidad no puede estar vacía")
        return v.strip().upper()

    @field_validator("first_name", "last_name")
    @classmethod
    def names_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class EmployeeCreate(EmployeeBase):
    """Schema para crear empleado."""
    pass


class EmployeeUpdate(BaseModel):
    """Schema para actualizar empleado."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    current_salary: Optional[float] = Field(None, gt=0)
    department_id: Optional[int] = Field(None, gt=0)
    position_id: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, description="Activo, Baja, Suspendido")


class EmployeeResponse(EmployeeBase):
    """Schema de respuesta para empleado."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID único del empleado")
    status: str = Field(..., description="Estado del empleado")
    created_at: datetime
    updated_at: datetime


class EmployeeDetailResponse(EmployeeResponse):
    """Schema de respuesta detallada con relaciones."""
    department: DepartmentResponse = Field(..., description="Información del departamento")
    position: PositionResponse = Field(..., description="Información de la posición")


# ============== RESPUESTAS GENÉRICAS ==============

class ErrorResponse(BaseModel):
    """Schema de respuesta de error."""
    detail: str = Field(..., description="Descripción del error")
    status_code: int = Field(..., description="Código HTTP del error")


class MessageResponse(BaseModel):
    """Schema de respuesta genérica con mensaje."""
    message: str = Field(..., description="Mensaje de respuesta")
