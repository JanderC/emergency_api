# app/routes/incidentes.py
from flask import Blueprint, request, jsonify, current_app, g
from app.schemas.incidente_schema import ReporteIncidenteSchema, IncidenteSchema
from app.services.incidente_service import (
    reportar_incidente, 
    obtener_incidentes, 
    obtener_incidente, 
    actualizar_estado_incidente
)
from app.middlewares.auth import token_required

incidente_bp = Blueprint('incidente', __name__, url_prefix='/api/incidentes')

@incidente_bp.route('', methods=['POST'])
@token_required
def crear_incidente():
    """
    Endpoint para reportar un nuevo incidente
    """
    current_app.logger.info("=== INICIO DEBUG CREAR INCIDENTE ===")
    
    current_app.logger.info(f"Token procesado: usuario_id = {g.usuario_id if hasattr(g, 'usuario_id') else 'No disponible'}")
    
    auth_header = request.headers.get('Authorization', 'No hay header de autorización')
    current_app.logger.info(f"Header de autorización: {auth_header}")
    
    if not hasattr(g, 'usuario_id'):
        current_app.logger.error("No se encontró usuario_id en el contexto global")
        return jsonify({"error": "No autorizado - Token inválido o ausente"}), 401
    
    usuario_id = g.usuario_id
    current_app.logger.info(f"Usuario ID validado: {usuario_id}")
    
    try:
        current_app.logger.info(f"Datos recibidos: {request.json}")
        
        schema = ReporteIncidenteSchema()
        try:
            datos = schema.load(request.json)
            current_app.logger.info(f"Datos validados por el schema correctamente: {datos}")
        except Exception as schema_error:
            current_app.logger.error(f"Error en la validación del schema: {str(schema_error)}")
            return jsonify({"error": f"Error en los datos proporcionados: {str(schema_error)}"}), 400
        
        current_app.logger.info(f"Llamando a reportar_incidente con usuario_id: {usuario_id}")
        resultado, codigo = reportar_incidente(usuario_id, datos)
        current_app.logger.info(f"Resultado de reportar_incidente: {resultado}, código: {codigo}")
        
        current_app.logger.info("=== FIN DEBUG CREAR INCIDENTE ===")
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error general en endpoint de crear incidente: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        current_app.logger.info("=== FIN DEBUG CREAR INCIDENTE (CON ERROR) ===")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@incidente_bp.route('', methods=['GET'])
@token_required
def listar_incidentes():
    """
    Endpoint para obtener lista de incidentes con filtros mejorados
    """
    try:
        from app import db
        
        # Construir filtros de MongoDB
        filtros_mongo = {}
        
        # Filtro de estado - soporta múltiples valores separados por coma
        if 'estado' in request.args:
            estados = request.args.get('estado').split(',')
            # Si hay múltiples estados, usar $in
            if len(estados) > 1:
                filtros_mongo['estado'] = {"$in": [e.strip() for e in estados]}
            else:
                filtros_mongo['estado'] = estados[0].strip()
        
        # Filtro de nivel de urgencia
        if 'nivel_urgencia' in request.args:
            filtros_mongo['nivel_urgencia'] = request.args.get('nivel_urgencia')
        
        # Filtro de tipo de emergencia
        if 'tipo_emergencia' in request.args:
            filtros_mongo['tipo_emergencia'] = request.args.get('tipo_emergencia')
        
        # Filtro para incidentes sin bombero asignado
        if request.args.get('sin_bombero') == 'true':
            filtros_mongo['$or'] = [
                {'bombero_asignado_id': None},
                {'bombero_asignado_id': {"$exists": False}}
            ]
        
        # Filtro para incidentes activos (reportado o en_proceso) sin bombero
        if request.args.get('activos_sin_atender') == 'true':
            filtros_mongo['estado'] = {"$in": ['reportado', 'en_proceso']}
            filtros_mongo['$or'] = [
                {'bombero_asignado_id': None},
                {'bombero_asignado_id': {"$exists": False}}
            ]
        
        current_app.logger.info(f"Filtros MongoDB aplicados: {filtros_mongo}")
        
        # Buscar en MongoDB
        incidentes_cursor = db.incidentes.find(filtros_mongo).sort("fecha_reporte", -1)
        incidentes = list(incidentes_cursor)
        
        # Convertir ObjectId a string
        for incidente in incidentes:
            incidente["_id"] = str(incidente["_id"])
        
        current_app.logger.info(f"Incidentes encontrados: {len(incidentes)}")
        
        # Serializar con schema
        schema = IncidenteSchema(many=True)
        return jsonify(schema.dump(incidentes)), 200
            
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de listar incidentes: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@incidente_bp.route('/mongodb/<string:mongodb_id>', methods=['GET'])
@token_required
def obtener_incidente_por_mongodb_id(mongodb_id):
    """
    Endpoint para obtener un incidente por su ID de MongoDB
    """
    try:
        try:
            from bson.objectid import ObjectId
            object_id = ObjectId(mongodb_id)
        except Exception as e:
            return jsonify({"error": f"ID de MongoDB inválido: {str(e)}"}), 400
            
        from app import db
        incidente = db.incidentes.find_one({"_id": object_id})
        
        if not incidente:
            return jsonify({"error": "Incidente no encontrado"}), 404
            
        incidente["_id"] = str(incidente["_id"])
        
        schema = IncidenteSchema()
        return jsonify(schema.dump(incidente)), 200
            
    except Exception as e:
        current_app.logger.error(f"Error al buscar incidente por MongoDB ID: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@incidente_bp.route('/<string:incidente_id>', methods=['GET'])
@token_required
def detalle_incidente(incidente_id):
    """
    Endpoint para obtener detalles de un incidente por ID (entero o MongoDB ObjectId)
    """
    try:
        if incidente_id.isdigit():
            incidente, codigo = obtener_incidente(int(incidente_id))
        else:
            try:
                from bson.objectid import ObjectId
                object_id = ObjectId(incidente_id)
                
                from app import db
                incidente = db.incidentes.find_one({"_id": object_id})
                
                if not incidente:
                    return jsonify({"error": "Incidente no encontrado"}), 404
                    
                incidente["_id"] = str(incidente["_id"])
                codigo = 200
                
            except Exception as e:
                return jsonify({"error": f"ID inválido: {str(e)}"}), 400
        
        if codigo == 200:
            schema = IncidenteSchema()
            return jsonify(schema.dump(incidente)), 200
        else:
            return jsonify(incidente), codigo
            
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de detalle incidente: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@incidente_bp.route('/<string:incidente_id>/estado', methods=['PUT'])
@token_required
def cambiar_estado_incidente(incidente_id):
    """
    Endpoint para actualizar el estado de un incidente (acepta MongoDB ObjectId)
    """
    try:
        datos = request.json
        
        if 'estado' not in datos:
            return jsonify({"error": "El estado es requerido"}), 400
        
        # Intentar convertir a ObjectId
        try:
            from bson.objectid import ObjectId
            object_id = ObjectId(incidente_id)
        except Exception as e:
            return jsonify({"error": f"ID de incidente inválido: {str(e)}"}), 400
        
        from app import db
        from datetime import datetime
        
        # Verificar que el incidente existe
        incidente = db.incidentes.find_one({"_id": object_id})
        if not incidente:
            return jsonify({"error": "Incidente no encontrado"}), 404
        
        # Construir el update
        update_data = {
            "estado": datos['estado']
        }
        
        # Si se proporciona bombero_id, agregarlo
        if 'bombero_id' in datos:
            update_data['bombero_asignado_id'] = datos['bombero_id']
        
        # Si se proporciona ambulancia_id, agregarlo
        if 'ambulancia_id' in datos:
            update_data['ambulancia_id'] = datos['ambulancia_id']
        
        # Si el estado es 'en_proceso', actualizar fecha_atencion
        if datos['estado'] == 'en_proceso':
            update_data['fecha_atencion'] = datetime.utcnow()
        
        # Actualizar en MongoDB
        result = db.incidentes.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "No se pudo actualizar el incidente"}), 400
        
        # Obtener el incidente actualizado
        incidente_actualizado = db.incidentes.find_one({"_id": object_id})
        incidente_actualizado["_id"] = str(incidente_actualizado["_id"])
        
        return jsonify({
            "mensaje": "Estado del incidente actualizado exitosamente",
            "incidente": incidente_actualizado
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de cambiar estado: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500
    

@incidente_bp.route('/<string:incidente_id>/completar', methods=['PUT'])
@token_required
def completar_incidente(incidente_id):
    """
    Endpoint para completar un incidente (shortcut de cambiar estado a completado)
    """
    try:
        from bson.objectid import ObjectId
        from app import db
        from datetime import datetime
        
        # Validar ObjectId
        try:
            object_id = ObjectId(incidente_id)
        except Exception as e:
            return jsonify({"error": f"ID de incidente inválido: {str(e)}"}), 400
        
        # Verificar que existe
        incidente = db.incidentes.find_one({"_id": object_id})
        if not incidente:
            return jsonify({"error": "Incidente no encontrado"}), 404
        
        # Verificar que tiene bombero asignado
        if not incidente.get('bombero_asignado_id'):
            return jsonify({"error": "El incidente no tiene bombero asignado"}), 400
        
        # Actualizar a completado
        result = db.incidentes.update_one(
            {"_id": object_id},
            {"$set": {
                "estado": "completado",
                "fecha_completado": datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "No se pudo completar el incidente"}), 400
        
        # Obtener incidente actualizado
        incidente_actualizado = db.incidentes.find_one({"_id": object_id})
        incidente_actualizado["_id"] = str(incidente_actualizado["_id"])
        
        return jsonify({
            "mensaje": "Incidente completado exitosamente",
            "incidente": incidente_actualizado
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al completar incidente: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500