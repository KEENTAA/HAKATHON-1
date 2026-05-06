"""
Routes - Endpoints de la API para gestión de contratos
Expone los siguientes endpoints:
- POST /contratos/generate
- GET /contratos/empleado/{employee_id}
- GET /contratos/{id}
- PUT /contratos/{id}/status
- GET /contratos/tipos
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Contract, ContractType, ContractStatus
from app.schemas import (
    ContractCreate,
    ContractResponse,
    ContractListResponse,
    ContractUpdateStatus,
    ContractTypeResponse
)
from app.services.contrato_service import generar_documento_contrato

# Crear router para contratos
router = APIRouter(prefix="/contratos", tags=["Contratos"])


# ==================== ENDPOINT: Generar Contrato ====================
@router.post("/generate", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def generar_contrato(
    contrato_data: ContractCreate,
    db: Session = Depends(get_db)
):
    """
    Genera un nuevo contrato para un empleado.
    
    Acciones:
    1. Valida que el tipo de contrato exista
    2. Genera el documento legal con f-strings
    3. Guarda en la BD
    4. Retorna contrato con documento completo
    
    Args:
        contrato_data: Datos del contrato a crear
        db: Sesión de base de datos
    
    Returns:
        ContractResponse: Contrato creado con document_text
    
    Raises:
        HTTPException 400: Si el contract_type_id no existe
        HTTPException 500: Error al guardar en BD
    """
    try:
        print(f"[Endpoints] Generando contrato para empleado {contrato_data.employee_id}")
        
        # Verificar que el tipo de contrato exista
        contract_type = db.query(ContractType).filter(
            ContractType.id == contrato_data.contract_type_id
        ).first()
        
        if not contract_type:
            print(f"✗ [Endpoints] Tipo de contrato no encontrado: {contrato_data.contract_type_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de contrato con ID {contrato_data.contract_type_id} no existe"
            )
        
        # Generar documento legal
        documento_legal = generar_documento_contrato(
            employee_id=contrato_data.employee_id,
            contract_type=contract_type,
            start_date=contrato_data.start_date,
            end_date=contrato_data.end_date,
            salary=contrato_data.salary,
            trial_period_days=contrato_data.trial_period_days
        )
        
        # Crear objeto Contract
        nuevo_contrato = Contract(
            employee_id=contrato_data.employee_id,
            contract_type_id=contrato_data.contract_type_id,
            start_date=contrato_data.start_date,
            end_date=contrato_data.end_date,
            salary=contrato_data.salary,
            trial_period_days=contrato_data.trial_period_days,
            status=ContractStatus.ACTIVO,
            document_text=documento_legal
        )
        
        # Guardar en BD
        db.add(nuevo_contrato)
        db.commit()
        db.refresh(nuevo_contrato)
        
        print(f"✓ [Endpoints] Contrato generado exitosamente. ID: {nuevo_contrato.id}")
        return nuevo_contrato
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"✗ [Endpoints] Error al generar contrato: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar contrato: {str(e)}"
        )


# ==================== ENDPOINT: Listar Contratos por Empleado ====================
@router.get("/empleado/{employee_id}", response_model=list[ContractListResponse])
async def listar_contratos_empleado(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los contratos de un empleado específico.
    
    Args:
        employee_id: ID del empleado
        db: Sesión de base de datos
    
    Returns:
        Lista de contratos del empleado
    
    Raises:
        HTTPException 404: Si no hay contratos para el empleado
    """
    try:
        if employee_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El employee_id debe ser mayor a 0"
            )
        
        print(f"[Endpoints] Listando contratos del empleado {employee_id}")
        
        contratos = db.query(Contract).filter(
            Contract.employee_id == employee_id
        ).order_by(Contract.created_at.desc()).all()
        
        if not contratos:
            print(f"⚠️ [Endpoints] No se encontraron contratos para empleado {employee_id}")
            return []
        
        print(f"✓ [Endpoints] Se encontraron {len(contratos)} contrato(s) para empleado {employee_id}")
        return contratos
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ [Endpoints] Error al listar contratos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar contratos: {str(e)}"
        )


# ==================== ENDPOINT: Obtener Contrato Específico ====================
@router.get("/{id}", response_model=ContractResponse)
async def obtener_contrato(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles completos de un contrato específico.
    
    Args:
        id: ID del contrato
        db: Sesión de base de datos
    
    Returns:
        ContractResponse: Contrato con documento completo
    
    Raises:
        HTTPException 404: Si el contrato no existe
    """
    try:
        if id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ID debe ser mayor a 0"
            )
        
        print(f"[Endpoints] Obteniendo contrato {id}")
        
        contrato = db.query(Contract).filter(Contract.id == id).first()
        
        if not contrato:
            print(f"✗ [Endpoints] Contrato no encontrado: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contrato con ID {id} no existe"
            )
        
        print(f"✓ [Endpoints] Contrato obtenido: {id}")
        return contrato
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ [Endpoints] Error al obtener contrato: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener contrato: {str(e)}"
        )


# ==================== ENDPOINT: Actualizar Estado ====================
@router.put("/{id}/status", response_model=ContractResponse)
async def actualizar_estado_contrato(
    id: int,
    status_data: ContractUpdateStatus,
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de un contrato existente.
    
    Estados permitidos: "Activo", "Vencido", "Reemplazado"
    
    Args:
        id: ID del contrato
        status_data: Nuevo estado
        db: Sesión de base de datos
    
    Returns:
        ContractResponse: Contrato actualizado
    
    Raises:
        HTTPException 404: Si el contrato no existe
        HTTPException 400: Si el estado es inválido
    """
    try:
        if id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ID debe ser mayor a 0"
            )
        
        print(f"[Endpoints] Actualizando estado del contrato {id} a {status_data.status}")
        
        contrato = db.query(Contract).filter(Contract.id == id).first()
        
        if not contrato:
            print(f"✗ [Endpoints] Contrato no encontrado: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contrato con ID {id} no existe"
            )
        
        # Actualizar estado
        contrato.status = status_data.status
        db.commit()
        db.refresh(contrato)
        
        print(f"✓ [Endpoints] Estado del contrato {id} actualizado a {status_data.status}")
        return contrato
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"✗ [Endpoints] Error al actualizar estado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estado: {str(e)}"
        )


# ==================== ENDPOINT: Listar Tipos de Contrato ====================
@router.get("/tipos", response_model=list[ContractTypeResponse])
async def listar_tipos_contrato(db: Session = Depends(get_db)):
    """
    Obtiene la lista de todos los tipos de contrato disponibles.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Lista de ContractTypeResponse con tipos disponibles
    """
    try:
        print("[Endpoints] Listando tipos de contrato")
        
        tipos = db.query(ContractType).order_by(ContractType.name).all()
        
        print(f"✓ [Endpoints] Se encontraron {len(tipos)} tipo(s) de contrato")
        return tipos
        
    except Exception as e:
        print(f"✗ [Endpoints] Error al listar tipos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar tipos de contrato: {str(e)}"
        )
