from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.crud import crud_vacation
from app.schemas.vacation import (
    VacationRequestCreate, 
    VacationRequestResponse, 
    VacationBalanceResponse,
    VacationRequestStatusUpdate
)

router = APIRouter(prefix="/vacations", tags=["Vacations"])

@router.get("/balance/{employee_id}", response_model=VacationBalanceResponse)
def read_vacation_balance(employee_id: int, db: Session = Depends(get_db)):
    """
    Devuelve el desglose completo de días: ganados, usados y disponibles.
    """
    try:
        balance = crud_vacation.get_vacation_balance(db, employee_id=employee_id)
        return balance
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/request", response_model=VacationRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(request_in: VacationRequestCreate, db: Session = Depends(get_db)):
    """
    Registra una solicitud. 
    Bloquea automáticamente si:
    - No tiene 1 año de antigüedad.
    - No tiene días suficientes.
    - El rango de fechas es inválido.
    """
    try:
        return crud_vacation.create_vacation_request(db, request_in=request_in)
    except ValueError as e:
        if "ratificado" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/approve/{request_id}", response_model=VacationRequestResponse)
def approve_vacation(
    request_id: int, 
    status_update: VacationRequestStatusUpdate, 
    db: Session = Depends(get_db)
):
    """
    Endpoint para el rol de 'Jefe'. 
    Cambia el estado a APPROVED o REJECTED.
    """
    try:
        return crud_vacation.update_request_status(
            db, 
            request_id=request_id, 
            new_status=status_update.status
        )
    except ValueError as e:
        if "no encontrada" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))