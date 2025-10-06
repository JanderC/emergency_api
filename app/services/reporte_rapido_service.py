"""
Servicio para gestionar reportes rápidos de emergencia
"""
from flask import current_app
from app import db
from datetime import datetime
from bson.objectid import ObjectId

def crear_reporte_rapido(datos, usuario_id=None):
    """
    Crea un reporte rápido de emergencia
    Solo requiere: tipo_emergencia, foto, nombre_foto, direccion
    """
    try:
        # Preparar coordenadas si existen
        coordenadas = {}
        if 'lat' in datos and 'lng' in datos:
            coordenadas = {
                "lat": float(datos['lat']),
                "lng": float(datos['lng'])
            }
        
        # Crear reporte
        reporte_data = {
            "tipo_emergencia": datos['tipo_emergencia'],
            "foto": datos['foto'],
            "nombre_foto": datos['nombre_foto'],
            "direccion": datos['direccion'],
            "coordenadas": coordenadas,
            "usuario_id": usuario_id,
            "estado": "pendiente",
            "bombero_asignado_id": None,
            "fecha_reporte": datetime.utcnow(),
            "fecha_atencion": None,
            "notas": None
        }
        
        result = db.reportes_rapidos.insert_one(reporte_data)
        
        return {
            "mensaje": "Reporte de emergencia enviado exitosamente",
            "reporte_id": str(result.inserted_id),
            "tipo_emergencia": datos['tipo_emergencia'],
            "estado": "pendiente"
        }, 201
    
    except Exception as e:
        current_app.logger.error(f"Error al crear reporte rápido: {str(e)}")
        return {"error": "Error al crear el reporte"}, 500

def obtener_reportes_pendientes():
    """
    Obtiene todos los reportes rápidos pendientes
    """
    try:
        reportes = list(db.reportes_rapidos.find({
            "estado": "pendiente"
        }).sort("fecha_reporte", -1))
        
        reportes_formateados = []
        for reporte in reportes:
            reporte["_id"] = str(reporte["_id"])
            
            # Si tiene usuario, agregar info básica
            if reporte.get("usuario_id"):
                usuario = db.usuarios.find_one({"_id": ObjectId(reporte["usuario_id"])})
                if usuario:
                    reporte["usuario_info"] = {
                        "nombre": f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}",
                        "telefono": usuario.get("telefono", "")
                    }
            
            reportes_formateados.append(reporte)
        
        return reportes_formateados, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener reportes pendientes: {str(e)}")
        return {"error": "Error al obtener reportes"}, 500

def obtener_reporte_por_id(reporte_id):
    """
    Obtiene un reporte específico por ID
    """
    try:
        reporte = db.reportes_rapidos.find_one({"_id": ObjectId(reporte_id)})
        if not reporte:
            return {"error": "Reporte no encontrado"}, 404
        
        reporte["_id"] = str(reporte["_id"])
        
        # Agregar info del usuario si existe
        if reporte.get("usuario_id"):
            usuario = db.usuarios.find_one({"_id": ObjectId(reporte["usuario_id"])})
            if usuario:
                reporte["usuario_info"] = {
                    "nombre": f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}",
                    "telefono": usuario.get("telefono", ""),
                    "email": usuario.get("email", "")
                }
        
        # Agregar info del bombero si está asignado
        if reporte.get("bombero_asignado_id"):
            bombero = db.bomberos.find_one({"usuario_id": reporte["bombero_asignado_id"]})
            if bombero:
                usuario_bombero = db.usuarios.find_one({"_id": ObjectId(reporte["bombero_asignado_id"])})
                if usuario_bombero:
                    reporte["bombero_info"] = {
                        "nombre": f"{usuario_bombero.get('nombre', '')} {usuario_bombero.get('apellido', '')}",
                        "codigo_bombero": bombero.get("codigo_bombero", "")
                    }
        
        return reporte, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener reporte: {str(e)}")
        return {"error": "Error al obtener el reporte"}, 500

def asignar_bombero_a_reporte(reporte_id, bombero_id):
    """
    Asigna un bombero a un reporte rápido
    """
    try:
        # Verificar que el reporte existe
        reporte = db.reportes_rapidos.find_one({"_id": ObjectId(reporte_id)})
        if not reporte:
            return {"error": "Reporte no encontrado"}, 404
        
        # Verificar que el bombero existe y está disponible
        bombero = db.bomberos.find_one({
            "usuario_id": bombero_id,
            "estado_servicio": "disponible"
        })
        if not bombero:
            return {"error": "Bombero no disponible"}, 400
        
        # Asignar bombero
        db.reportes_rapidos.update_one(
            {"_id": ObjectId(reporte_id)},
            {
                "$set": {
                    "bombero_asignado_id": bombero_id,
                    "estado": "en_atencion",
                    "ultima_actualizacion": datetime.utcnow()
                }
            }
        )
        
        # Cambiar estado del bombero
        db.bomberos.update_one(
            {"usuario_id": bombero_id},
            {"$set": {"estado_servicio": "en_servicio"}}
        )
        
        return {
            "mensaje": "Bombero asignado exitosamente",
            "reporte_id": reporte_id,
            "bombero_id": bombero_id
        }, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al asignar bombero: {str(e)}")
        return {"error": "Error al asignar bombero"}, 500

def marcar_reporte_atendido(reporte_id, notas=None):
    """
    Marca un reporte como atendido
    """
    try:
        reporte = db.reportes_rapidos.find_one({"_id": ObjectId(reporte_id)})
        if not reporte:
            return {"error": "Reporte no encontrado"}, 404
        
        update_data = {
            "estado": "atendido",
            "fecha_atencion": datetime.utcnow(),
            "ultima_actualizacion": datetime.utcnow()
        }
        
        if notas:
            update_data["notas"] = notas
        
        db.reportes_rapidos.update_one(
            {"_id": ObjectId(reporte_id)},
            {"$set": update_data}
        )
        
        # Si tiene bombero asignado, cambiar su estado a disponible
        if reporte.get("bombero_asignado_id"):
            db.bomberos.update_one(
                {"usuario_id": reporte["bombero_asignado_id"]},
                {"$set": {"estado_servicio": "disponible"}}
            )
            
            # Incrementar contador de incidentes atendidos
            db.bomberos.update_one(
                {"usuario_id": reporte["bombero_asignado_id"]},
                {"$inc": {"incidentes_atendidos": 1}}
            )
        
        return {
            "mensaje": "Reporte marcado como atendido",
            "reporte_id": reporte_id
        }, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al marcar reporte atendido: {str(e)}")
        return {"error": "Error al actualizar reporte"}, 500

def obtener_reportes_por_usuario(usuario_id):
    """
    Obtiene todos los reportes de un usuario específico
    """
    try:
        reportes = list(db.reportes_rapidos.find({
            "usuario_id": usuario_id
        }).sort("fecha_reporte", -1))
        
        for reporte in reportes:
            reporte["_id"] = str(reporte["_id"])
            
            # Agregar info del bombero si fue asignado
            if reporte.get("bombero_asignado_id"):
                bombero = db.bomberos.find_one({"usuario_id": reporte["bombero_asignado_id"]})
                if bombero:
                    usuario_bombero = db.usuarios.find_one({"_id": ObjectId(reporte["bombero_asignado_id"])})
                    if usuario_bombero:
                        reporte["bombero_info"] = {
                            "nombre": f"{usuario_bombero.get('nombre', '')} {usuario_bombero.get('apellido', '')}",
                            "codigo_bombero": bombero.get("codigo_bombero", "")
                        }
        
        return reportes, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener reportes del usuario: {str(e)}")
        return {"error": "Error al obtener reportes"}, 500