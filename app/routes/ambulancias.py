# app/routes/ambulancias.py
from flask import Blueprint, request, jsonify, current_app, g
from app.schemas.ambulancia_schema import RegistroAmbulanciaSchema, AmbulanciaSchema
from app.services.ambulancia_service import (
    registrar_ambulancia, 
    asignar_ambulancia, 
    actualizar_estado_ambulancia, 
    obtener_ambulancias
)
from app.middlewares.auth import token_required, bombero_required

ambulancia_bp = Blueprint('ambulancia', __name__, url_prefix='/api/ambulancias')

@ambulancia_bp.route('', methods=['POST'])
@token_required
@bombero_required
def crear_ambulancia():
    """
    Endpoint para registrar una nueva ambulancia
    """
    try:
        # Identificar al bombero que crea la ambulancia
        bombero_id = g.bombero_id
        
        # Validar datos
        schema = RegistroAmbulanciaSchema()
        datos = schema.load(request.json)
        
        # Registrar ambulancia
        resultado, codigo = registrar_ambulancia(datos, bombero_id)
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de crear ambulancia: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('', methods=['GET'])
@token_required
def listar_ambulancias():
    """
    Endpoint para obtener lista de ambulancias
    """
    try:
        # Filtros opcionales
        filtros = {}
        if 'estado' in request.args:
            filtros['estado'] = request.args.get('estado')
        if 'disponible' in request.args:
            filtros['disponible'] = request.args.get('disponible').lower() == 'true'
        
        # Obtener ambulancias
        ambulancias, codigo = obtener_ambulancias(filtros)
        
        if isinstance(ambulancias, list):
            schema = AmbulanciaSchema(many=True)
            return jsonify(schema.dump(ambulancias)), codigo
        else:
            return jsonify(ambulancias), codigo
            
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de listar ambulancias: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('/<int:ambulancia_id>/asignar', methods=['PUT'])
@token_required
@bombero_required
def asignar_a_bombero(ambulancia_id):
    """
    Endpoint para asignar una ambulancia a un bombero
    """
    try:
        bombero_id = g.bombero_id
        
        # Asignar ambulancia
        resultado, codigo = asignar_ambulancia(ambulancia_id, bombero_id)
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de asignar ambulancia: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('/<int:ambulancia_id>/estado', methods=['PUT'])
@token_required
@bombero_required
def cambiar_estado_ambulancia(ambulancia_id):
    """
    Endpoint para actualizar el estado de una ambulancia
    """
    try:
        datos = request.json
        
        if 'estado' not in datos:
            return jsonify({"error": "El estado es requerido"}), 400
            
        # Actualizar estado
        resultado, codigo = actualizar_estado_ambulancia(ambulancia_id, datos['estado'])
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de cambiar estado ambulancia: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500