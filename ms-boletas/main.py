"""Aplicación principal FastAPI - Microservicio de Boletas ARCA LTDA."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import boletas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando microservicio de Boletas...")
    await init_db()
    logger.info("Base de datos de Boletas inicializada")
    yield
    logger.info("Cerrando microservicio de Boletas...")


app = FastAPI(
    title="Microservicio de Boletas de Pago - ARCA LTDA",
    description="MVP de boletas de pago para el hackathon.",
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

app.include_router(boletas.router)


@app.get(
    "/",
    tags=["Información"],
    summary="Estado general",
    description="Retorna información básica del servicio"
)
async def root():
    return {
        "service": "Microservicio de Boletas de Pago - ARCA LTDA",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "generate": "/boletas/generate",
            "by_employee": "/boletas/{empleado_id}",
            "concepts": "/boletas/concepts",
        }
    }


@app.get(
    "/health",
    tags=["Información"],
    summary="Health Check",
    description="Verifica que el microservicio está funcionando correctamente"
)
async def health_check():
    return {
        "status": "healthy",
        "service": "Payroll Management Service",
        "version": "1.0.0",
        "database": "connected",
        "modules": ["PaymentConcepts", "PaySlips", "PaySlipDetails"]
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("MICROSERVICIO DE BOLETAS DE PAGO - ARCA LTDA")
    logger.info("=" * 60)
    logger.info("URL: http://localhost:8004")
    logger.info("Documentación Swagger: http://localhost:8004/docs")
    logger.info("Documentación ReDoc: http://localhost:8004/redoc")
    logger.info("=" * 60)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
