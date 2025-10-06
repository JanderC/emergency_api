from bson import ObjectId
from datetime import datetime
from app import db

class ReporteRapido:
    """Modelo para reportes rápidos de emergencia"""
    
    collection = db.reportes_rapidos
    
    def __init__(self, tipo_emergencia, foto, nombre_foto, direccion,
                 coordenadas=None, usuario_id=None, estado='pendiente',
                 bombero_asignado_id=None, fecha_reporte=None, 
                 fecha_atencion=None, notas=None, _id=None):
        self.id = _id
        self.tipo_emergencia = tipo_emergencia
        self.foto = foto
        self.nombre_foto = nombre_foto
        self.direccion = direccion
        self.coordenadas = coordenadas or {}
        self.usuario_id = usuario_id
        self.estado = estado
        self.bombero_asignado_id = bombero_asignado_id
        self.fecha_reporte = fecha_reporte or datetime.utcnow()
        self.fecha_atencion = fecha_atencion
        self.notas = notas
    
    def save(self):
        """Guarda o actualiza el reporte en la base de datos"""
        reporte_data = {
            "tipo_emergencia": self.tipo_emergencia,
            "foto": self.foto,
            "nombre_foto": self.nombre_foto,
            "direccion": self.direccion,
            "coordenadas": self.coordenadas,
            "usuario_id": self.usuario_id,
            "estado": self.estado,
            "bombero_asignado_id": self.bombero_asignado_id,
            "fecha_reporte": self.fecha_reporte,
            "fecha_atencion": self.fecha_atencion,
            "notas": self.notas,
            "ultima_actualizacion": datetime.utcnow()
        }
        
        if self.id:
            result = self.collection.update_one(
                {"_id": ObjectId(self.id)}, 
                {"$set": reporte_data}
            )
            return result.modified_count > 0
        else:
            result = self.collection.insert_one(reporte_data)
            self.id = str(result.inserted_id)
            return self.id is not None
    
    @classmethod
    def find_by_id(cls, reporte_id):
        """Busca un reporte por ID"""
        try:
            reporte_data = cls.collection.find_one({"_id": ObjectId(reporte_id)})
            if reporte_data:
                return cls._from_dict(reporte_data)
        except Exception as e:
            print(f"Error finding reporte by ID: {e}")
        return None
    
    @classmethod
    def find_pendientes(cls):
        """Obtiene reportes pendientes"""
        reportes_data = cls.collection.find({"estado": "pendiente"}).sort("fecha_reporte", -1)
        return [cls._from_dict(data) for data in reportes_data]
    
    @classmethod
    def find_by_usuario(cls, usuario_id):
        """Obtiene reportes de un usuario"""
        reportes_data = cls.collection.find({"usuario_id": usuario_id}).sort("fecha_reporte", -1)
        return [cls._from_dict(data) for data in reportes_data]
    
    @classmethod
    def _from_dict(cls, data):
        """Crea una instancia desde un diccionario"""
        return cls(
            _id=str(data["_id"]),
            tipo_emergencia=data["tipo_emergencia"],
            foto=data["foto"],
            nombre_foto=data["nombre_foto"],
            direccion=data["direccion"],
            coordenadas=data.get("coordenadas", {}),
            usuario_id=data.get("usuario_id"),
            estado=data.get("estado", "pendiente"),
            bombero_asignado_id=data.get("bombero_asignado_id"),
            fecha_reporte=data.get("fecha_reporte", datetime.utcnow()),
            fecha_atencion=data.get("fecha_atencion"),
            notas=data.get("notas")
        )
    
    def asignar_bombero(self, bombero_id):
        """Asigna un bombero al reporte"""
        self.bombero_asignado_id = bombero_id
        self.estado = "en_atencion"
        return self.save()
    
    def marcar_atendido(self, notas=None):
        """Marca el reporte como atendido"""
        self.estado = "atendido"
        self.fecha_atencion = datetime.utcnow()
        if notas:
            self.notas = notas
        return self.save()
    
    def to_dict(self):
        """Convierte el reporte a un diccionario"""
        return {
            "_id": str(self.id) if self.id else None,
            "tipo_emergencia": self.tipo_emergencia,
            "foto": self.foto,
            "nombre_foto": self.nombre_foto,
            "direccion": self.direccion,
            "coordenadas": self.coordenadas,
            "usuario_id": self.usuario_id,
            "estado": self.estado,
            "bombero_asignado_id": self.bombero_asignado_id,
            "fecha_reporte": self.fecha_reporte.isoformat() if self.fecha_reporte else None,
            "fecha_atencion": self.fecha_atencion.isoformat() if self.fecha_atencion else None,
            "notas": self.notas
        }