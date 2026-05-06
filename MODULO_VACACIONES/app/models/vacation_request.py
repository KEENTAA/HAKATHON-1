import enum
from sqlalchemy import Column, Integer, Date, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
from app.db.session import Base

class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class VacationRequest(Base):
    __tablename__ = "vacation_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    total_days = Column(Integer, nullable=False)
    
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    description = Column(String, nullable=True)

    employee = relationship("Employee", back_populates="vacations")