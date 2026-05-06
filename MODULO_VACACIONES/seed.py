from datetime import date, timedelta
from app.db.session import SessionLocal
from app.models.employee import Employee

def seed_data():
    db = SessionLocal()
    today = date.today()

    # 1. Empleado Nuevo (6 meses de antigüedad) -> Probar Bloqueo
    emp_new = Employee(
        id=1,
        full_name="Juan Novato",
        hire_date=today - timedelta(days=180)
    )

    # 2. Empleado Senior (3 años de antigüedad) -> Probar Tope de 30 días
    emp_senior = Employee(
        id=2,
        full_name="Maria Veterana",
        hire_date=today - timedelta(days=365 * 3)
    )

    # 3. Empleado Estándar (1.5 años de antigüedad) -> Probar 15 días ganados
    emp_standard = Employee(
        id=3,
        full_name="Carlos Promedio",
        hire_date=today - timedelta(days=365 + 180)
    )

    try:
        db.add_all([emp_new, emp_senior, emp_standard])
        db.commit()
        print("✅ Seeds insertados con éxito.")
    except Exception as e:
        print(f"❌ Error al insertar: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()