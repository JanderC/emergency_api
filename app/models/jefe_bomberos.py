# app/models/jefe_bomberos.py
from bson import ObjectId
from datetime import datetime
from app import db

class JefeBomberos:
    """Modelo para Jefe de Bomberos"""
    
    collection = db.jefes_bomberos
    
    def __init__(self, usuario_id, codigo_jefe, estacion_asignada,
                 fecha_asignacion=None, activo=True, _id=None):
        self.id = _id
        self.usuario_id = usuario_id
        self.codigo_jefe = codigo_jefe
        self.estacion_asignada = estacion_asignada
        self.fecha_asignacion = fecha_asignacion or datetime.utcnow()
        self.activo = activo
    
    def save(self):
        """Guarda o actualiza el jefe en la base de datos"""
        jefe_data = {
            "usuario_id": self.usuario_id,
            "codigo_jefe": self.codigo_jefe,
            "estacion_asignada": self.estacion_asignada,
            "fecha_asignacion": self.fecha_asignacion,
            "activo": self.activo,
            "ultima_actualizacion": datetime.utcnow()
        }
        
        if self.id:
            result = self.collection.update_one(
                {"_id": ObjectId(self.id)}, 
                {"$set": jefe_data}
            )
            return result.modified_count > 0
        else:
            result = self.collection.insert_one(jefe_data)
            self.id = str(result.inserted_id)
            return self.id is not None
    
    @classmethod
    def find_by_usuario_id(cls, usuario_id):
        """Busca un jefe por el ID del usuario"""
        jefe_data = cls.collection.find_one({"usuario_id": usuario_id, "activo": True})
        if jefe_data:
            return cls._from_dict(jefe_data)
        return None
    
    @classmethod
    def find_by_codigo(cls, codigo_jefe):
        """Busca un jefe por su código"""
        jefe_data = cls.collection.find_one({"codigo_jefe": codigo_jefe, "activo": True})
        if jefe_data:
            return cls._from_dict(jefe_data)
        return None
    
    @classmethod
    def _from_dict(cls, data):
        """Crea una instancia desde un diccionario"""
        return cls(
            _id=str(data["_id"]),
            usuario_id=data["usuario_id"],
            codigo_jefe=data["codigo_jefe"],
            estacion_asignada=data["estacion_asignada"],
            fecha_asignacion=data.get("fecha_asignacion", datetime.utcnow()),
            activo=data.get("activo", True)
        )
    
    def to_dict(self):
        """Convierte el jefe a un diccionario"""
        return {
            "_id": str(self.id) if self.id else None,
            "usuario_id": self.usuario_id,
            "codigo_jefe": self.codigo_jefe,
            "estacion_asignada": self.estacion_asignada,
            "fecha_asignacion": self.fecha_asignacion.isoformat() if self.fecha_asignacion else None,
            "activo": self.activo
        }