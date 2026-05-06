# ms-contratos

Microservicio de contratos para ARCA LTDA.

## Funcionalidad

- Generar un contrato básico parametrizable
- Persistir el contrato generado en PostgreSQL
- Consultar contratos por ID o por funcionario
- Listar tipos de contrato disponibles

## Endpoint principal

- `POST /contratos/generate`

## Endpoints adicionales

- `GET /`
- `GET /health`
- `GET /contratos/types`
- `GET /contratos/{contract_id}`
- `GET /contratos/employees/{employee_id}`

## Ejecución local

```bash
pip install -r requirements.txt
set DATABASE_URL=postgresql+asyncpg://postgres:admin@localhost:5432/arca_personal
python main.py
```

## Ejecución en Docker

```bash
docker build -t ms-contratos:local .
docker run --rm -p 8003:8000 -e DATABASE_URL=postgresql+asyncpg://postgres:admin@host.docker.internal:5432/arca_personal ms-contratos:local
```
