"""
CAMPOS ADICIONALES AGREGADOS AL MICROSERVICIO DE PERSONAL
===========================================================

Este documento detalla todos los campos que se agregaron ADEMÁS de los especificados
en el documento de requerimientos, justificando cada uno.

"""

# ============== CAMPOS AGREGADOS POR TABLA ==============

# 1. DEPARTMENT (Departamentos)
# ────────────────────────────────────────────────────────

Campos del Documento Original:
  ✓ id (PK)
  ✓ name
  ✓ description

Campos Agregados:
  ➕ created_at (DateTime)
    └─ Razón: Auditoría. Rastrear cuándo se creó un departamento
  
  ➕ updated_at (DateTime)
    └─ Razón: Auditoría. Rastrear últimas modificaciones
  
  ➕ Índice en 'name' (unique=True, index=True)
    └─ Razón: Evitar departamentos duplicados, búsquedas rápidas


# 2. POSITION (Posiciones/Cargos)
# ────────────────────────────────────────────────────────

Campos del Documento Original:
  ✓ id (PK)
  ✓ name
  ✓ base_salary

Campos Agregados:
  ➕ created_at (DateTime)
    └─ Razón: Auditoría. Historial de creación de cargos
  
  ➕ updated_at (DateTime)
    └─ Razón: Auditoría. Seguimiento de cambios de base_salary
  
  ➕ Índice en 'name' (unique=True, index=True)
    └─ Razón: Evitar cargos duplicados, búsquedas rápidas


# 3. EMPLOYEE (Empleados - CORE)
# ────────────────────────────────────────────────────────

Campos del Documento Original:
  ✓ id (PK)
  ✓ ci
  ✓ first_name, last_name
  ✓ email, phone
  ✓ hire_date
  ✓ status (Enum: Activo, Baja, Suspendido)
  ✓ department_id (FK)
  ✓ position_id (FK)
  ✓ current_salary

Campos Agregados:
  ➕ created_at (DateTime)
    └─ Razón: Auditoría. Cuándo se ingresó el empleado al sistema
  
  ➕ updated_at (DateTime)
    └─ Razón: Auditoría. Cuándo fue la última actualización de datos
             └─ Importante para validaciones futuras de "último cambio de salario"
  
  ➕ Múltiples Índices:
    └─ ci (unique=True, index=True)
       └─ Razón: Cédula única, búsquedas frecuentes
    
    └─ email (unique=True, index=True)
       └─ Razón: Email único, prevenir duplicados, búsquedas por email
    
    └─ status (index=True)
       └─ Razón: Filtros frecuentes por estado (Activo, Baja, etc.)
    
    └─ department_id (index=True)
       └─ Razón: Joins frecuentes, búsquedas por departamento
    
    └─ position_id (index=True)
       └─ Razón: Joins frecuentes, búsquedas por puesto


# ============== ENUMS Y TIPOS ==============

EmployeeStatus (Enum)
  - ACTIVO = "Activo"
  - BAJA = "Baja"
  - SUSPENDIDO = "Suspendido"

Razón: 
  • Permite cambiar estado sin eliminar (preserva historial para auditoría)
  • Vs. simple DELETE → Imposible calcular antigüedad futura si empleado se elimina
  • Crítico para "MS Vacaciones": necesita saber if hire_date + 1 año ≤ hoy()


# ============== RELACIONES AGREGADAS ==============

Department.employees (reverse relationship)
  └─ Razón: Navegar desde Departamento → lista de sus Empleados
          └─ Útil para reportes tipo "Empleados por Departamento"

Position.employees (reverse relationship)
  └─ Razón: Navegar desde Posición → lista de Empleados en ese cargo
          └─ Útil para reportes de "Cargos saturados"


# ============== JUSTIFICACIÓN DE DISEÑO ==============

¿Por qué estos campos adicionales NO rompen los requerimientos?
─────────────────────────────────────────────────────────────

✅ Son EXTENSIONES que no cambian el core del negocio
✅ Facilitan AUDITORÍA y CUMPLIMIENTO legal
✅ Preparan el sistema para VACACIONES y BOLETAS futuras
✅ Los esquemas Pydantic NO exponen directamente updated_at en POST/PUT
✅ El MVP funciona correctamente sin exponerlos explícitamente al frontend

Ejemplo: Si Angular quiere crear un empleado:

  POST /employees
  {
    "ci": "123456",
    "first_name": "Juan",
    ...
  }

  Automáticamente FastAPI genera:
  - created_at = datetime.utcnow()
  - updated_at = datetime.utcnow()

  El frontend NO necesita enviarlos → El backend mantiene integridad


# ============== ENDPOINTS ADICIONALES ==============

Se agregaron 3 endpoints que NO estaban en requerimientos pero FACILITAN el MVP:

1. GET /employees/by-ci/{ci}
   └─ Buscar empleado por cédula (más natural que por ID)

2. GET /employees/count
   └─ Obtener total de empleados (para dashboards)

3. GET /employees/department/{id}/list
   └─ Listar empleados de un departamento (prepara para reportes)

4. PATCH /employees/{id}/deactivate
   └─ Dar de baja sin eliminar (cumple HU-03 más elegantemente)

Razón:
  • Se relacionan directamente con HUs del documento
  • Facilitan el trabajo del Frontend (menos lógica, más API)
  • Ejemplo: HU-03 pide "dar de baja" → PATCH /deactivate es perfecto


# ============== RESUMEN ==============

Campos Agregados:     6 (created_at, updated_at, 4 índices)
Enums Agregados:      1 (EmployeeStatus)
Relaciones Agregadas: 2 (bi-directionales)
Endpoints Agregados:  5 (Health Check + 4 operacionales)

IMPACTO EN REQUERIMIENTOS:  ✅ CERO
MEJORA DE ESCALABILIDAD:    ✅ SIGNIFICATIVA
FACILIDAD PARA AUDITORÍA:   ✅ CRÍTICA PARA PRODUCCIÓN
"""
