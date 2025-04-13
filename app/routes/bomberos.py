# app/routes/bomberos.py
from flask import Blueprint, request, jsonify, current_app
from app.schemas.bombero_schema import RegistroBomberoSchema, BomberoSchema
from app.services.bombero_service import (
    registrar_bombero, 
    obtener_bombero, 
    actualizar_estado_bombero
)
from flask_jwt_extended import jwt_required, get_jwt_identity

bombero_bp = Blueprint('bombero', __name__, url_prefix='/api/bomberos')

@bombero_bp.route('/registro', methods=['POST'])
def registrar_nuevo_bombero():
    """
    Endpoint para registrar un nuevo bombero
    """
    try:
        print("entro en la funcion de registrar bombero")
        # Validar datos
        schema = RegistroBomberoSchema()
        datos = schema.load(request.json)
        print("segundo debuggear")
        # Registrar bombero
        resultado, codigo = registrar_bombero(datos)
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de registro bombero: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@bombero_bp.route('/<bombero_id>', methods=['GET'])
@jwt_required()
def detalle_bombero(bombero_id):
    """
    Endpoint para obtener detalles de un bombero específico
    """
    try:
        bombero, codigo = obtener_bombero(bombero_id)
        
        if codigo == 200:
            return jsonify(bombero.to_dict()), 200
        else:
            return jsonify(bombero), codigo
            
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de detalle bombero: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@bombero_bp.route('/<bombero_id>/estado', methods=['PUT'])
@jwt_required()
def cambiar_estado_bombero(bombero_id):
    """
    Endpoint para actualizar el estado de servicio de un bombero
    """
    try:
        datos = request.json
        
        if 'estado_servicio' not in datos:
            return jsonify({"error": "El estado de servicio es requerido"}), 400
            
        # Actualizar estado
        resultado, codigo = actualizar_estado_bombero(bombero_id, datos['estado_servicio'])
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de cambiar estado bombero: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500