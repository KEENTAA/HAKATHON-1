from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.vacation_request import VacationRequest, RequestStatus
from app.models.employee import Employee
from app.models.vacation_balance import VacationBalance
from app.schemas.vacation import VacationRequestCreate
from app.utils.vacation_logic import calculate_business_days, calculate_earned_days

def get_vacation_balance(db: Session, employee_id: int):
    """Calcula y devuelve el balance actual de vacaciones de un empleado."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError("Empleado no encontrado en el sistema.")

    # 1. Calcular días ganados según antigüedad (Lógica de negocio)
    earned = calculate_earned_days(employee.hire_date)

    # 2. Sumar los días que ya ha usado (Solo solicitudes APROBADAS)
    used_query = db.query(func.sum(VacationRequest.total_days)).filter(
        VacationRequest.employee_id == employee_id,
        VacationRequest.status == RequestStatus.APPROVED
    ).scalar()
    
    used = used_query if used_query else 0
    
    # 3. Calcular disponibles
    available = earned - used

    # (Opcional) Actualizar la tabla de balances para consultas rápidas del Frontend
    balance_record = db.query(VacationBalance).filter(VacationBalance.employee_id == employee_id).first()
    if not balance_record:
        balance_record = VacationBalance(employee_id=employee_id)
        db.add(balance_record)
        
    balance_record.days_earned = earned
    balance_record.days_used = used
    balance_record.days_available = available
    db.commit()

    return {
        "employee_id": employee_id,
        "days_earned": earned,
        "days_used": used,
        "days_expired": 0, # Para el MVP lo mantenemos simple
        "days_available": available
    }

def create_vacation_request(db: Session, request_in: VacationRequestCreate):
    """Crea una nueva solicitud en estado PENDIENTE verificando reglas."""
    # 1. Verificar balance actual
    balance = get_vacation_balance(db, request_in.employee_id)
    
    if balance["days_earned"] == 0:
        raise ValueError("El funcionario no está ratificado. Requiere 1 año de antigüedad.")

    # 2. Calcular días hábiles solicitados
    requested_days = calculate_business_days(request_in.start_date, request_in.end_date)
    
    if requested_days <= 0:
        raise ValueError("Rango de fechas inválido o solo incluye días no hábiles.")
        
    if requested_days > balance["days_available"]:
        raise ValueError(f"Días insuficientes. Solicita {requested_days} pero solo tiene {balance['days_available']} disponibles.")

    # 3. Guardar en base de datos
    db_request = VacationRequest(
        employee_id=request_in.employee_id,
        start_date=request_in.start_date,
        end_date=request_in.end_date,
        total_days=requested_days,
        status=RequestStatus.PENDING,
        description=request_in.description
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    return db_request

def update_request_status(db: Session, request_id: int, new_status: str):
    """Permite a un jefe aprobar o rechazar una solicitud."""
    db_request = db.query(VacationRequest).filter(VacationRequest.id == request_id).first()
    if not db_request:
        raise ValueError("Solicitud no encontrada.")
        
    if db_request.status != RequestStatus.PENDING:
        raise ValueError(f"La solicitud ya fue procesada y está en estado: {db_request.status.value}")

    # Mapear el string al Enum de la BD
    status_enum = RequestStatus(new_status.upper())
    db_request.status = status_enum
    
    db.commit()
    db.refresh(db_request)
    
    # Al aprobar, recalculamos el balance para que la tabla quede actualizada
    if status_enum == RequestStatus.APPROVED:
        get_vacation_balance(db, db_request.employee_id)
        
    return db_request