"""
Main - Punto de entrada de la aplicación FastAPI
Configura:
- Inicialización de FastAPI
- CORS habilitado
- Rutas y routers
- Startup/shutdown events
- Inicialización de datos semilla
"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import init_db, get_db, engine, SessionLocal
from app.models import ContractType, Base
from app.routes.contratos import router as contratos_router

# ==================== DATOS SEMILLA ====================
TIPOS_CONTRATO_SEMILLA = [
    "Indefinido",
    "Plazo Fijo",
    "Consultoría"
]


# ==================== STARTUP/SHUTDOWN ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Eventos de ciclo de vida de la aplicación.
    Startup: Crea tablas e inicializa datos semilla
    Shutdown: Limpia recursos
    """
    # ========== STARTUP ==========
    print("\n" + "="*80)
    print("[STARTUP] Inicializando microservicio ms-contratos...")
    print("="*80)
    
    # Crear tablas
    try:
        init_db()
    except Exception as e:
        print(f"✗ [STARTUP] Error al crear tablas: {str(e)}")
        raise
    
    # Inicializar datos semilla (tipos de contrato)
    try:
        db = SessionLocal()
        
        # Verificar si ya existen tipos de contrato
        tipos_existentes = db.query(ContractType).count()
        
        if tipos_existentes == 0:
            print("[STARTUP] Inicializando datos semilla - Tipos de Contrato...")
            
            for tipo_nombre in TIPOS_CONTRATO_SEMILLA:
                tipo = ContractType(name=tipo_nombre)
                db.add(tipo)
                print(f"  ✓ Tipo creado: {tipo_nombre}")
            
            db.commit()
            print("✓ [STARTUP] Datos semilla inicializados correctamente")
        else:
            print(f"[STARTUP] Datos semilla ya existen ({tipos_existentes} tipos de contrato)")
        
        db.close()
        
    except Exception as e:
        print(f"✗ [STARTUP] Error al inicializar datos semilla: {str(e)}")
        db.close()
        raise
    
    print("[STARTUP] ✓ Microservicio ms-contratos listo para recibir requests")
    print("="*80 + "\n")
    
    yield
    
    # ========== SHUTDOWN ==========
    print("\n[SHUTDOWN] Cerrando microservicio ms-contratos...")
    print("[SHUTDOWN] ✓ Recursos liberados")


# ==================== CREAR APP FASTAPI ====================
app = FastAPI(
    title="Microservicio de Contratos - ARCA LTDA",
    description="API para gestión de contratos laborales. Integrante 3",
    version="1.0.0",
    lifespan=lifespan
)

# ==================== CONFIGURAR CORS ====================
# Permitir CORS desde cualquier origen para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],           # Permitir todos los métodos HTTP
    allow_headers=["*"],           # Permitir todos los headers
)

print("[Config] CORS habilitado para all_origins=['*']")

# ==================== REGISTRAR ROUTERS ====================
app.include_router(contratos_router, prefix="/api/v1")

print("[Config] Router de contratos registrado en /api/v1/contratos")

# ==================== ENDPOINT: Health Check ====================
@app.get("/")
async def health_check():
    """
    Health check endpoint.
    Indica que el servicio está activo y funcionando.
    """
    return {
        "servicio": "ms-contratos",
        "estado": "activo",
        "empresa": "ARCA LTDA",
        "version": "1.0.0",
        "integrante": 3
    }


@app.get("/health")
async def health_detailed():
    """
    Health check detallado con información de base de datos.
    """
    try:
        db = SessionLocal()
        
        # Intentar consulta simple a BD
        count_tipos = db.query(ContractType).count()
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "contract_types_count": count_tipos
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


# ==================== ENDPOINT: Información de API ====================
@app.get("/api/info")
async def info_api():
    """
    Información sobre los endpoints disponibles.
    """
    return {
        "endpoints": {
            "health": "GET /",
            "health_detailed": "GET /health",
            "generar_contrato": "POST /api/v1/contratos/generate",
            "listar_por_empleado": "GET /api/v1/contratos/empleado/{employee_id}",
            "obtener_contrato": "GET /api/v1/contratos/{id}",
            "actualizar_estado": "PUT /api/v1/contratos/{id}/status",
            "listar_tipos": "GET /api/v1/contratos/tipos",
        },
        "documentacion": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    import uvicorn
    
    # Configuración desde variables de entorno
    APP_PORT = int(os.getenv("APP_PORT", 8002))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=DEBUG,
        log_level="info"
    )
