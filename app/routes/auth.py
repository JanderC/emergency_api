# app/routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from app.schemas.usuario_schema import RegistroSchema, LoginSchema
from app.services.auth_service import AuthService
from app.models.usuarios import Usuario
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        current_app.logger.info("=== INICIO REGISTRO USUARIO ===")
        current_app.logger.info(f"Datos recibidos: {request.data}")
        current_app.logger.info(f"JSON parseado: {request.json}")
        
        # Validar datos de entrada
        schema = RegistroSchema()
        current_app.logger.info("Schema creado, validando datos...")
        
        try:
            data = schema.load(request.json)
            current_app.logger.info(f"Datos validados correctamente: {data}")
        except ValidationError as ve:
            current_app.logger.error(f"Error de validación: {ve.messages}")
            return jsonify({'error': 'Datos inválidos', 'detalles': ve.messages}), 400
        
        # Registrar usuario
        current_app.logger.info("Llamando a AuthService.registrar_usuario...")
        resultado, codigo = AuthService.registrar_usuario(data)
        current_app.logger.info(f"Resultado del registro: {resultado}, Código: {codigo}")
        
        return jsonify(resultado), codigo
    
    except Exception as e:
        current_app.logger.error("=== ERROR EN REGISTRO ===")
        current_app.logger.error(f"Error: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        current_app.logger.info("=== INICIO LOGIN ===")
        current_app.logger.info(f"Datos recibidos: {request.json}")
        
        # Validar datos de entrada
        schema = LoginSchema()
        
        try:
            data = schema.load(request.json)
        except ValidationError as ve:
            current_app.logger.error(f"Error de validación: {ve.messages}")
            return jsonify({'error': 'Datos inválidos', 'detalles': ve.messages}), 400
        
        # Iniciar sesión
        resultado, codigo = AuthService.login(data)
        return jsonify(resultado), codigo
    
    except Exception as e:
        current_app.logger.error(f"Error en login: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        usuario_id = get_jwt_identity()
        resultado, codigo = AuthService.refresh_token(usuario_id)
        return jsonify(resultado), codigo
    except Exception as e:
        current_app.logger.error(f"Error en refresh: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    try:
        usuario_id = get_jwt_identity()
        current_app.logger.info(f"Obteniendo usuario con ID: {usuario_id}")
        
        # Usar el método find_by_id del modelo Usuario de MongoDB
        usuario = Usuario.find_by_id(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        return jsonify(usuario.to_dict()), 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener usuario: {str(e)}")
        return jsonify({'error': str(e)}), 500