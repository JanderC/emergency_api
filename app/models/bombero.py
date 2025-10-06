# app/models/bombero.py
from bson import ObjectId
from datetime import datetime
from app import db

class Bombero:
    """Bombero model for MongoDB"""
    
    collection = db.bomberos
    
    def __init__(self, usuario_id, codigo_bombero, estacion_pertenencia, 
                 rango='bombero', especialidades=None, certificaciones=None,
                 estado_servicio='disponible', carnet_foto=None, 
                 experiencia_anos=0, contacto_emergencia=None,
                 ambulancia_id=None, ubicacion_actual=None,
                 turnos_completados=0, incidentes_atendidos=0,
                 estado_aprobacion='pendiente', aprobado_por=None,  # NUEVO
                 fecha_aprobacion=None, fecha_registro=None, _id=None):  # NUEVO
        self.id = _id
        self.usuario_id = usuario_id
        self.codigo_bombero = codigo_bombero
        self.estacion_pertenencia = estacion_pertenencia
        self.rango = rango
        self.especialidades = especialidades or []
        self.certificaciones = certificaciones or []
        self.estado_servicio = estado_servicio
        self.carnet_foto = carnet_foto
        self.experiencia_anos = experiencia_anos
        self.contacto_emergencia = contacto_emergencia or {}
        self.ambulancia_id = ambulancia_id
        self.ubicacion_actual = ubicacion_actual
        self.turnos_completados = turnos_completados
        self.incidentes_atendidos = incidentes_atendidos
        self.estado_aprobacion = estado_aprobacion  # NUEVO
        self.aprobado_por = aprobado_por  # NUEVO
        self.fecha_aprobacion = fecha_aprobacion  # NUEVO
        self.fecha_registro = fecha_registro or datetime.utcnow()
    
    def save(self):
        """Guarda o actualiza el bombero en la base de datos"""
        bombero_data = {
            "usuario_id": self.usuario_id,
            "codigo_bombero": self.codigo_bombero,
            "estacion_pertenencia": self.estacion_pertenencia,
            "rango": self.rango,
            "especialidades": self.especialidades,
            "certificaciones": self.certificaciones,
            "estado_servicio": self.estado_servicio,
            "carnet_foto": self.carnet_foto,
            "experiencia_anos": self.experiencia_anos,
            "contacto_emergencia": self.contacto_emergencia,
            "ambulancia_id": self.ambulancia_id,
            "ubicacion_actual": self.ubicacion_actual,
            "turnos_completados": self.turnos_completados,
            "incidentes_atendidos": self.incidentes_atendidos,
            "estado_aprobacion": self.estado_aprobacion,  # NUEVO
            "aprobado_por": self.aprobado_por,  # NUEVO
            "fecha_aprobacion": self.fecha_aprobacion,  # NUEVO
            "fecha_registro": self.fecha_registro,
            "ultima_actualizacion": datetime.utcnow()
        }
        
        if self.id:
            result = self.collection.update_one(
                {"_id": ObjectId(self.id)}, 
                {"$set": bombero_data}
            )
            return result.modified_count > 0
        else:
            result = self.collection.insert_one(bombero_data)
            self.id = str(result.inserted_id)
            return self.id is not None
    
    @classmethod
    def find_pendientes_aprobacion(cls):
        """Obtiene bomberos pendientes de aprobación"""
        bomberos_data = cls.collection.find({"estado_aprobacion": "pendiente"}).sort("fecha_registro", -1)
        return [cls._from_dict(data) for data in bomberos_data]
    
    def aprobar(self, jefe_id):
        """Aprueba el registro del bombero"""
        self.estado_aprobacion = "aprobado"
        self.aprobado_por = jefe_id
        self.fecha_aprobacion = datetime.utcnow()
        
        result = self.collection.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "estado_aprobacion": "aprobado",
                    "aprobado_por": jefe_id,
                    "fecha_aprobacion": datetime.utcnow(),
                    "ultima_actualizacion": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    def rechazar(self, jefe_id):
        """Rechaza el registro del bombero"""
        self.estado_aprobacion = "rechazado"
        self.aprobado_por = jefe_id
        self.fecha_aprobacion = datetime.utcnow()
        
        result = self.collection.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "estado_aprobacion": "rechazado",
                    "aprobado_por": jefe_id,
                    "fecha_aprobacion": datetime.utcnow(),
                    "ultima_actualizacion": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    # ... (mantén todos los demás métodos existentes)
    
    @classmethod
    def _from_dict(cls, data):
        """Crea una instancia de Bombero desde un diccionario"""
        return cls(
            _id=str(data["_id"]),
            usuario_id=data["usuario_id"],
            codigo_bombero=data["codigo_bombero"],
            estacion_pertenencia=data["estacion_pertenencia"],
            rango=data.get("rango", "bombero"),
            especialidades=data.get("especialidades", []),
            certificaciones=data.get("certificaciones", []),
            estado_servicio=data.get("estado_servicio", "disponible"),
            carnet_foto=data.get("carnet_foto"),
            experiencia_anos=data.get("experiencia_anos", 0),
            contacto_emergencia=data.get("contacto_emergencia", {}),
            ambulancia_id=data.get("ambulancia_id"),
            ubicacion_actual=data.get("ubicacion_actual"),
            turnos_completados=data.get("turnos_completados", 0),
            incidentes_atendidos=data.get("incidentes_atendidos", 0),
            estado_aprobacion=data.get("estado_aprobacion", "pendiente"),  # NUEVO
            aprobado_por=data.get("aprobado_por"),  # NUEVO
            fecha_aprobacion=data.get("fecha_aprobacion"),  # NUEVO
            fecha_registro=data.get("fecha_registro", datetime.utcnow())
        )
    
    def to_dict(self):
        """Convierte el bombero a un diccionario"""
        return {
            "_id": str(self.id) if self.id else None,
            "usuario_id": self.usuario_id,
            "codigo_bombero": self.codigo_bombero,
            "estacion_pertenencia": self.estacion_pertenencia,
            "rango": self.rango,
            "especialidades": self.especialidades,
            "certificaciones": self.certificaciones,
            "estado_servicio": self.estado_servicio,
            "carnet_foto": self.carnet_foto,
            "experiencia_anos": self.experiencia_anos,
            "contacto_emergencia": self.contacto_emergencia,
            "ambulancia_id": self.ambulancia_id,
            "ubicacion_actual": self.ubicacion_actual,
            "turnos_completados": self.turnos_completados,
            "incidentes_atendidos": self.incidentes_atendidos,
            "estado_aprobacion": self.estado_aprobacion,  # NUEVO
            "aprobado_por": self.aprobado_por,  # NUEVO
            "fecha_aprobacion": self.fecha_aprobacion.isoformat() if self.fecha_aprobacion else None,  # NUEVO
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None
        }