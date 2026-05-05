"""
Servicio de generación de contratos legales
Contiene la lógica de negocio para crear el documento de contrato
"""

from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Contract, ContractType


def generar_documento_contrato(
    employee_id: int,
    contract_type: ContractType,
    start_date: date,
    end_date: date,
    salary: float,
    trial_period_days: int
) -> str:
    """
    Genera el texto legal del contrato en formato String usando f-strings.
    Incluye 8+ cláusulas profesionales en formato legal.
    
    Args:
        employee_id: ID del empleado
        contract_type: Objeto ContractType con nombre
        start_date: Fecha de inicio
        end_date: Fecha de fin (puede ser None)
        salary: Salario mensual
        trial_period_days: Días de período de prueba
    
    Returns:
        String con el documento de contrato legal formateado
    """
    
    # Formatear fechas para el documento
    fecha_inicio = start_date.strftime("%d de %B de %Y").replace("January", "enero").replace("February", "febrero").replace("March", "marzo").replace("April", "abril").replace("May", "mayo").replace("June", "junio").replace("July", "julio").replace("August", "agosto").replace("September", "septiembre").replace("October", "octubre").replace("November", "noviembre").replace("December", "diciembre")
    
    if end_date:
        fecha_fin = end_date.strftime("%d de %B de %Y").replace("January", "enero").replace("February", "febrero").replace("March", "marzo").replace("April", "abril").replace("May", "mayo").replace("June", "junio").replace("July", "julio").replace("August", "agosto").replace("September", "septiembre").replace("October", "octubre").replace("November", "noviembre").replace("December", "diciembre")
        tipo_contrato = f"{contract_type.name} hasta {fecha_fin}"
    else:
        tipo_contrato = contract_type.name
        fecha_fin = "A Plazo Indefinido"
    
    # Calcular fecha de fin de prueba
    fecha_fin_prueba = start_date + timedelta(days=trial_period_days)
    fecha_fin_prueba_str = fecha_fin_prueba.strftime("%d de %B de %Y").replace("January", "enero").replace("February", "febrero").replace("March", "marzo").replace("April", "abril").replace("May", "mayo").replace("June", "junio").replace("July", "julio").replace("August", "agosto").replace("September", "septiembre").replace("October", "octubre").replace("November", "noviembre").replace("December", "diciembre")
    
    # Fecha de generación
    fecha_generacion = datetime.utcnow().strftime("%d de %B de %Y a las %H:%M:%S").replace("January", "enero").replace("February", "febrero").replace("March", "marzo").replace("April", "abril").replace("May", "mayo").replace("June", "junio").replace("July", "julio").replace("August", "agosto").replace("September", "septiembre").replace("October", "octubre").replace("November", "noviembre").replace("December", "diciembre")
    
    # Generar documento con f-strings
    documento = f"""
════════════════════════════════════════════════════════════════════════════════
                             CONTRATO DE TRABAJO
                                  ARCA LTDA
════════════════════════════════════════════════════════════════════════════════

Generado: {fecha_generacion}
ID Empleado: {employee_id}

────────────────────────────────────────────────────────────────────────────────
CLÁUSULA 1: OBJETO DEL CONTRATO
────────────────────────────────────────────────────────────────────────────────

ARCA LTDA (en adelante "EMPLEADOR") contrata al empleado con ID {employee_id} 
(en adelante "EMPLEADO") para que desempeñe las funciones inherentes a su cargo, 
conforme a lo establecido en el presente contrato y bajo los términos y 
condiciones que se detallan a continuación.

────────────────────────────────────────────────────────────────────────────────
CLÁUSULA 2: DURACIÓN DEL CONTRATO
────────────────────────────────────────────────────────────────────────────────

El presente contrato es de tipo "{contract_type.name}" y comenzará a partir del 
{fecha_inicio}. El contrato se regirá de conformidad con el tipo seleccionado.

Tipo de Contrato: {tipo_contrato}
Fecha de Inicio: {fecha_inicio}
Fecha de Fin: {fecha_fin}

────────────────────────────────────────────────────────────────────────────────
CLÁUSULA 3: REMUNERACIÓN
────────────────────────────────────────────────────────────────────────────────

El EMPLEADOR acuerda pagar al EMPLEADO una remuneración mensual de 
${salary:,.2f} USD, pagadera en forma quincenal o mensual según lo establecido 
en las políticas internas de la empresa.

Salario Mensual: ${salary:,.2f}
Forma de Pago: Depósito bancario
Período de Pago: Mensual

────────────────────────────────────────────────────────────────────────────────
CLÁUSULA 4: PERÍODO DE PRUEBA
────────────────────────────────────────────────────────────────────────────────

Las partes acuerdan un período de prueba de {trial_period_days} días naturales, 
contados a partir de la fecha de inicio del contrato, es decir, hasta el 
{fecha_fin_prueba_str}.

Durante este período, tanto el EMPLEADOR como el EMPLEADO pueden dar por 
terminado el contrato sin responsabilidad legal ni pago de indemnización, 
excepto lo ya devengado en concepto de salario y beneficios.

Período de Prueba: {trial_period_days} días
Finalización de Prueba: {fecha_fin_prueba_str}

────────────────────────────────────────────────────────────────────────────────
CLÁUSULA 5: OBLIGACIONES DEL EMPLEADO
────────────────────────────────────────────────────────────────────────────────

El EMPLEADO se compromete a:

a) Cumplir diligentemente con todas las funciones y responsabilidades 
   inherentes a su cargo.

b) Asistir puntualmente al trabajo en los horarios establecidos por el 
   EMPLEADOR.

c) Respetar y acatar las políticas, normas y procedimientos establecidos 
   por ARCA LTDA.

d) Mantener una conducta honesta, ética y profesional en el cumplimiento 
   de sus funciones.

e) Cuidar y preservar los activos y recursos puestos a su disposición.

f) Reportar cualquier irregularidad o inconveniente relacionado con sus 
   funciones.

────────────────────────────────────────────────────────────────────────────────
CLÁUSULA 6: OBLIGACIONES DEL EMPLEADOR
────────────────────────────────────────────────────────────────────────────────

El EMPLEADOR se compromete a:

a) Pagar oportunamente la remuneración acordada.

b) Proporcionar un ambiente de trabajo seguro y saludable.

c) Respetar los derechos fundamentales del EMPLEADO conforme a la 
   legislación vigente.

d) Garantizar la seguridad social integral del EMPLEADO.

e) Permitir que el EMPLEADO goce de sus derechos laborales establecidos 
   por la ley.

────────────────────────────────────────────────────────────────────────────────
CLÁUSULA 7: TERMINACIÓN DEL CONTRATO
────────────────────────────────────────────────────────────────────────────────

El presente contrato puede ser terminado por:

a) Mutuo consentimiento de las partes.

b) Por vencimiento del plazo establecido en el contrato.

c) Por muerte del EMPLEADO.

d) Por incapacidad permanente del EMPLEADO.

e) Por justa causa, conforme a la ley aplicable.

f) Por causa no imputable al EMPLEADO (capacidad económica de la empresa).

g) Por renuncia voluntaria del EMPLEADO.

────────────────────────────────────────────────────────────────────────────────
CLÁUSULA 8: CONFIDENCIALIDAD
────────────────────────────────────────────────────────────────────────────────

El EMPLEADO se compromete a mantener en absoluta confidencialidad toda 
información técnica, comercial, financiera, estratégica y de negocio de 
ARCA LTDA, tanto durante la vigencia del contrato como después de su 
terminación.

Esta obligación de confidencialidad se mantiene indefinidamente, incluso 
después de la terminación de la relación laboral.

────────────────────────────────────────────────────────────────────────────────
CLÁUSULA 9: JURISDICCIÓN Y LEY APLICABLE
────────────────────────────────────────────────────────────────────────────────

El presente contrato se rige y es interpretado de conformidad con las leyes 
de la República de Colombia, especialmente por el Código Sustantivo del Trabajo 
y demás normas laborales aplicables.

Las partes se someten a la jurisdicción de los jueces civiles competentes, 
conforme a la ley aplicable.

════════════════════════════════════════════════════════════════════════════════

Documento generado automáticamente por el sistema de gestión de contratos
ARCA LTDA - Todos los derechos reservados

Fecha de Generación: {fecha_generacion}

════════════════════════════════════════════════════════════════════════════════
"""
    
    return documento.strip()
