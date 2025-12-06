"""
csv_connection.py

Este módulo contiene funciones para manejar contraseñas almacenadas
en un archivo CSV, incluyendo carga de usuarios, validación de contraseñas
y registro de nuevos usuarios.
"""

import csv

# Ruta del archivo CSV donde se almacenan las contraseñas
import os
import csv

# Esto hace que la ruta funcione en cualquier PC automáticamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "..", "csv", "passwords.csv")


def load_passwords():
    """
    Carga todas las contraseñas del archivo CSV en un diccionario.

    El archivo CSV debe contener las columnas:
        - user_id
        - password

    Esta función recorre cada fila del archivo y crea un diccionario donde
    la llave es el ID del usuario y el valor es la contraseña registrada.

    Retorna:
        dict: Un diccionario con formato { user_id: password }
              Si ocurre un error o no existe el archivo, retorna {}.
    """
    users = {}

    try:
        with open(CSV_FILE, mode="r", newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Recorrer cada fila del archivo CSV
            for row in reader:
                users[row["user_id"]] = row["password"]

        return users

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo CSV '{CSV_FILE}'.")
        return {}

    except Exception as e:
        print("❌ Error al cargar el archivo CSV:", e)
        return {}


def is_valid_password(user_id, password):
    """
    Verifica si la contraseña ingresada coincide con la registrada en el CSV.

    Busca el user_id dentro del archivo CSV y compara la contraseña ingresada
    con la contraseña almacenada.

    Parámetros:
        user_id (int): ID del usuario que intenta iniciar sesión.
        password (str): Contraseña ingresada por el usuario.

    Retorna:
        bool: True si la contraseña es correcta, False si es incorrecta
              o si el usuario no existe.

    """
    try:
        with open(CSV_FILE, mode="r", newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Buscar el usuario dentro del archivo CSV
            for row in reader:
                if int(row["user_id"]) == user_id:
                    if row["password"] == password:
                        return True

        return False

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV '{CSV_FILE}'.")
        return False

    except Exception as e:
        print("Error al validar la contraseña:", e)
        return False


def register_user(user_id, password):
    """
    Registra un nuevo usuario en el archivo CSV.

    Antes de registrar:
        - Verifica si el usuario ya existe en el archivo.
        - Si existe, no permite duplicados.
        - Si no existe, agrega una nueva fila con (user_id, password).

    Parámetros:
        user_id (str o int): ID del nuevo usuario.
        password (str): Contraseña del nuevo usuario.

    Retorna:
        bool: True si el usuario fue registrado exitosamente,
              False si hubo un error o si ya existe.
    """
    try:
        # Cargar usuarios existentes para evitar duplicados
        users = load_passwords()

        if str(user_id) in users:
            print("Error: El usuario ya existe en el archivo.")
            return False

        # Registrar al nuevo usuario
        with open(CSV_FILE, mode="a", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([user_id, password])

        print("✔ Usuario registrado exitosamente.")
        return True

    except Exception as e:
        print("Error al registrar usuario:", e)
        return False


def remove_user(user_id):
    """
    Elimina un usuario del archivo CSV basándose en su ID.

    Parámetros:
        user_id (int): ID del usuario que se desea eliminar.

    Retorna:
        bool: True si se eliminó un registro, False si no se encontró.
    """
    try:
        rows = []
        removed = False
        with open(CSV_FILE, mode="r", newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["user_id"]) == int(user_id):
                    removed = True
                    continue
                rows.append(row)

        if not removed:
            return False

        with open(CSV_FILE, mode="w", newline='', encoding="utf-8") as file:
            fieldnames = ["user_id", "password"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        return True

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV '{CSV_FILE}'.")
        return False

    except Exception as e:
        print("Error al eliminar usuario del CSV:", e)
        return False


def seed_passwords():
    """
    Inserta o actualiza contraseñas por lotes siguiendo un diccionario.

    Parámetros:
        password_map (dict[int,str]): llaves user_id, valores contraseñas.

    Retorna:
        bool: True si se pudo procesar al menos una entrada, False en caso contrario.
    """

    try:
        # Cargar contraseñas existentes
        existing = load_passwords()

        # Actualizar con los nuevos valores
        for i in range(13):
            existing[str(i + 1)] = str("user123")

        if not existing:
            print("No se generaron entradas válidas para guardar.")
            return False

        # Escribir el CSV completo
        with open(CSV_FILE, mode="w", newline='', encoding="utf-8") as file:
            fieldnames = ["user_id", "password"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for uid, pwd in existing.items():
                writer.writerow({"user_id": uid, "password": pwd})

        print("✔ Contraseñas guardadas correctamente.")
        return True

    except Exception as exc:
        print("Error al generar el CSV de contraseñas:", exc)
        return False
