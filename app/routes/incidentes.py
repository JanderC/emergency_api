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
    usuario_id = g.usuario_id
    
    try:
        # Validar datos
        schema = ReporteIncidenteSchema()
        datos = schema.load(request.json)
        
        # Registrar incidente
        resultado, codigo = reportar_incidente(usuario_id, datos)
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de crear incidente: {str(e)}")
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