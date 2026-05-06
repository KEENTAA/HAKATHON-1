"""Configuración de la conexión a base de datos PostgreSQL para Boletas."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:admin@localhost:5432/arca_personal"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    poolclass=NullPool,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    from app.models import PaymentConcept, PaySlip, PaySlipDetail
    from app.crud import seed_payment_concepts

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                sync_conn,
                tables=[PaymentConcept.__table__, PaySlip.__table__, PaySlipDetail.__table__],
            )
        )

    async with async_session() as session:
        await seed_payment_concepts(session)
