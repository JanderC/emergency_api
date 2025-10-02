# app/services/ambulancia_service.py

from app import db
from bson.objectid import ObjectId
from datetime import datetime
from flask import current_app

def registrar_ambulancia(datos, bombero_id):
    """
    Registra una nueva ambulancia en MongoDB
    """
    try:
        # Verificar si ya existe una ambulancia con esa placa
        ambulancia_existente = db.ambulancias.find_one({"placa": datos['placa']})
        if ambulancia_existente:
            return {"error": "Ya existe una ambulancia con esa placa"}, 400
        
        ambulancia_data = {
            "placa": datos['placa'],
            "modelo": datos.get('modelo'),
            "tipo": datos.get('tipo'),
            "capacidad": datos.get('capacidad'),
            "ano": datos.get('ano'),
            "estado": datos.get('estado', 'operativa'),
            "estacion_pertenencia": datos.get('estacion_pertenencia'),
            "bombero_asignado_id": None,
            "ubicacion_actual": None,
            "fecha_registro": datetime.utcnow()
        }
        
        result = db.ambulancias.insert_one(ambulancia_data)
        
        current_app.logger.info(f"Ambulancia registrada: {str(result.inserted_id)}")
        
        return {
            "mensaje": "Ambulancia registrada exitosamente",
            "ambulancia_id": str(result.inserted_id)
        }, 201
        
    except Exception as e:
        current_app.logger.error(f"Error al registrar ambulancia: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": "Error al registrar ambulancia"}, 500

def asignar_ambulancia(ambulancia_id, bombero_id):
    """
    Asigna una ambulancia a un bombero
    """
    try:
        current_app.logger.info(f"Asignando ambulancia {ambulancia_id} a bombero {bombero_id}")
        
        object_id = ObjectId(ambulancia_id)
        
        # Verificar que la ambulancia existe
        ambulancia = db.ambulancias.find_one({"_id": object_id})
        if not ambulancia:
            return {"error": "Ambulancia no encontrada"}, 404
        
        # Verificar que está operativa
        if ambulancia.get('estado') != 'operativa':
            return {"error": f"La ambulancia no está operativa (estado: {ambulancia.get('estado')})"}, 400
        
        # Verificar que no está asignada
        if ambulancia.get('bombero_asignado_id'):
            return {"error": "La ambulancia ya está asignada a otro bombero"}, 400
        
        # Asignar ambulancia
        result = db.ambulancias.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "bombero_asignado_id": bombero_id,
                    "estado": "en_servicio",
                    "fecha_asignacion": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            current_app.logger.error("No se pudo modificar la ambulancia")
            return {"error": "No se pudo asignar la ambulancia"}, 400
        
        current_app.logger.info(f"Ambulancia asignada exitosamente")
        return {"mensaje": "Ambulancia asignada exitosamente"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al asignar ambulancia: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": "Error al asignar ambulancia"}, 500

def desasignar_ambulancia(ambulancia_id):
    """
    Libera una ambulancia (remueve la asignación del bombero)
    """
    try:
        current_app.logger.info(f"Liberando ambulancia {ambulancia_id}")
        
        object_id = ObjectId(ambulancia_id)
        
        # Verificar que existe
        ambulancia = db.ambulancias.find_one({"_id": object_id})
        if not ambulancia:
            return {"error": "Ambulancia no encontrada"}, 404
        
        # Liberar asignación
        result = db.ambulancias.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "bombero_asignado_id": None,
                    "estado": "operativa"
                },
                "$unset": {"fecha_asignacion": ""}
            }
        )
        
        if result.modified_count == 0:
            return {"error": "No se pudo liberar la ambulancia"}, 400
        
        current_app.logger.info("Ambulancia liberada exitosamente")
        return {"mensaje": "Ambulancia liberada exitosamente"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al desasignar ambulancia: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": "Error al liberar ambulancia"}, 500

def actualizar_estado_ambulancia(ambulancia_id, nuevo_estado):
    """
    Actualiza el estado de una ambulancia
    Estados válidos: operativa, en_servicio, mantenimiento, fuera_de_servicio
    """
    try:
        estados_validos = ['operativa', 'en_servicio', 'mantenimiento', 'fuera_de_servicio']
        
        if nuevo_estado not in estados_validos:
            return {"error": f"Estado inválido. Estados válidos: {estados_validos}"}, 400
        
        object_id = ObjectId(ambulancia_id)
        
        # Verificar que existe
        ambulancia = db.ambulancias.find_one({"_id": object_id})
        if not ambulancia:
            return {"error": "Ambulancia no encontrada"}, 404
        
        # Actualizar estado
        result = db.ambulancias.update_one(
            {"_id": object_id},
            {"$set": {"estado": nuevo_estado}}
        )
        
        if result.modified_count == 0:
            return {"error": "No se pudo actualizar el estado"}, 400
        
        current_app.logger.info(f"Estado de ambulancia actualizado a: {nuevo_estado}")
        return {"mensaje": f"Estado actualizado a {nuevo_estado} exitosamente"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al actualizar estado: {str(e)}")
        return {"error": "Error al actualizar estado"}, 500

def obtener_ambulancias(filtros=None):
    """
    Obtiene lista de ambulancias con filtros opcionales
    Filtros disponibles:
    - estado: filtra por estado específico
    - disponible: true para obtener solo ambulancias disponibles (sin asignar y operativas)
    """
    try:
        query = {}
        
        current_app.logger.info(f"Obteniendo ambulancias con filtros: {filtros}")
        
        if filtros:
            # Filtro por estado
            if 'estado' in filtros:
                query['estado'] = filtros['estado']
            
            # Filtro de disponibilidad
            if 'disponible' in filtros and filtros['disponible']:
                # Ambulancias disponibles: sin bombero asignado Y operativas
                query = {
                    'estado': 'operativa',
                    '$or': [
                        {'bombero_asignado_id': None},
                        {'bombero_asignado_id': {'$exists': False}}
                    ]
                }
        
        current_app.logger.info(f"Query MongoDB: {query}")
        
        ambulancias = list(db.ambulancias.find(query))
        
        current_app.logger.info(f"Ambulancias encontradas: {len(ambulancias)}")
        
        # Convertir ObjectIds a strings y agregar info del bombero
        for ambulancia in ambulancias:
            ambulancia['_id'] = str(ambulancia['_id'])
            
            # Si tiene bombero asignado, buscar su información
            if ambulancia.get('bombero_asignado_id'):
                try:
                    bombero = db.bomberos.find_one({"usuario_id": ambulancia['bombero_asignado_id']})
                    if bombero:
                        usuario = db.usuarios.find_one({"_id": ObjectId(ambulancia['bombero_asignado_id'])})
                        if usuario:
                            ambulancia['bombero_info'] = {
                                'nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}",
                                'codigo': bombero.get('codigo_bombero', '')
                            }
                except Exception as e:
                    current_app.logger.warning(f"Error al obtener info del bombero: {str(e)}")
        
        return ambulancias, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener ambulancias: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": "Error al obtener ambulancias"}, 500

def obtener_ambulancia_por_id(ambulancia_id):
    """
    Obtiene una ambulancia específica por ID
    """
    try:
        object_id = ObjectId(ambulancia_id)
        ambulancia = db.ambulancias.find_one({"_id": object_id})
        
        if not ambulancia:
            return {"error": "Ambulancia no encontrada"}, 404
        
        # Convertir ObjectId a string
        ambulancia['_id'] = str(ambulancia['_id'])
        
        # Agregar info del bombero si está asignada
        if ambulancia.get('bombero_asignado_id'):
            try:
                bombero = db.bomberos.find_one({"usuario_id": ambulancia['bombero_asignado_id']})
                if bombero:
                    usuario = db.usuarios.find_one({"_id": ObjectId(ambulancia['bombero_asignado_id'])})
                    if usuario:
                        ambulancia['bombero_info'] = {
                            'nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}",
                            'codigo': bombero.get('codigo_bombero', '')
                        }
            except Exception as e:
                current_app.logger.warning(f"Error al obtener info del bombero: {str(e)}")
        
        return ambulancia, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener ambulancia: {str(e)}")
        return {"error": "Error al obtener ambulancia"}, 500