"""
Models - Modelos ORM de SQLAlchemy para tablas de la BD
Define las tablas: contract_types y contracts
"""

from datetime import datetime, date
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


# ==================== ENUMS ====================
class ContractStatus(str, PyEnum):
    """Estados posibles de un contrato"""
    ACTIVO = "Activo"
    VENCIDO = "Vencido"
    REEMPLAZADO = "Reemplazado"


# ==================== MODELO: ContractType ====================
class ContractType(Base):
    """
    Modelo ORM para tipos de contrato.
    Ejemplos: Indefinido, Plazo Fijo, Consultoría
    """
    __tablename__ = "contract_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    # Relación inversa
    contracts = relationship("Contract", back_populates="contract_type")

    def __repr__(self):
        return f"<ContractType id={self.id} name={self.name}>"


# ==================== MODELO: Contract ====================
class Contract(Base):
    """
    Modelo ORM para contratos de empleados.
    
    Campos:
    - employee_id: ID del empleado (referencia a ms-personal, sin FK real)
    - contract_type_id: Tipo de contrato (FK -> contract_types)
    - start_date: Fecha de inicio
    - end_date: Fecha de fin (nullable si es indefinido)
    - salary: Salario mensual
    - trial_period_days: Días de período de prueba
    - status: Estado del contrato (Enum)
    - document_text: Texto generado del contrato legal
    - created_at: Timestamp de creación
    """
    __tablename__ = "contracts"

    # Campos clave
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False, index=True)  # Sin FK real (microservicio)
    contract_type_id = Column(Integer, ForeignKey("contract_types.id"), nullable=False)
    
    # Fechas
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # Null si es indefinido
    
    # Términos del contrato
    salary = Column(Numeric(10, 2), nullable=False)
    trial_period_days = Column(Integer, default=90)
    
    # Estado y documento
    status = Column(Enum(ContractStatus), default=ContractStatus.ACTIVO, nullable=False)
    document_text = Column(Text, nullable=False)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación con ContractType
    contract_type = relationship("ContractType", back_populates="contracts")

    def __repr__(self):
        return (f"<Contract id={self.id} employee_id={self.employee_id} "
                f"status={self.status} created_at={self.created_at}>")
