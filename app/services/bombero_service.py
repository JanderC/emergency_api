# app/services/bombero_service_mongo.py
"""
Servicio mejorado para gestionar bomberos en MongoDB
"""
from flask import current_app
from app import db
from werkzeug.security import generate_password_hash
from datetime import datetime
from bson.objectid import ObjectId

def registrar_bombero(datos):
    """
    Registra un nuevo bombero en el sistema MongoDB
    """
    try:
        print(f"🔧 Iniciando registro de bombero con datos: {datos}")
        
        # Verificar si el email ya existe
        usuario_existente = db.usuarios.find_one({"email": datos['email']})
        if usuario_existente:
            print(f"❌ Email ya existe: {datos['email']}")
            return {"error": "El correo electrónico ya está registrado"}, 400
        
        # Verificar si el código de bombero ya existe
        bombero_existente = db.bomberos.find_one({"codigo_bombero": datos['codigo_bombero']})
        if bombero_existente:
            print(f"❌ Código de bombero ya existe: {datos['codigo_bombero']}")
            return {"error": "El código de bombero ya está registrado"}, 400
        
        # Crear documento de usuario
        nuevo_usuario_data = {
            "nombre": datos['nombre'],
            "apellido": datos['apellido'],
            "email": datos['email'],
            "password_hash": generate_password_hash(datos['password']),
            "telefono": datos.get('telefono', ''),
            "es_bombero": True,
            "fecha_registro": datetime.utcnow(),
            "activo": True,
            "foto_perfil": None
        }
        
        print(f"📝 Insertando usuario en colección 'usuarios'")
        # Insertar usuario en la colección USUARIOS
        usuario_result = db.usuarios.insert_one(nuevo_usuario_data)
        usuario_id = str(usuario_result.inserted_id)
        print(f"✅ Usuario creado con ID: {usuario_id}")
        
        # Crear documento de bombero en la colección BOMBEROS
        nuevo_bombero_data = {
            "usuario_id": usuario_id,  # Referencia al usuario
            "codigo_bombero": datos['codigo_bombero'],
            "estacion_pertenencia": datos['estacion_pertenencia'],
            "rango": datos.get('rango', 'bombero'),
            "especialidades": datos.get('especialidades', []),
            "carnet_foto": datos.get('carnet_foto'),
            "estado_servicio": 'disponible',
            "fecha_registro": datetime.utcnow(),
            "certificaciones": datos.get('certificaciones', []),
            "experiencia_anos": datos.get('experiencia_anos', 0),
            "contacto_emergencia": datos.get('contacto_emergencia', {}),
            "ambulancia_id": None,
            "ubicacion_actual": None,
            "turnos_completados": 0,
            "incidentes_atendidos": 0
        }
        
        print(f"📝 Insertando bombero en colección 'bomberos'")
        # Insertar bombero en la colección BOMBEROS
        bombero_result = db.bomberos.insert_one(nuevo_bombero_data)
        print(f"✅ Bombero creado con ID: {str(bombero_result.inserted_id)}")
        
        return {
            "mensaje": "Bombero registrado con éxito",
            "usuario_id": usuario_id,
            "bombero_id": str(bombero_result.inserted_id),
            "codigo_bombero": datos['codigo_bombero']
        }, 201
    
    except Exception as e:
        current_app.logger.error(f"Error al registrar bombero: {str(e)}")
        print(f"❌ Error al registrar bombero: {str(e)}")
        return {"error": f"Error al registrar el bombero: {str(e)}"}, 500

def obtener_bombero(usuario_id):
    """
    Obtiene información completa de un bombero
    """
    try:
        print(f"🔍 Buscando bombero con usuario_id: {usuario_id}")
        print(f"🔍 Tipo de usuario_id: {type(usuario_id)}")
        
        # Buscar bombero por usuario_id (puede estar como string o como ObjectId)
        bombero = db.bomberos.find_one({"usuario_id": usuario_id})
        
        if not bombero:
            # Intentar buscar también por ObjectId si no se encontró como string
            try:
                bombero = db.bomberos.find_one({"usuario_id": ObjectId(usuario_id)})
                print(f"✅ Bombero encontrado usando ObjectId")
            except:
                pass
        else:
            print(f"✅ Bombero encontrado usando string")
        
        if not bombero:
            print(f"❌ Bombero no encontrado en la colección")
            # Debug: Listar algunos bomberos para ver el formato
            sample = list(db.bomberos.find().limit(2))
            print(f"📋 Sample de bomberos en DB: {sample}")
            return {"error": "Bombero no encontrado"}, 404
        
        print(f"📄 Documento bombero: {bombero}")
        
        # Buscar información del usuario
        usuario = db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        if not usuario:
            print(f"❌ Usuario no encontrado con _id: {usuario_id}")
            return {"error": "Usuario no encontrado"}, 404
        
        print(f"✅ Usuario encontrado: {usuario.get('email')}")
        
        # Combinar información
        info_completa = {
            "_id": str(bombero["_id"]),
            "usuario_id": usuario_id,
            "nombre": usuario.get("nombre", ""),
            "apellido": usuario.get("apellido", ""),
            "email": usuario.get("email", ""),
            "telefono": usuario.get("telefono", ""),
            "foto_perfil": usuario.get("foto_perfil"),
            "codigo_bombero": bombero.get("codigo_bombero"),
            "estacion_pertenencia": bombero.get("estacion_pertenencia"),
            "rango": bombero.get("rango"),
            "especialidades": bombero.get("especialidades", []),
            "estado_servicio": bombero.get("estado_servicio"),
            "fecha_registro": bombero.get("fecha_registro"),
            "certificaciones": bombero.get("certificaciones", []),
            "experiencia_anos": bombero.get("experiencia_anos", 0),
            "contacto_emergencia": bombero.get("contacto_emergencia", {}),
            "ambulancia_id": bombero.get("ambulancia_id"),
            "ubicacion_actual": bombero.get("ubicacion_actual"),
            "turnos_completados": bombero.get("turnos_completados", 0),
            "incidentes_atendidos": bombero.get("incidentes_atendidos", 0),
            "activo": usuario.get("activo", True)
        }
        
        # Si tiene ambulancia asignada, agregar detalles
        if bombero.get("ambulancia_id"):
            try:
                ambulancia = db.ambulancias.find_one({"_id": ObjectId(bombero["ambulancia_id"])})
                if ambulancia:
                    info_completa["ambulancia_info"] = {
                        "placa": ambulancia.get("placa"),
                        "modelo": ambulancia.get("modelo"),
                        "estado": ambulancia.get("estado")
                    }
            except:
                pass
        
        return info_completa, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener bombero: {str(e)}")
        return {"error": "Error al obtener información del bombero"}, 500

def actualizar_estado_bombero(usuario_id, nuevo_estado):
    """
    Actualiza el estado de servicio de un bombero
    """
    try:
        estados_validos = ['disponible', 'en_servicio', 'fuera_servicio', 'descanso']
        if nuevo_estado not in estados_validos:
            return {"error": f"Estado inválido. Estados válidos: {estados_validos}"}, 400
        
        # Buscar bombero
        bombero = db.bomberos.find_one({"usuario_id": usuario_id})
        if not bombero:
            return {"error": "Bombero no encontrado"}, 404
        
        # Actualizar estado
        result = db.bomberos.update_one(
            {"usuario_id": usuario_id},
            {
                "$set": {
                    "estado_servicio": nuevo_estado,
                    "ultima_actualizacion": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return {"error": "No se pudo actualizar el estado"}, 500
        
        return {
            "mensaje": f"Estado actualizado a {nuevo_estado}",
            "usuario_id": usuario_id,
            "estado": nuevo_estado
        }, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al actualizar estado del bombero: {str(e)}")
        return {"error": "Error al actualizar el estado del bombero"}, 500

def obtener_bomberos_disponibles():
    """
    Obtiene lista de bomberos disponibles
    """
    try:
        # Buscar bomberos disponibles
        bomberos = list(db.bomberos.find({
            "estado_servicio": "disponible"
        }))
        
        # Enriquecer con información del usuario
        bomberos_completos = []
        for bombero in bomberos:
            try:
                usuario = db.usuarios.find_one({"_id": ObjectId(bombero["usuario_id"])})
                if usuario and usuario.get("activo", True):
                    info = {
                        "_id": str(bombero["_id"]),
                        "usuario_id": bombero["usuario_id"],
                        "nombre": f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}",
                        "codigo_bombero": bombero.get("codigo_bombero"),
                        "estacion_pertenencia": bombero.get("estacion_pertenencia"),
                        "rango": bombero.get("rango"),
                        "especialidades": bombero.get("especialidades", []),
                        "ambulancia_asignada": bombero.get("ambulancia_id") is not None,
                        "ubicacion_actual": bombero.get("ubicacion_actual"),
                        "experiencia_anos": bombero.get("experiencia_anos", 0)
                    }
                    bomberos_completos.append(info)
            except Exception as e:
                current_app.logger.warning(f"Error al procesar bombero {bombero.get('usuario_id')}: {str(e)}")
                continue
        
        return bomberos_completos, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener bomberos disponibles: {str(e)}")
        return {"error": "Error al obtener bomberos disponibles"}, 500

def obtener_todos_bomberos(filtros=None):
    """
    Obtiene lista de todos los bomberos con filtros opcionales
    """
    try:
        query = {}
        
        # Aplicar filtros
        if filtros:
            if filtros.get("estado_servicio"):
                query["estado_servicio"] = filtros["estado_servicio"]
            if filtros.get("estacion_pertenencia"):
                query["estacion_pertenencia"] = filtros["estacion_pertenencia"]
            if filtros.get("rango"):
                query["rango"] = filtros["rango"]
            if filtros.get("tiene_ambulancia") is not None:
                if filtros["tiene_ambulancia"]:
                    query["ambulancia_id"] = {"$ne": None}
                else:
                    query["$or"] = [
                        {"ambulancia_id": None},
                        {"ambulancia_id": {"$exists": False}}
                    ]
        
        # Obtener bomberos
        bomberos = list(db.bomberos.find(query).sort("fecha_registro", -1))
        
        # Enriquecer con información del usuario
        bomberos_completos = []
        for bombero in bomberos:
            try:
                usuario = db.usuarios.find_one({"_id": ObjectId(bombero["usuario_id"])})
                if usuario:
                    info = {
                        "_id": str(bombero["_id"]),
                        "usuario_id": bombero["usuario_id"],
                        "nombre": usuario.get("nombre", ""),
                        "apellido": usuario.get("apellido", ""),
                        "email": usuario.get("email", ""),
                        "telefono": usuario.get("telefono", ""),
                        "codigo_bombero": bombero.get("codigo_bombero"),
                        "estacion_pertenencia": bombero.get("estacion_pertenencia"),
                        "rango": bombero.get("rango"),
                        "especialidades": bombero.get("especialidades", []),
                        "estado_servicio": bombero.get("estado_servicio"),
                        "fecha_registro": bombero.get("fecha_registro"),
                        "ambulancia_id": bombero.get("ambulancia_id"),
                        "turnos_completados": bombero.get("turnos_completados", 0),
                        "incidentes_atendidos": bombero.get("incidentes_atendidos", 0),
                        "activo": usuario.get("activo", True)
                    }
                    
                    # Agregar info de ambulancia si tiene
                    if bombero.get("ambulancia_id"):
                        try:
                            ambulancia = db.ambulancias.find_one({"_id": ObjectId(bombero["ambulancia_id"])})
                            if ambulancia:
                                info["ambulancia_info"] = {
                                    "placa": ambulancia.get("placa"),
                                    "modelo": ambulancia.get("modelo"),
                                    "estado": ambulancia.get("estado")
                                }
                        except:
                            pass
                    
                    bomberos_completos.append(info)
            except Exception as e:
                current_app.logger.warning(f"Error al procesar bombero {bombero.get('usuario_id')}: {str(e)}")
                continue
        
        return bomberos_completos, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener bomberos: {str(e)}")
        return {"error": "Error al obtener bomberos"}, 500

def actualizar_ubicacion_bombero(usuario_id, coordenadas_lat, coordenadas_lng):
    """
    Actualiza la ubicación actual del bombero
    """
    try:
        # Validar coordenadas
        try:
            lat = float(coordenadas_lat)
            lng = float(coordenadas_lng)
            
            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                return {"error": "Coordenadas fuera del rango válido"}, 400
        except (ValueError, TypeError):
            return {"error": "Coordenadas inválidas"}, 400
        
        # Actualizar ubicación
        result = db.bomberos.update_one(
            {"usuario_id": usuario_id},
            {
                "$set": {
                    "ubicacion_actual": {
                        "lat": lat,
                        "lng": lng,
                        "timestamp": datetime.utcnow()
                    },
                    "ultima_actualizacion": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return {"error": "Bombero no encontrado"}, 404
        
        return {"mensaje": "Ubicación actualizada exitosamente"}, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al actualizar ubicación: {str(e)}")
        return {"error": "Error al actualizar ubicación"}, 500

def completar_incidente_bombero(usuario_id, incidente_id):
    """
    Marca un incidente como completado y actualiza estadísticas del bombero
    """
    try:
        # Verificar que el bombero tenga el incidente asignado
        incidente = db.incidentes.find_one({
            "_id": ObjectId(incidente_id),
            "bombero_asignado_id": usuario_id
        })
        
        if not incidente:
            return {"error": "Incidente no encontrado o no asignado a este bombero"}, 404
        
        # Actualizar estadísticas del bombero
        db.bomberos.update_one(
            {"usuario_id": usuario_id},
            {
                "$inc": {"incidentes_atendidos": 1},
                "$set": {"ultima_actualizacion": datetime.utcnow()}
            }
        )
        
        return {"mensaje": "Estadísticas actualizadas exitosamente"}, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al completar incidente: {str(e)}")
        return {"error": "Error al actualizar estadísticas"}, 500

def actualizar_perfil_bombero(usuario_id, datos):
    """
    Actualiza el perfil de un bombero
    """
    try:
        # Campos permitidos para actualizar en bomberos
        campos_bombero = ['especialidades', 'certificaciones', 'experiencia_anos', 'contacto_emergencia', 'rango']
        campos_usuario = ['telefono', 'foto_perfil']
        
        update_bombero = {}
        update_usuario = {}
        
        # Separar campos de bombero y usuario
        for campo, valor in datos.items():
            if campo in campos_bombero:
                update_bombero[campo] = valor
            elif campo in campos_usuario:
                update_usuario[campo] = valor
        
        # Actualizar bombero
        if update_bombero:
            update_bombero["ultima_actualizacion"] = datetime.utcnow()
            result_bombero = db.bomberos.update_one(
                {"usuario_id": usuario_id},
                {"$set": update_bombero}
            )
            
            if result_bombero.matched_count == 0:
                return {"error": "Bombero no encontrado"}, 404
        
        # Actualizar usuario
        if update_usuario:
            update_usuario["fecha_actualizacion"] = datetime.utcnow()
            result_usuario = db.usuarios.update_one(
                {"_id": ObjectId(usuario_id)},
                {"$set": update_usuario}
            )
            
            if result_usuario.matched_count == 0:
                return {"error": "Usuario no encontrado"}, 404
        
        return {
            "mensaje": "Perfil actualizado exitosamente",
            "success": True
        }, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al actualizar perfil del bombero: {str(e)}")
        return {"error": "Error al actualizar perfil"}, 500

def desactivar_bombero(usuario_id, admin_id):
    """
    Desactiva un bombero del sistema
    """
    try:
        # Verificar permisos de admin
        admin = db.usuarios.find_one({"_id": ObjectId(admin_id)})
        if not admin or not admin.get("es_bombero"):
            return {"error": "No tienes permisos para realizar esta acción"}, 403
        
        # Verificar que el bombero no tenga incidentes activos
        incidentes_activos = db.incidentes.count_documents({
            "bombero_asignado_id": usuario_id,
            "estado": {"$in": ["en_proceso", "reportado"]}
        })
        
        if incidentes_activos > 0:
            return {"error": "El bombero tiene incidentes activos asignados"}, 400
        
        # Desactivar usuario
        db.usuarios.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": {"activo": False, "fecha_desactivacion": datetime.utcnow()}}
        )
        
        # Actualizar estado del bombero
        db.bomberos.update_one(
            {"usuario_id": usuario_id},
            {"$set": {"estado_servicio": "fuera_servicio"}}
        )
        
        return {"mensaje": "Bombero desactivado exitosamente"}, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al desactivar bombero: {str(e)}")
        return {"error": "Error al desactivar bombero"}, 500