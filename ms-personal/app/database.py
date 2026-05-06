"""Configuración de la conexión a base de datos PostgreSQL."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import event
from sqlalchemy.pool import NullPool
import os
from typing import AsyncGenerator

# Variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/arca_personal"
)

# Crear engine async
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para debug
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    poolclass=NullPool,
)

# Crear sesión async
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base declarativa para modelos
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia para inyectar sesión en endpoints."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Crear todas las tablas."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Eliminar todas las tablas (para testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
