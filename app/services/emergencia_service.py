# app/services/emergencia_service.py
"""
Servicio para que los bomberos gestionen emergencias (tomar, cambiar estado)
"""
from flask import current_app
from app import db
from datetime import datetime
from bson.objectid import ObjectId

def tomar_emergencia(bombero_id, incidente_id):
    """
    Permite que un bombero tome una emergencia disponible
    """
    try:
        # Convertir IDs a ObjectId si es necesario
        if isinstance(incidente_id, str):
            try:
                _id = ObjectId(incidente_id)
            except:
                return {"error": "ID de incidente inválido"}, 400
        else:
            _id = incidente_id

        # Buscar el incidente
        incidente = db.incidentes.find_one({"_id": _id})
        if not incidente:
            return {"error": "Incidente no encontrado"}, 404

        # Verificar que el incidente esté disponible para ser tomado
        if incidente.get("estado") != "reportado":
            return {"error": "El incidente no está disponible para ser tomado"}, 400

        if incidente.get("bombero_asignado_id"):
            return {"error": "El incidente ya está asignado a otro bombero"}, 400

        # Verificar que el bombero existe y está disponible
        bombero = db.bomberos.find_one({"usuario_id": bombero_id})
        if not bombero:
            return {"error": "Bombero no encontrado"}, 404

        if bombero.get("estado_servicio") != "disponible":
            return {"error": "El bombero no está disponible"}, 400

        # Asignar el incidente al bombero
        update_result = db.incidentes.update_one(
            {"_id": _id},
            {
                "$set": {
                    "bombero_asignado_id": bombero_id,
                    "estado": "en_proceso",
                    "fecha_asignacion": datetime.utcnow()
                }
            }
        )

        if update_result.modified_count == 0:
            return {"error": "No se pudo asignar el incidente"}, 500

        # Actualizar estado del bombero
        db.bomberos.update_one(
            {"usuario_id": bombero_id},
            {"$set": {"estado_servicio": "en_servicio"}}
        )

        # Crear notificación al usuario que reportó
        crear_notificacion_emergencia(
            incidente["usuario_id"], 
            str(_id), 
            f"Un bombero ha tomado tu emergencia y está en camino"
        )

        return {
            "mensaje": "Emergencia tomada exitosamente",
            "incidente_id": str(_id),
            "estado": "en_proceso"
        }, 200

    except Exception as e:
        current_app.logger.error(f"Error al tomar emergencia: {str(e)}")
        return {"error": f"Error al tomar la emergencia: {str(e)}"}, 500

def liberar_emergencia(bombero_id, incidente_id, razon):
    """
    Permite que un bombero libere una emergencia asignada
    """
    try:
        # Convertir ID a ObjectId
        if isinstance(incidente_id, str):
            try:
                _id = ObjectId(incidente_id)
            except:
                return {"error": "ID de incidente inválido"}, 400
        else:
            _id = incidente_id

        # Buscar el incidente
        incidente = db.incidentes.find_one({"_id": _id})
        if not incidente:
            return {"error": "Incidente no encontrado"}, 404

        # Verificar que el bombero es el asignado
        if str(incidente.get("bombero_asignado_id")) != str(bombero_id):
            return {"error": "No tienes permisos para liberar este incidente"}, 403

        # Liberar el incidente
        db.incidentes.update_one(
            {"_id": _id},
            {
                "$set": {
                    "estado": "reportado",
                    "fecha_liberacion": datetime.utcnow(),
                    "razon_liberacion": razon
                },
                "$unset": {
                    "bombero_asignado_id": "",
                    "fecha_asignacion": ""
                }
            }
        )

        # Actualizar estado del bombero a disponible
        db.bomberos.update_one(
            {"usuario_id": bombero_id},
            {"$set": {"estado_servicio": "disponible"}}
        )

        # Notificar al usuario
        crear_notificacion_emergencia(
            incidente["usuario_id"], 
            str(_id), 
            f"Tu emergencia ha sido liberada. Motivo: {razon}"
        )

        return {
            "mensaje": "Emergencia liberada exitosamente",
            "incidente_id": str(_id)
        }, 200

    except Exception as e:
        current_app.logger.error(f"Error al liberar emergencia: {str(e)}")
        return {"error": f"Error al liberar la emergencia: {str(e)}"}, 500

def obtener_emergencias_bombero(bombero_id, filtros=None):
    """
    Obtiene las emergencias asignadas a un bombero específico
    """
    try:
        query = {"bombero_asignado_id": bombero_id}
        
        # Aplicar filtros adicionales
        if filtros:
            if filtros.get("estado"):
                query["estado"] = filtros["estado"]
            if filtros.get("fecha_desde"):
                query["fecha_reporte"] = {"$gte": filtros["fecha_desde"]}

        emergencias = list(db.incidentes.find(query).sort("fecha_reporte", -1))
        
        # Convertir ObjectIds a string
        for emergencia in emergencias:
            emergencia["_id"] = str(emergencia["_id"])

        return emergencias, 200

    except Exception as e:
        current_app.logger.error(f"Error al obtener emergencias del bombero: {str(e)}")
        return {"error": "Error al obtener emergencias"}, 500

def obtener_emergencias_disponibles(filtros=None):
    """
    Obtiene emergencias disponibles para ser tomadas por bomberos
    """
    try:
        query = {
            "estado": "reportado",
            "$or": [
                {"bombero_asignado_id": {"$exists": False}},
                {"bombero_asignado_id": None}
            ]
        }
        
        # Aplicar filtros
        if filtros:
            if filtros.get("nivel_urgencia"):
                query["nivel_urgencia"] = filtros["nivel_urgencia"]
            if filtros.get("tipo_emergencia"):
                query["tipo_emergencia"] = filtros["tipo_emergencia"]

        emergencias = list(db.incidentes.find(query).sort([
            ("nivel_urgencia", -1),  # Primero por urgencia (alta, media, baja)
            ("fecha_reporte", 1)     # Luego por fecha (más antiguos primero)
        ]))
        
        # Convertir ObjectIds a string
        for emergencia in emergencias:
            emergencia["_id"] = str(emergencia["_id"])

        return emergencias, 200

    except Exception as e:
        current_app.logger.error(f"Error al obtener emergencias disponibles: {str(e)}")
        return {"error": "Error al obtener emergencias disponibles"}, 500

def actualizar_ubicacion_bombero(bombero_id, coordenadas_lat, coordenadas_lng):
    """
    Actualiza la ubicación actual del bombero
    """
    try:
        # Validar coordenadas
        if not validar_coordenadas(coordenadas_lat, coordenadas_lng):
            return {"error": "Coordenadas inválidas"}, 400

        # Actualizar ubicación del bombero
        result = db.bomberos.update_one(
            {"usuario_id": bombero_id},
            {
                "$set": {
                    "ubicacion_actual": {
                        "lat": float(coordenadas_lat),
                        "lng": float(coordenadas_lng),
                        "ultima_actualizacion": datetime.utcnow()
                    }
                }
            }
        )

        if result.modified_count == 0:
            return {"error": "No se pudo actualizar la ubicación"}, 500

        return {"mensaje": "Ubicación actualizada exitosamente"}, 200

    except Exception as e:
        current_app.logger.error(f"Error al actualizar ubicación del bombero: {str(e)}")
        return {"error": "Error al actualizar ubicación"}, 500

# Funciones auxiliares
def validar_coordenadas(lat, lng):
    """
    Valida que las coordenadas estén en un rango válido
    """
    try:
        lat_float = float(lat)
        lng_float = float(lng)
        
        if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
            return True
        return False
    except (ValueError, TypeError):
        return False

def crear_notificacion_emergencia(usuario_id, incidente_id, mensaje):
    """
    Crea una notificación para emergencias
    """
    try:
        notificacion = {
            "usuario_id": str(usuario_id),
            "incidente_id": incidente_id,
            "mensaje": mensaje,
            "tipo": "emergencia",
            "fecha": datetime.utcnow(),
            "leida": False
        }
        
        result = db.notificaciones.insert_one(notificacion)
        return {"id": str(result.inserted_id)}, 201
    
    except Exception as e:
        current_app.logger.error(f"Error al crear notificación: {str(e)}")
        return {"error": "Error al crear notificación"}, 500