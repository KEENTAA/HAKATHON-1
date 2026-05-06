# MODULO BOLETAS

Microservicio MVP para generar y almacenar boletas de pago con base de datos relacional y volumen persistente.

## Incluye

- `employees` (snapshot minimo para pruebas locales del modulo)
- `payment_concepts`
- `pay_slips` (cabecera)
- `pay_slip_details` (detalle)
- Calculo automatico de `total_net = ingresos - egresos`

## Ejecutar con Docker

```bash
docker compose up --build
```

Servicios:

- API: `http://localhost:8004`
- Swagger: `http://localhost:8004/docs`
- PostgreSQL: `localhost:5433`
- Volumen persistente: `boletas_db_data`

## Endpoints principales

- `GET /health`
- `POST /employees`
- `GET /employees`
- `POST /payment-concepts`
- `GET /payment-concepts`
- `POST /pay-slips`
- `GET /pay-slips/:id`
- `GET /pay-slips?employee_id=&period_month=&period_year=`

## Ejemplo rapido de generacion de boleta

1. Crear funcionario:

```json
POST /employees
{
  "ci": "1234567",
  "first_name": "Ana",
  "last_name": "Perez"
}
```

2. Crear conceptos:

```json
POST /payment-concepts
{
  "name": "Sueldo Basico",
  "type": "Ingreso"
}
```

```json
POST /payment-concepts
{
  "name": "Descuento Salud",
  "type": "Egreso"
}
```

3. Generar boleta:

```json
POST /pay-slips
{
  "employee_id": 1,
  "period_month": 5,
  "period_year": 2026,
  "details": [
    { "concept_id": 1, "amount": 5000 },
    { "concept_id": 2, "amount": 450 }
  ]
}
```

