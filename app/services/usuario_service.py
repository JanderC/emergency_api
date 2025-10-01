# app/services/usuario_service_mongo.py
"""
Servicio completo para gestionar usuarios en MongoDB
"""
from flask import current_app
from app import db
from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash

def obtener_perfil_usuario(usuario_id):
    """
    Obtiene el perfil completo de un usuario
    """
    try:
        # Convertir a ObjectId
        if isinstance(usuario_id, str):
            try:
                _id = ObjectId(usuario_id)
            except:
                return {"error": "ID de usuario inválido"}, 400
        else:
            _id = usuario_id
        
        # Buscar usuario
        usuario = db.usuarios.find_one({"_id": _id})
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404
        
        # Convertir ObjectId para JSON
        usuario["_id"] = str(usuario["_id"])
        
        # Si es bombero, agregar información adicional
        if usuario.get("es_bombero"):
            bombero = db.bomberos.find_one({"usuario_id": str(_id)})
            if bombero:
                usuario["info_bombero"] = {
                    "codigo_bombero": bombero.get("codigo_bombero"),
                    "estacion_pertenencia": bombero.get("estacion_pertenencia"),
                    "estado_servicio": bombero.get("estado_servicio"),
                    "ambulancia_id": bombero.get("ambulancia_id"),
                    "fecha_ingreso": bombero.get("fecha_registro")
                }
                
                # Si tiene ambulancia asignada, agregar detalles
                if bombero.get("ambulancia_id"):
                    ambulancia = db.ambulancias.find_one({"_id": ObjectId(bombero["ambulancia_id"])})
                    if ambulancia:
                        usuario["info_bombero"]["ambulancia_info"] = {
                            "placa": ambulancia.get("placa"),
                            "modelo": ambulancia.get("modelo"),
                            "estado": ambulancia.get("estado")
                        }
        
        # Estadísticas del usuario
        stats = obtener_estadisticas_usuario(str(_id))
        usuario["estadisticas"] = stats
        
        return usuario, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener perfil de usuario: {str(e)}")
        return {"error": "Error al obtener perfil del usuario"}, 500

def actualizar_perfil_usuario(usuario_id, datos):
    """
    Actualiza el perfil de un usuario
    """
    try:
        # Convertir a ObjectId
        if isinstance(usuario_id, str):
            try:
                _id = ObjectId(usuario_id)
            except:
                return {"error": "ID de usuario inválido"}, 400
        else:
            _id = usuario_id
        
        # Campos permitidos para actualizar - AGREGAR foto_perfil
        campos_permitidos = ['nombre', 'apellido', 'telefono', 'direccion', 'foto_perfil']
        update_data = {}
        
        for campo in campos_permitidos:
            if campo in datos:
                update_data[campo] = datos[campo]
        
        if not update_data:
            return {"error": "No hay datos válidos para actualizar"}, 400
        
        # Verificar si el usuario existe
        usuario_existe = db.usuarios.find_one({"_id": _id})
        if not usuario_existe:
            return {"error": "Usuario no encontrado"}, 404
        
        # Actualizar
        update_data["fecha_actualizacion"] = datetime.utcnow()
        
        result = db.usuarios.update_one(
            {"_id": _id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return {"error": "No se realizaron cambios"}, 400
        
        return {"mensaje": "Perfil actualizado exitosamente"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al actualizar perfil: {str(e)}")
        return {"error": "Error al actualizar el perfil"}, 500
    
def cambiar_password_usuario(usuario_id, password_actual, password_nueva):
    """
    Cambia la contraseña de un usuario
    """
    try:
        # Convertir a ObjectId
        if isinstance(usuario_id, str):
            try:
                _id = ObjectId(usuario_id)
            except:
                return {"error": "ID de usuario inválido"}, 400
        else:
            _id = usuario_id
        
        # Buscar usuario
        usuario = db.usuarios.find_one({"_id": _id})
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404
        
        # Verificar contraseña actual (esto depende de cómo manejes las contraseñas)
        # Asumiendo que tienes un método para verificar contraseñas
        from werkzeug.security import check_password_hash
        if not check_password_hash(usuario.get("contrasena", ""), password_actual):
            return {"error": "Contraseña actual incorrecta"}, 400
        
        # Generar hash de nueva contraseña
        nueva_contrasena_hash = generate_password_hash(password_nueva)
        
        # Actualizar contraseña
        result = db.usuarios.update_one(
            {"_id": _id},
            {
                "$set": {
                    "contrasena": nueva_contrasena_hash,
                    "fecha_cambio_password": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return {"error": "No se pudo cambiar la contraseña"}, 500
        
        return {"mensaje": "Contraseña cambiada exitosamente"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al cambiar contraseña: {str(e)}")
        return {"error": "Error al cambiar la contraseña"}, 500

def obtener_historial_incidentes_usuario(usuario_id, filtros=None):
    """
    Obtiene el historial de incidentes reportados por un usuario
    """
    try:
        query = {"usuario_id": str(usuario_id)}
        
        # Aplicar filtros
        if filtros:
            if filtros.get("estado"):
                query["estado"] = filtros["estado"]
            if filtros.get("fecha_desde"):
                query["fecha_reporte"] = {"$gte": filtros["fecha_desde"]}
            if filtros.get("fecha_hasta"):
                if "fecha_reporte" in query:
                    query["fecha_reporte"]["$lte"] = filtros["fecha_hasta"]
                else:
                    query["fecha_reporte"] = {"$lte": filtros["fecha_hasta"]}
        
        # Obtener incidentes
        incidentes = list(db.incidentes.find(query).sort("fecha_reporte", -1))
        
        # Convertir ObjectIds
        for incidente in incidentes:
            incidente["_id"] = str(incidente["_id"])
            
            # Agregar información del bombero asignado si existe
            if incidente.get("bombero_asignado_id"):
                bombero = db.bomberos.find_one({"usuario_id": incidente["bombero_asignado_id"]})
                if bombero:
                    usuario_bombero = db.usuarios.find_one({"_id": ObjectId(incidente["bombero_asignado_id"])})
                    if usuario_bombero:
                        incidente["bombero_info"] = {
                            "nombre": f"{usuario_bombero.get('nombre', '')} {usuario_bombero.get('apellido', '')}",
                            "codigo": bombero.get("codigo_bombero", "")
                        }
        
        return incidentes, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener historial de incidentes: {str(e)}")
        return {"error": "Error al obtener historial"}, 500

def obtener_notificaciones_usuario(usuario_id, solo_no_leidas=False):
    """
    Obtiene las notificaciones de un usuario
    """
    try:
        query = {"usuario_id": str(usuario_id)}
        
        if solo_no_leidas:
            query["leida"] = False
        
        # Obtener notificaciones
        notificaciones = list(db.notificaciones.find(query).sort("fecha", -1).limit(50))
        
        # Convertir ObjectIds
        for notif in notificaciones:
            notif["_id"] = str(notif["_id"])
        
        return notificaciones, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener notificaciones: {str(e)}")
        return {"error": "Error al obtener notificaciones"}, 500

def marcar_notificacion_leida(usuario_id, notificacion_id):
    """
    Marca una notificación como leída
    """
    try:
        # Convertir ID
        if isinstance(notificacion_id, str):
            try:
                _id = ObjectId(notificacion_id)
            except:
                return {"error": "ID de notificación inválido"}, 400
        else:
            _id = notificacion_id
        
        # Actualizar notificación
        result = db.notificaciones.update_one(
            {
                "_id": _id,
                "usuario_id": str(usuario_id)
            },
            {
                "$set": {
                    "leida": True,
                    "fecha_lectura": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return {"error": "Notificación no encontrada"}, 404
        
        return {"mensaje": "Notificación marcada como leída"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al marcar notificación como leída: {str(e)}")
        return {"error": "Error al marcar notificación"}, 500

def obtener_estadisticas_usuario(usuario_id):
    """
    Obtiene estadísticas del usuario
    """
    try:
        stats = {
            "incidentes_reportados": 0,
            "incidentes_completados": 0,
            "incidentes_pendientes": 0,
            "notificaciones_no_leidas": 0
        }
        
        # Contar incidentes
        stats["incidentes_reportados"] = db.incidentes.count_documents({"usuario_id": str(usuario_id)})
        stats["incidentes_completados"] = db.incidentes.count_documents({
            "usuario_id": str(usuario_id),
            "estado": "completado"
        })
        stats["incidentes_pendientes"] = db.incidentes.count_documents({
            "usuario_id": str(usuario_id),
            "estado": {"$in": ["reportado", "en_proceso"]}
        })
        
        # Contar notificaciones no leídas
        stats["notificaciones_no_leidas"] = db.notificaciones.count_documents({
            "usuario_id": str(usuario_id),
            "leida": False
        })
        
        return stats
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener estadísticas: {str(e)}")
        return {
            "incidentes_reportados": 0,
            "incidentes_completados": 0,
            "incidentes_pendientes": 0,
            "notificaciones_no_leidas": 0
        }

def eliminar_usuario(usuario_id, admin_id):
    """
    Elimina un usuario del sistema (solo para administradores)
    """
    try:
        # Verificar que el admin existe y es bombero
        admin = db.usuarios.find_one({"_id": ObjectId(admin_id)})
        if not admin or not admin.get("es_bombero"):
            return {"error": "No tienes permisos para realizar esta acción"}, 403
        
        # Convertir ID del usuario a eliminar
        if isinstance(usuario_id, str):
            try:
                _id = ObjectId(usuario_id)
            except:
                return {"error": "ID de usuario inválido"}, 400
        else:
            _id = usuario_id
        
        # Verificar que el usuario existe
        usuario = db.usuarios.find_one({"_id": _id})
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404
        
        # No permitir eliminar administradores
        if usuario.get("es_bombero"):
            return {"error": "No se puede eliminar un bombero"}, 400
        
        # Verificar que no tenga incidentes activos
        incidentes_activos = db.incidentes.count_documents({
            "usuario_id": str(_id),
            "estado": {"$in": ["reportado", "en_proceso"]}
        })
        
        if incidentes_activos > 0:
            return {"error": "El usuario tiene incidentes activos, no se puede eliminar"}, 400
        
        # Eliminar usuario y sus datos relacionados
        db.usuarios.delete_one({"_id": _id})
        db.notificaciones.delete_many({"usuario_id": str(_id)})
        
        return {"mensaje": "Usuario eliminado exitosamente"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al eliminar usuario: {str(e)}")
        return {"error": "Error al eliminar usuario"}, 500

def obtener_usuarios_sistema(admin_id, filtros=None):
    """
    Obtiene lista de usuarios del sistema (solo para administradores)
    """
    try:
        # Verificar permisos de admin
        admin = db.usuarios.find_one({"_id": ObjectId(admin_id)})
        if not admin or not admin.get("es_bombero"):
            return {"error": "No tienes permisos para realizar esta acción"}, 403
        
        query = {}
        
        # Aplicar filtros
        if filtros:
            if filtros.get("es_bombero") is not None:
                query["es_bombero"] = filtros["es_bombero"]
            if filtros.get("nombre"):
                query["$or"] = [
                    {"nombre": {"$regex": filtros["nombre"], "$options": "i"}},
                    {"apellido": {"$regex": filtros["nombre"], "$options": "i"}}
                ]
        
        # Obtener usuarios
        usuarios = list(db.usuarios.find(query, {
            "contrasena": 0  # Excluir contraseñas
        }).sort("fecha_registro", -1))
        
        # Convertir ObjectIds y agregar estadísticas
        for usuario in usuarios:
            usuario["_id"] = str(usuario["_id"])
            usuario["estadisticas"] = obtener_estadisticas_usuario(usuario["_id"])
        
        return usuarios, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener usuarios del sistema: {str(e)}")
        return {"error": "Error al obtener usuarios"}, 500