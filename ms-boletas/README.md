# ms-boletas

Microservicio de boletas de pago para ARCA LTDA.

## Funcionalidad

- Generar boletas de pago basadas en el salario actual del funcionario
- Persistir cabecera y detalles de cada boleta
- Consultar boletas por funcionario
- Consultar boleta por ID
- Listar conceptos de pago base

## Endpoint principal

- `POST /boletas/generate`

## Endpoints adicionales

- `GET /`
- `GET /health`
- `GET /boletas/{empleado_id}`
- `GET /boletas/{empleado_id}/slips`
- `GET /boletas/{slip_id}/detail`
- `GET /boletas/concepts`

## Ejecución local

```bash
pip install -r requirements.txt
set DATABASE_URL=postgresql+asyncpg://postgres:admin@localhost:5432/arca_personal
python main.py
```

## Ejecución en Docker

```bash
docker build -t ms-boletas:local .
docker run --rm -p 8004:8000 -e DATABASE_URL=postgresql+asyncpg://postgres:admin@host.docker.internal:5432/arca_personal ms-boletas:local
```
