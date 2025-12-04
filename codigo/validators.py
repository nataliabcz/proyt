"""
validators.py
Este módulo contiene funciones de utilidad para validar diferentes tipos 
de datos ingresados por el usuario, tales como texto alfabético, números 
enteros, números decimales, correos electrónicos, fechas, rangos numéricos,
valores no vacíos y opciones de menú.
"""

import re
from datetime import datetime


def validate_alpha(text):
    """
    Valida que el texto ingresado contenga únicamente caracteres alfabéticos y espacios.

    Esta función utiliza una expresión regular que permite letras mayúsculas, 
    minúsculas, caracteres acentuados, la letra Ñ/ñ y espacios.

    Parámetros:
        text (str): El texto ingresado por el usuario.

    Retorna:
        bool: True si el texto es válido (solo letras), False en caso contrario.

    """
    pattern = r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+"

    if re.fullmatch(pattern, text):
        return True

    print("❌ Error: Solo se permiten caracteres alfabéticos.")
    return False


def validate_integer(value):
    """
    Valida que el valor ingresado sea un número entero.

    Intenta convertir el valor a entero; si ocurre un error, no es válido.

    Parámetros:
        value (str): El valor ingresado por el usuario.

    Retorna:
        bool: True si es un número entero válido, False si no lo es.
    """
    try:
        int(value)
        return True
    except ValueError:
        print("❌ Error: Se requiere un valor numérico entero.")
        return False


def validate_float(value):
    """
    Valida que el valor ingresado sea un número decimal (float).

    Parámetros:
        value (str): El valor ingresado.

    Retorna:
        bool: True si el valor puede convertirse a float, False en caso contrario.
    """
    try:
        float(value)
        return True
    except ValueError:
        print("❌ Error: Se requiere un valor numérico decimal.")
        return False


def validate_range(value, min_val, max_val):
    """
    Valida que un valor numérico se encuentre dentro de un rango aceptado.

    Este tipo de validación es útil para campos como estado de ánimo (1–10), 
    niveles de azúcar, etc.

    Parámetros:
        value (str): El valor numérico como cadena.
        min_val (float): Valor mínimo permitido.
        max_val (float): Valor máximo permitido.

    Retorna:
        bool: True si el valor está dentro del rango, False si no lo está.
    """
    try:
        number = float(value)
        if min_val <= number <= max_val:
            return True

        print(f"❌ Error: El valor debe estar entre {min_val} y {max_val}.")
        return False

    except ValueError:
        print("❌ Error: Valor numérico inválido.")
        return False


def validate_email(email):
    """
    Valida que el email tenga un formato correcto.

    Utiliza una expresión regular para verificar la estructura de un correo electrónico.

    Parámetros:
        email (str): El correo ingresado.

    Retorna:
        bool: True si el formato es válido, False si no lo es.
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if re.match(pattern, email):
        return True

    print("❌ Error: Formato de correo electrónico inválido.")
    return False


def validate_date(date_str):
    """
    Valida que la fecha tenga el formato AAAA-MM-DD (YYYY-MM-DD).

    Utiliza datetime.strptime para verificar tanto el formato como la validez de la fecha.

    Parámetros:
        date_str (str): Fecha ingresada como cadena.

    Retorna:
        bool: True si la fecha es válida, False si no lo es.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        print("❌ Error: La fecha debe tener el formato YYYY-MM-DD.")
        return False


def validate_menu_option(option, max_option):
    """
    Valida que la opción seleccionada del menú sea válida.

    Comprueba que:
        1. La opción sea un número entero.
        2. El número esté dentro del rango permitido.

    Parámetros:
        option (str): La opción ingresada por el usuario.
        max_option (int): El número máximo de opciones permitidas.

    Retorna:
        bool: True si la opción es válida, False en caso contrario.
    """
    if validate_integer(option):
        option = int(option)
        if 1 <= option <= max_option:
            return True

        print(f"❌ Error: La opción debe estar entre 1 y {max_option}.")
        return False

    return False


def validate_not_empty(value):
    """
    Valida que el valor ingresado no esté vacío.

    Parámetros:
        value (str): El texto ingresado.

    Retorna:
        bool: True si el texto no está vacío, False si está vacío.
    """
    if value.strip() != "":
        return True

    print("❌ Error: El valor no puede estar vacío.")
    return False