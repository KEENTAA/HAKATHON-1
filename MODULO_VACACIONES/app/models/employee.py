from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.db.session import Base

class Employee(Base):
    __tablename__ = "employees"

    # El ID debe ser el mismo que maneja el Microservicio de Personal
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    hire_date = Column(Date, nullable=False)

    vacations = relationship("VacationRequest", back_populates="employee")
    balance = relationship("VacationBalance", back_populates="employee", uselist=False)