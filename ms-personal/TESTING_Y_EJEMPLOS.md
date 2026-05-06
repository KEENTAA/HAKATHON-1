"""Archivo de datos de ejemplo para testing e inicialización."""

# ============== SCRIPT SQL PARA INICIALIZAR DATOS DE PRUEBA ==============
# Ejecutar en PostgreSQL después de que se haya iniciado la aplicación una vez
# (Para que las tablas se creen automáticamente)

-- 1. DEPARTAMENTOS
INSERT INTO departments (name, description) VALUES
('Tecnología', 'Departamento de Desarrollo e Infraestructura'),
('Contabilidad', 'Departamento Contable y Financiero'),
('Recursos Humanos', 'Gestión de Personal'),
('Operaciones', 'Operaciones Generales de la Empresa');

-- 2. POSICIONES
INSERT INTO positions (name, base_salary) VALUES
('Desarrollador Junior', 1500.00),
('Desarrollador Senior', 2500.00),
('Arquitecto de Software', 3500.00),
('Contador', 2000.00),
('Especialista RH', 2200.00),
('Gerente Operacional', 3000.00);

-- 3. EMPLEADOS
INSERT INTO employees (ci, first_name, last_name, email, phone, hire_date, current_salary, department_id, position_id, status) VALUES
('12345678', 'Juan', 'Pérez', 'juan.perez@arca.com', '+595961234001', '2023-01-15', 2500.00, 1, 2, 'Activo'),
('23456789', 'María', 'González', 'maria.gonzalez@arca.com', '+595961234002', '2023-03-20', 1500.00, 1, 1, 'Activo'),
('34567890', 'Carlos', 'López', 'carlos.lopez@arca.com', '+595961234003', '2024-01-10', 2000.00, 2, 4, 'Activo'),
('45678901', 'Ana', 'Martínez', 'ana.martinez@arca.com', '+595961234004', '2023-06-01', 2200.00, 3, 5, 'Activo'),
('56789012', 'Roberto', 'Sánchez', 'roberto.sanchez@arca.com', '+595961234005', '2022-11-05', 3500.00, 1, 3, 'Activo'),
('67890123', 'Laura', 'Fernández', 'laura.fernandez@arca.com', '+595961234006', '2023-05-15', 3000.00, 4, 6, 'Activo');

-- 4. VERIFICAR DATOS INSERTADOS
SELECT 
    e.id,
    e.ci,
    CONCAT(e.first_name, ' ', e.last_name) as nombre_completo,
    e.email,
    d.name as departamento,
    p.name as posicion,
    e.current_salary,
    e.status,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date)) as años_antiguedad
FROM employees e
JOIN departments d ON e.department_id = d.id
JOIN positions p ON e.position_id = p.id
ORDER BY e.hire_date DESC;
"""

# ============== EJEMPLOS DE CURL PARA TESTING ==============

"""
1. CREAR DEPARTAMENTO
───────────────────────

curl -X POST http://localhost:8000/departments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marketing",
    "description": "Departamento de Marketing y Comunicaciones"
  }'


2. CREAR POSICIÓN
──────────────────

curl -X POST http://localhost:8000/positions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Especialista Marketing Digital",
    "base_salary": 2100.00
  }'


3. CREAR EMPLEADO (COMPLETO)
──────────────────────────────

curl -X POST http://localhost:8000/employees \
  -H "Content-Type: application/json" \
  -d '{
    "ci": "98765432",
    "first_name": "Diego",
    "last_name": "Rodríguez",
    "email": "diego.rodriguez@arca.com",
    "phone": "+595961234567",
    "hire_date": "2024-01-15",
    "current_salary": 2100.00,
    "department_id": 1,
    "position_id": 2
  }'


4. LISTAR EMPLEADOS
────────────────────

curl http://localhost:8000/employees


5. LISTAR EMPLEADOS CON FILTROS
─────────────────────────────────

curl "http://localhost:8000/employees?status=Activo&department_id=1"


6. OBTENER EMPLEADO POR ID
──────────────────────────

curl http://localhost:8000/employees/1


7. OBTENER EMPLEADO POR CI
──────────────────────────

curl http://localhost:8000/employees/by-ci/12345678


8. ACTUALIZAR EMPLEADO
──────────────────────

curl -X PUT http://localhost:8000/employees/1 \
  -H "Content-Type: application/json" \
  -d '{
    "current_salary": 2800.00,
    "department_id": 2
  }'


9. DAR DE BAJA EMPLEADO
───────────────────────

curl -X PATCH http://localhost:8000/employees/1/deactivate


10. ELIMINAR EMPLEADO
──────────────────────

curl -X DELETE http://localhost:8000/employees/1


11. LISTAR EMPLEADOS POR DEPARTAMENTO
──────────────────────────────────────

curl http://localhost:8000/employees/department/1/list


12. CONTAR EMPLEADOS
─────────────────────

curl http://localhost:8000/employees/count


13. CONTAR EMPLEADOS ACTIVOS
──────────────────────────────

curl "http://localhost:8000/employees/count?status=Activo"


14. HEALTH CHECK
─────────────────

curl http://localhost:8000/health


15. OBTENER INFO DEL SERVICIO
──────────────────────────────

curl http://localhost:8000/
"""

# ============== CASOS DE PRUEBA (TEST SCENARIOS) ==============

"""
CASO 1: Flujo Completo de Contratación (HU-01, HU-02, HU-03)
──────────────────────────────────────────────────────────────

1.1. Crear una nuevo Departamento
   POST /departments
   → Crear "Consultoría"

1.2. Crear una Posición
   POST /positions
   → Crear "Consultor Senior" con salario base 3000

1.3. Crear un Empleado (HU-01: Alta de Personal)
   POST /employees
   → Crear empleado nuevo: "Diego Rodríguez"
   → department_id = ID del departamento creado
   → position_id = ID de la posición creada
   → Verificar que status = "Activo"

1.4. Actualizar Empleado (HU-02: Modificación)
   PUT /employees/{id}
   → Cambiar salary: 3000 → 3500
   → Cambiar departamento
   → Verificar updated_at cambió

1.5. Dar de Baja Empleado (HU-03: Baja de Personal)
   PATCH /employees/{id}/deactivate
   → Verificar que status = "Baja"
   → El empleado sigue en la BD (auditoría)


CASO 2: Validaciones de Negocio
─────────────────────────────────

2.1. Intentar crear empleado con CI duplicada
   POST /employees con ci que ya existe
   → Debe obtener 409 CONFLICT

2.2. Intentar crear empleado con email duplicado
   POST /employees con email que ya existe
   → Debe obtener 409 CONFLICT

2.3. Intentar crear empleado sin departamento valido
   POST /employees con department_id inválido
   → Debe obtener 404 NOT FOUND

2.4. Intentar crear empleado con salario <= 0
   POST /employees con current_salary <= 0
   → Valida Pydantic debe rechazar (422)


CASO 3: Listar y Filtrar (Preparación para Otros MS)
────────────────────────────────────────────────────

3.1. Listar todos los empleados
   GET /employees
   → Debe retornar lista con todos

3.2. Listar solo empleados ACTIVOS
   GET /employees?status=Activo
   → Filtrar por estado

3.3. Listar empleados de un departamento
   GET /employees?department_id=1
   → Preparar para cálculos de antigüedad

3.4. Listar empleados de departamento específico
   GET /employees/department/1/list
   → Endpoint especializado
"""
