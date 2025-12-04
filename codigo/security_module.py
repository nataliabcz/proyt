"""
security_module.py
Este módulo gestiona el proceso de inicio de sesión del usuario. Este modulo implementa:

    - Conexión a MySQL (datos del usuario)
    - Validación de contraseña mediante CSV
"""

import mysql_connection as SQLC
import csv_connection as CSVC


def create_mysql_connection():
    """
    Crea y devuelve una conexión a la base de datos MySQL.

    Esta función simplemente encapsula la función definida en
    mysql_connection.py para mantener un punto centralizado de acceso.

    Retorna:
        connection (MySQLConnection): conexión activa a MySQL.

    Ejemplo:
        >>> conn = create_mysql_connection()
    """
    return SQLC.create_connection()


def create_mysql_conecction():
    """Alias para create_mysql_connection() con nombre corregido."""
    return create_mysql_connection()


def validate_login(connection, email, password):
    """
    Valida las credenciales de un usuario combinando MySQL y CSV.

    Proceso:
        1. Buscar el usuario en MySQL por su email.
        2. Si el usuario existe → obtener user_id.
        3. Validar la contraseña usando csv_connection.py
        4. Si la contraseña coincide → retornar datos del usuario.
        5. Si falla → retornar {} (diccionario vacío).

    Parámetros:
        connection: conexión MySQL activa.
        email (str): correo electrónico ingresado.
        password (str): contraseña ingresada por el usuario.

    Retorna:
        dict o tuple: datos del usuario si es válido.
        {} si el usuario no existe o la contraseña es incorrecta.
    """
    # Obtener usuario por correo
    user = SQLC.obtain_user_from_email(connection, email)

    # Si no existe el usuario o hubo error en MySQL
    if not user:
        return {}

    user_id = user[0]  # ID del usuario

    # Validación de contraseña usando CSV
    if CSVC.is_valid_password(user_id, password):
        return user

    return {}
