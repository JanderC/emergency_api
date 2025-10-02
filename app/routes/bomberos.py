# app/routes/bomberos.py
from flask import Blueprint, request, jsonify, current_app
from app.schemas.bombero_schema import RegistroBomberoSchema, BomberoSchema
from app.services.bombero_service import (
    registrar_bombero, 
    obtener_bombero, 
    actualizar_estado_bombero,
    actualizar_perfil_bombero,
    actualizar_ubicacion_bombero,
    obtener_bomberos_disponibles,
    obtener_todos_bomberos,
    desactivar_bombero
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

@bombero_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obtener_mi_perfil():
    """
    Endpoint para obtener el perfil del bombero autenticado
    """
    try:
        print("entro en la funcion de obtener perfil")
        usuario_id = get_jwt_identity()
        print("usuario_id:", usuario_id)
        bombero, codigo = obtener_bombero(usuario_id)
        
        if codigo == 200:
            return jsonify(bombero), 200
        else:
            return jsonify(bombero), codigo
            
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de obtener perfil: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@bombero_bp.route('/perfil', methods=['PUT'])
@jwt_required()
def actualizar_mi_perfil():
    """
    Endpoint para actualizar el perfil del bombero autenticado
    """
    try:
        usuario_id = get_jwt_identity()
        datos = request.json
        
        if not datos:
            return jsonify({"error": "No se enviaron datos para actualizar"}), 400
        
        resultado, codigo = actualizar_perfil_bombero(usuario_id, datos)
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de actualizar perfil: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@bombero_bp.route('/estado', methods=['PUT'])
@jwt_required()
def cambiar_mi_estado():
    """
    Endpoint para actualizar el estado de servicio del bombero autenticado
    """
    try:
        usuario_id = get_jwt_identity()
        datos = request.json
        
        if 'estado_servicio' not in datos:
            return jsonify({"error": "El estado de servicio es requerido"}), 400
            
        # Actualizar estado
        resultado, codigo = actualizar_estado_bombero(usuario_id, datos['estado_servicio'])
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de cambiar estado: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@bombero_bp.route('/ubicacion', methods=['PUT'])
@jwt_required()
def actualizar_mi_ubicacion():
    """
    Endpoint para actualizar la ubicación del bombero autenticado
    """
    try:
        usuario_id = get_jwt_identity()
        datos = request.json
        
        if 'lat' not in datos or 'lng' not in datos:
            return jsonify({"error": "Las coordenadas lat y lng son requeridas"}), 400
            
        resultado, codigo = actualizar_ubicacion_bombero(
            usuario_id, 
            datos['lat'], 
            datos['lng']
        )
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de actualizar ubicación: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@bombero_bp.route('/disponibles', methods=['GET'])
@jwt_required()
def listar_bomberos_disponibles():
    """
    Endpoint para obtener lista de bomberos disponibles
    """
    try:
        bomberos, codigo = obtener_bomberos_disponibles()
        return jsonify(bomberos), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de bomberos disponibles: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@bombero_bp.route('', methods=['GET'])
@jwt_required()
def listar_todos_bomberos():
    """
    Endpoint para obtener lista de todos los bomberos con filtros opcionales
    """
    try:
        filtros = {
            'estado_servicio': request.args.get('estado_servicio'),
            'estacion_pertenencia': request.args.get('estacion_pertenencia'),
            'rango': request.args.get('rango'),
            'tiene_ambulancia': request.args.get('tiene_ambulancia') == 'true' if request.args.get('tiene_ambulancia') else None
        }
        
        # Remover filtros None
        filtros = {k: v for k, v in filtros.items() if v is not None}
        
        bomberos, codigo = obtener_todos_bomberos(filtros if filtros else None)
        return jsonify(bomberos), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de listar bomberos: {str(e)}")
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
            return jsonify(bombero), 200
        else:
            return jsonify(bombero), codigo
            
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de detalle bombero: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@bombero_bp.route('/<bombero_id>/estado', methods=['PUT'])
@jwt_required()
def cambiar_estado_bombero(bombero_id):
    """
    Endpoint para actualizar el estado de servicio de un bombero específico
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

@bombero_bp.route('/<bombero_id>/desactivar', methods=['PUT'])
@jwt_required()
def desactivar_bombero_endpoint(bombero_id):
    """
    Endpoint para desactivar un bombero del sistema (Solo administradores)
    """
    try:
        admin_id = get_jwt_identity()
        resultado, codigo = desactivar_bombero(bombero_id, admin_id)
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint de desactivar bombero: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500