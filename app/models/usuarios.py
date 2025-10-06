# app/models/usuarios.py
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime
from app import db

class Usuario:
    """Usuario model for MongoDB"""
    
    collection = db.usuarios
    
    def __init__(self, nombre, apellido, email, cedula='', direccion='', 
                 telefono='', es_bombero=False, foto_perfil='', 
                 password_hash=None, fecha_registro=None, activo=True, _id=None):
        self.id = _id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.cedula = cedula  # NUEVO
        self.direccion = direccion  # NUEVO
        self.password_hash = password_hash
        self.telefono = telefono
        self.es_bombero = es_bombero
        self.foto_perfil = foto_perfil
        self.fecha_registro = fecha_registro or datetime.utcnow()
        self.activo = activo
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        user_data = {
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "cedula": self.cedula,  # NUEVO
            "direccion": self.direccion,  # NUEVO
            "password_hash": self.password_hash,
            "telefono": self.telefono,
            "es_bombero": self.es_bombero,
            "foto_perfil": self.foto_perfil,
            "fecha_registro": self.fecha_registro,
            "activo": self.activo
        }
        
        if self.id:
            result = self.collection.update_one({"_id": ObjectId(self.id)}, {"$set": user_data})
            return result.modified_count > 0
        else:
            result = self.collection.insert_one(user_data)
            self.id = str(result.inserted_id)
            return self.id is not None
    
    @classmethod
    def find_by_email(cls, email):
        user_data = db.usuarios.find_one({"email": email})
        if user_data:
            return cls(
                _id=str(user_data["_id"]),
                nombre=user_data["nombre"],
                apellido=user_data["apellido"],
                email=user_data["email"],
                cedula=user_data.get("cedula", ""),  # NUEVO
                direccion=user_data.get("direccion", ""),  # NUEVO
                telefono=user_data.get("telefono", ""),
                es_bombero=user_data.get("es_bombero", False),
                foto_perfil=user_data.get("foto_perfil", ""),
                password_hash=user_data.get("password_hash", ""),
                fecha_registro=user_data.get("fecha_registro", datetime.utcnow()),
                activo=user_data.get("activo", True)
            )
        return None
    
    @classmethod
    def find_by_cedula(cls, cedula):
        """Busca un usuario por cédula"""
        user_data = db.usuarios.find_one({"cedula": cedula})
        if user_data:
            return cls(
                _id=str(user_data["_id"]),
                nombre=user_data["nombre"],
                apellido=user_data["apellido"],
                email=user_data["email"],
                cedula=user_data.get("cedula", ""),
                direccion=user_data.get("direccion", ""),
                telefono=user_data.get("telefono", ""),
                es_bombero=user_data.get("es_bombero", False),
                foto_perfil=user_data.get("foto_perfil", ""),
                password_hash=user_data.get("password_hash", ""),
                fecha_registro=user_data.get("fecha_registro", datetime.utcnow()),
                activo=user_data.get("activo", True)
            )
        return None
    
    @classmethod
    def find_by_id(cls, user_id):
        try:
            user_data = db.usuarios.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return cls(
                    _id=str(user_data["_id"]),
                    nombre=user_data["nombre"],
                    apellido=user_data["apellido"],
                    email=user_data["email"],
                    cedula=user_data.get("cedula", ""),  # NUEVO
                    direccion=user_data.get("direccion", ""),  # NUEVO
                    telefono=user_data.get("telefono", ""),
                    es_bombero=user_data.get("es_bombero", False),
                    foto_perfil=user_data.get("foto_perfil", ""),
                    password_hash=user_data.get("password_hash", ""),
                    fecha_registro=user_data.get("fecha_registro", datetime.utcnow()),
                    activo=user_data.get("activo", True)
                )
        except Exception as e:
            print(f"Error finding user by ID: {e}")
            pass
        return None
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "cedula": self.cedula,  # NUEVO
            "direccion": self.direccion,  # NUEVO
            "telefono": self.telefono,
            "es_bombero": self.es_bombero,
            "foto_perfil": self.foto_perfil,
            "fecha_registro": self.fecha_registro,
            "activo": self.activo
        }