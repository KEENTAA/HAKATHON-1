from decimal import Decimal
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg import errors

from app.db import get_conn, run_schema
from app.schemas import EmployeeCreate, PaymentConceptCreate, PaySlipCreate

app = FastAPI(title="MODULO BOLETAS", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    run_schema()


@app.get("/health")
def health() -> dict[str, str]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    return {"status": "ok", "service": "modulo-boletas"}


@app.post("/employees", status_code=201)
def create_employee(payload: EmployeeCreate) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO employees (ci, first_name, last_name, email, phone, hire_date, status)
                    VALUES (%s, %s, %s, %s, %s, COALESCE(%s::date, CURRENT_DATE), %s)
                    RETURNING id, ci, first_name, last_name, email, phone, hire_date, status
                    """,
                    (
                        payload.ci,
                        payload.first_name,
                        payload.last_name,
                        payload.email,
                        payload.phone,
                        payload.hire_date,
                        payload.status,
                    ),
                )
                row = cur.fetchone()
            conn.commit()
            return dict(row)
    except errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Funcionario duplicado (ci/email).")


@app.get("/employees")
def list_employees() -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, ci, first_name, last_name, email, phone, hire_date, status
                FROM employees
                ORDER BY id DESC
                """
            )
            return [dict(row) for row in cur.fetchall()]


@app.post("/payment-concepts", status_code=201)
def create_payment_concept(payload: PaymentConceptCreate) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO payment_concepts (name, type)
                    VALUES (%s, %s)
                    RETURNING id, name, type
                    """,
                    (payload.name, payload.type),
                )
                row = cur.fetchone()
            conn.commit()
            return dict(row)
    except errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Concepto ya existente.")


@app.get("/payment-concepts")
def list_payment_concepts() -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, type FROM payment_concepts ORDER BY id DESC"
            )
            return [dict(row) for row in cur.fetchall()]


@app.post("/pay-slips", status_code=201)
def create_pay_slip(payload: PaySlipCreate) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, status FROM employees WHERE id = %s",
                    (payload.employee_id,),
                )
                employee = cur.fetchone()
                if not employee:
                    raise HTTPException(status_code=400, detail="employee_id no existe.")
                if employee["status"] == "Baja":
                    raise HTTPException(
                        status_code=400,
                        detail="No se puede generar boleta para funcionario de baja.",
                    )

                concept_ids = [d.concept_id for d in payload.details]
                cur.execute(
                    """
                    SELECT id, type FROM payment_concepts
                    WHERE id = ANY(%s)
                    """,
                    (concept_ids,),
                )
                concepts = cur.fetchall()
                if len(concepts) != len(concept_ids):
                    raise HTTPException(
                        status_code=400,
                        detail="Uno o mas concept_id no existen.",
                    )
                concept_type = {row["id"]: row["type"] for row in concepts}

                cur.execute(
                    """
                    INSERT INTO pay_slips (employee_id, period_month, period_year, payment_date)
                    VALUES (%s, %s, %s, COALESCE(%s::date, CURRENT_DATE))
                    RETURNING id, employee_id, period_month, period_year, payment_date
                    """,
                    (
                        payload.employee_id,
                        payload.period_month,
                        payload.period_year,
                        payload.payment_date,
                    ),
                )
                pay_slip = cur.fetchone()

                total_income = Decimal("0")
                total_expense = Decimal("0")
                for detail in payload.details:
                    cur.execute(
                        """
                        INSERT INTO pay_slip_details (pay_slip_id, concept_id, amount)
                        VALUES (%s, %s, %s)
                        """,
                        (pay_slip["id"], detail.concept_id, detail.amount),
                    )
                    if concept_type[detail.concept_id] == "Ingreso":
                        total_income += detail.amount
                    else:
                        total_expense += detail.amount

                total_net = total_income - total_expense
                cur.execute(
                    "UPDATE pay_slips SET total_net = %s WHERE id = %s",
                    (total_net, pay_slip["id"]),
                )
            conn.commit()
            return {
                **dict(pay_slip),
                "total_net": total_net,
                "totals": {"income": total_income, "expense": total_expense},
            }
    except errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Ya existe boleta para este funcionario en ese periodo.",
        )


@app.get("/pay-slips/{pay_slip_id}")
def get_pay_slip(pay_slip_id: int) -> dict[str, Any]:
    if pay_slip_id <= 0:
        raise HTTPException(status_code=400, detail="id invalido.")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ps.id, ps.employee_id, e.ci, e.first_name, e.last_name,
                       ps.period_month, ps.period_year, ps.payment_date, ps.total_net, ps.created_at
                FROM pay_slips ps
                JOIN employees e ON e.id = ps.employee_id
                WHERE ps.id = %s
                """,
                (pay_slip_id,),
            )
            slip = cur.fetchone()
            if not slip:
                raise HTTPException(status_code=404, detail="Boleta no encontrada.")

            cur.execute(
                """
                SELECT d.id, d.concept_id, c.name AS concept_name, c.type, d.amount
                FROM pay_slip_details d
                JOIN payment_concepts c ON c.id = d.concept_id
                WHERE d.pay_slip_id = %s
                ORDER BY d.id
                """,
                (pay_slip_id,),
            )
            details = [dict(row) for row in cur.fetchall()]

    return {**dict(slip), "details": details}


@app.get("/pay-slips")
def list_pay_slips(
    employee_id: int | None = Query(default=None, gt=0),
    period_month: int | None = Query(default=None, ge=1, le=12),
    period_year: int | None = Query(default=None, ge=2000),
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []

    if employee_id is not None:
        params.append(employee_id)
        where.append(f"employee_id = ${len(params)}")
    if period_month is not None:
        params.append(period_month)
        where.append(f"period_month = ${len(params)}")
    if period_year is not None:
        params.append(period_year)
        where.append(f"period_year = ${len(params)}")

    sql = (
        "SELECT id, employee_id, period_month, period_year, payment_date, total_net, created_at "
        "FROM pay_slips"
    )
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

