# ============================================================================
# Dockerfile - MODULO_VACACIONES
# Base: python:3.12-slim (optimizado y ligero)
# ============================================================================

FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Configurar variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema (mínimas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ app/
COPY alembic.ini .
COPY migrations/ migrations/

# Exponer puerto
EXPOSE 8006

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8006"]
