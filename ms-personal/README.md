# Microservicio de Gestión de Personal - ARCA LTDA

## Descripción

Este es el **Módulo Core** del sistema de gestión humana MVP para ARCA LTDA, desarrollado en 2 horas para presentación al Directorio.

Implementa la gestión completa de empleados (Personal), siendo la base maestra sobre la cual se construyen los demás microservicios:
- 📋 Departamentos (Áreas)
- 👔 Posiciones (Cargos)
- 👥 Empleados (Funcionarios)

## Stack Tecnológico

- **Backend**: FastAPI (Python) con Uvicorn
- **Base de Datos**: PostgreSQL + SQLAlchemy Async ORM
- **Validación**: Pydantic V2
- **Documentación**: Swagger/OpenAPI automático

## Estructura del Proyecto

```
ms-personal/
├── app/
│   ├── __init__.py
│   ├── database.py          # Configuración de BD async
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Validación Pydantic V2
│   ├── crud.py              # Operaciones de BD
│   └── routers/
│       ├── __init__.py
│       ├── departments.py   # Endpoints de departamentos
│       ├── positions.py     # Endpoints de posiciones
│       └── employees.py     # Endpoints de empleados (CORE)
├── main.py                  # Aplicación FastAPI + CORS
├── requirements.txt         # Dependencias Python
├── .env.example             # Variables de entorno (ejemplo)
└── README.md                # Este archivo
```

## Configuración e Instalación

### 1. Crear base de datos PostgreSQL

```sql
CREATE DATABASE arca_personal;
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL
```

### 5. Ejecutar el microservicio

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Uso de la API

### 📚 Documentación Interactiva

- **Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 🏥 Health Check

```bash
curl http://localhost:8000/health
```

### 👥 Operaciones con Empleados

#### Listar empleados
```bash
curl http://localhost:8000/employees
```

#### Crear empleado
```bash
curl -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" \
  -d '{
    "ci": "12345678",
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan@example.com",
    "phone": "+595961234567",
    "hire_date": "2024-05-05",
    "current_salary": 2500.00,
    "department_id": 1,
    "position_id": 1
  }'
```

#### Obtener empleado
```bash
curl http://localhost:8000/employees/1
```

#### Actualizar empleado
```bash
curl -X PUT http://localhost:8000/employees/1 \
  -H "Content-Type: application/json" \
  -d '{
    "current_salary": 3000.00,
    "department_id": 2
  }'
```

#### Dar de baja empleado
```bash
curl -X PATCH http://localhost:8000/employees/1/deactivate
```

#### Eliminar empleado
```bash
curl -X DELETE http://localhost:8000/employees/1
```

### 🏢 Operaciones con Departamentos

#### Listar departamentos
```bash
curl http://localhost:8000/departments
```

#### Crear departamento
```bash
curl -X POST http://localhost:8000/departments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tecnología",
    "description": "Departamento de TI"
  }'
```

### 👔 Operaciones con Posiciones

#### Listar posiciones
```bash
curl http://localhost:8000/positions
```

#### Crear posición
```bash
curl -X POST http://localhost:8000/positions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Desarrollador Senior",
    "base_salary": 2500.00
  }'
```

## Modelos de Datos

### Departments (Departamentos)
```
- id (PK)
- name (único)
- description
- created_at
- updated_at
```

### Positions (Posiciones)
```
- id (PK)
- name (único)
- base_salary
- created_at
- updated_at
```

### Employees (Empleados - CORE)
```
- id (PK)
- ci (único)                    # Cédula de Identidad
- first_name
- last_name
- email (único)
- phone
- hire_date                     # Fecha de ingreso
- current_salary
- status (Activo/Baja/Suspendido)
- department_id (FK)
- position_id (FK)
- created_at
- updated_at
```

## Características Implementadas

✅ **CRUD Completo** para empleados, departamentos y posiciones
✅ **Validación Pydantic V2** con reglas de negocio
✅ **Relaciones ORM** entre tablas
✅ **Async/Await** para operaciones de BD no bloqueantes
✅ **CORS Configurado** para Angular (localhost:4200)
✅ **Swagger Automático** (/docs)
✅ **Health Check** endpoints
✅ **Filtrado y Paginación** en listados
✅ **Estados de Empleado** (Activo, Baja, Suspendido)
✅ **Manejo de Errores** con códigos HTTP apropiados

## Campos Adicionales Agregados

Además de los campos especificados, se agregaron:

1. **Campos de Auditoría** (created_at, updated_at):
   - Para rastrear cuándo se crean/modifican registros
   - Útil para cumplimiento y auditoría futura

2. **Status Enum** para Empleados:
   - Mejor que simple baja física (preserva historial)
   - Facilita cálculo de antigüedad y vacaciones en otros microservicios

3. **Índices de Base de Datos**:
   - En CI, Email, Status para búsquedas rápidas
   - En department_id y position_id para joins eficientes

4. **Relaciones Reverse (back_populates)**:
   - Permite navegar de Departamento → Empleados
   - De Posición → Empleados
   - Útil para reportes futuros

5. **Endpoints Adicionales**:
   - `/employees/by-ci/{ci}` - Búsqueda por cédula
   - `/employees/count` - Cuenta total con filtros
   - `/employees/department/{id}/list` - Empleados por departamento
   - `/employees/{id}/deactivate` - Dar de baja sin eliminar

## Integración con Otros Microservicios

Este módulo de Personal es la **base maestra**. Los otros microservicios lo consumirán:

- **MS Vacaciones**: Consultará antiguedad vía `hire_date` del empleado
- **MS Contratos**: Creará contratos asociados a `employee_id`
- **MS Boletas**: Generará boletas basándose en `current_salary`

## Notas Importantes para el MVP (Hackathon)

⚠️ **CORS**: Configurado para permitir `*` (todos). En producción, especificar dominios.

⚠️ **Pool de Conexiones**: Configurado con `NullPool` para compatibilidad con entornos serverless.

⚠️ **Base de Datos**: PostgreSQL configurada sin SSL (ajustar en producción).

⚠️ **Logging**: En modo INFO. Cambiar a DEBUG solo en desarrollo.

## Próximos Pasos (Para Otros Integrantes)

1. **MS Vacaciones** - Consultar `employees.hire_date` para calcular antigüedad
2. **MS Contratos** - Crear contratos vinculados a `employee_id`
3. **MS Boletas** - Generar boletas basadas en `employees.current_salary`
4. **Frontend Angular** - Consumir estos 4 endpoints vía HttpClient + RxJS

## Contribuyentes

- **Inicialmente Funcional**: MVP Hackathon 2026-05-05
- **Responsable**: Integrante 1 - Microservicio de Personal

## Licencia

Propiedad intelectual de ARCA LTDA para fines del hackathon.
