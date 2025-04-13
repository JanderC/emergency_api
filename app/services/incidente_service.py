"""
Servicios para gestionar incidentes en MongoDB
"""
from flask import current_app
from app.models.incidentes import crear_documento_incidente
from datetime import datetime
from bson.objectid import ObjectId
from app import db

def reportar_incidente(usuario_id, datos):
    """
    Crea un nuevo reporte de incidente en el sistema usando MongoDB
    """
    try:
        # Validar coordenadas (asumimos que esta función existe)
        if not validar_coordenadas(datos['coordenadas_lat'], datos['coordenadas_lng']):
            return {"error": "Coordenadas inválidas"}, 400
        
        # Crear documento de incidente
        incidente = crear_documento_incidente(
            usuario_id=usuario_id,
            tipo_emergencia=datos['tipo_emergencia'],
            descripcion=datos['descripcion'],
            ubicacion=datos['ubicacion'],
            coordenadas_lat=datos['coordenadas_lat'],
            coordenadas_lng=datos['coordenadas_lng'],
            nivel_urgencia=datos['nivel_urgencia'],
            imagenes=datos.get('imagenes', [])
        )

        # Guardar en MongoDB
        result = db.incidentes.insert_one(incidente)
        incidente_id = str(result.inserted_id)

        # Notificar a bomberos disponibles (si existe la colección bomberos)
        bomberos_disponibles = list(db.bomberos.find({"estado_servicio": "disponible"}))
        for bombero in bomberos_disponibles:
            mensaje = f"Nuevo incidente reportado: {datos['tipo_emergencia']} - {datos['ubicacion']} - Nivel: {datos['nivel_urgencia']}"
            crear_notificacion(bombero["usuario_id"], incidente_id, mensaje)

        return {"mensaje": "Incidente reportado con éxito", "id": incidente_id}, 201
    
    except Exception as e:
        current_app.logger.error(f"Error al reportar incidente: {str(e)}")
        return {"error": f"Error al reportar el incidente: {str(e)}"}, 500

def obtener_incidentes(filtros=None):
    """
    Obtiene lista de incidentes con filtros opcionales desde MongoDB
    """
    try:
        # Construir filtro para MongoDB
        query = {}
        if filtros:
            for key, value in filtros.items():
                if value:
                    query[key] = value
        
        # Obtener incidentes de MongoDB
        incidentes = list(db.incidentes.find(query).sort("fecha_reporte", -1))
        
        # Convertir ObjectId a string para JSON
        for incidente in incidentes:
            incidente["_id"] = str(incidente["_id"])
        
        return incidentes, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener incidentes: {str(e)}")
        return {"error": f"Error al obtener incidentes: {str(e)}"}, 500

def obtener_incidente(incidente_id):
    """
    Obtiene detalles de un incidente específico desde MongoDB
    """
    try:
        # Convertir ID a ObjectId
        try:
            if isinstance(incidente_id, int):
                # Si es un ID numérico (como se usa en la ruta), buscamos por número
                incidente = next((inc for inc in db.incidentes.find().sort("fecha_reporte", -1) 
                                if inc.get("_id") == incidente_id), None)
            else:
                # Si es un string, intentamos convertirlo a ObjectId
                _id = ObjectId(incidente_id)
                incidente = db.incidentes.find_one({"_id": _id})
        except:
            return {"error": "ID de incidente inválido"}, 400
            
        if not incidente:
            return {"error": "Incidente no encontrado"}, 404
        
        # Convertir ObjectId a string para JSON
        incidente["_id"] = str(incidente["_id"])
        
        return incidente, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener incidente {incidente_id}: {str(e)}")
        return {"error": f"Error al obtener detalles del incidente: {str(e)}"}, 500

def actualizar_estado_incidente(incidente_id, bombero_id, ambulancia_id, nuevo_estado):
    """
    Actualiza el estado de un incidente y asigna bombero/ambulancia en MongoDB
    """
    try:
        # Convertir ID a ObjectId
        try:
            if isinstance(incidente_id, int):
                # Buscar por número secuencial si es un entero
                incidente = next((inc for inc in db.incidentes.find() 
                                if inc.get("_id") == incidente_id), None)
                if incidente:
                    _id = incidente["_id"]
                else:
                    return {"error": "Incidente no encontrado"}, 404
            else:
                # Si es un string, intentamos convertirlo a ObjectId
                _id = ObjectId(incidente_id)
                incidente = db.incidentes.find_one({"_id": _id})
        except:
            return {"error": "ID de incidente inválido"}, 400
            
        if not incidente:
            return {"error": "Incidente no encontrado"}, 404
        
        # Preparar actualización
        update_data = {"estado": nuevo_estado}
        
        # Si se asigna un bombero
        if bombero_id:
            update_data["bombero_asignado_id"] = bombero_id
            
            # Actualizar estado del bombero si existe la colección
            try:
                db.bomberos.update_one(
                    {"_id": ObjectId(bombero_id) if isinstance(bombero_id, str) else bombero_id},
                    {"$set": {"estado_servicio": "en_servicio"}}
                )
            except Exception as e:
                current_app.logger.warning(f"No se pudo actualizar el bombero: {str(e)}")
        
        # Si se asigna una ambulancia
        if ambulancia_id:
            update_data["ambulancia_id"] = ambulancia_id
            
            # Actualizar estado de la ambulancia si existe la colección
            try:
                db.ambulancias.update_one(
                    {"_id": ObjectId(ambulancia_id) if isinstance(ambulancia_id, str) else ambulancia_id},
                    {"$set": {"estado": "en_servicio", "bombero_asignado_id": bombero_id}}
                )
            except Exception as e:
                current_app.logger.warning(f"No se pudo actualizar la ambulancia: {str(e)}")
        
        # Si el estado es completado, registrar fecha de atención
        if nuevo_estado == "completado":
            update_data["fecha_atencion"] = datetime.utcnow()
            
            # Restablecer estado de bombero y ambulancia
            if incidente.get("bombero_asignado_id"):
                try:
                    db.bomberos.update_one(
                        {"_id": ObjectId(incidente["bombero_asignado_id"]) if isinstance(incidente["bombero_asignado_id"], str) else incidente["bombero_asignado_id"]},
                        {"$set": {"estado_servicio": "disponible"}}
                    )
                except Exception as e:
                    current_app.logger.warning(f"No se pudo actualizar el bombero: {str(e)}")
                
            if incidente.get("ambulancia_id"):
                try:
                    db.ambulancias.update_one(
                        {"_id": ObjectId(incidente["ambulancia_id"]) if isinstance(incidente["ambulancia_id"], str) else incidente["ambulancia_id"]},
                        {"$set": {"estado": "disponible"}}
                    )
                except Exception as e:
                    current_app.logger.warning(f"No se pudo actualizar la ambulancia: {str(e)}")
        
        # Actualizar incidente
        db.incidentes.update_one(
            {"_id": _id},
            {"$set": update_data}
        )
        
        # Notificar al usuario que reportó el incidente
        mensaje = f"Tu incidente ha sido actualizado a: {nuevo_estado}"
        crear_notificacion(incidente["usuario_id"], str(_id), mensaje)
        
        return {"mensaje": f"Estado del incidente actualizado a {nuevo_estado}"}, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al actualizar estado del incidente {incidente_id}: {str(e)}")
        return {"error": f"Error al actualizar el estado del incidente: {str(e)}"}, 500

# Funciones auxiliares

def validar_coordenadas(lat, lng):
    """
    Valida que las coordenadas estén en un rango válido:
    - Latitud: -90 a 90
    - Longitud: -180 a 180
    """
    try:
        lat_float = float(lat)
        lng_float = float(lng)
        
        if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
            return True
        return False
    except (ValueError, TypeError):
        return False

def crear_notificacion(usuario_id, incidente_id, mensaje):
    """
    Crea una nueva notificación en MongoDB
    """
    try:
        notificacion = {
            "usuario_id": usuario_id,
            "incidente_id": incidente_id,
            "mensaje": mensaje,
            "fecha": datetime.utcnow(),
            "leida": False
        }
        
        result = db.notificaciones.insert_one(notificacion)
        return {"id": str(result.inserted_id)}, 201
    
    except Exception as e:
        current_app.logger.error(f"Error al crear notificación: {str(e)}")
        return {"error": "Error al crear notificación"}, 500