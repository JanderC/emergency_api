# app/routes/emergencias.py
from flask import Blueprint, request, jsonify, current_app, g
from app.services.emergencia_service import (
    tomar_emergencia,
    liberar_emergencia, 
    obtener_emergencias_bombero,
    obtener_emergencias_disponibles,
    actualizar_ubicacion_bombero
)
from app.middlewares.auth import token_required, bombero_required

emergencia_bp = Blueprint('emergencia', __name__, url_prefix='/api/emergencias')

@emergencia_bp.route('/disponibles', methods=['GET'])
@token_required
@bombero_required
def listar_emergencias_disponibles():
    """
    Obtiene emergencias disponibles para ser tomadas por bomberos
    """
    try:
        # Filtros opcionales
        filtros = {}
        if 'nivel_urgencia' in request.args:
            filtros['nivel_urgencia'] = request.args.get('nivel_urgencia')
        if 'tipo_emergencia' in request.args:
            filtros['tipo_emergencia'] = request.args.get('tipo_emergencia')
        
        emergencias, codigo = obtener_emergencias_disponibles(filtros)
        return jsonify(emergencias), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint emergencias disponibles: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@emergencia_bp.route('/<string:incidente_id>/tomar', methods=['POST'])
@token_required
@bombero_required
def tomar_emergencia_endpoint(incidente_id):
    """
    Permite que un bombero tome una emergencia
    """
    try:
        bombero_id = g.usuario_id
        resultado, codigo = tomar_emergencia(bombero_id, incidente_id)
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint tomar emergencia: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@emergencia_bp.route('/<string:incidente_id>/liberar', methods=['POST'])
@token_required
@bombero_required
def liberar_emergencia_endpoint(incidente_id):
    """
    Permite que un bombero libere una emergencia asignada
    """
    try:
        bombero_id = g.usuario_id
        datos = request.json
        razon = datos.get('razon', 'No especificada')
        
        resultado, codigo = liberar_emergencia(bombero_id, incidente_id, razon)
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint liberar emergencia: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@emergencia_bp.route('/mis-emergencias', methods=['GET'])
@token_required
@bombero_required
def listar_mis_emergencias():
    
    """
    Obtiene las emergencias asignadas al bombero actual
    """
    print("Esto trae bombero id", bombero_id)

    try:
        datos = request.json
        #buscamos el bombero id 
        bombero_id = datos.get('bombero_id')
        # Filtros opcionales
        filtros = {}
        if 'estado' in request.args:
            filtros['estado'] = request.args.get('estado')
        
        emergencias, codigo = obtener_emergencias_bombero(bombero_id, filtros)
        return jsonify(emergencias), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint mis emergencias: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@emergencia_bp.route('/ubicacion', methods=['PUT'])
@token_required
@bombero_required
def actualizar_ubicacion():
    """
    Actualiza la ubicación actual del bombero
    """
    try:
        bombero_id = g.usuario_id
        datos = request.json
        
        if 'lat' not in datos or 'lng' not in datos:
            return jsonify({"error": "Coordenadas lat y lng son requeridas"}), 400
        
        resultado, codigo = actualizar_ubicacion_bombero(
            bombero_id, 
            datos['lat'], 
            datos['lng']
        )
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint actualizar ubicación: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500