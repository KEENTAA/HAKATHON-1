# MODULO BOLETAS

Microservicio MVP para generar y almacenar boletas de pago con base de datos relacional y volumen persistente.

## Incluye

- `employees` (snapshot minimo para pruebas locales del modulo)
- `payment_concepts`
- `pay_slips` (cabecera)
- `pay_slip_details` (detalle)
- Calculo automatico de `total_net = ingresos - egresos`

## Ejecutar con Docker (sin docker-compose)

```powershell
docker network create rrhh-network
docker volume create boletas_db_data

docker build -f Dockerfile.db -t boletas-db:latest .
docker run -d --name boletas-db `
  --network rrhh-network `
  -e POSTGRES_DB=boletas_db `
  -e POSTGRES_USER=boletas_user `
  -e POSTGRES_PASSWORD=boletas_pass `
  -p 5433:5432 `
  -v boletas_db_data:/var/lib/postgresql/data `
  boletas-db:latest

docker build -f Dockerfile -t modulo-boletas:latest .
docker run -d --name modulo-boletas `
  --network rrhh-network `
  -e DB_HOST=boletas-db `
  -e DB_PORT=5432 `
  -e DB_NAME=boletas_db `
  -e DB_USER=boletas_user `
  -e DB_PASSWORD=boletas_pass `
  -e DB_SSL=false `
  -e DB_SCHEMA_PATH=app/schema.sql `
  -p 8004:8004 `
  modulo-boletas:latest
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

