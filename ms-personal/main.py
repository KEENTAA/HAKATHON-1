"""Aplicación principal FastAPI - Microservicio de Personal ARCA LTDA."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import init_db
from app.routers import employees, departments, positions

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Eventos de ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar eventos de startup y shutdown."""
    # Startup
    logger.info("🚀 Inicializando microservicio de Personal...")
    await init_db()
    logger.info("✅ Base de datos inicializada")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando microservicio de Personal...")


# Crear aplicación FastAPI
app = FastAPI(
    title="Microservicio de Gestión de Personal - ARCA LTDA",
    description="MVP de gestión humana para el hackathon. Módulo Core de Personal.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============== CONFIGURACIÓN DE CORS ==============
# CRÍTICO: Permitir llamadas desde Angular en localhost:4200
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:3000",
        "http://localhost:8080",
        "*"  # Para MVP, permitir todo. En producción, ser específico.
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============== RUTAS/ENDPOINTS ==============

# Importar y registrar routers
app.include_router(departments.router)
app.include_router(positions.router)
app.include_router(employees.router)


# ============== ENDPOINT RAÍZ ==============

@app.get(
    "/",
    tags=["Información"],
    summary="Health Check",
    description="Verifica que el microservicio está funcionando correctamente"
)
async def root():
    """
    Endpoint raíz de health check.
    
    Retorna información sobre el estado del microservicio.
    """
    return {
        "service": "Microservicio de Gestión de Personal - ARCA LTDA",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "departments": "/departments",
            "positions": "/positions",
            "employees": "/employees"
        }
    }


@app.get(
    "/health",
    tags=["Información"],
    summary="Health Check Detallado",
    description="Retorna información detallada del estado del microservicio"
)
async def health_check():
    """Verificación de salud del microservicio con información adicional."""
    return {
        "status": "healthy",
        "service": "Personal Management Service",
        "version": "1.0.0",
        "database": "connected",
        "modules": ["Departments", "Positions", "Employees"]
    }


# ============== MANEJO DE ERRORES ==============

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejador genérico de excepciones."""
    logger.error(f"Error no manejado: {str(exc)}")
    return {
        "detail": "Error interno del servidor",
        "status_code": 500
    }


# ============== INFORMACIÓN AL INICIAR ==============

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("🏢 MICROSERVICIO DE GESTIÓN DE PERSONAL - ARCA LTDA")
    logger.info("=" * 60)
    logger.info("📍 URL: http://localhost:8000")
    logger.info("📚 Documentación Swagger: http://localhost:8000/docs")
    logger.info("📚 Documentación ReDoc: http://localhost:8000/redoc")
    logger.info("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
