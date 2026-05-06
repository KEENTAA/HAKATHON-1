"""Aplicación principal FastAPI - Microservicio de Contratos ARCA LTDA."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import contracts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando microservicio de Contratos...")
    await init_db()
    logger.info("Base de datos de Contratos inicializada")
    yield
    logger.info("Cerrando microservicio de Contratos...")


app = FastAPI(
    title="Microservicio de Contratos - ARCA LTDA",
    description="MVP de generación de contratos para el hackathon.",
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

app.include_router(contracts.router)


@app.get(
    "/",
    tags=["Información"],
    summary="Estado general",
    description="Retorna información básica del servicio"
)
async def root():
    return {
        "service": "Microservicio de Contratos - ARCA LTDA",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "generate": "/contratos/generate",
            "types": "/contratos/types",
            "by_id": "/contratos/{contract_id}",
            "by_employee": "/contratos/employees/{employee_id}",
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
        "service": "Contracts Management Service",
        "version": "1.0.0",
        "database": "connected",
        "modules": ["ContractTypes", "Contracts"]
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("MICROSERVICIO DE CONTRATOS - ARCA LTDA")
    logger.info("=" * 60)
    logger.info("URL: http://localhost:8003")
    logger.info("Documentación Swagger: http://localhost:8003/docs")
    logger.info("Documentación ReDoc: http://localhost:8003/redoc")
    logger.info("=" * 60)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
