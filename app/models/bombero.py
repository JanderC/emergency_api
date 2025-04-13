# app/models/bombero.py
from bson import ObjectId
from datetime import datetime
from app import db

class Bombero:
    """Bombero model for MongoDB"""
    
    collection = db.bomberos
    
    def __init__(self, usuario_id, codigo_bombero, estacion_pertenencia, 
                 estado_servicio='disponible', carnet_foto='', _id=None):
        self.id = _id
        self.usuario_id = usuario_id
        self.codigo_bombero = codigo_bombero
        self.estacion_pertenencia = estacion_pertenencia
        self.estado_servicio = estado_servicio
        self.carnet_foto = carnet_foto
    
    def save(self):
        bombero_data = {
            "usuario_id": self.usuario_id,
            "codigo_bombero": self.codigo_bombero,
            "estacion_pertenencia": self.estacion_pertenencia,
            "estado_servicio": self.estado_servicio,
            "carnet_foto": self.carnet_foto
        }
        
        if self.id:
            result = self.collection.update_one({"_id": ObjectId(self.id)}, {"$set": bombero_data})
            return result.modified_count > 0
        else:
            result = self.collection.insert_one(bombero_data)
            self.id = str(result.inserted_id)
            return self.id is not None
    
    @classmethod
    def find_by_id(cls, bombero_id):
        try:
            bombero_data = cls.collection.find_one({"_id": ObjectId(bombero_id)})
            if bombero_data:
                return cls(
                    _id=str(bombero_data["_id"]),
                    usuario_id=bombero_data["usuario_id"],
                    codigo_bombero=bombero_data["codigo_bombero"],
                    estacion_pertenencia=bombero_data["estacion_pertenencia"],
                    estado_servicio=bombero_data.get("estado_servicio", "disponible"),
                    carnet_foto=bombero_data.get("carnet_foto", "")
                )
        except Exception as e:
            print(f"Error finding bombero by ID: {e}")
        return None
    
    @classmethod
    def find_by_usuario_id(cls, usuario_id):
        bombero_data = cls.collection.find_one({"usuario_id": usuario_id})
        if bombero_data:
            return cls(
                _id=str(bombero_data["_id"]),
                usuario_id=bombero_data["usuario_id"],
                codigo_bombero=bombero_data["codigo_bombero"],
                estacion_pertenencia=bombero_data["estacion_pertenencia"],
                estado_servicio=bombero_data.get("estado_servicio", "disponible"),
                carnet_foto=bombero_data.get("carnet_foto", "")
            )
        return None
    
    @classmethod
    def find_by_codigo(cls, codigo_bombero):
        bombero_data = cls.collection.find_one({"codigo_bombero": codigo_bombero})
        if bombero_data:
            return cls(
                _id=str(bombero_data["_id"]),
                usuario_id=bombero_data["usuario_id"],
                codigo_bombero=bombero_data["codigo_bombero"],
                estacion_pertenencia=bombero_data["estacion_pertenencia"],
                estado_servicio=bombero_data.get("estado_servicio", "disponible"),
                carnet_foto=bombero_data.get("carnet_foto", "")
            )
        return None
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "usuario_id": self.usuario_id,
            "codigo_bombero": self.codigo_bombero,
            "estacion_pertenencia": self.estacion_pertenencia,
            "estado_servicio": self.estado_servicio,
            "carnet_foto": self.carnet_foto
        }   