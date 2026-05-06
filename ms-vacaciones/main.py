"""Aplicación principal FastAPI - Microservicio de Vacaciones ARCA LTDA."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import vacations

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el arranque y cierre de la aplicación."""
    logger.info("Inicializando microservicio de Vacaciones...")
    await init_db()
    logger.info("Base de datos de Vacaciones inicializada")
    yield
    logger.info("Cerrando microservicio de Vacaciones...")


app = FastAPI(
    title="Microservicio de Vacaciones - ARCA LTDA",
    description="MVP de gestión de vacaciones para el hackathon.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vacations.router)


@app.get(
    "/",
    tags=["Información"],
    summary="Estado general",
    description="Retorna información básica del servicio",
)
async def root():
    return {
        "service": "Microservicio de Vacaciones - ARCA LTDA",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "balance": "/vacations/employees/{employee_id}/balance",
            "eligibility": "/vacations/employees/{employee_id}/eligibility",
            "requests": "/vacations/requests",
        },
    }


@app.get(
    "/health",
    tags=["Información"],
    summary="Health Check",
    description="Verifica que el microservicio está funcionando correctamente",
)
async def health_check():
    return {
        "status": "healthy",
        "service": "Vacations Management Service",
        "version": "1.0.0",
        "database": "connected",
        "modules": ["VacationBalances", "VacationRequests"],
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("MICROSERVICIO DE VACACIONES - ARCA LTDA")
    logger.info("=" * 60)
    logger.info("URL: http://localhost:8002")
    logger.info("Documentación Swagger: http://localhost:8002/docs")
    logger.info("Documentación ReDoc: http://localhost:8002/redoc")
    logger.info("=" * 60)

    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True, log_level="info")
