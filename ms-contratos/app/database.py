"""
Database module - Configuración de conexión a PostgreSQL con SQLAlchemy
Incluye reintentos automáticos y gestión de sesiones
"""

import os
import time
from typing import Generator
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Configuración de BD desde variables de entorno
DB_USER = os.getenv("DB_USER", "arca_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "arca_password")
DB_HOST = os.getenv("DB_HOST", "ms_contratos_db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "db_contratos")

# Construcción de URL de conexión
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"[Database] Conectando a: postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ==================== DECLARATIVE BASE ====================
Base = declarative_base()

# ==================== ENGINE CON REINTENTOS ====================
def create_database_engine(max_retries: int = 5, retry_delay: int = 3):
    """
    Crea engine de SQLAlchemy con reintentos automáticos.
    Útil cuando PostgreSQL tarda en iniciar en Docker.
    
    Args:
        max_retries: Número máximo de intentos de conexión
        retry_delay: Segundos de espera entre intentos
    
    Returns:
        Engine de SQLAlchemy configurado
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Database] Intento {attempt}/{max_retries} de conexión a PostgreSQL...")
            
            engine = create_engine(
                DATABASE_URL,
                echo=False,
                pool_pre_ping=True,  # Validar conexión antes de usar
                pool_size=20,        # Tamaño del pool
                max_overflow=10,     # Conexiones extras si necesario
                pool_recycle=3600,   # Reciclar conexiones cada hora
                connect_args={
                    "connect_timeout": 10,
                    "options": "-c statement_timeout=30000"  # 30s timeout
                }
            )
            
            # Probar la conexión
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            
            print(f"✓ [Database] Conexión establecida correctamente")
            return engine
            
        except Exception as e:
            print(f"✗ [Database] Error en intento {attempt}: {str(e)}")
            
            if attempt < max_retries:
                print(f"[Database] Reintentando en {retry_delay} segundos...")
                time.sleep(retry_delay)
            else:
                print(f"✗ [Database] No se pudo conectar después de {max_retries} intentos")
                raise


# Crear engine con reintentos
engine = create_database_engine(max_retries=5, retry_delay=3)

# ==================== SESSION FACTORY ====================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# ==================== DEPENDENCY PARA INYECCIÓN ====================
def get_db() -> Generator[Session, None, None]:
    """
    Dependency que proporciona sesión de BD para cada request.
    Uso: def endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"✗ [Database] Error en sesión: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# ==================== CREAR TABLAS ====================
def init_db():
    """
    Crea todas las tablas definidas en Base.metadata.
    Se ejecuta automáticamente en el startup de la app.
    """
    print("[Database] Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✓ [Database] Tablas verificadas/creadas")
