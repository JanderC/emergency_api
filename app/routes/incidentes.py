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
    # Verificamos si tenemos acceso a g.usuario_id
    current_app.logger.info("=== INICIO DEBUG CREAR INCIDENTE ===")
    
    # Log para verificar si el token llegó y se procesó correctamente
    current_app.logger.info(f"Token procesado: usuario_id = {g.usuario_id if hasattr(g, 'usuario_id') else 'No disponible'}")
    
    # Log para verificar los headers de la solicitud
    auth_header = request.headers.get('Authorization', 'No hay header de autorización')
    current_app.logger.info(f"Header de autorización: {auth_header}")
    
    # Verificamos que el usuario_id exista antes de continuar
    if not hasattr(g, 'usuario_id'):
        current_app.logger.error("No se encontró usuario_id en el contexto global")
        return jsonify({"error": "No autorizado - Token inválido o ausente"}), 401
    
    usuario_id = g.usuario_id
    current_app.logger.info(f"Usuario ID validado: {usuario_id}")
    
    try:
        # Log para verificar el body recibido
        current_app.logger.info(f"Datos recibidos: {request.json}")
        
        # Validar datos
        schema = ReporteIncidenteSchema()
        try:
            datos = schema.load(request.json)
            current_app.logger.info(f"Datos validados por el schema correctamente: {datos}")
        except Exception as schema_error:
            current_app.logger.error(f"Error en la validación del schema: {str(schema_error)}")
            return jsonify({"error": f"Error en los datos proporcionados: {str(schema_error)}"}), 400
        
        # Registrar incidente
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
    Endpoint para obtener lista de incidentes
    """
    try:
        # Filtros opcionales
        filtros = {}
        if 'estado' in request.args:
            filtros['estado'] = request.args.get('estado')
        if 'nivel_urgencia' in request.args:
            filtros['nivel_urgencia'] = request.args.get('nivel_urgencia')
        if 'tipo_emergencia' in request.args:
            filtros['tipo_emergencia'] = request.args.get('tipo_emergencia')
        
        # Obtener incidentes
        incidentes, codigo = obtener_incidentes(filtros)
        
        if isinstance(incidentes, list):
            schema = IncidenteSchema(many=True)
            return jsonify(schema.dump(incidentes)), codigo
        else:
            return jsonify(incidentes), codigo
            
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de listar incidentes: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@incidente_bp.route('/mongodb/<string:mongodb_id>', methods=['GET'])
@token_required
def obtener_incidente_por_mongodb_id(mongodb_id):
    """
    Endpoint para obtener un incidente por su ID de MongoDB
    """
    try:
        # Intentar convertir el ID a ObjectId
        try:
            from bson.objectid import ObjectId
            object_id = ObjectId(mongodb_id)
        except Exception as e:
            return jsonify({"error": f"ID de MongoDB inválido: {str(e)}"}), 400
            
        # Buscar el incidente
        from app import db
        incidente = db.incidentes.find_one({"_id": object_id})
        
        if not incidente:
            return jsonify({"error": "Incidente no encontrado"}), 404
            
        # Convertir ObjectId a string para JSON
        incidente["_id"] = str(incidente["_id"])
        
        # Usar el schema para formatear la respuesta
        schema = IncidenteSchema()
        return jsonify(schema.dump(incidente)), 200
            
    except Exception as e:
        current_app.logger.error(f"Error al buscar incidente por MongoDB ID: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@incidente_bp.route('/<int:incidente_id>', methods=['GET'])
@token_required
def detalle_incidente(incidente_id):
    """
    Endpoint para obtener detalles de un incidente específico
    """
    try:
        # Obtener incidente
        incidente, codigo = obtener_incidente(incidente_id)
        
        if codigo == 200:
            schema = IncidenteSchema()
            return jsonify(schema.dump(incidente)), 200
        else:
            return jsonify(incidente), codigo
            
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de detalle incidente: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@incidente_bp.route('/<int:incidente_id>/estado', methods=['PUT'])
@token_required
def cambiar_estado_incidente(incidente_id):
    """
    Endpoint para actualizar el estado de un incidente
    """
    try:
        datos = request.json
        
        if 'estado' not in datos:
            return jsonify({"error": "El estado es requerido"}), 400
            
        bombero_id = datos.get('bombero_id')
        ambulancia_id = datos.get('ambulancia_id')
        nuevo_estado = datos['estado']
        
        # Actualizar estado
        resultado, codigo = actualizar_estado_incidente(
            incidente_id, 
            bombero_id, 
            ambulancia_id, 
            nuevo_estado
        )
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de cambiar estado: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500