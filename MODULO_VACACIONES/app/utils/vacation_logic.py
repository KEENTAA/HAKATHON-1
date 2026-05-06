from datetime import date, timedelta

# Feriados fijos para el MVP (Un detalle excelente para impresionar al directorio)
# Incluimos feriados nacionales clave
BOLIVIAN_HOLIDAYS = [
    date(2026, 1, 1),   # Año Nuevo
    date(2026, 1, 22),  # Día del Estado Plurinacional
    date(2026, 2, 16),  # Carnaval (Lunes)
    date(2026, 2, 17),  # Carnaval (Martes)
    date(2026, 4, 3),   # Viernes Santo
    date(2026, 5, 1),   # Día del Trabajo
    date(2026, 6, 4),   # Corpus Christi
    date(2026, 6, 21),  # Año Nuevo Andino
    date(2026, 8, 6),   # Día de la Independencia
    date(2026, 12, 25), # Navidad
]

def is_business_day(check_date: date) -> bool:
    """Verifica si es lunes-viernes y no es feriado."""
    # 5 = Sábado, 6 = Domingo
    if check_date.weekday() >= 5:
        return False
    if check_date in BOLIVIAN_HOLIDAYS:
        return False
    return True

def calculate_business_days(start_date: date, end_date: date) -> int:
    """Calcula la cantidad de días hábiles entre dos fechas."""
    days = 0
    current_date = start_date
    while current_date <= end_date:
        if is_business_day(current_date):
            days += 1
        current_date += timedelta(days=1)
    return days

def calculate_earned_days(hire_date: date, current_date: date = None) -> int:
    """Calcula cuántos días tiene acumulados (tope 30 días o 2 gestiones)."""
    if current_date is None:
        current_date = date.today()
        
    delta = current_date - hire_date
    years_worked = delta.days // 365
    
    # Si no tiene el año de antigüedad, 0 días (Bloqueo automático)
    if years_worked < 1:
        return 0
    
    earned = years_worked * 15
    # La regla dice máximo 2 años acumulables, así que el tope es 30
    return min(earned, 30)