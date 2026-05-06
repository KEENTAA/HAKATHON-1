"""
GUÍA DE CONFIGURACIÓN RÁPIDA - MS-PERSONAL
===========================================

Este archivo contiene los pasos EXACTOS para que el microservicio funcione
en tu máquina en máximo 5 minutos.

Fecha: 05 de Mayo de 2026 (Hackathon)
"""

# ============== PASO 1: VERIFICAR PYTHON ==============

Windows (PowerShell o CMD):
  $ python --version
  
  Esperado: Python 3.9.x o superior
  Si no lo tienes:
    → Descargar de https://www.python.org/downloads/
    → Instalar (marcar "Add Python to PATH")

Linux/Mac (Terminal):
  $ python3 --version
  
  Si no lo tienes:
    Linux: sudo apt-get install python3 python3-pip python3-venv
    Mac:   brew install python3

# ============== PASO 2: INSTALAR/INICIAR POSTGRESQL ==============

OPCIÓN A: PostgreSQL YA INSTALADO
───────────────────────────────────

Linux:
  $ sudo systemctl start postgresql
  $ sudo -u postgres psql

Windows:
  1. Abrir "Services" (Win+R → services.msc)
  2. Buscar "PostgreSQL"
  3. Si está detenido, clic derecho → Start
  4. Abrir cmd y escribir: psql -U postgres
  5. Pedir contraseña (la que pusiste en instalación)

Mac:
  $ brew services start postgresql
  $ psql postgres

OPCIÓN B: NO TIENES POSTGRESQL - INSTALACIÓN RÁPIDA
──────────────────────────────────────────────────

Windows:
  1. Ir a https://www.postgresql.org/download/windows/
  2. Descargar "Interactive installer by EDB"
  3. Ejecutar instalador
  4. Cuando pida contraseña para usuario "postgres": usa "postgres"
  5. Todos los defaults están bien
  6. Continuar a PASO 3

Linux (Debian/Ubuntu):
  $ sudo apt-get update
  $ sudo apt-get install postgresql postgresql-contrib
  $ sudo systemctl start postgresql
  $ sudo -u postgres psql

Mac:
  $ brew install postgresql
  $ brew services start postgresql

# ============== PASO 3: CREAR BASE DE DATOS ==============

Una vez dentro de psql (deberías ver "postgres=#"):

  CREATE DATABASE arca_personal;
  
  Resultado esperado:
  CREATE DATABASE

  \q  (para salir de psql)

Verificar que se creó:
  psql -U postgres -d arca_personal  (deberías entrar sin errores)
  \q

# ============== PASO 4: CREAR ENTORNO VIRTUAL PYTHON ==============

En la carpeta del proyecto (ms-personal):

Windows (PowerShell):
  $ python -m venv venv
  $ .\venv\Scripts\Activate.ps1
  
  Si te da error de "execution policy":
    $ Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    $ .\venv\Scripts\Activate.ps1

Windows (CMD):
  $ python -m venv venv
  $ venv\Scripts\activate

Linux/Mac:
  $ python3 -m venv venv
  $ source venv/bin/activate

Deberías ver (venv) en el prompt ==> ✅ CORRECTO

# ============== PASO 5: INSTALAR DEPENDENCIAS ==============

Ya con el entorno activado (ves el (venv)):

  (venv) $ pip install --upgrade pip
  (venv) $ pip install -r requirements.txt
  
  Espera a que termine (puede tardar 2-3 minutos)
  
  Verificar instalación:
  (venv) $ python -c "import fastapi; print('✅ FastAPI OK')"

# ============== PASO 6: VERIFICAR CONEXIÓN A BD ==============

  (venv) $ python -c "
import asyncio
from app.database import engine, init_db

async def test():
    try:
        await init_db()
        print('✅ Conexión a BD exitosa')
    except Exception as e:
        print(f'❌ Error: {e}')

asyncio.run(test())
  "
  
  Si está todo OK, deberías ver: ✅ Conexión a BD exitosa

# ============== PASO 7: EJECUTAR EL MICROSERVICIO ==============

  (venv) $ python main.py
  
  Deberías ver algo como:
  
  ============================================================
  🏢 MICROSERVICIO DE GESTIÓN DE PERSONAL - ARCA LTDA
  ============================================================
  📍 URL: http://localhost:8000
  📚 Documentación Swagger: http://localhost:8000/docs
  📚 Documentación ReDoc: http://localhost:8000/redoc
  ============================================================
  
  INFO:     Uvicorn running on http://0.0.0.0:8000
  INFO:     Application startup complete

Si ves esto: 🎉 ¡EL MICROSERVICIO ESTÁ FUNCIONANDO!

# ============== PASO 8: VERIFICAR FUNCIONAMIENTO ==============

Abre una NUEVA terminal (sin cerrar la anterior donde corre el servicio):

Test 1: Health Check
──────────────────
  $ curl http://localhost:8000/health
  
  Esperado:
  {
    "status": "healthy",
    "service": "Personal Management Service",
    "database": "connected",
    "modules": ["Departments", "Positions", "Employees"]
  }

Test 2: Ver API Swagger
──────────────────────
  Abre en el navegador: http://localhost:8000/docs
  Deberías ver la UI de Swagger con todos los endpoints

Test 3: Crear un Departamento
────────────────────────────
  $ curl -X POST http://localhost:8000/departments \
    -H "Content-Type: application/json" \
    -d '{"name": "Tecnología", "description": "Área de TI"}'
    
  Esperado (status 201):
  {
    "id": 1,
    "name": "Tecnología",
    "description": "Área de TI",
    "created_at": "2026-05-05T18:30:00",
    "updated_at": "2026-05-05T18:30:00"
  }

# ============== TROUBLESHOOTING ==============

Problema 1: "psql: command not found"
────────────────────────────────────
Solución: PostgreSQL no está en PATH
  Windows:
    → Añadir "C:\Program Files\PostgreSQL\15\bin" al PATH (variables entorno)
    → Reiniciar terminal
  
  Linux:
    $ sudo apt-get install postgresql-client
  
  Mac:
    $ brew install postgresql

Problema 2: "FATAL: role 'postgres' does not exist"
──────────────────────────────────────────────────
Solución: PostgreSQL no inicializado correctamente
  Linux:
    $ sudo -i -u postgres
    $ createdb arca_personal
    $ exit
  
  Windows/Mac:
    Reinstalar PostgreSQL

Problema 3: "ModuleNotFoundError: No module named 'sqlalchemy'"
────────────────────────────────────────────────────────────
Solución: Entorno virtual no activado correctamente
  Windows: .\venv\Scripts\activate
  Linux/Mac: source venv/bin/activate
  
  O reinstalar: pip install -r requirements.txt

Problema 4: Puerto 8000 ya en uso
─────────────────────────────────
Solución: Cambiar puerto en main.py
  
  Línea al final de main.py:
  uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8001,  # ← Cambiar de 8000 a otro
    ...
  )

Problema 5: "Connection refused" al intentar conectar BD
───────────────────────────────────────────────────────
Solución: PostgreSQL no está corriendo
  
  Windows:
    → Ir a Services (services.msc)
    → Buscar "PostgreSQL"
    → Click derecho → Start
  
  Linux:
    $ sudo systemctl start postgresql
  
  Mac:
    $ brew services start postgresql

Problema 6: "psycopg failed to connect"
──────────────────────────────────────
Solución: Credenciales BD incorrectas (revisar .env)

  .env debe tener:
  DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/arca_personal
  
  Adaptarlo si tu contraseña es diferente

# ============== CONFIGURACIÓN FINAL ==============

Una vez que TODO funcione:

1. Terminal 1: MANTENER CORRIENDO
   (venv) $ python main.py
   [NO cerrar esta ventana - el servicio debe estar activo]

2. Terminal 2: Para PRUEBAS
   Usar curl, Swagger (http://localhost:8000/docs), o Postman

3. Terminal 3: Para TERMINAL (si necesita)
   Trabajar en otras cosas sin cerrar el servicio

# ============== COMANDOS ÚTILES ==============

Verificar BD directamente:
  $ psql -U postgres -d arca_personal -c "SELECT * FROM employees;"

Limpiar BD (⚠️ CUIDADO - borra TODO):
  $ psql -U postgres -d arca_personal -c "DROP TABLE IF EXISTS employees, positions, departments CASCADE;"

Crear datos de prueba:
  Ver archivo: TESTING_Y_EJEMPLOS.md → Sección "Script SQL"

Detener PostgreSQL:
  Linux:   $ sudo systemctl stop postgresql
  Windows: Services → PostgreSQL → Stop
  Mac:     $ brew services stop postgresql

Desactivar entorno virtual:
  (venv) $ deactivate
  
  (Vuelves al prompt normal sin (venv))

# ============== VERIFICACIÓN FINAL ==============

✅ Python 3.9+          [Verificado con: python --version]
✅ PostgreSQL corriendo  [Verificado con: psql -U postgres]
✅ BD "arca_personal"   [Verificado con: \l en psql]
✅ Venv activado        [Verificado con: (venv) en prompt]
✅ Dependencias         [Verificado con: pip list]
✅ Conexión a BD        [Verificado con: curl /health]
✅ Swagger UI           [Verificado con: http://localhost:8000/docs]

Si todo está ✅: ¡Listo para el hackathon! 🚀

═════════════════════════════════════════════════════════════
Tiempo total de configuración: ~5 minutos
Fin de Guía de Configuración
═════════════════════════════════════════════════════════════
"""
