from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.session import Base

class VacationBalance(Base):
    __tablename__ = "vacation_balances"

    employee_id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    
    #dias totales ganados por antigüedad 
    days_earned = Column(Integer, default=0)
    
    #dias ya gastados
    days_used = Column(Integer, default=0)
    
    #dias que ya vencieron por antiguedad
    days_expired = Column(Integer, default=0)
    
    #dias netos
    days_available = Column(Integer, default=0)

    employee = relationship("Employee", back_populates="balance")