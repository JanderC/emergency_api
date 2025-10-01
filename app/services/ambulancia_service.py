# app/services/ambulancia_service.py

# ❌ ELIMINAR ESTA LÍNEA:
# from app.models.ambulancia import Ambulancia

# ✅ En su lugar, trabajar directamente con la base de datos
from app import db
from bson.objectid import ObjectId
from datetime import datetime
from flask import current_app

# app/services/ambulancia_service.py

def registrar_ambulancia(datos, bombero_id):
    """
    Registra una nueva ambulancia en MongoDB
    """
    try:
        ambulancia_data = {
            "placa": datos['placa'],
            "modelo": datos.get('modelo'),
            "tipo": datos.get('tipo'),  # AGREGAR
            "capacidad": datos.get('capacidad'),  # AGREGAR
            "ano": datos.get('ano'),
            "estado": datos.get('estado', 'operativa'),
            "estacion_pertenencia": datos.get('estacion_pertenencia'),  # AGREGAR
            "bombero_asignado_id": None,
            "ubicacion_actual": None,
            "fecha_registro": datetime.utcnow()
        }
        
        result = db.ambulancias.insert_one(ambulancia_data)
        
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
        object_id = ObjectId(ambulancia_id)
        
        # Verificar que la ambulancia existe y está disponible
        ambulancia = db.ambulancias.find_one({"_id": object_id})
        if not ambulancia:
            return {"error": "Ambulancia no encontrada"}, 404
        
        if ambulancia.get('estado') != 'operativa':
            return {"error": "La ambulancia no está operativa"}, 400
        
        if ambulancia.get('bombero_asignado_id'):
            return {"error": "La ambulancia ya está asignada"}, 400
        
        # Asignar
        result = db.ambulancias.update_one(
            {"_id": object_id},
            {"$set": {
                "bombero_asignado_id": bombero_id,
                "fecha_asignacion": datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            return {"error": "No se pudo asignar la ambulancia"}, 400
        
        return {"mensaje": "Ambulancia asignada exitosamente"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al asignar ambulancia: {str(e)}")
        return {"error": "Error al asignar ambulancia"}, 500

def actualizar_estado_ambulancia(ambulancia_id, nuevo_estado):
    """
    Actualiza el estado de una ambulancia
    """
    try:
        object_id = ObjectId(ambulancia_id)
        
        # Verificar que existe
        ambulancia = db.ambulancias.find_one({"_id": object_id})
        if not ambulancia:
            return {"error": "Ambulancia no encontrada"}, 404
        
        # Actualizar
        result = db.ambulancias.update_one(
            {"_id": object_id},
            {"$set": {"estado": nuevo_estado}}
        )
        
        if result.modified_count == 0:
            return {"error": "No se pudo actualizar el estado"}, 400
        
        return {"mensaje": "Estado actualizado exitosamente"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al actualizar estado: {str(e)}")
        return {"error": "Error al actualizar estado"}, 500

def obtener_ambulancias(filtros=None):
    """
    Obtiene lista de ambulancias con filtros opcionales
    """
    try:
        query = {}
        
        if filtros:
            if 'estado' in filtros:
                query['estado'] = filtros['estado']
            if 'disponible' in filtros and filtros['disponible']:
                query['bombero_asignado_id'] = None
                query['estado'] = 'operativa'
        
        ambulancias = list(db.ambulancias.find(query))
        
        # Convertir ObjectIds a strings
        for ambulancia in ambulancias:
            ambulancia['_id'] = str(ambulancia['_id'])
            if ambulancia.get('bombero_asignado_id'):
                # Obtener info del bombero si existe
                bombero = db.bomberos.find_one({"usuario_id": ambulancia['bombero_asignado_id']})
                if bombero:
                    usuario = db.usuarios.find_one({"_id": ObjectId(ambulancia['bombero_asignado_id'])})
                    if usuario:
                        ambulancia['bombero_info'] = {
                            'nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}",
                            'codigo': bombero.get('codigo_bombero', '')
                        }
        
        return ambulancias, 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener ambulancias: {str(e)}")
        return {"error": "Error al obtener ambulancias"}, 500