"""
mysql_connection.py
Este módulo gestiona la conexión hacia la base de datos MySQL del proyecto,
crea las tablas necesarias, inserta datos de ejemplo y provee las funciones relacionadas con la BD de MySQL
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

def create_connection():
    """
    Crea y retorna una conexión hacia la base de datos MySQL del proyecto.

    La base de datos utilizada es:
        Nombre: FP_Info12025_2
        Usuario: informatica1
        Contraseña: info2025_2
        Puerto: 3306

    Retorna:
        connection (MySQLConnection): Conexión activa a la base de datos.
        None si ocurre un error.

    Ejemplo:
        >>> conn = create_connection()
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port="3306",
            user=" informatica1",
            password="info2025_2",
            database="FP_Info12025_2"
        )
        return connection

    except Error as e:
        print("❌ Error al conectar con MySQL:", e)
        return None


def create_tables(connection):
    """
    Crea todas las tablas necesarias para el funcionamiento del proyecto.

    Tablas creadas:
        - roles: lista de roles (admin, user)
        - permits: permisos del sistema
        - role_permits: relación N:N entre roles y permisos
        - users: usuarios del sistema
        - daily_records: registros diarios de salud

    Parámetros:
        connection: conexión MySQL activa.

    Ejemplo:
        >>> create_tables(connection)
    """
    try:
        cursor = connection.cursor()

        # Tabla de roles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100)
            );
        """)

        # Tabla de permisos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100)
            );
        """)

        # Relación roles-permisos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_permits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                role_id INT,
                permit_id INT,
                FOREIGN KEY (role_id) REFERENCES roles(id),
                FOREIGN KEY (permit_id) REFERENCES permits(id)
            );
        """)

        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                email VARCHAR(100),
                role_id INT,
                FOREIGN KEY (role_id) REFERENCES roles(id)
            );
        """)

        # Tabla de registros diarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                date DATE,
                sleep_hours FLOAT,
                mood INT,
                physical_activity VARCHAR(255),
                food VARCHAR(255),
                symptoms VARCHAR(255),
                blood_pressure VARCHAR(20),
                glucose FLOAT,
                bpm INT,
                weight FLOAT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

        connection.commit()
        print("Tablas creadas correctamente")

    except Error as e:
        print("Error al crear las tablas:", e)


def insert_sample_data(connection):
    """
    Inserta datos de ejemplo en las tablas del proyecto.

    Inserta:
        - Roles
        - Permisos
        - Relaciones entre roles y permisos
        - Usuarios
        - Registros diarios de salud

    Parámetros:
        connection: conexión MySQL activa.
    """
    try:
        cursor = connection.cursor()

        # Inserción de roles
        cursor.execute("""
            INSERT INTO roles (name)
            VALUES ('admin'), ('user')
            ON DUPLICATE KEY UPDATE name = name;
        """)

        # Inserción de permisos
        cursor.execute("""
            INSERT INTO permits (name)
            VALUES
            ('create_user'),
            ('edit_user'),
            ('delete_user'),
            ('view_health_records'),
            ('edit_health_records'),
            ('delete_health_records'),
            ('upload_files'),
            ('delete_files')
            ON DUPLICATE KEY UPDATE name = name;
        """)

        # Obtener ID del rol admin
        cursor.execute("SELECT id FROM roles WHERE name='admin';")
        admin_role_id = cursor.fetchone()[0]

        # Asignar TODOS los permisos al rol admin
        cursor.execute("SELECT id FROM permits;")
        permits = cursor.fetchall()

        for permit in permits:
            cursor.execute("""
                INSERT INTO role_permits (role_id, permit_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE role_id = role_id;
            """, (admin_role_id, permit[0]))

        # Obtener ID rol user
        cursor.execute("SELECT id FROM roles WHERE name='user';")
        user_role_id = cursor.fetchone()[0]

        # Permisos limitados del usuario
        limited_permits = ['view_health_records', 'edit_health_records', 'upload_files']

        for permit_name in limited_permits:
            cursor.execute("SELECT id FROM permits WHERE name=%s", (permit_name,))
            permit_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO role_permits (role_id, permit_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE role_id = role_id;
            """, (user_role_id, permit_id))

        def get_or_create_user(name, age, email, role_id):
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing = cursor.fetchone()
            if existing:
                return existing[0]

            cursor.execute("""
                INSERT INTO users (name, age, email, role_id)
                VALUES (%s, %s, %s, %s)
            """, (name, age, email, role_id))
            return cursor.lastrowid

        sample_people = [
            {"name": "Lucía Torres", "age": 34, "email": "lucia.admin@mail.com", "role": "admin"},
            {"name": "Andrés Mejía", "age": 37, "email": "andres.admin@mail.com", "role": "admin"},
            {"name": "María Carvajal", "age": 32, "email": "maria.admin@mail.com", "role": "admin"},
            {"name": "Carlos Pérez", "age": 28, "email": "carlos.user@mail.com", "role": "user"},
            {"name": "Laura Gómez", "age": 25, "email": "laura.user@mail.com", "role": "user"},
            {"name": "Felipe Ríos", "age": 22, "email": "felipe.user@mail.com", "role": "user"},
            {"name": "Daniela Hurtado", "age": 31, "email": "daniela.user@mail.com", "role": "user"},
            {"name": "Elena Vivas", "age": 27, "email": "elena.user@mail.com", "role": "user"},
            {"name": "Mateo Bernal", "age": 29, "email": "mateo.user@mail.com", "role": "user"},
            {"name": "Sara Villada", "age": 24, "email": "sara.user@mail.com", "role": "user"},
            {"name": "Nicolás Molina", "age": 33, "email": "nicolas.user@mail.com", "role": "user"},
            {"name": "Juana Velasco", "age": 26, "email": "juana.user@mail.com", "role": "user"},
            {"name": "David Valencia", "age": 30, "email": "david.user@mail.com", "role": "user"},
        ]

        created_users = []
        for index, person in enumerate(sample_people):
            role_id = admin_role_id if person["role"] == "admin" else user_role_id
            user_id = get_or_create_user(person["name"], person["age"], person["email"], role_id)
            created_users.append({
                "id": user_id,
                "name": person["name"],
                "base_weight": 58 + index,
            })

        base_date = datetime.now().date() - timedelta(days=21)

        for idx, data in enumerate(created_users):
            for day_offset in range(3):
                record_date = base_date + timedelta(days=idx * 3 + day_offset)
                cursor.execute("""
                    SELECT id FROM daily_records
                    WHERE user_id = %s AND date = %s
                """, (data["id"], record_date))
                if cursor.fetchone():
                    continue

                sleep_hours = round(6 + ((idx + day_offset) % 4) + 0.5, 1)
                mood = max(1, min(10, 5 + ((idx + day_offset) % 5)))
                activity_type = ["Caminata", "Yoga", "Ciclismo"][day_offset % 3]
                physical_activity = f"{activity_type} de {25 + day_offset * 10} minutos"
                food = f"Menú balanceado día {day_offset + 1}"
                symptoms = "Sin síntomas reportados" if day_offset != 1 else "Cansancio leve"
                systolic = 115 + ((idx + day_offset) % 5) * 4
                diastolic = 75 + ((idx + day_offset) % 4) * 3
                blood_pressure = f"{systolic}/{diastolic}"
                glucose = round(90 + ((idx + day_offset) % 4) * 6, 1)
                bpm = 65 + ((idx + day_offset) % 6) * 2
                weight = round(data["base_weight"] + day_offset * 0.3, 1)

                cursor.execute("""
                    INSERT INTO daily_records
                    (user_id, date, sleep_hours, mood, physical_activity, food,
                     symptoms, blood_pressure, glucose, bpm, weight)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (data["id"], record_date, sleep_hours, mood, physical_activity,
                      food, symptoms, blood_pressure, glucose, bpm, weight))

        connection.commit()
        print("Datos de ejemplo insertados correctamente")

    except Error as e:
        print("Error al insertar datos:", e)


def has_permission(connection, user_id, permit_name):
    """
    Verifica si un usuario posee un permiso específico.

    Parámetros:
        connection: conexión MySQL activa
        user_id (int): ID del usuario
        permit_name (str): nombre del permiso buscado

    Retorna:
        True si el usuario posee el permiso.
        False si no lo posee o si ocurre un error.
    """
    try:
        cursor = connection.cursor()

        query = """
            SELECT COUNT(*) 
            FROM users
            JOIN role_permits ON users.role_id = role_permits.role_id
            JOIN permits ON role_permits.permit_id = permits.id
            WHERE users.id = %s AND permits.name = %s;
        """

        cursor.execute(query, (user_id, permit_name))
        result = cursor.fetchone()[0]

        return result > 0

    except Error as e:
        print("Error al comprobar permisos:", e)
        return False


def register_user(connection, name, age, email, role_id):
    """
    Registra un nuevo usuario en la base de datos.

    Parámetros:
        name (str): nombre del usuario
        age (int): edad
        email (str): correo electrónico
        role_id (int): ID del rol asignado

    Retorna:
        int: ID del usuario creado si es exitoso.
        None si hubo un error.
    """
    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (name, age, email, role_id)
            VALUES (%s, %s, %s, %s)
        """, (name, age, email, role_id))

        connection.commit()

        return cursor.lastrowid

    except Error as e:
        print("Error al registrar usuario:", e)
        return None


def obtain_user_from_email(connection, email):
    """
    Busca un usuario por su correo electrónico.

    Parámetros:
        email (str): correo del usuario

    Retorna:
        Una tupla con los datos del usuario,
        o False si ocurre un error.
    """
    try:
        cursor = connection.cursor(buffered=True)

        query = """
            SELECT * 
            FROM users
            WHERE users.email = %s;
        """

        cursor.execute(query, (email,))
        result = cursor.fetchone()

        return result

    except Error as e:
        print("Error al buscar usuario:", e)
        return False


def register_daily_record(connection, user_id, date, sleep_hours, mood,
                          physical_activity, food, symptoms, blood_pressure,
                          glucose, bpm, weight):
    """
    Registra un nuevo registro diario de salud para un usuario.

    Parámetros:
        user_id (int)
        date (str, formato YYYY-MM-DD)
        sleep_hours (float)
        mood (int)
        physical_activity (str)
        food (str)
        symptoms (str)
        blood_pressure (str)
        glucose (float)
        bpm (int)
        weight (float)

    Retorna:
        True si se insertó correctamente.
        False si hubo un error.
    """
    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO daily_records 
            (user_id, date, sleep_hours, mood, physical_activity, food,
             symptoms, blood_pressure, glucose, bpm, weight)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, date, sleep_hours, mood, physical_activity, food,
              symptoms, blood_pressure, glucose, bpm, weight))

        connection.commit()
        return True

    except Error as e:
        print("Error al registrar el registro diario:", e)
        return False


def get_role_id(connection, role_name):
    """
    Obtiene el ID de un rol por nombre.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print("Error al obtener el rol:", e)
        return None


def get_users(connection, role_name=None):
    """
    Recupera usuarios opcionalmente filtrando por nombre de rol.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT users.id, users.name, users.age, users.email,
                   users.role_id, roles.name AS role_name
            FROM users
            JOIN roles ON users.role_id = roles.id
        """
        params = []
        if role_name:
            query += " WHERE roles.name = %s"
            params.append(role_name)

        query += " ORDER BY users.id ASC"

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Error as e:
        print("Error al obtener usuarios:", e)
        return []


def get_user_by_id(connection, user_id):
    """
    Retorna los datos de un usuario específico.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT users.id, users.name, users.age, users.email,
                   users.role_id, roles.name AS role_name
            FROM users
            JOIN roles ON users.role_id = roles.id
            WHERE users.id = %s
        """, (user_id,))
        return cursor.fetchone()
    except Error as e:
        print("Error al obtener usuario:", e)
        return None


def update_user(connection, user_id, name, age, email, role_id):
    """
    Actualiza un usuario existente.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE users
            SET name = %s, age = %s, email = %s, role_id = %s
            WHERE id = %s
        """, (name, age, email, role_id, user_id))
        connection.commit()
        return cursor.rowcount > 0
    except Error as e:
        print("Error al actualizar usuario:", e)
        return False


def delete_user(connection, user_id):
    """
    Elimina un usuario y sus registros diarios de salud.
    """
    cursor = connection.cursor()
    try:
        # 1. Primero borramos los registros médicos de ese usuario (Tabla hija)
        sql_records = "DELETE FROM daily_records WHERE user_id = %s"
        cursor.execute(sql_records, (user_id,))
        
        # 2. NO TOCAMOS role_permits (ahí no hay user_id, eso causaba tu error anterior)
        
        # 3. Finalmente, borramos al usuario
        sql_user = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql_user, (user_id,))
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error al eliminar usuario completo: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()

def get_daily_records_admin(connection, user_id=None, limit=50):
    """
    Obtiene registros diarios con información del usuario.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT dr.*, users.name AS user_name
            FROM daily_records dr
            JOIN users ON dr.user_id = users.id
        """
        params = []
        if user_id:
            query += " WHERE dr.user_id = %s"
            params.append(user_id)

        query += " ORDER BY dr.date DESC, dr.id DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Error as e:
        print("Error al obtener registros diarios:", e)
        return []


def get_daily_record_by_id(connection, record_id):
    """
    Obtiene un registro diario específico.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT dr.*, users.name AS user_name
            FROM daily_records dr
            JOIN users ON dr.user_id = users.id
            WHERE dr.id = %s
        """, (record_id,))
        return cursor.fetchone()
    except Error as e:
        print("Error al obtener el registro diario:", e)
        return None


def update_daily_record(connection, record_id, updates):
    """
    Actualiza campos de un registro diario.
    """
    if not updates:
        return False

    try:
        cursor = connection.cursor()
        set_clauses = []
        params = []
        for field, value in updates.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)
        params.append(record_id)

        query = f"""
            UPDATE daily_records
            SET {", ".join(set_clauses)}
            WHERE id = %s
        """
        cursor.execute(query, tuple(params))
        connection.commit()
        return cursor.rowcount > 0
    except Error as e:
        print("Error al actualizar el registro diario:", e)
        return False


def delete_daily_record(connection, record_id):
    """
    Elimina un registro diario.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM daily_records WHERE id = %s", (record_id,))
        connection.commit()
        return cursor.rowcount > 0
    except Error as e:
        print("Error al eliminar el registro diario:", e)
        return False


def has_existing_data(connection):
    """
    Verifica si alguna tabla clave ya tiene datos.

    Retorna True si hay al menos un registro en users o daily_records.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM daily_records")
        records_count = cursor.fetchone()[0]

        return (users_count + records_count) > 0
    except Error as e:
        print("Error al verificar datos existentes:", e)
        return False


def get_all_user_ids(connection):
    """
    Obtiene la lista de todos los IDs de usuarios registrados.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users ORDER BY id")
        return [row[0] for row in cursor.fetchall()]
    except Error as e:
        print("Error al obtener los usuarios:", e)
        return []


def get_daily_records_for_analysis(connection, user_id, limit=30):
    """
    Recupera los registros diarios más recientes para análisis cronológico.

    Retorna los registros ordenados ascendentemente por fecha.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                id,
                user_id,
                date,
                sleep_hours,
                mood,
                physical_activity,
                food,
                symptoms,
                blood_pressure,
                glucose,
                bpm,
                weight
            FROM daily_records
            WHERE user_id = %s
            ORDER BY date DESC, id DESC
            LIMIT %s
        """, (user_id, limit))
        records = cursor.fetchall()
        return list(reversed(records))
    except Error as e:
        print("Error al obtener registros para análisis:", e)
        return []


def get_daily_records_in_range(connection, user_id, start_date, end_date):
    """
    Recupera los registros diarios de un usuario dentro de un rango de fechas.

    Parámetros:
        connection: conexión MySQL activa.
        user_id (int): ID del usuario.
        start_date (str): fecha inicial (YYYY-MM-DD).
        end_date (str): fecha final (YYYY-MM-DD).

    Retorna:
        list[dict]: registros ordenados ascendentemente por fecha e ID.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                id,
                user_id,
                date,
                sleep_hours,
                mood,
                physical_activity,
                food,
                symptoms,
                blood_pressure,
                glucose,
                bpm,
                weight
            FROM daily_records
            WHERE user_id = %s
              AND date BETWEEN %s AND %s
            ORDER BY date ASC, id ASC
        """, (user_id, start_date, end_date))
        return cursor.fetchall()
    except Error as e:
        print("Error al obtener registros del rango solicitado:", e)
        return []


def search_daily_records(connection, user_id, date_from=None, date_to=None,
                         keyword=None, mood_min=None, mood_max=None,
                         has_symptoms=None, limit=50):
    """
    Busca registros diarios con filtros opcionales por fecha, palabra clave y estado de ánimo.

    Parámetros:
        connection: conexión MySQL activa.
        user_id (int): usuario propietario de los registros.
        date_from/date_to (str|None): rangos de fecha YYYY-MM-DD.
        keyword (str|None): texto a buscar en actividad, alimentación o síntomas.
        mood_min/mood_max (int|None): rango de estado de ánimo.
        has_symptoms (bool|None): True para solo con síntomas, False para sin síntomas, None para todos.
        limit (int): máximo de filas a devolver.

    Retorna:
        list[dict]: resultados ordenados por fecha descendente.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                id, user_id, date, sleep_hours, mood, physical_activity,
                food, symptoms, blood_pressure, glucose, bpm, weight
            FROM daily_records
            WHERE user_id = %s
        """
        params = [user_id]

        if date_from:
            query += " AND date >= %s"
            params.append(date_from)
        if date_to:
            query += " AND date <= %s"
            params.append(date_to)
        if keyword:
            like_kw = f"%{keyword}%"
            query += """
                AND (
                    physical_activity LIKE %s OR
                    food LIKE %s OR
                    symptoms LIKE %s
                )
            """
            params.extend([like_kw, like_kw, like_kw])
        if mood_min is not None:
            query += " AND mood >= %s"
            params.append(mood_min)
        if mood_max is not None:
            query += " AND mood <= %s"
            params.append(mood_max)
        if has_symptoms is True:
            query += " AND symptoms IS NOT NULL AND TRIM(symptoms) <> ''"
        elif has_symptoms is False:
            query += " AND (symptoms IS NULL OR TRIM(symptoms) = '')"

        query += " ORDER BY date DESC, id DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except Error as e:
        print("Error al buscar registros diarios:", e)
        return []


def get_daily_records(connection, user_id, start_date=None, end_date=None, limit=20):
    """
    Obtiene registros diarios de salud para un usuario con filtros opcionales.

    Parámetros:
        connection: conexión MySQL activa.
        user_id (int): ID del usuario cuyos registros se consultan.
        start_date (str|None): fecha mínima (YYYY-MM-DD), opcional.
        end_date (str|None): fecha máxima (YYYY-MM-DD), opcional.
        limit (int): cantidad máxima de registros a devolver.

    Retorna:
        list[dict]: registros obtenidos ordenados por fecha descendente.
        Lista vacía si ocurre un error.
    """
    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id,
                user_id,
                date,
                sleep_hours,
                mood,
                physical_activity,
                food,
                symptoms,
                blood_pressure,
                glucose,
                bpm,
                weight
            FROM daily_records
            WHERE user_id = %s
        """
        params = [user_id]

        if start_date:
            query += " AND date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND date <= %s"
            params.append(end_date)

        query += " ORDER BY date DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()

    except Error as e:
        print("Error al obtener registros diarios:", e)
        return []
