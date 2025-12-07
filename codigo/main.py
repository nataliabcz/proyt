#Integrantes: Valentina Monterroza y Natalia Barrera 
#Link a el repositorio: https://github.com/nataliabcz/proyt.git


"""
main.py

Archivo principal de la aplicación.

Este módulo se encarga de:
    - Inicializar las conexiones a MySQL, MongoDB y al archivo CSV.
    - Gestionar el flujo principal del programa.
    - Mostrar los menús por consola para los usuarios con roles de admin y usuario.
"""
import json
import sys
import threading
from datetime import datetime, timedelta, date
from pathlib import Path

import mysql_connection as SQLC
import mongodb_connection as MONGOC
import csv_connection as CSVC
from security_module import validate_login, create_mysql_connection
from validators import (
    validate_date,
    validate_float,
    validate_integer,
    validate_menu_option,
    validate_not_empty,
    validate_range,
    validate_email,
)

ALERT_THREAD = None
ALERT_STOP_EVENT = None
ALERT_INTERVAL_SECONDS = 180
REPORTS_DIR = Path("reportes")

# FUNCIONES DE INICIALIZACIÓN

def initialize_system():
    """
    Inicializa el sistema creando las conexiones necesarias.
    """
    print("Bienvenido/a al sistema 'SALUD A TU ALCANCE'")
    

    # Conexión a MySQL
    mysql_conn = create_mysql_connection()
    if mysql_conn is None:
        print("No fue posible conectar a MySQL. Saliendo del sistema")
        sys.exit(1)
        
    # Conexión a MongoDB
    mongo_db = MONGOC.create_mongo_connection()
    if mongo_db is None:
        print("No fue posible conectar a MongoDB. Saliendo del sistema")
        sys.exit(1)

    # Verificar acceso al CSV de contraseñas
    try:
        passwords = CSVC.load_passwords()
        print(f"Archivo CSV de contraseñas cargado. Usuarios en CSV: {len(passwords)}")
    except Exception as e:
        print("Error al acceder al archivo CSV de contraseñas:", e)
        sys.exit(1)

    # Se llama a la función que usa hilos para ejecutar tareas en paralelo, como es el caso de
    # las alertas automáticas de acuerdo a los registros que hagan los usuarios.
    start_automatic_alerts(mysql_conn, ALERT_INTERVAL_SECONDS)

    return {
        "mysql": mysql_conn,
        "mongo": mongo_db
    }

# FUNCIONES DE MENÚ Y UTILIDADES DE CONSOLA

def get_menu_option(max_option):
    """
    Solicita al usuario una opción de menú y la valida.

    Utiliza la función validate_menu_option del módulo validators
    para asegurarse de que la opción sea numérica y esté en el rango.

    Parámetros:
        max_option (int): número máximo de opción permitida.

    Retorna:
        int: opción seleccionada por el usuario (ya validada).
    """
    # Repite la pregunta hasta que el usuario entregue una opción válida.
    while True:
        option = input("Selecciona una opción: ")
        if validate_menu_option(option, max_option):
            return int(option)


def _input_date_with_default():
    """
    Devuelve una fecha valida en formato YYYY-MM-DD (por defecto, hoy).
    

    Retorna:
        str: fecha ingresada por el usuario o fecha actual en el caso de que el usuario no la haya ingresado.
    """
    
    # Obtiene la fecha actual, la cual se usará como valor por defecto.
    default_date = datetime.now().date().isoformat()
    while True:
        date = input(f"Fecha del registro (YYYY-MM-DD) [por defecto {default_date}]: ").strip()
        if date == "":
            return default_date
        # Valida la fecha con la función implementada en el modulo de validadores (validators)
        if validate_date(date):
            return date


def _input_float(prompt_text, min_value=None, max_value=None, allow_empty=False):
    """
    Solicita un numero decimal y valida rangos opcionales.
    
    Parámetros:
        prompt_text (str): texto a mostrar en los mensajes.
        min_value (float): valor mínimo que puede tener el número flotante
        max_value (float): valor máximo que puede tener el número flotante.
        allow_empty (bool): permitir que el campo sea opcional (por defecto false).

    Retorna:
        float: valor ingresado por el usuario de tipo flotante.
    """
    while True:
        value = input(prompt_text).strip()
        if allow_empty and value == "":
            return None
        
        if not validate_float(value):
            continue
        number = float(value)
        
        # Comprueba los posibles rangos antes de aceptar el valor.
        if min_value is not None and number < min_value:
            print(f"Error: el valor debe ser mayor o igual a {min_value}.")
            continue
        if max_value is not None and number > max_value:
            print(f"Error: el valor debe ser menor o igual a {max_value}.")
            continue
        
        return number


def _input_int(prompt_text, min_value=None, max_value=None, allow_empty=False):
    """
    Solicita un entero y valida rangos opcionales.
    
    Parámetros:
        prompt_text (str): texto a mostrar en los mensajes.
        min_value (int): valor mínimo que puede tener el número entero
        max_value (floatint): valor máximo que puede tener el número entero.
        allow_empty (bool): permitir que el campo sea opcional (por defecto false).

    Retorna:
        int: valor ingresado por el usuario de tipo entero.
    """
    while True:
        value = input(prompt_text).strip()
        
        if allow_empty and value == "":
            return None
        
        if not validate_integer(value):
            continue
        
        number = int(value)
        
        # Se asegura de respetar los límites definidos para el entero.
        if min_value is not None and number < min_value:
            print(f"Error: el valor debe ser mayor o igual a {min_value}.")
            continue
        
        if max_value is not None and number > max_value:
            print(f"Error: el valor debe ser menor o igual a {max_value}.")
            continue
        
        return number


def _input_optional_date(prompt_text):
    """
    Pide una fecha opcional en formato YYYY-MM-DD.
    
    Parámetros:
        prompt_text (str): texto a mostrar en los mensajes.
    
    Retorna:
        str: Devuelve un str con formato de fecha.
    
    """
    while True:
        value = input(prompt_text).strip()
        if value == "":
            return None
        # Solo se acepta la fecha si pasa la validación del módulo validators.
        if validate_date(value):
            return value


def _input_positive_int_with_default(prompt_text, default_value):
    """Pide un entero positivo permitiendo usar un valor por defecto."""
    while True:
        value = input(prompt_text).strip()
        if value == "":
            return default_value
        if validate_integer(value) and int(value) > 0:
            return int(value)
        print("Error: ingresa un número entero mayor que 0.")


def _input_date_with_current(prompt_text, current_value):
    """Solicita una fecha permitiendo conservar la anterior."""
    while True:
        value = input(prompt_text).strip()
        if value == "":
            return current_value
        if validate_date(value):
            return value


def _input_optional_integer(prompt_text):
    """Devuelve un entero opcional."""
    while True:
        value = input(prompt_text).strip()
        if value == "":
            return None
        if validate_integer(value):
            return int(value)


def _input_int_with_default(prompt_text, default_value, min_value=None, max_value=None):
    """Solicita un entero permitiendo conservar el valor anterior."""
    while True:
        value = input(prompt_text).strip()
        if value == "":
            return default_value
        if not validate_integer(value):
            continue
        number = int(value)
        if min_value is not None and number < min_value:
            print(f"Error: el valor debe ser mayor o igual a {min_value}.")
            continue
        if max_value is not None and number > max_value:
            print(f"Error: el valor debe ser menor o igual a {max_value}.")
            continue
        return number


def _input_float_with_default(prompt_text, default_value, min_value=None, max_value=None):
    """Solicita un float permitiendo conservar el valor anterior."""
    while True:
        value = input(prompt_text).strip()
        if value == "":
            return default_value
        if not validate_float(value):
            continue
        number = float(value)
        if min_value is not None and number < min_value:
            print(f"Error: el valor debe ser mayor o igual a {min_value}.")
            continue
        if max_value is not None and number > max_value:
            print(f"Error: el valor debe ser menor o igual a {max_value}.")
            continue
        return number


def _input_nullable_float_with_default(prompt_text, default_value, min_value=None, max_value=None):
    """Solicita un float opcional; 'none' limpia el valor."""
    while True:
        value = input(prompt_text).strip()
        if value == "":
            return default_value
        if value.lower() == "none":
            return None
        if not validate_float(value):
            continue
        number = float(value)
        if min_value is not None and number < min_value:
            print(f"Error: el valor debe ser mayor o igual a {min_value}.")
            continue
        if max_value is not None and number > max_value:
            print(f"Error: el valor debe ser menor o igual a {max_value}.")
            continue
        return number


def _input_nullable_int_with_default(prompt_text, default_value, min_value=None, max_value=None):
    """Solicita un entero opcional; 'none' limpia el valor."""
    while True:
        value = input(prompt_text).strip()
        if value == "":
            return default_value
        if value.lower() == "none":
            return None
        if not validate_integer(value):
            continue
        number = int(value)
        if min_value is not None and number < min_value:
            print(f"Error: el valor debe ser mayor o igual a {min_value}.")
            continue
        if max_value is not None and number > max_value:
            print(f"Error: el valor debe ser menor o igual a {max_value}.")
            continue
        return number


def _input_text_with_default(prompt_text, default_value, allow_clear=False):
    """Solicita texto permitiendo conservar o limpiar ('none')."""
    value = input(prompt_text).strip()
    if value == "":
        return default_value
    if allow_clear and value.lower() == "none":
        return ""
    return value


def _build_physical_activity():
    """Construye el texto de actividad fisica combinando tipo y duracion."""
    activity_type = input("Actividad fisica (tipo, ejemplo: correr, yoga, ninguna): ").strip()
    if activity_type == "":
        activity_type = "Sin actividad"
    duration = _input_float("Duración de la actividad (minutos, 0 si ninguna): ", min_value=0)
    if duration == 0 and activity_type.lower() in ["sin actividad", "ninguna", "no", "ningun"]:
        return "Sin actividad registrada"
    return f"{activity_type} - {duration} minutos"


def _build_food_entry():
    """Construye el texto de alimentación, agregando foto opcional."""
    while True:
        food_desc = input("Alimentación (descripción breve): ").strip()
        if validate_not_empty(food_desc):
            break
    photo = input("Foto opcional (ruta o URL, deja vacío si no aplica): ").strip()
    if photo == "":
        return food_desc
    return f"{food_desc} | Foto: {photo}"

def record_daily_health_data(mysql_conn, user):
    """
    Permite a un usuario registrar un nuevo registro diario de salud.

    Solicita los campos requeridos y opcionales, valida rangos y guarda el
    registro mediante mysql_connection.register_daily_record.
    """
    user_id = user[0]
    print("\nRegistro diario de salud")

    record_date = _input_date_with_default()
    sleep_hours = _input_float("Horas de sueno (0 a 24): ", min_value=0, max_value=24)

    while True:
        mood_value = input("Estado de animo (1-10): ").strip()
        if validate_integer(mood_value) and validate_range(mood_value, 1, 10):
            mood = int(mood_value)
            break

    physical_activity = _build_physical_activity()
    food = _build_food_entry()
    symptoms = input("Sintomas (dolor, fatiga, etc.) [opcional]: ").strip() or "Sin sintomas reportados"
    blood_pressure = input("Presion arterial (ejemplo 120/80) [opcional]: ").strip() or "N/A"
    glucose = _input_float("Glucosa (mg/dL) [opcional, deja vacio]: ", allow_empty=True)
    bpm = _input_int("Latidos por minuto (bpm) [opcional, deja vacio]: ", min_value=0, allow_empty=True)
    weight = _input_float("Peso (kg) [opcional, deja vacio]: ", min_value=0, allow_empty=True)

    saved = SQLC.register_daily_record(
        mysql_conn,
        user_id,
        record_date,
        sleep_hours,
        mood,
        physical_activity,
        food,
        symptoms,
        blood_pressure,
        glucose,
        bpm,
        weight,
    )

    if saved:
        print("Registro diario guardado correctamente.")
    else:
        print("No se pudo guardar el registro. Intenta nuevamente.")


def view_daily_health_records(mysql_conn, user):
    """
    Muestra los registros diarios de salud del usuario autenticado.
    """
    user_id = user[0]

    if not SQLC.has_permission(mysql_conn, user_id, "view_health_records"):
        print("No tienes permiso para ver registros de salud.")
        return

    print("\n--- Mis registros diarios de salud ---")
    start_date = _input_optional_date("Filtrar desde fecha (YYYY-MM-DD) [opcional]: ")
    end_date = _input_optional_date("Filtrar hasta fecha (YYYY-MM-DD) [opcional]: ")
    limit = _input_positive_int_with_default(
        "Cantidad máxima de registros a mostrar [por defecto 10]: ",
        default_value=10,
    )

    records = SQLC.get_daily_records(
        mysql_conn,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    if not records:
        print("No se encontraron registros diarios con los filtros indicados.")
        return

    for record in records:
        date = record.get("date")
        sleep_hours = record.get("sleep_hours")
        mood = record.get("mood")
        physical_activity = record.get("physical_activity") or "Sin actividad registrada"
        food = record.get("food") or "Sin registro de alimentación"
        symptoms = record.get("symptoms") or "Sin síntomas reportados"
        blood_pressure = record.get("blood_pressure") or "N/A"
        glucose = record.get("glucose")
        bpm = record.get("bpm")
        weight = record.get("weight")

        print(f"* {date} | Sueño: {sleep_hours} h | Ánimo: {mood}")
        print(f"  Actividad: {physical_activity}")
        print(f"  Alimentación: {food}")
        print(f"  Síntomas: {symptoms}")
        print(
            "  Signos vitales -> "
            f"Presión: {blood_pressure} | "
            f"Glucosa: {glucose if glucose is not None else 'N/A'} | "
            f"BPM: {bpm if bpm is not None else 'N/A'} | "
            f"Peso: {weight if weight is not None else 'N/A'}"
        )
        print("")


def _calculate_metric_trend(values, tolerance):
    """Calcula la tendencia entre la mitad inicial y final."""
    if len(values) < 2:
        return None
    midpoint = len(values) // 2
    first_half = values[:midpoint]
    second_half = values[midpoint:]
    if not first_half or not second_half:
        return None
    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)
    delta = round(second_avg - first_avg, 2)

    if abs(delta) <= tolerance:
        direction = "estable"
    elif delta > 0:
        direction = "al alza"
    else:
        direction = "a la baja"

    return direction, round(second_avg, 2), delta


def _analyze_metric_trends(records):
    """Construye un resumen de tendencias para métricas clave."""
    metrics = {
        "weight": {"label": "Peso", "tolerance": 0.3},
        "glucose": {"label": "Glucosa", "tolerance": 5},
        "mood": {"label": "Estado de ánimo", "tolerance": 0.5},
        "sleep_hours": {"label": "Horas de sueño", "tolerance": 0.4},
        "bpm": {"label": "Latidos por minuto", "tolerance": 2},
    }

    trends = {}

    for field, props in metrics.items():
        values = [
            float(record[field])
            for record in records
            if record.get(field) is not None
        ]
        if not values:
            trends[props["label"]] = "Sin datos suficientes."
            continue

        result = _calculate_metric_trend(values, props["tolerance"])
        if not result:
            trends[props["label"]] = "Sin datos suficientes."
            continue

        direction, avg_value, delta = result
        if direction == "estable":
            trends[props["label"]] = f"Tendencia estable (~{avg_value})"
        elif direction == "al alza":
            trends[props["label"]] = f"{direction} (+{delta}) promedio reciente {avg_value}"
        else:
            trends[props["label"]] = f"{direction} ({delta}) promedio reciente {avg_value}"

    return trends


def _detect_behavior_patterns(records):
    """Detecta patrones sencillos a partir de los registros."""
    patterns = []

    low_sleep_bad_mood = sum(
        1
        for record in records
        if record.get("sleep_hours") is not None
        and record.get("sleep_hours") < 6
        and record.get("mood") is not None
        and record.get("mood") <= 4
    )
    if low_sleep_bad_mood >= 3:
        patterns.append(
            "Se detecta que dormir menos de 6 horas se asocia con estados de ánimo bajos."
        )

    sedentary_days = sum(
        1
        for record in records
        if record.get("physical_activity")
        and "sin actividad" in record.get("physical_activity").lower()
    )
    weight_values = [
        float(record["weight"])
        for record in records
        if record.get("weight") is not None
    ]
    if (
        len(weight_values) >= 2
        and sedentary_days >= max(2, len(records) // 3)
        and (weight_values[-1] - weight_values[0]) >= 1
    ):
        patterns.append(
            "El peso ha aumentado mientras predominan días sin actividad física."
        )

    repeated_glucose_high = sum(
        1
        for record in records
        if record.get("glucose") is not None and record.get("glucose") >= 130
    )
    if repeated_glucose_high >= 3:
        patterns.append(
            "Se observan valores frecuentes de glucosa elevados. Revisa tu alimentación."
        )

    return patterns


def _parse_blood_pressure(value):
    """Devuelve tupla (sistólica, diastólica) si es posible."""
    if not value or "/" not in value:
        return None, None
    try:
        systolic, diastolic = value.split("/", 1)
        return int(systolic.strip()), int(diastolic.strip())
    except ValueError:
        return None, None


def _has_consecutive_condition(records, required_days, predicate):
    """Verifica si la condición se cumple en días consecutivos."""
    counter = 0
    for record in records:
        if predicate(record):
            counter += 1
            if counter >= required_days:
                return True
        else:
            counter = 0
    return False


def generate_alerts(records):
    """Genera alertas basadas en los registros más recientes."""
    alerts = []
    if not records:
        return alerts

    # Se define cada regla como una función para reutilizarlas en el evaluador genérico.
    def high_pressure(record):
        systolic, diastolic = _parse_blood_pressure(record.get("blood_pressure"))
        if systolic is None or diastolic is None:
            return False
        return systolic >= 130 or diastolic >= 85

    # Se dispara una alerta si hay al menos 3 días seguidos con la condición.
    if _has_consecutive_condition(records, 3, high_pressure):
        alerts.append("Tres días consecutivos con presión arterial elevada.")

    def high_glucose(record):
        value = record.get("glucose")
        return value is not None and value >= 130

    if _has_consecutive_condition(records, 3, high_glucose):
        alerts.append("Tres días seguidos con glucosa elevada. Considera consultar al médico.")

    def low_sleep(record):
        value = record.get("sleep_hours")
        return value is not None and value < 5

    # Cada bloque añade un mensaje distinto según el tipo de patrón detectado.
    if _has_consecutive_condition(records, 3, low_sleep):
        alerts.append("Pocas horas de sueño durante tres días consecutivos.")

    def tachycardia(record):
        value = record.get("bpm")
        return value is not None and value >= 100

    if _has_consecutive_condition(records, 2, tachycardia):
        alerts.append("Dos días seguidos con ritmo cardiaco elevado.")

    return alerts


def build_health_analysis(records):
    """Crea un resumen estructurado con tendencias, patrones y alertas."""
    return {
        "trends": _analyze_metric_trends(records),
        "patterns": _detect_behavior_patterns(records),
        "alerts": generate_alerts(records),
    }


def display_health_analysis(analysis, title):
    """Imprime un análisis en consola."""
    print(f"\nAnálisis de salud: {title}")
    print("Tendencias:")
    for metric, summary in analysis["trends"].items():
        print(f"  • {metric}: {summary}")

    print("\nPatrones detectados:")
    if analysis["patterns"]:
        for pattern in analysis["patterns"]:
            print(f"  • {pattern}")
    else:
        print("  • Sin patrones significativos.")

    print("\nAlertas:")
    if analysis["alerts"]:
        for alert in analysis["alerts"]:
            print(f"  • {alert}")
    else:
        print("  • No se detectaron alertas recientes.")


def view_health_analysis(mysql_conn, user):
    """Muestra el análisis personalizado para el usuario autenticado."""
    user_id = user[0]

    if not SQLC.has_permission(mysql_conn, user_id, "view_health_records"):
        print("No tienes permiso para ver análisis de salud.")
        return

    records = SQLC.get_daily_records_for_analysis(mysql_conn, user_id, limit=14)
    if not records:
        print("Aún no hay registros suficientes para generar un análisis.")
        return

    analysis = build_health_analysis(records)
    display_health_analysis(analysis, f"{user[1]} (últimos {len(records)} registros)")


def _prompt_keyword():
    """Solicita una palabra clave para filtrar texto en registros/notas."""
    text = input("Palabra clave (actividad, comida, síntomas) [opcional]: ").strip()
    return text if text != "" else None


def _prompt_symptom_filter():
    """Pregunta si se quiere limitar la búsqueda por presencia de síntomas."""
    print("Filtrar por síntomas:")
    print("1. Todos")
    print("2. Solo con síntomas")
    print("3. Solo sin síntomas")
    option = get_menu_option(3)
    if option == 2:
        return True
    if option == 3:
        return False
    return None


def _prompt_mood_range():
    """Define el rango opcional de estado de ánimo a aplicar en los filtros."""
    min_mood = _input_optional_integer("Estado de ánimo mínimo (1-10) [opcional]: ")
    max_mood = _input_optional_integer("Estado de ánimo máximo (1-10) [opcional]: ")
    return min_mood, max_mood


def _prompt_tags_list():
    """Obtiene una lista de etiquetas a partir de texto separado por comas."""
    raw = input("Etiquetas separadas por coma [opcional]: ").strip()
    if not raw:
        return []
    # Limpia espacios y descarta entradas vacías.
    return [tag.strip() for tag in raw.split(",") if tag.strip() != ""]


def search_records_and_notes(mysql_conn, mongo_db, user):
    """
    Permite buscar registros diarios o notas personales con filtros.
    """
    user_id = user[0]
    print("\nBúsqueda avanzada ---")
    print("1. Buscar en registros diarios")
    print("2. Buscar en notas personales")
    option = get_menu_option(2)

    date_from = _input_optional_date("Fecha desde (YYYY-MM-DD) [opcional]: ")
    date_to = _input_optional_date("Fecha hasta (YYYY-MM-DD) [opcional]: ")
    keyword = _prompt_keyword()
    min_mood, max_mood = _prompt_mood_range()

    if option == 1:
        symptom_filter = _prompt_symptom_filter()
        records = SQLC.search_daily_records(
            mysql_conn,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            keyword=keyword,
            mood_min=min_mood,
            mood_max=max_mood,
            has_symptoms=symptom_filter,
            limit=50,
        )
        if not records:
            print("No se encontraron registros con esos filtros.")
            return
        print(f"\nRegistros encontrados: {len(records)}")
        for rec in records:
            print(
                f"- {rec['date']} | Sueño: {rec.get('sleep_hours')} h | "
                f"Ánimo: {rec.get('mood')} | Actividad: {rec.get('physical_activity')}"
            )
            if rec.get("symptoms"):
                print(f"  Síntomas: {rec.get('symptoms')}")
            if rec.get("food"):
                print(f"  Alimentación: {rec.get('food')}")
    else:
        tags = _prompt_tags_list()
        notes = MONGOC.search_notes(
            mongo_db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            keyword=keyword,
            mood_min=min_mood,
            mood_max=max_mood,
            tags=tags,
            limit=30,
        )
        if not notes:
            print("No se encontraron notas con esos filtros.")
            return
        print(f"\nNotas encontradas: {len(notes)}")
        for note in notes:
            tags_str = ", ".join(note.get("tags") or []) or "Sin etiquetas"
            print(
                f"- {note.get('date')} | Ánimo: {note.get('mood', 'N/A')} | "
                f"{(note.get('text') or '')[:120]}"
            )
            print(f"  Etiquetas: {tags_str}")


def admin_view_health_analysis(mysql_conn):
    """Permite al administrador ver análisis para cualquier usuario."""
    user_id = _input_int("ID del usuario a analizar: ", min_value=1)
    user = SQLC.get_user_by_id(mysql_conn, user_id)
    if not user:
        print("No se encontró el usuario especificado.")
        return

    records = SQLC.get_daily_records_for_analysis(mysql_conn, user_id, limit=20)
    if not records:
        print("No hay registros suficientes para este usuario.")
        return

    analysis = build_health_analysis(records)
    display_health_analysis(analysis, f"{user['name']} (ID {user_id})")


def _prompt_report_timeframe():
    """Solicita al usuario si desea un reporte semanal o mensual."""
    
    print("\nSelecciona el tipo de reporte:")
    print("1. Resumen semanal (últimos 7 días)")
    print("2. Resumen mensual (últimos 30 días)")
    
    option = get_menu_option(2)
    return "weekly" if option == 1 else "monthly"


def _calculate_report_dates(timeframe):
    """Devuelve las fechas de inicio y fin según el tipo de reporte."""
    today = datetime.now().date()
    if timeframe == "weekly":
        start = today - timedelta(days=6)
    else:
        start = today - timedelta(days=29)
    return start.isoformat(), today.isoformat()


def _prompt_report_format():
    """Permite seleccionar el formato de salida."""
    print("\nFormato de exportación:")
    print("1. JSON")
    print("2. TXT")
    option = get_menu_option(2)
    return "json" if option == 1 else "txt"


def _average(values, decimals=2):
    """
    Permite calcular el pomedio a partir de una lista de valores numéricos. 
    Así mismo, se pasa por parámetro el número de decimales que se espera que tenga el número final.
    """
    if not values:
        return None
    return round(sum(values) / len(values), decimals)


def _format_optional_number(value):
    """Permite formatear un valor a un string, en donde si el valor es None, se guardara un N/A"""
    return f"{value:.2f}" if value is not None else "N/A"


def _ensure_date_str(value):
    """Convierte instancias date/datetime en cadenas con formato de fecha ISO."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _summarize_statistics(records):
    """
    Permite resumir las principales estadísticas de un usuario a partir de sus registros diarios.
    """
    # Calcula valores medios para cada métrica numérica disponible.
    stats = {
        "total_records": len(records),
        "avg_sleep_hours": _average([float(r["sleep_hours"]) for r in records if r.get("sleep_hours") is not None]),
        "avg_mood": _average([float(r["mood"]) for r in records if r.get("mood") is not None]),
        "avg_glucose": _average([float(r["glucose"]) for r in records if r.get("glucose") is not None]),
        "avg_weight": _average([float(r["weight"]) for r in records if r.get("weight") is not None]),
        "avg_bpm": _average([float(r["bpm"]) for r in records if r.get("bpm") is not None]),
    }

    # Determina los extremos de horas de sueño si hay datos suficientes.
    sleep_values = [float(r["sleep_hours"]) for r in records if r.get("sleep_hours") is not None]
    if sleep_values:
        stats["max_sleep_hour"] = max(sleep_values)
        stats["min_sleep_hour"] = min(sleep_values)

    # Registra los días con mejor y peor estado de ánimo.
    mood_entries = [r for r in records if r.get("mood") is not None]
    if mood_entries:
        best = max(mood_entries, key=lambda r: r["mood"])
        worst = min(mood_entries, key=lambda r: r["mood"])
        stats["best_mood_day"] = {
            "date": _ensure_date_str(best["date"]),
            "value": best["mood"]
        }
        stats["worst_mood_day"] = {
            "date": _ensure_date_str(worst["date"]),
            "value": worst["mood"]
        }

    # Conteo de días donde se reportaron síntomas relevantes.
    stats["symptomatic_days"] = sum(
        1
        for r in records
        if r.get("symptoms")
        and r["symptoms"].strip().lower() not in ("sin sintomas reportados", "sin sintomas", "n/a")
    )

    # Número de días con presión arterial elevada.
    stats["high_pressure_days"] = sum(
        1
        for r in records
        if (lambda bp: (bp[0] is not None and bp[0] >= 130) or (bp[1] is not None and bp[1] >= 85))(
            _parse_blood_pressure(r.get("blood_pressure"))
        )
    )

    return stats


def _prepare_notes_highlights(notes, limit=3):
    """Permite obtener las partes principales a partir de las notas ingresadas por el usuario"""
    highlights = []
    for note in notes[:limit]:
        highlights.append({
            "date": _ensure_date_str(note.get("date")),
            "text": (note.get("text") or "")[:200],
            "mood": note.get("mood"),
            "tags": note.get("tags") or [],
        })
    return highlights


def _build_report_payload(user_info, timeframe, start_date, end_date, records, notes):
    """Permite construir los reportes solicitados por el usuario, los cuales se entregaran en formato JSON o TXT en la carpeta de reportes"""
    stats = _summarize_statistics(records)
    highlights = _prepare_notes_highlights(notes)

    # Estructura completa que se exportará a JSON o TXT.
    report = {
        "user": user_info,
        "timeframe": timeframe,
        "start_date": start_date,
        "end_date": end_date,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "stats": stats,
        "notes_highlights": highlights,
        "alerts": generate_alerts(records),
        "total_notes_considered": len(notes),
    }

    if stats["total_records"] == 0:
        report["summary"] = "No se registraron datos en el periodo seleccionado."
    else:
        # Resumen textual con los datos más útiles para el usuario.
        avg_mood = stats["avg_mood"]
        mood_text = f"{avg_mood:.2f}" if avg_mood is not None else "N/A"
        report["summary"] = (
            f"Se registraron {stats['total_records']} eventos. "
            f"Promedio de estado de ánimo: {mood_text}. "
            f"Alertas detectadas: {len(report['alerts'])}."
        )

    return report


def _render_report_txt(report):
    """Permite exportar en un archivo TXT el reporte solicitado por el usuario, destacando las partes principales de este:
        - Total registros
        - Promedio horas de sueño
        - Promedio estado de ánimo
        - Promedio glucosa
        - Promedio peso
        - Promedio BPM
        - Días con síntomas
        - Días con presión alta
    """
    
    stats = report["stats"]
    lines = [
        f"Reporte de salud - {report['user']['name']} (ID {report['user']['id']})",
        f"Periodo: {report['start_date']} al {report['end_date']} ({report['timeframe']})",
        f"Generado: {report['generated_at']}",
        "",
        report["summary"],
        "",
        "Estadísticas:",
        f"  - Total registros: {stats['total_records']}",
        f"  - Promedio horas de sueño: {_format_optional_number(stats.get('avg_sleep_hours'))}",
        f"  - Promedio estado de ánimo: {_format_optional_number(stats.get('avg_mood'))}",
        f"  - Promedio glucosa: {_format_optional_number(stats.get('avg_glucose'))}",
        f"  - Promedio peso: {_format_optional_number(stats.get('avg_weight'))}",
        f"  - Promedio BPM: {_format_optional_number(stats.get('avg_bpm'))}",
        f"  - Días con síntomas: {stats.get('symptomatic_days', 0)}",
        f"  - Días con presión alta: {stats.get('high_pressure_days', 0)}",
    ]

    # Permite obtener el día en que el usuario tuvo el mejor estado de ánimo
    if stats.get("best_mood_day"):
        lines.append(
            f"  - Mejor estado de ánimo: {stats['best_mood_day']['value']} (fecha {stats['best_mood_day']['date']})"
        )
    
    # Permite obtener el día en que el usuario tuvo el pero estado de ánimo
    if stats.get("worst_mood_day"):
        lines.append(
            f"  - Peor estado de ánimo: {stats['worst_mood_day']['value']} (fecha {stats['worst_mood_day']['date']})"
        )

    lines.append("")
    lines.append("Notas destacadas:")
    if report["notes_highlights"]:
        for note in report["notes_highlights"]:
            tags = ", ".join(note["tags"]) if note["tags"] else "Sin etiquetas"
            lines.append(f"- {note['date']} | Ánimo: {note.get('mood', 'N/A')} | {note['text']}")
            lines.append(f"  Etiquetas: {tags}")
    else:
        lines.append("  No hay notas para este periodo.")

    lines.append("")
    lines.append("Alertas detectadas:")
    if report["alerts"]:
        for alert in report["alerts"]:
            lines.append(f"- {alert}")
    else:
        lines.append("  Sin alertas en este periodo.")

    return "\n".join(lines)


def _export_report_to_file(report_data, output_format):
    """
    Permite exportar un archivo sobre el reporte solicitado por el usuario, tanto en formato JSON como en formato TXT, de acuerdo a la opción seleccionada
    por el usuario.
    """
    # Asegura que la carpeta de reportes exista y define el nombre del archivo.
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    slug_date = report_data["end_date"].replace("-", "")
    filename = f"reporte_{report_data['user']['id']}_{report_data['timeframe']}_{slug_date}.{output_format}"
    filepath = REPORTS_DIR / filename

    if output_format == "json":
        # Exporta el archivo en formato JSON, con los principales datos estadísticos obtenidos del reporte del usuario.
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(report_data, file, ensure_ascii=False, indent=2)
    else:
        content = _render_report_txt(report_data)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

    return filepath


def _collect_report_data(mysql_conn, mongo_db, user_id, user_name, timeframe):
    """ Obtiene registros y notas dentro del rango requerido antes de construir el reporte."""
    start_date, end_date = _calculate_report_dates(timeframe)
    records = SQLC.get_daily_records_in_range(mysql_conn, user_id, start_date, end_date)

    notes = []
    if mongo_db is not None:
        notes = MONGOC.get_notes_in_range(mongo_db, user_id, start_date, end_date, limit=10)

    user_info = {"id": user_id, "name": user_name}
    return _build_report_payload(user_info, timeframe, start_date, end_date, records, notes)


def export_personal_report(mysql_conn, mongo_db, user):
    """Genera un reporte para el usuario autenticado con los últimos datos."""
    timeframe = _prompt_report_timeframe()
    output_format = _prompt_report_format()
    report_data = _collect_report_data(mysql_conn, mongo_db, user[0], user[1], timeframe)
    filepath = _export_report_to_file(report_data, output_format)
    print(f"\nReporte generado correctamente en: {filepath}")


def admin_export_user_report(mysql_conn, mongo_db):
    """Permite al administrador exportar reportes para cualquier usuario."""
    user_id = _input_int("ID del usuario para exportar el reporte: ", min_value=1)
    user = SQLC.get_user_by_id(mysql_conn, user_id)
    if not user:
        print("No se encontró el usuario indicado.")
        return

    timeframe = _prompt_report_timeframe()
    output_format = _prompt_report_format()
    report_data = _collect_report_data(mysql_conn, mongo_db, user_id, user["name"], timeframe)
    filepath = _export_report_to_file(report_data, output_format)
    print(f"\nReporte del usuario {user['name']} guardado en: {filepath}")


def run_alerts_for_all_users(mysql_conn):
    """Ejecuta las alertas para todos los usuarios registrados."""
    if mysql_conn is None:
        return

    user_ids = SQLC.get_all_user_ids(mysql_conn)
    for user_id in user_ids:
        records = SQLC.get_daily_records_for_analysis(mysql_conn, user_id, limit=10)
        if not records:
            continue

        alerts = generate_alerts(records)
        if not alerts:
            continue

        user = SQLC.get_user_by_id(mysql_conn, user_id)
        user_name = user["name"] if user else f"Usuario {user_id}"
        print(f"\n[ALERTA AUTOMÁTICA] {user_name} (ID {user_id})")
        for alert in alerts:
            print(f"  - {alert}")


def start_automatic_alerts(mysql_conn, interval_seconds=ALERT_INTERVAL_SECONDS):
    """Inicia un hilo en segundo plano para generar alertas periódicas."""
    global ALERT_THREAD, ALERT_STOP_EVENT

    if mysql_conn is None:
        return

    if ALERT_THREAD and ALERT_THREAD.is_alive():
        return

    ALERT_STOP_EVENT = threading.Event()

    def _worker():
        while not ALERT_STOP_EVENT.is_set():
            run_alerts_for_all_users(mysql_conn)
            ALERT_STOP_EVENT.wait(interval_seconds)

    ALERT_THREAD = threading.Thread(target=_worker, daemon=True)
    ALERT_THREAD.start()


def stop_automatic_alerts():
    """Detiene el hilo de alertas automáticas."""
    global ALERT_THREAD, ALERT_STOP_EVENT

    if ALERT_STOP_EVENT:
        ALERT_STOP_EVENT.set()

    if ALERT_THREAD:
        ALERT_THREAD.join(timeout=1)

    ALERT_THREAD = None
    ALERT_STOP_EVENT = None


def _parse_list_from_input(raw_text):
    """Convierte una entrada separada por comas en lista limpia."""
    if not raw_text:
        return []
    return [item.strip() for item in raw_text.split(",") if item.strip() != ""]


def _parse_metadata_input(raw_text):
    """Convierte texto clave=valor en un diccionario."""
    metadata = {}
    if not raw_text:
        return metadata
    for pair in raw_text.split(","):
        if "=" in pair:
            key, val = pair.split("=", 1)
            key = key.strip()
            if key != "":
                metadata[key] = val.strip()
    return metadata


def record_personal_note(mongo_db, user):
    """
    Solicita los datos de una nota personal y la guarda en MongoDB.
    """
    if mongo_db is None:
        print("No hay conexión con MongoDB. Intenta más tarde.")
        return

    user_id = user[0]
    print("\nRegistrar nota personal")
    note_date = _input_date_with_default()
    note_text = input("Nota (texto libre): ").strip()
    if not validate_not_empty(note_text):
        return
    tags = _parse_list_from_input(input("Etiquetas separadas por coma [opcional]: "))
    mood  = _input_int("Estado de animo (1-10): ", min_value=1, max_value=10)
    attachments = _parse_list_from_input(input("Rutas de archivos separadas por coma [opcional]: "))
    while True:
        location = input("Ingrese su ubicación (Nombre de la ciudad, Departamento): ").strip()
        if validate_not_empty(location):
            break
    temperature = _input_int("Ingrese la temperatura de su ubicación:")
    while True:
        weather_condition= input("Ingrese la condición de la zona en la que se encuentra (ej, lluviozo, soleado, etc): ")
        if validate_not_empty(weather_condition):
            break
        
    result = MONGOC.add_personal_note(
        mongo_db,
        user_id=user_id,
        text=note_text,
        date=note_date,
        tags=tags,
        mood=mood,
        location=location,
        weather={
            "temperature": temperature,
            "condition": weather_condition
            },
        attachments=attachments,
    )

    if result:
        print("Nota guardada correctamente.")
    else:
        print("No se pudo guardar la nota.")


def record_attachment(mongo_db, user):
    """
    Solicita la información de un adjunto y lo guarda en MongoDB.
    """
    if mongo_db is None:
        print("No hay conexión con MongoDB. Intenta más tarde.")
        return

    user_id = user[0]
    print("\n--- Registrar archivo adjunto ---")
    attach_date = _input_date_with_default()
    file_path = input("Ruta del archivo (obligatorio): ").strip()
    if not validate_not_empty(file_path):
        return
    attachment_type = input("Tipo (imagen, pdf, captura, etc.) [opcional]: ").strip() or "general"
    tags = _parse_list_from_input(input("Etiquetas separadas por coma [opcional]: "))
    description = input("Descripción corta [opcional]: ").strip()
    metadata_input = input("Metadatos como clave=valor separados por coma [opcional]: ").strip()
    metadata = _parse_metadata_input(metadata_input)

    result = MONGOC.add_attachment(
        mongo_db,
        user_id=user_id,
        file_path=file_path,
        date=attach_date,
        attachment_type=attachment_type,
        tags=tags,
        description=description,
        metadata=metadata,
    )

    if result:
        print("Adjunto guardado correctamente.")
    else:
        print("No se pudo guardar el adjunto.")


def _prompt_basic_user_data(existing=None):
    """Solicita los datos básicos de un usuario."""
    if existing:
        name = _input_text_with_default(
            f"Nombre [{existing['name']}]: ",
            existing["name"]
        )
        age = _input_int_with_default(
            f"Edad [{existing['age']}]: ",
            existing["age"],
            min_value=0
        )
    else:
        while True:
            name = input("Nombre completo: ").strip()
            if validate_not_empty(name):
                break
        age = _input_int("Edad: ", min_value=0)

    while True:
        if existing:
            email_candidate = _input_text_with_default(
                f"Correo electrónico [{existing['email']}]: ",
                existing["email"]
            )
        else:
            email_candidate = input("Correo electrónico: ").strip()
        if not validate_not_empty(email_candidate):
            continue
        if validate_email(email_candidate):
            email = email_candidate
            break

    return {
        "name": name,
        "age": age,
        "email": email,
    }


def manage_admin_accounts(mysql_conn, mongo_db): # <--- Recibe mongo_db
    """Gestiona usuarios con rol de administrador."""
    # Abajo pasamos mongo_db a la siguiente funcion
    _manage_users_by_role(mysql_conn, mongo_db, "admin", "administrador", "administradores")


def manage_standard_users(mysql_conn, mongo_db): # <--- Recibe mongo_db
    """Gestiona usuarios con rol estándar."""
    # Abajo pasamos mongo_db a la siguiente funcion
    _manage_users_by_role(mysql_conn, mongo_db, "user", "usuario", "usuarios")


def _manage_users_by_role(mysql_conn, mongo_db, role_name, singular_label, plural_label):
    role_id = SQLC.get_role_id(mysql_conn, role_name)
    if role_id is None:
        print(f"No se encontró el rol '{role_name}' en la base de datos.")
        return

    while True:
        print(f"\nGestión de {plural_label}")
        print("1. Crear")
        print("2. Ver listado")
        print("3. Modificar")
        print("4. Eliminar")
        print("5. Volver")

        option = get_menu_option(5)

        if option == 1:
            _create_user_with_role(mysql_conn, role_id, singular_label)
        elif option == 2:
            _list_users_by_role(mysql_conn, role_name, plural_label)
        elif option == 3:
            _update_user_by_role(mysql_conn, role_id, role_name, singular_label)
        elif option == 4:
            # AQUÍ ESTABA EL ERROR: Ahora pasamos mongo_db correctamente
            _delete_user_by_role(mysql_conn, mongo_db, role_name, singular_label)
        elif option == 5:
            break

def _create_user_with_role(mysql_conn, role_id, singular_label):
    print(f"\nCrear {singular_label}")
    data = _prompt_basic_user_data()
    password = input("Contraseña temporal: ").strip()
    while not validate_not_empty(password):
        password = input("Contraseña temporal: ").strip()

    user_id = SQLC.register_user(
        mysql_conn,
        data["name"],
        data["age"],
        data["email"],
        role_id,
    )
    if user_id is None:
        print(f"No se pudo crear el {singular_label}.")
        return

    csv_result = CSVC.register_user(user_id, password)
    if csv_result:
        print(f"{singular_label.capitalize()} creado con ID {user_id}.")
    else:
        print(
            f"{singular_label.capitalize()} creado con ID {user_id}, "
            "pero no se pudo registrar su contraseña en el CSV."
        )


def _list_users_by_role(mysql_conn, role_name, plural_label):
    users = SQLC.get_users(mysql_conn, role_name=role_name)
    if not users:
        print(f"No hay {plural_label} registrados.")
        return

    print(f"\nListado de {plural_label}:")
    for user in users:
        print(
            f"ID {user['id']:>3} | Nombre: {user['name']} | "
            f"Edad: {user['age']} | Email: {user['email']}"
        )


def _get_user_for_role(mysql_conn, role_name, singular_label):
    user_id = _input_int(f"Ingresa el ID del {singular_label}: ", min_value=1)
    user = SQLC.get_user_by_id(mysql_conn, user_id)
    if not user or user["role_name"] != role_name:
        print(f"No se encontró un {singular_label} con ese ID.")
        return None
    return user


def _update_user_by_role(mysql_conn, role_id, role_name, singular_label):
    user = _get_user_for_role(mysql_conn, role_name, singular_label)
    if not user:
        return

    print(f"Editando {singular_label}: {user['name']} (ID {user['id']})")
    data = _prompt_basic_user_data(existing=user)
    updated = SQLC.update_user(
        mysql_conn,
        user["id"],
        data["name"],
        data["age"],
        data["email"],
        role_id,
    )
    if updated:
        print(f"{singular_label.capitalize()} actualizado correctamente.")
    else:
        print("No se pudieron guardar los cambios.")


"""def _delete_user_by_role(mysql_conn, role_name, singular_label):
    user = _get_user_for_role(mysql_conn, role_name, singular_label)
    if not user:
        return

    confirm = input(
        f"¿Estás seguro de eliminar al {singular_label} '{user['name']}'? (s/n): "
    ).strip().lower()
    if confirm != "s":
        print("Operación cancelada.")
        return

    deleted = SQLC.delete_user(mysql_conn, user["id"])
    if deleted:
        if hasattr(CSVC, "remove_user"):
            CSVC.remove_user(user["id"])
        print(f"{singular_label.capitalize()} eliminado correctamente.")
    else:
        print("No se pudo eliminar el registro.")"""


def _delete_user_by_role(mysql_conn, mongo_db, role_name, singular_label):
    user = _get_user_for_role(mysql_conn, role_name, singular_label)
    if not user:
        return

    confirm = input(
        f"¿Estás seguro de eliminar al {singular_label} '{user['name']}' y TODOS sus datos (SQL, CSV y Mongo)? (s/n): "
    ).strip().lower()
    if confirm != "s":
        print("Operación cancelada.")
        return

    # 1. Eliminar de MySQL (Usuarios y Registros Diarios)
    deleted_sql = SQLC.delete_user(mysql_conn, user["id"])
    
    if deleted_sql:
        # 2. Eliminar de CSV (Contraseñas)
        if hasattr(CSVC, "remove_user"):
            CSVC.remove_user(user["id"])
            
        # 3. Eliminar de MongoDB (Notas y Adjuntos)
        if mongo_db is not None:
             MONGOC.delete_user_data(mongo_db, user["id"])
             
        print(f"{singular_label.capitalize()} eliminado correctamente de todos los sistemas.")
    else:
        print("No se pudo eliminar el registro de la base de datos SQL.")


def admin_manage_daily_records(mysql_conn):
    """Submenú para gestionar registros diarios."""
    while True:
        print("\nGestión de registros diarios")
        print("1. Crear registro")
        print("2. Ver registros")
        print("3. Modificar registro")
        print("4. Eliminar registro")
        print("5. Volver")

        option = get_menu_option(5)

        if option == 1:
            _admin_create_daily_record(mysql_conn)
        elif option == 2:
            _admin_view_daily_records(mysql_conn)
        elif option == 3:
            _admin_edit_daily_record(mysql_conn)
        elif option == 4:
            _admin_delete_daily_record(mysql_conn)
        elif option == 5:
            break


def _admin_create_daily_record(mysql_conn):
    user_id = _input_int("ID del usuario para el registro: ", min_value=1)
    user = SQLC.get_user_by_id(mysql_conn, user_id)
    if not user:
        print("No se encontró el usuario.")
        return

    print(f"Creando registro para {user['name']} (ID {user['id']}).")
    user_tuple = (
        user["id"],
        user["name"],
        user["age"],
        user["email"],
        user["role_id"],
    )
    record_daily_health_data(mysql_conn, user_tuple)


def _admin_view_daily_records(mysql_conn):
    user_id = _input_optional_integer("Filtrar por ID de usuario [opcional]: ")
    limit = _input_positive_int_with_default(
        "Cantidad máxima de registros a mostrar [por defecto 20]: ",
        default_value=20,
    )
    records = SQLC.get_daily_records_admin(mysql_conn, user_id=user_id, limit=limit)
    if not records:
        print("No hay registros que coincidan con el filtro.")
        return

    print("\nRegistros diarios:")
    for record in records:
        date = record.get("date")
        print(
            f"ID {record['id']} | Usuario {record['user_name']} (ID {record['user_id']}) "
            f"| Fecha: {date}"
        )
        print(
            f"  Sueño: {record.get('sleep_hours')} h, Ánimo: {record.get('mood')}"
        )
        print(f"  Actividad: {record.get('physical_activity')}")
        print(f"  Alimentación: {record.get('food')}")
        print(f"  Síntomas: {record.get('symptoms')}")
        print(
            "  Signos vitales -> "
            f"Presión: {record.get('blood_pressure')} | "
            f"Glucosa: {record.get('glucose')} | "
            f"BPM: {record.get('bpm')} | "
            f"Peso: {record.get('weight')}"
        )


def _admin_edit_daily_record(mysql_conn):
    record_id = _input_int("ID del registro a modificar: ", min_value=1)
    record = SQLC.get_daily_record_by_id(mysql_conn, record_id)
    if not record:
        print("No se encontró el registro.")
        return

    print(
        f"Editando registro {record_id} del usuario {record['user_name']} "
        f"(ID {record['user_id']})."
    )

    new_date = _input_date_with_current(
        f"Fecha (YYYY-MM-DD) [actual {record['date']}]: ",
        str(record["date"]),
    )
    sleep_hours = _input_float_with_default(
        f"Horas de sueño [actual {record['sleep_hours']}]: ",
        float(record["sleep_hours"]),
        min_value=0,
        max_value=24,
    )
    mood = _input_int_with_default(
        f"Estado de ánimo (1-10) [actual {record['mood']}]: ",
        int(record["mood"]),
        min_value=1,
        max_value=10,
    )
    physical_activity = _input_text_with_default(
        f"Actividad física [actual: {record.get('physical_activity') or 'Sin dato'}]: ",
        record.get("physical_activity") or "",
        allow_clear=True,
    )
    food = _input_text_with_default(
        f"Alimentación [actual: {record.get('food') or 'Sin dato'}]: ",
        record.get("food") or "",
        allow_clear=True,
    )
    symptoms = _input_text_with_default(
        f"Síntomas [actual: {record.get('symptoms') or 'Sin dato'}]: ",
        record.get("symptoms") or "",
        allow_clear=True,
    )
    blood_pressure = _input_text_with_default(
        f"Presión arterial [actual: {record.get('blood_pressure') or 'N/A'}]: ",
        record.get("blood_pressure") or "",
        allow_clear=True,
    )
    glucose = _input_nullable_float_with_default(
        f"Glucosa (mg/dL) [actual {record.get('glucose')} | 'none' para limpiar]: ",
        record.get("glucose"),
        min_value=0,
    )
    bpm = _input_nullable_int_with_default(
        f"BPM [actual {record.get('bpm')} | 'none' para limpiar]: ",
        record.get("bpm"),
        min_value=0,
    )
    weight = _input_nullable_float_with_default(
        f"Peso (kg) [actual {record.get('weight')} | 'none' para limpiar]: ",
        record.get("weight"),
        min_value=0,
    )

    updates = {
        "date": new_date,
        "sleep_hours": sleep_hours,
        "mood": mood,
        "physical_activity": physical_activity,
        "food": food,
        "symptoms": symptoms,
        "blood_pressure": blood_pressure,
        "glucose": glucose,
        "bpm": bpm,
        "weight": weight,
    }
    saved = SQLC.update_daily_record(mysql_conn, record_id, updates)
    if saved:
        print("Registro actualizado correctamente.")
    else:
        print("No se pudo actualizar el registro.")


def _admin_delete_daily_record(mysql_conn):
    record_id = _input_int("ID del registro a eliminar: ", min_value=1)
    record = SQLC.get_daily_record_by_id(mysql_conn, record_id)
    if not record:
        print("No se encontró el registro.")
        return

    confirm = input(
        f"¿Eliminar registro {record_id} del usuario {record['user_name']}? (s/n): "
    ).strip().lower()
    if confirm != "s":
        print("Operación cancelada.")
        return

    deleted = SQLC.delete_daily_record(mysql_conn, record_id)
    if deleted:
        print("Registro eliminado.")
    else:
        print("No se pudo eliminar el registro.")


def admin_manage_files(mongo_db):
    """Submenú para gestionar archivos personales."""
    if mongo_db is None:
        print("No hay conexión con MongoDB.")
        return

    while True:
        print("\nGestión de archivos personales")
        print("1. Crear archivo")
        print("2. Ver archivos")
        print("3. Modificar archivo")
        print("4. Eliminar archivo")
        print("5. Volver")

        option = get_menu_option(5)

        if option == 1:
            _admin_create_attachment(mongo_db)
        elif option == 2:
            _admin_view_attachments(mongo_db)
        elif option == 3:
            _admin_update_attachment(mongo_db)
        elif option == 4:
            _admin_delete_attachment(mongo_db)
        elif option == 5:
            break


def _admin_create_attachment(mongo_db):
    user_id = _input_int("ID del usuario para el archivo: ", min_value=1)
    attach_date = _input_date_with_default()
    file_path = input("Ruta del archivo: ").strip()
    if not validate_not_empty(file_path):
        return
    attachment_type = input("Tipo (imagen, pdf, etc.) [opcional]: ").strip() or "general"
    tags = _parse_list_from_input(input("Etiquetas separadas por coma [opcional]: "))
    description = input("Descripción [opcional]: ").strip()
    metadata_text = input("Metadatos clave=valor separados por coma [opcional]: ").strip()
    metadata = _parse_metadata_input(metadata_text)

    result = MONGOC.add_attachment(
        mongo_db,
        user_id=user_id,
        file_path=file_path,
        date=attach_date,
        attachment_type=attachment_type,
        tags=tags,
        description=description,
        metadata=metadata,
    )
    if result:
        print(f"Adjunto creado con ID {result}.")
    else:
        print("No se pudo crear el adjunto.")


def _admin_view_attachments(mongo_db):
    user_id = _input_optional_integer("Filtrar por ID de usuario [opcional]: ")
    limit = _input_positive_int_with_default(
        "Cantidad máxima de archivos [por defecto 20]: ",
        default_value=20,
    )
    attachments = MONGOC.get_attachments(mongo_db, user_id=user_id, limit=limit)
    if not attachments:
        print("No hay archivos registrados.")
        return

    print("\nArchivos personales:")
    for item in attachments:
        tags = ", ".join(item.get("tags") or []) or "Sin etiquetas"
        print(
            f"ID {item.get('_id')} | Usuario {item.get('user_id')} "
            f"| Fecha: {item.get('date')} | Tipo: {item.get('type')}"
        )
        print(f"  Ruta: {item.get('file_path')}")
        print(f"  Descripción: {item.get('description') or 'Sin descripción'}")
        print(f"  Etiquetas: {tags}")
        metadata = item.get("metadata") or {}
        if metadata:
            print(f"  Metadatos: {metadata}")


def _admin_update_attachment(mongo_db):
    attachment_id = input("ID del archivo a modificar: ").strip()
    attachment = MONGOC.get_attachment_by_id(mongo_db, attachment_id)
    if not attachment:
        print("No se encontró el archivo.")
        return

    print(f"Editando archivo {attachment_id} del usuario {attachment.get('user_id')}.")
    user_id = _input_int_with_default(
        f"ID de usuario [actual {attachment.get('user_id')}]: ",
        attachment.get("user_id"),
        min_value=1,
    )
    date_value = _input_date_with_current(
        f"Fecha (YYYY-MM-DD) [actual {attachment.get('date')}]: ",
        attachment.get("date"),
    )
    file_path = _input_text_with_default(
        f"Ruta del archivo [actual: {attachment.get('file_path')}]: ",
        attachment.get("file_path"),
    )
    attachment_type = _input_text_with_default(
        f"Tipo [actual: {attachment.get('type')}]: ",
        attachment.get("type"),
    )
    description = _input_text_with_default(
        f"Descripción [actual: {attachment.get('description') or 'Sin descripción'}]: ",
        attachment.get("description") or "",
        allow_clear=True,
    )

    current_tags = ", ".join(attachment.get("tags") or [])
    tags_input = input(
        f"Etiquetas separadas por coma [actual: {current_tags or 'Sin etiquetas'} | '-' para limpiar]: "
    ).strip()
    if tags_input == "":
        tags = attachment.get("tags") or []
    elif tags_input == "-":
        tags = []
    else:
        tags = _parse_list_from_input(tags_input)

    metadata_current = attachment.get("metadata") or {}
    metadata_text = input(
        "Metadatos clave=valor [deja vacío para conservar, '-' para limpiar]: "
    ).strip()
    if metadata_text == "":
        metadata = metadata_current
    elif metadata_text == "-":
        metadata = {}
    else:
        metadata = _parse_metadata_input(metadata_text)

    updates = {
        "user_id": user_id,
        "date": date_value,
        "file_path": file_path,
        "type": attachment_type,
        "description": description,
        "tags": tags,
        "metadata": metadata,
    }

    updated = MONGOC.update_attachment(mongo_db, attachment_id, updates)
    if updated:
        print("Archivo actualizado correctamente.")
    else:
        print("No se pudo actualizar el archivo.")


def _admin_delete_attachment(mongo_db):
    attachment_id = input("ID del archivo a eliminar: ").strip()
    attachment = MONGOC.get_attachment_by_id(mongo_db, attachment_id)
    if not attachment:
        print("No se encontró el archivo.")
        return

    confirm = input(
        f"¿Eliminar el archivo {attachment_id} del usuario {attachment.get('user_id')}? (s/n): "
    ).strip().lower()
    if confirm != "s":
        print("Operación cancelada.")
        return

    deleted = MONGOC.delete_attachment(mongo_db, attachment_id)
    if deleted:
        print("Archivo eliminado.")
    else:
        print("No se pudo eliminar el archivo.")

def main_menu(connections):
    """
    Muestra el menú principal de la aplicación.

    Opciones:
        1. Iniciar sesión
        2. Registrarse
        3. Salir
        4. Cargar datos de ejemplo (si las bases de datos están vacía)

    Parámetros:
        connections (dict): diccionario con las conexiones a MySQL y MongoDB.
    """
    mysql_conn = connections["mysql"]
    mongo_db = connections["mongo"]  # Reservado para futuras funcionalidades.

    while True:
        print("\nMenú Principal")
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("3. Salir")
        print("4. Cargar datos de ejemplo (En el caso que las bases de datos esten vacías)")

        option = get_menu_option(4)

        if option == 1:
            handle_login(mysql_conn, mongo_db)
        elif option == 2:
            register_new_user(mysql_conn)
        elif option == 3:
            print("\nSaliendo de la aplicación. ¡Hasta luego!")
            break
        elif option == 4:
            print("\nCreando tablas e insertando valores de prueba (si procede)")
            
            # Crear tablas y colecciones (si no existen)
            SQLC.create_tables(mysql_conn)
            
            # Evitar insertar datos si ya hay registros.
            if SQLC.has_existing_data(mysql_conn):
                print("ℹ Se detectaron datos existentes. No se insertaron datos de ejemplo en MySQL.")
            else:
                SQLC.insert_sample_data(mysql_conn)
                # Generar contraseñas simples para los usuarios cargados.
                user_ids = SQLC.get_all_user_ids(mysql_conn)
                password_map = {uid: "1234" for uid in user_ids}
                if password_map:
                    CSVC.seed_passwords(password_map)
                print("Datos de ejemplo y contraseñas cargados en MySQL/CSV.")
                
            MONGOC.create_collections(mongo_db)
            
            # Datos de MongoDB: solo si las colecciones están vacías.
            if mongo_db is not None:
                if MONGOC.has_existing_data(mongo_db):
                    print("ℹ Colecciones de MongoDB ya contienen datos. No se insertaron ejemplos.")
                else:
                    MONGOC.insert_sample_data(mongo_db)
                    print("Datos de ejemplo insertados en MongoDB.")


def handle_login(mysql_conn, mongo_db):
    """
    Maneja el proceso de inicio de sesión.

    Solicita al usuario:
        - Correo electrónico
        - Contraseña

    Luego delega la validación en la función validate_login del módulo auth_manager.

    Si el inicio de sesión es exitoso:
        - Obtiene el rol del usuario.
        - Redirige al menú correspondiente (admin o usuario).

    Parámetros:
        mysql_conn: conexión MySQL activa.
        mongo_db: conexión a MongoDB (por ahora no se usa en login).
    """
    print("\nInicio de sesión")
    email = input("Correo electrónico: ")
    while not validate_not_empty(email):
        email = input("Correo electrónico: ")

    password = input("Contraseña: ")
    while not validate_not_empty(password):
        password = input("Contraseña: ")

    user = validate_login(mysql_conn, email, password)

    if not user:
        print("Credenciales inválidas. Verifica tu correo y contraseña.")
        return

    # La tabla users tiene la estructura:
    # id, name, age, email, role_id
    user_id = user[0]
    user_name = user[1]
    role_id = user[4]

    print(f"\nInicio de sesión exitoso. Bienvenido/a, {user_name} (ID: {user_id})")

    # Redirigir según el rol
    if role_id == 1:
        admin_menu(mysql_conn, mongo_db, user)
    else:
        user_menu(mysql_conn, mongo_db, user)


def register_new_user(mysql_conn):
    """Permite que un visitante cree una cuenta básica de usuario."""
    if mysql_conn is None:
        print("No hay conexión con la base de datos. Intenta más tarde.")
        return

    print("\nRegistro de nuevo ususario")
    while True:
        name = input("Nombre completo: ").strip()
        if validate_not_empty(name):
            break

    age = _input_int("Edad: ", min_value=0)

    while True:
        email = input("Correo electrónico: ").strip()
        if not validate_not_empty(email):
            continue
        if not validate_email(email):
            continue
        # Verificar que no exista otro usuario registrado con el mismo correo.
        existing = SQLC.obtain_user_from_email(mysql_conn, email)
        if existing is not None:
            print("Ya existe una cuenta asociada a este correo.")
            continue
        break

    while True:
        password = input("Contraseña: ").strip()
        if not validate_not_empty(password):
            continue
        confirm = input("Confirma la contraseña: ").strip()
        if password != confirm:
            print("Las contraseñas no coinciden. Intenta de nuevo.")
            continue
        break

    role_id = SQLC.get_role_id(mysql_conn, "user")
    if role_id is None:
        print("No se encontró el rol de usuario estándar. Contacta al administrador.")
        return

    user_id = SQLC.register_user(mysql_conn, name, age, email, role_id)
    if user_id is None:
        print("No se pudo crear el usuario. Intenta nuevamente.")
        return

    if CSVC.register_user(user_id, password):
        print("\nUsuario registrado exitosamente. Ya puedes iniciar sesión.")
    else:
        print(
            "\nEl usuario se creó, pero hubo un error al guardar la contraseña en el CSV. "
            "Contacta al administrador."
        )

# MENÚS ESPECÍFICOS POR ROL

def admin_menu(mysql_conn, mongo_db, user):
    """
    Muestra el menú para usuarios con rol de administrador.

    Parámetros:
        mysql_conn: conexión MySQL activa.
        mongo_db: conexión MongoDB activa.
        user (tuple): información del usuario autenticado.
    """
    user_name = user[1]

    while True:
        print("\n Menú Administrador ")
        print(f"Administrador: {user_name}")
        print("1. Gestión de administradores")
        print("2. Gestión de usuarios")
        print("3. Gestión de registros de salud")
        print("4. Gestión de archivos personales")
        print("5. Ver análisis de usuarios")
        print("6. Buscar registros/notas de usuario")
        print("7. Exportar reporte de usuario")
        print("8. Cerrar sesión")

        option = get_menu_option(8)

        # ... dentro de admin_menu ...
        if option == 1:
            # CAMBIO AQUÍ: Agregamos mongo_db
            manage_admin_accounts(mysql_conn, mongo_db) 
        elif option == 2:
            # CAMBIO AQUÍ: Agregamos mongo_db
            manage_standard_users(mysql_conn, mongo_db)
        elif option == 3:
            admin_manage_daily_records(mysql_conn)
        elif option == 4:
            admin_manage_files(mongo_db)
        elif option == 5:
            admin_view_health_analysis(mysql_conn)
        elif option == 6:
            search_records_and_notes(mysql_conn, mongo_db, user)
        elif option == 7:
            admin_export_user_report(mysql_conn, mongo_db)
        elif option == 8:
            print("Sesión cerrada. Regresando al menú principal")
            break


def user_menu(mysql_conn, mongo_db, user):
    """
    Muestra el menú para usuarios con rol de usuario normal.

    Por ahora, las opciones funcionales son:
        - Cerrar sesión

    Otras opciones se dejan como futuras funcionalidades.

    Parámetros:
        mysql_conn: conexión MySQL activa.
        mongo_db: conexión MongoDB activa (para usos futuros).
        user (tuple): información del usuario autenticado.
    """
    user_name = user[1]

    while True:
        print("\nMenú del Usuario")
        print(f"Usuario: {user_name}")
        print("1. Registrar dato diario de salud")
        print("2. Ver registros de salud")
        print("3. Ver análisis y alertas")
        print("4. Exportar reporte (JSON/TXT)")
        print("5. Registrar nota personal")
        print("6. Registrar archivo adjunto")
        print("7. Buscar registros/notas")
        print("8. Cerrar sesión")


        option = get_menu_option(8)

        if option == 1:
            record_daily_health_data(mysql_conn, user)
        elif option == 2:
            view_daily_health_records(mysql_conn, user)
        elif option == 3:
            view_health_analysis(mysql_conn, user)
        elif option == 4:
            export_personal_report(mysql_conn, mongo_db, user)
        elif option == 5:
            record_personal_note(mongo_db, user)
        elif option == 6:
            record_attachment(mongo_db, user)
        elif option == 7:
            search_records_and_notes(mysql_conn, mongo_db, user)
        elif option == 8:
            print("Sesión cerrada. Regresando al menú principal")
            break

# PUNTO DE ENTRADA PRINCIPAL

if __name__ == "__main__":
    connections = initialize_system()
    try:
        main_menu(connections)
    finally:
        stop_automatic_alerts()

        # Cerrar conexión MySQL
        if connections.get("mysql") is not None:
            connections["mysql"].close()

        # Cerrar conexión MongoDB
        if connections.get("mongo") is not None:
            # Acceder al cliente padre para cerrarlo
            connections["mongo"].client.close()

        print("\nConexiones cerradas correctamente.")
