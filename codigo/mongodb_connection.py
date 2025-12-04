"""
mongodb_connection.py

Este módulo permite realizar la conexión hacia la base de datos MongoDB,
crear las colecciones necesarias para el proyecto e insertar datos de prueba.
"""

from datetime import datetime, timedelta

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from bson.errors import InvalidId


def create_mongo_connection():
    """
    Crea y retorna una conexión hacia la base de datos MongoDB del proyecto.

    Esta función utiliza las credenciales proporcionadas en el enunciado del proyecto:
        usuario: informatica1
        contraseña: info2025_2
        base de datos: FP_Info12025_2
        puerto: 27020

    Si la conexión es exitosa, retorna el objeto de la base de datos.
    Si ocurre un error, muestra un mensaje y retorna None.

    Retorna:
        db (Database): Objeto de la base de datos MongoDB.
        None si la conexión falla.
    """
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["FP_Info12025_2"]
        print("✔ Conexión exitosa a MongoDB")
        return db

    except ConnectionFailure as e:
        print("❌ Error al conectar a MongoDB:", e)
        return None


def create_collections(db):
    """
    Crea las colecciones necesarias para el proyecto si aún no existen.

    Las colecciones requeridas son:
        - personal_notes  (Notas personales del usuario)
        - attachments      (Archivos adjuntos como fotos, capturas, etc.)

    Si la colección ya existe, se informa al usuario.
    Si no existe, se crea una nueva colección.

    Parámetros:
        db (Database): La base de datos MongoDB previamente conectada.
    """
    existing_collections = db.list_collection_names()

    required_collections = ["personal_notes", "attachments"]

    for col in required_collections:
        if col not in existing_collections:
            db.create_collection(col)
            print(f"✔ Colección creada: {col}")
        else:
            print(f"ℹ La colección '{col}' ya existe.")


def add_personal_note(db, user_id, text, mood, weather, location, date=None, tags=None, attachments=None):
    """
    Registra una nota personal con metadatos basicos.

    Parametros:
        db: conexion MongoDB ya inicializada.
        user_id (int): identificador del usuario.
        text (str): contenido libre de la nota.
        date (str): fecha en formato YYYY-MM-DD. Si es None usa la fecha actual.
        tags (list[str]): etiquetas para clasificar la nota.
        attachments (list): rutas de archivos asociados (opcional).

    Retorna:
        insert_id del documento creado o None si ocurre un error.
    """
    note_date = date or datetime.now().date().isoformat()
    payload = {
        "user_id": user_id,
        "date": note_date,
        "text": text,
        "tags": tags or [],
        "mood": mood,
        "location": location,
        "weather": weather,
        "attachments": attachments or [],
    }
    try:
        result = db["personal_notes"].insert_one(payload)
        return result.inserted_id
    except Exception as exc:
        print("ƒ?O Error al guardar la nota personal:", exc)
        return None


def add_attachment(db, user_id, file_path, date=None, attachment_type="general",
                   tags=None, description=None, metadata=None):
    """
    Registra un archivo adjunto como ruta dentro de MongoDB con metadatos.

    Parametros:
        db: conexion MongoDB.
        user_id (int): identificador del usuario.
        file_path (str): ruta o nombre del archivo almacenado externamente.
        date (str): fecha en formato YYYY-MM-DD. Si es None usa la fecha actual.
        attachment_type (str): tipo (imagen, pdf, captura, etc.).
        tags (list[str]): etiquetas para clasificar.
        description (str): descripcion opcional del archivo.
        metadata (dict): metadatos adicionales (app origen, dimensiones, etc.).

    Retorna:
        insert_id del documento creado o None si ocurre un error.
    """
    attach_date = date or datetime.now().date().isoformat()
    payload = {
        "user_id": user_id,
        "date": attach_date,
        "type": attachment_type,
        "tags": tags or [],
        "file_path": file_path,
        "description": description or "",
        "metadata": metadata or {},
    }
    try:
        result = db["attachments"].insert_one(payload)
        return result.inserted_id
    except Exception as exc:
        print("ƒ?O Error al guardar el adjunto:", exc)
        return None


def get_notes_by_user(db, user_id, limit=20):
    """
    Recupera notas personales de un usuario ordenadas por fecha descendente.
    """
    return list(
        db["personal_notes"]
        .find({"user_id": user_id})
        .sort("date", -1)
        .limit(limit)
    )


def get_notes_in_range(db, user_id, start_date, end_date, limit=10):
    """
    Recupera notas dentro de un rango de fechas (inclusive).
    """
    query = {
        "user_id": user_id,
        "date": {
            "$gte": start_date,
            "$lte": end_date
        }
    }
    return list(
        db["personal_notes"]
        .find(query)
        .sort("date", 1)
        .limit(limit)
    )


def search_notes(db, user_id, date_from=None, date_to=None, keyword=None,
                 mood_min=None, mood_max=None, tags=None, limit=30):
    """
    Busca notas personales con filtros por fecha, palabra clave, ánimo y etiquetas.
    """
    query = {"user_id": user_id}

    if date_from or date_to:
        query["date"] = {}
        if date_from:
            query["date"]["$gte"] = date_from
        if date_to:
            query["date"]["$lte"] = date_to

    if mood_min is not None or mood_max is not None:
        query["mood"] = {}
        if mood_min is not None:
            query["mood"]["$gte"] = mood_min
        if mood_max is not None:
            query["mood"]["$lte"] = mood_max

    if tags:
        query["tags"] = {"$all": tags}

    if keyword:
        query["$or"] = [
            {"text": {"$regex": keyword, "$options": "i"}},
            {"tags": {"$elemMatch": {"$regex": keyword, "$options": "i"}}}
        ]

    return list(
        db["personal_notes"]
        .find(query)
        .sort("date", -1)
        .limit(limit)
    )


def get_attachments_by_user(db, user_id, limit=20):
    """
    Recupera adjuntos de un usuario ordenados por fecha descendente.
    """
    return list(
        db["attachments"]
        .find({"user_id": user_id})
        .sort("date", -1)
        .limit(limit)
    )


def get_attachments(db, user_id=None, limit=20):
    """
    Recupera adjuntos con filtro opcional por usuario.
    """
    query = {}
    if user_id is not None:
        query["user_id"] = user_id
    return list(
        db["attachments"]
        .find(query)
        .sort("date", -1)
        .limit(limit)
    )


def get_attachment_by_id(db, attachment_id):
    """
    Obtiene un adjunto específico por su ObjectId.
    """
    try:
        object_id = ObjectId(attachment_id)
    except (InvalidId, TypeError):
        return None
    return db["attachments"].find_one({"_id": object_id})


def update_attachment(db, attachment_id, updates):
    """
    Actualiza los campos proporcionados para un adjunto.
    """
    if not updates:
        return False
    try:
        object_id = ObjectId(attachment_id)
    except (InvalidId, TypeError):
        return False

    result = db["attachments"].update_one({"_id": object_id}, {"$set": updates})
    return result.matched_count > 0


def delete_attachment(db, attachment_id):
    """
    Elimina un adjunto mediante su ObjectId.
    """
    try:
        object_id = ObjectId(attachment_id)
    except (InvalidId, TypeError):
        return False
    result = db["attachments"].delete_one({"_id": object_id})
    return result.deleted_count > 0


def insert_sample_data(db):
    """
    Inserta datos de ejemplo en las colecciones de MongoDB.

    Esta función elimina previamente los datos existentes (solo para pruebas)
    y luego inserta documentos de muestra tanto en:
        - personal_notes (notas personales del usuario)
        - attachments (archivos adjuntos con metadatos)
    """
    personal_notes = db["personal_notes"]
    attachments = db["attachments"]

    # Limpia las colecciones antes de insertar datos de prueba
    personal_notes.delete_many({})
    attachments.delete_many({})

    # Documentos de notas personales

    notes_data = []
    today = datetime.now().date()
    for uid in range(1, 16):
        for idx in range(2):  # dos notas por usuario
            note_date = (today - timedelta(days=uid + idx)).isoformat()
            mood = max(1, min(10, 4 + (uid + idx) % 6))
            notes_data.append({
                "_id": f"note_{uid:02d}_{idx+1}",
                "user_id": uid,
                "date": note_date,
                "text": f"Nota de ejemplo {idx + 1} para el usuario {uid}. Actividad y bienestar registrados.",
                "tags": [f"usuario_{uid}", "ejemplo", "salud"],
                "mood": mood,
                "location": "Ciudad de prueba",
                "weather": {
                    "temperature": 18 + (uid % 5),
                    "condition": "soleado" if idx % 2 == 0 else "nublado"
                },
                "highlight_activity": f"Actividad ligera de {20 + idx * 10} minutos"
            })

    
    # Documentos de archivos adjuntos
   
    attachments_data = []
    for uid in range(1, 16):
        attach_date = (today - timedelta(days=uid)).isoformat()
        attachments_data.append({
            "_id": f"file_{uid:02d}_1",
            "user_id": uid,
            "date": attach_date,
            "file_path": f"/uploads/user_{uid}/{attach_date}/documento_prueba.pdf",
            "type": "pdf",
            "description": f"Documento de seguimiento del usuario {uid}",
            "category": "documento",
            "metadata": {
                "source": "generado",
                "pages": 2 + (uid % 3)
            }
        })
        attachments_data.append({
            "_id": f"file_{uid:02d}_2",
            "user_id": uid,
            "date": attach_date,
            "file_path": f"/uploads/user_{uid}/{attach_date}/foto_alimento.jpg",
            "type": "image",
            "description": f"Registro fotográfico de comida del usuario {uid}",
            "category": "alimentacion",
            "metadata": {
                "estimated_calories": 400 + (uid % 5) * 30,
                "meal_time": "13:00"
            }
        })

    # Insertar datos en MongoDB
    personal_notes.insert_many(notes_data)
    attachments.insert_many(attachments_data)

    print("✔ Datos de ejemplo insertados correctamente en MongoDB")
