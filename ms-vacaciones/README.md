# ms-vacaciones

Microservicio de vacaciones para ARCA LTDA.

## Funcionalidad

- Consultar balance de vacaciones por funcionario
- Calcular automáticamente los días ganados según antigüedad
- Solicitar vacaciones
- Aprobar o rechazar solicitudes
- Listar solicitudes por funcionario o estado

## Endpoints principales

- `GET /`
- `GET /health`
- `GET /vacations/employees/{employee_id}/balance`
- `GET /vacations/employees/{employee_id}/eligibility`
- `POST /vacations/requests`
- `GET /vacations/requests`
- `GET /vacations/requests/{request_id}`
- `POST /vacations/requests/{request_id}/approve`
- `POST /vacations/requests/{request_id}/reject`
- `GET /vacations/employees/{employee_id}/requests`

## Ejecución local

```bash
pip install -r requirements.txt
set DATABASE_URL=postgresql+asyncpg://postgres:admin@localhost:5432/arca_personal
python main.py
```

## Ejecución en Docker

```bash
docker build -t ms-vacaciones:local .
docker run --rm -p 8001:8000 -e DATABASE_URL=postgresql+asyncpg://postgres:admin@host.docker.internal:5432/arca_personal ms-vacaciones:local
```
