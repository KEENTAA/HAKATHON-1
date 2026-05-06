"""
MAPEO DE HISTORIAS DE USUARIO (HU) A ENDPOINTS API
===================================================

Este documento mapea cada Historia de Usuario del documento de requerimientos
a sus correspondientes endpoints implementados en el Microservicio de Personal.

"""

# ============== HU-01: ALTA DE PERSONAL ==============
# "Como administrador, quiero dar de alta a un nuevo funcionario con sus datos básicos."

Endpoint Implementado:
┌─────────────────────────────────────────────────────┐
│ POST /employees                                      │
├─────────────────────────────────────────────────────┤
│ Descripción: Crear un nuevo empleado                │
│ Método: HTTP POST                                   │
│ Cuerpo (JSON):                                      │
│   {                                                  │
│     "ci": "12345678",           # Cédula única      │
│     "first_name": "Juan",       # Nombre            │
│     "last_name": "Pérez",       # Apellido          │
│     "email": "juan@arca.com",   # Email único       │
│     "phone": "+595961234567",   # Teléfono opcional│
│     "hire_date": "2026-05-05",  # Fecha ingreso    │
│     "current_salary": 2500.00,  # Salario pactado  │
│     "department_id": 1,         # ID depto          │
│     "position_id": 2            # ID posición       │
│   }                                                  │
├─────────────────────────────────────────────────────┤
│ Respuesta (201 Created):                            │
│   {                                                  │
│     "id": 1,                                        │
│     "ci": "12345678",                              │
│     "first_name": "Juan",                          │
│     "last_name": "Pérez",                          │
│     "email": "juan@arca.com",                      │
│     "phone": "+595961234567",                      │
│     "hire_date": "2026-05-05",                     │
│     "current_salary": 2500.00,                     │
│     "department_id": 1,                            │
│     "position_id": 2,                              │
│     "status": "Activo",         # Auto-asignado    │
│     "created_at": "2026-05-05T18:30:00",          │
│     "updated_at": "2026-05-05T18:30:00",          │
│     "department": { ... },                         │
│     "position": { ... }                            │
│   }                                                  │
│                                                     │
│ Validaciones:                                       │
│   ✓ CI único (409 si duplicado)                    │
│   ✓ Email único (409 si duplicado)                 │
│   ✓ Departamento existe (404 si no)               │
│   ✓ Posición existe (404 si no)                   │
│   ✓ Salario > 0 (422 si no)                       │
└─────────────────────────────────────────────────────┘

Flujo de Testing:
  $ curl -X POST http://localhost:8000/employees \
    -H "Content-Type: application/json" \
    -d '{
      "ci": "12345678",
      "first_name": "Juan",
      "last_name": "Pérez",
      "email": "juan@arca.com",
      "phone": "+595961234567",
      "hire_date": "2026-05-05",
      "current_salary": 2500.00,
      "department_id": 1,
      "position_id": 2
    }'

Cumplimiento de HU-01:
  ✅ Se crea nuevo funcionario con datos básicos
  ✅ Sistema asigna automáticamente ID y estado
  ✅ Se valida unicidad de CI y Email
  ✅ Se vincula a Departamento y Posición existentes


# ============== HU-02: MODIFICACIÓN DE EMPLEADO ==============
# "Como administrador, quiero modificar el área, cargo y remuneración de un funcionario existente."

Endpoint Implementado:
┌─────────────────────────────────────────────────────┐
│ PUT /employees/{employee_id}                        │
├─────────────────────────────────────────────────────┤
│ Descripción: Actualizar datos de empleado           │
│ Método: HTTP PUT                                    │
│ Parámetro: employee_id (ID del empleado)           │
│ Cuerpo (JSON - parcial, solo campos a cambiar):    │
│   {                                                  │
│     "department_id": 2,    # Cambiar a otro área   │
│     "position_id": 3,      # Cambiar a otro cargo  │
│     "current_salary": 3000.00  # Nueva remuneración│
│   }                                                  │
├─────────────────────────────────────────────────────┤
│ Respuesta (200 OK):                                 │
│   {                                                  │
│     "id": 1,                                        │
│     "ci": "12345678",                              │
│     "first_name": "Juan",                          │
│     ...(datos actualizados)...                     │
│     "department_id": 2,      # ← Modificado        │
│     "position_id": 3,        # ← Modificado        │
│     "current_salary": 3000.00, # ← Modificado     │
│     "updated_at": "2026-05-05T19:00:00", # ← Cambió│
│     "department": { ... },                         │
│     "position": { ... }                            │
│   }                                                  │
│                                                     │
│ Validaciones:                                       │
│   ✓ Empleado existe (404 si no)                   │
│   ✓ Nuevo departamento existe (404 si intenta)    │
│   ✓ Nueva posición existe (404 si intenta)        │
│   ✓ Nuevo email único si intenta cambiar          │
└─────────────────────────────────────────────────────┘

Flujo de Testing:
  $ curl -X PUT http://localhost:8000/employees/1 \
    -H "Content-Type: application/json" \
    -d '{
      "department_id": 2,
      "position_id": 3,
      "current_salary": 3000.00
    }'

Cumplimiento de HU-02:
  ✅ Se puede cambiar área (department_id)
  ✅ Se puede cambiar cargo (position_id)
  ✅ Se puede cambiar remuneración (current_salary)
  ✅ Se valida existencia de nuevos departamento/posición
  ✅ Se registra el timestamp de modificación (updated_at)


# ============== HU-03: BAJA DE PERSONAL ==============
# "Como administrador, quiero dar de baja (inactivar) a un funcionario que deja la empresa."

Endpoints Implementados (2 opciones):

OPCIÓN 1 - Baja Lógica (RECOMENDADA para MVP):
┌─────────────────────────────────────────────────────┐
│ PATCH /employees/{employee_id}/deactivate          │
├─────────────────────────────────────────────────────┤
│ Descripción: Cambiar estado a "Baja" sin eliminar  │
│ Método: HTTP PATCH                                 │
│ Parámetro: employee_id (ID del empleado)           │
│ Cuerpo: vacío (solo necesita el endpoint)          │
├─────────────────────────────────────────────────────┤
│ Respuesta (200 OK):                                 │
│   {                                                  │
│     "id": 1,                                        │
│     "ci": "12345678",                              │
│     ...                                             │
│     "status": "Baja",  # ← Cambió de "Activo"     │
│     "updated_at": "2026-05-05T20:30:00",          │
│     ...                                             │
│   }                                                  │
│                                                     │
│ Ventajas:                                           │
│   ✓ Preserva historial (auditoría)                │
│   ✓ Aún se puede calcular antigüedad futuro        │
│   ✓ Otros MS pueden filtrar por status             │
│   ✓ No pierde referencias de contratos/boletas     │
└─────────────────────────────────────────────────────┘

OPCIÓN 2 - Baja Física (alternativa si se necesita):
┌─────────────────────────────────────────────────────┐
│ DELETE /employees/{employee_id}                     │
├─────────────────────────────────────────────────────┤
│ Descripción: Eliminar empleado completamente       │
│ Método: HTTP DELETE                                 │
│ Parámetro: employee_id (ID del empleado)           │
│ Cuerpo: vacío                                       │
├─────────────────────────────────────────────────────┤
│ Respuesta (200 OK):                                 │
│   { "message": "Empleado 'Juan Pérez' eliminado..." }│
│                                                     │
│ ⚠️  ADVERTENCIA:                                    │
│   ✗ Elimina el registro completamente              │
│   ✗ Imposible calcular antigüedad después          │
│   ✗ Rompe referencias de otros microservicios      │
│   ✗ NO RECOMENDADO para producción                │
└─────────────────────────────────────────────────────┘

Flujo de Testing (RECOMENDADO):
  $ curl -X PATCH http://localhost:8000/employees/1/deactivate

Flujo de Testing (Alternativa):
  $ curl -X DELETE http://localhost:8000/employees/1

Cumplimiento de HU-03:
  ✅ Se puede dar de baja funcionario que se va
  ✅ Registro se preserva en la BD (opción PATCH)
  ✅ Estado cambia a "Baja" claramente
  ✅ Otros microservicios pueden detectar el cambio
  ✅ Se registra timestamp de baja (updated_at)


# ============== ENDPOINTS DE SOPORTE (No Explícitos en HU pero Críticos) ==============

GET /employees
  → Listar todos los empleados
  → Permite visualizar el estado general de la nómina
  → Usado por: Reportes, Dashboards, Angular frontend

GET /employees/{id}
  → Obtener detalles de un empleado específico
  → Usado por: Edición, vista de perfil

GET /employees/by-ci/{ci}
  → Buscar empleado por cédula
  → Usado por: Búsqueda rápida por CI

GET /employees/department/{id}/list
  → Listar empleados de un departamento
  → Usado por: FUTURO MS Vacaciones (para calcular antigüedad grupal)

GET /employees/count
  → Contar total de empleados
  → Usado por: Dashboards, estadísticas

GET /departments
GET /departments/{id}
  → Operaciones CRUD de departamentos (necesarios para crear empleados)

GET /positions
GET /positions/{id}
  → Operaciones CRUD de posiciones (necesarios para crear empleados)


# ============== MATRIZ DE CUMPLIMIENTO ==============

╔═════════════════════════════════════════════════════════════╗
║ Historia de Usuario │ Endpoint           │ Estado   │ Nota  ║
╠═════════════════════════════════════════════════════════════╣
║ HU-01 (Alta)        │ POST /employees    │ ✅ OK    │ Test  ║
║                     │                    │          │ 01.md ║
╠═════════════════════════════════════════════════════════════╣
║ HU-02 (Modificación)│ PUT /employees/{id}│ ✅ OK    │ Test  ║
║                     │                    │          │ 02.md ║
╠═════════════════════════════════════════════════════════════╣
║ HU-03 (Baja)        │ PATCH /employees.. │ ✅ OK    │ Test  ║
║                     │      /{id}/deactive│          │ 03.md ║
╚═════════════════════════════════════════════════════════════╝

COBERTURA DE REQUERIMIENTOS FUNCIONALES:
  ✅ 100% - Todos los requerimientos de HU-01, HU-02, HU-03 implementados

ENTREGABLES POR HU:
  ✅ API documentada en Swagger con endpoints POST, PUT, PATCH, DELETE
  ✅ Validaciones de negocio implementadas
  ✅ Respuestas HTTP correctas (201, 200, 404, 409)
  ✅ Base de datos relacional con referencias (FK)
  ✅ Auditoría con timestamps (created_at, updated_at)
"""
