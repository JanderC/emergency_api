# app/routes/auth.py
from flask import Blueprint, request, jsonify
from app.schemas.usuario_schema import RegistroSchema, LoginSchema
from app.services.auth_service import AuthService
from app.models.usuarios import Usuario
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        print("Entro a registrarse el usuario")
        # Imprimir el request.data antes de procesarlo
        print("Datos recibidos:", request.data)
        
        # Validar datos de entrada
        schema = RegistroSchema()
        print("Entro a registrarse el usuario dos")
        data = schema.load(request.json)
        print("Data cargada:", data)
        
        # Registrar usuario
        resultado, codigo = AuthService.registrar_usuario(data)
        print("Este es el resultado", resultado)
        return jsonify(resultado), codigo
    
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Esto imprimirá el stack trace completo
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # Validar datos de entrada
        schema = LoginSchema()
        data = schema.load(request.json)
        
        # Iniciar sesión
        resultado, codigo = AuthService.login(data)
        return jsonify(resultado), codigo
    
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    usuario_id = get_jwt_identity()
    resultado, codigo = AuthService.refresh_token(usuario_id)
    return jsonify(resultado), codigo

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    try:
        usuario_id = get_jwt_identity()
        # Usar el método find_by_id del modelo Usuario de MongoDB
        usuario = Usuario.find_by_id(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        return jsonify(usuario.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500