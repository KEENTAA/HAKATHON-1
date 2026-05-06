from fastapi import FastAPI
from app.api.vacations import router as vacations_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para la gestión de vacaciones de empleados - Hackathon MVP",
    version="1.0.0"
)

app.include_router(vacations_router)

@app.get("/")
def root():
    return {"message": "Microservicio de Vacaciones funcionando correctamente"}