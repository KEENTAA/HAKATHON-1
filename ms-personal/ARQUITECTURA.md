"""
DIAGRAMA DE ARQUITECTURA - MS-PERSONAL
======================================

Visualización de la arquitectura del Microservicio de Personal
"""

# ============== ARQUITECTURA DEL MICROSERVICIO ==============

┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLIENTE (Angular SPA en :4200)                           │
│                                                                              │
│  HttpClient (GET, POST, PUT, DELETE, PATCH)                               │
│  Consumidor: Integrante 5 (Frontend)                                       │
└──────────────────────────┬──────────────────────────────────────────────────┘
                           │
                           │ HTTP + JSON
                           │ CORS habilitado
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              MICROSERVICIO DE PERSONAL (FastAPI en :8000)                   │
│              Responsabilidad: Integrante 1                                  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ CAPA DE PRESENTACIÓN (Routers)                                       │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │  /employees     - POST (crear), GET (listar), DELETE                │  │
│  │  /employees/{id} - GET (detalle), PUT (actualizar)                  │  │
│  │  /employees/{id}/deactivate - PATCH (dar de baja)                   │  │
│  │  /departments   - CRUD (soporte)                                    │  │
│  │  /positions     - CRUD (soporte)                                    │  │
│  │  /health        - Health check                                       │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ CAPA DE LÓGICA DE NEGOCIO (CRUD)                                    │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │  Validaciones:                                                      │  │
│  │  • CI única                                                         │  │
│  │  • Email único                                                      │  │
│  │  • Departamento existe                                              │  │
│  │  • Posición existe                                                  │  │
│  │  • Salario > 0                                                      │  │
│  │  • Status enum (Activo/Baja/Suspendido)                             │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ CAPA DE VALIDACIÓN (Pydantic Schemas)                               │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │  EmployeeCreate     - Validar campos de entrada                     │  │
│  │  EmployeeUpdate     - Validar campos a actualizar                   │  │
│  │  EmployeeResponse   - Serializar respuesta                          │  │
│  │  EmployeeDetailResponse - Incluir relaciones                        │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ CAPA ORM (SQLAlchemy Models)                                         │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │  Employee                                                           │  │
│  │  ├─ id (PK)                                                         │  │
│  │  ├─ ci (unique)                                                     │  │
│  │  ├─ first_name, last_name                                           │  │
│  │  ├─ email (unique)                                                  │  │
│  │  ├─ phone                                                           │  │
│  │  ├─ hire_date         ← Critical para MS-Vacaciones                 │  │
│  │  ├─ current_salary    ← Critical para MS-Boletas                    │  │
│  │  ├─ status (enum)                                                   │  │
│  │  ├─ department_id (FK)                                              │  │
│  │  ├─ position_id (FK)                                                │  │
│  │  ├─ created_at                                                      │  │
│  │  └─ updated_at        ← Auditoría                                   │  │
│  │                                                                      │  │
│  │  Department                                                         │  │
│  │  ├─ id (PK)                                                         │  │
│  │  ├─ name (unique)                                                   │  │
│  │  ├─ description                                                     │  │
│  │  ├─ created_at, updated_at                                          │  │
│  │  └─ employees (reverse relation)                                    │  │
│  │                                                                      │  │
│  │  Position                                                           │  │
│  │  ├─ id (PK)                                                         │  │
│  │  ├─ name (unique)                                                   │  │
│  │  ├─ base_salary                                                     │  │
│  │  ├─ created_at, updated_at                                          │  │
│  │  └─ employees (reverse relation)                                    │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                           │                                                  │
│                           │ SQL async/await                                  │
│                           ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ CAPA DE ACCESO A DATOS (SQLAlchemy async engine + asyncpg)          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
                           │
                           │ TCP conexión async
                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                  POSTGRESQL DATABASE (arca_personal)                         │
│                  localhost:5432                                              │
│                                                                              │
│  Tablas:                                                                    │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │ departments  │      │ positions    │      │ employees    │              │
│  ├──────────────┤      ├──────────────┤      ├──────────────┤              │
│  │ id (PK)      │      │ id (PK)      │      │ id (PK)      │              │
│  │ name (U)     │      │ name (U)     │      │ ci (U)       │ ─┐           │
│  │ description  │      │ base_salary  │      │ first_name   │  │           │
│  │ created_at   │ ─┐   │ created_at   │ ─┐   │ last_name    │  │           │
│  │ updated_at   │  │   │ updated_at   │  │   │ email (U)    │  │           │
│  └──────────────┘  │   └──────────────┘  │   │ phone        │  │           │
│         ▲          │          ▲          │   │ hire_date    │  │           │
│         │          │          │          │   │ current_salary│ │           │
│         │          └─ FK ─────┘          │   │ status (enum)│  │           │
│         │          department_id         │   │ created_at   │  │           │
│         │                                │   │ updated_at   │  │           │
│         │                                │   │ department_FK├─────────┐    │
│         │                                └─ FK ─────────────  │        │    │
│         │                                  position_id        │        │    │
│         │                                               ├─────┘        │    │
│         │ Foreign Key Relationship (1 depto : N empls) │              │    │
│         │ Foreign Key Relationship (1 posición : N empls)             │    │
│         │                                          ├──────────────┘    │    │
│         │                                          Índices:          │    │
│         │                                          - idx_employees_ci │    │
│         │                                          - idx_employees_email
│         │                                          - idx_employees_status
│         │                                          - idx_employees_dept
│         │                                          - idx_employees_pos
│         └──────────────────────────────────────────────┘
│
│  Constraints:
│  • NOT NULL: PK, FK, name, base_salary, hire_date, current_salary, status
│  • UNIQUE: ci, email, department.name, position.name
│  • FOREIGN KEY: employees.department_id → departments.id
│  • FOREIGN KEY: employees.position_id → positions.id
│  • ENUM: employees.status IN ('Activo', 'Baja', 'Suspendido')
│
└──────────────────────────────────────────────────────────────────────────────┘


# ============== FLUJO DE DATOS DE UN REQUEST ==============

REQUEST: POST /employees (Crear empleado)
│
├─ ENTRADA: JSON { ci, first_name, ... }
│
├─► CAPA 1: PYDANTIC VALIDATION
│   └─ Validar tipos, ranges, email format
│   └─ Si válido → EmployeeCreate object
│   └─ Si inválido → 422 Unprocessable Entity
│
├─► CAPA 2: LÓGICA DE NEGOCIO (CRUD)
│   ├─ Verificar CI único en BD
│   │ └─ Si existe → 409 Conflict
│   ├─ Verificar email único en BD
│   │ └─ Si existe → 409 Conflict
│   ├─ Verificar department_id existe
│   │ └─ Si no → 404 Not Found
│   ├─ Verificar position_id existe
│   │ └─ Si no → 404 Not Found
│   └─ Si todo OK → Continuar
│
├─► CAPA 3: ORM (SQLAlchemy)
│   ├─ Crear objeto Employee
│   ├─ Set created_at = now()
│   ├─ Set updated_at = now()
│   ├─ Set status = "Activo"
│   └─ INSERT INTO employees ...
│
├─► CAPA 4: POSTGRESQL CONSTRAINTS
│   ├─ Verificar FK references
│   ├─ Verificar UNIQUE constraints
│   ├─ Verificar NOT NULL
│   └─ Si todo OK → Commit
│
├─► CAPA 5: RESPONSE SERIALIZATION
│   ├─ Cargar relaciones (department, position)
│   ├─ Convertir a EmployeeDetailResponse
│   └─ Serializar a JSON
│
└─ SALIDA: JSON { id: 1, ci: "12345678", ... } + 201 Created


# ============== INTEGRACIÓN CON OTROS MICROSERVICIOS ==============

El MS-Personal es el CORE. Los otros dependen de él:

┌─ MS-VACACIONES
│  Consumirá:
│  └─ GET /employees/{id}
│     └─ Lee: employee_id, hire_date
│     └─ Calcula: if (hoy - hire_date) >= 365 → 15 días
│
├─ MS-CONTRATOS
│  Consumirá:
│  └─ GET /employees/{id}
│     └─ Lee: employee_id, current_salary
│     └─ Crea: Contrato vinculado a employee_id
│
├─ MS-BOLETAS
│  Consumirá:
│  └─ GET /employees/{id}
│     └─ Lee: employee_id, current_salary
│     └─ Crea: Boleta basada en current_salary
│
└─ FRONTEND (Angular)
   Consumirá:
   └─ TODOS los endpoints
      └─ Componentes: Listado, Crear, Editar, Dar de Baja


# ============== MAPA DE PUERTOS ==============

ORCHESTRATION (localhost):

:8000 ← MS-Personal    (Este microservicio)
       └─ /employees, /departments, /positions

:8001 ← MS-Vacaciones  (Integrante 2)
       └─ /vacaciones, /balances

:8002 ← MS-Contratos   (Integrante 3)
       └─ /contratos

:8003 ← MS-Boletas     (Integrante 4)
       └─ /pay-slips

:4200 ← Angular SPA    (Integrante 5 Frontend)
       └─ http://localhost:8000/* (llama a todos los MS)

:5432 ← PostgreSQL Database
       └─ Base de datos compartida o separada (según diseño)


# ============== MATRIZ DE RESPONSABILIDADES ==============

┌──────────────────────┬────────────────────────────────────────────┐
│ Componente           │ Responsabilidad                            │
├──────────────────────┼────────────────────────────────────────────┤
│ FastAPI Router       │ HTTP requests/responses                    │
│ Pydantic Schema      │ Validar estructura JSON                    │
│ CRUD Functions       │ Lógica de negocio (FK, unique, etc.)      │
│ SQLAlchemy ORM       │ Mapeo objeto-relacional                    │
│ SQLAlchemy Engine    │ Connection pooling y transacciones         │
│ asyncpg Driver       │ Comunicación async con PostgreSQL          │
│ PostgreSQL Database  │ Persistencia, integridad, constrains       │
└──────────────────────┴────────────────────────────────────────────┘


# ============== DECISIONES ARQUITECTÓNICAS ==============

1. ASYNC/AWAIT
   ─────────────
   ✓ Permite manejar múltiples requests simultáneos sin bloqueo
   ✓ Ideal para MVP que necesita demostrar escalabilidad
   ✓ asyncpg + SQLAlchemy async = mejor performance

2. 3 TABLAS (No más)
   ───────────────
   ✓ Departamentos: Áreas de la empresa
   ✓ Posiciones: Cargos disponibles
   ✓ Empleados: Core del sistema (1 a N relación con ambas)
   ✓ Simple pero suficiente para MVP

3. STATUS ENUM vs DELETE
   ──────────────────────
   ✓ Cambiar a "Baja" NO elimina registro
   ✓ Preserva auditoría e historial
   ✓ Otros MS pueden calcular antigüedad aún
   ✓ Más profesional que abandonar FK orphans

4. CORS ABIERTO
   ─────────────
   ✓ allow_origins = ["*"] para MVP
   ✓ Angular en :4200 puede consumir sin restricciones
   ✓ En producción: especificar dominios exactos

5. SWAGGER AUTOMÁTICO
   ──────────────────
   ✓ FastAPI genera /docs desde tipos Python
   ✓ No hay documentación separada que mantener
   ✓ Siempre sincronizada con código


═════════════════════════════════════════════════════════════════════════════════
Fin de Diagrama de Arquitectura
═════════════════════════════════════════════════════════════════════════════════
"""
