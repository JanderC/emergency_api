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
                 fecha_registro=None, _id=None):
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
    def find_by_id(cls, bombero_id):
        """Busca un bombero por su ID de MongoDB"""
        try:
            bombero_data = cls.collection.find_one({"_id": ObjectId(bombero_id)})
            if bombero_data:
                return cls._from_dict(bombero_data)
        except Exception as e:
            print(f"Error finding bombero by ID: {e}")
        return None
    
    @classmethod
    def find_by_usuario_id(cls, usuario_id):
        """Busca un bombero por el ID del usuario"""
        bombero_data = cls.collection.find_one({"usuario_id": usuario_id})
        if bombero_data:
            return cls._from_dict(bombero_data)
        return None
    
    @classmethod
    def find_by_codigo(cls, codigo_bombero):
        """Busca un bombero por su código de bombero"""
        bombero_data = cls.collection.find_one({"codigo_bombero": codigo_bombero})
        if bombero_data:
            return cls._from_dict(bombero_data)
        return None
    
    @classmethod
    def find_disponibles(cls):
        """Obtiene todos los bomberos disponibles"""
        bomberos_data = cls.collection.find({"estado_servicio": "disponible"})
        return [cls._from_dict(data) for data in bomberos_data]
    
    @classmethod
    def find_all(cls, filtros=None):
        """Obtiene todos los bomberos con filtros opcionales"""
        query = filtros or {}
        bomberos_data = cls.collection.find(query).sort("fecha_registro", -1)
        return [cls._from_dict(data) for data in bomberos_data]
    
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
            fecha_registro=data.get("fecha_registro", datetime.utcnow())
        )
    
    def update_estado(self, nuevo_estado):
        """Actualiza el estado de servicio del bombero"""
        estados_validos = ['disponible', 'en_servicio', 'fuera_servicio', 'descanso']
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado inválido. Estados válidos: {estados_validos}")
        
        self.estado_servicio = nuevo_estado
        result = self.collection.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "estado_servicio": nuevo_estado,
                    "ultima_actualizacion": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    def update_ubicacion(self, lat, lng):
        """Actualiza la ubicación actual del bombero"""
        self.ubicacion_actual = {
            "lat": float(lat),
            "lng": float(lng),
            "timestamp": datetime.utcnow()
        }
        result = self.collection.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "ubicacion_actual": self.ubicacion_actual,
                    "ultima_actualizacion": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    def incrementar_incidentes(self):
        """Incrementa el contador de incidentes atendidos"""
        result = self.collection.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$inc": {"incidentes_atendidos": 1},
                "$set": {"ultima_actualizacion": datetime.utcnow()}
            }
        )
        if result.modified_count > 0:
            self.incidentes_atendidos += 1
        return result.modified_count > 0
    
    def incrementar_turnos(self):
        """Incrementa el contador de turnos completados"""
        result = self.collection.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$inc": {"turnos_completados": 1},
                "$set": {"ultima_actualizacion": datetime.utcnow()}
            }
        )
        if result.modified_count > 0:
            self.turnos_completados += 1
        return result.modified_count > 0
    
    def asignar_ambulancia(self, ambulancia_id):
        """Asigna una ambulancia al bombero"""
        self.ambulancia_id = ambulancia_id
        result = self.collection.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "ambulancia_id": ambulancia_id,
                    "ultima_actualizacion": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    def desasignar_ambulancia(self):
        """Remueve la ambulancia asignada al bombero"""
        self.ambulancia_id = None
        result = self.collection.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "ambulancia_id": None,
                    "ultima_actualizacion": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
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
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None
        }