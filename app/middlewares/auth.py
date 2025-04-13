# app/middlewares/auth.py
from flask import request, jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Verificar JWT en request
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token inválido o expirado'}), 401
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Verificar JWT en request
            verify_jwt_in_request()
            
            # Obtener claims del JWT
            claims = get_jwt()
            
            # Verificar si es admin
            if not claims.get('es_admin', False):
                return jsonify({'error': 'Se requieren permisos de administrador'}), 403
                
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token inválido o expirado'}), 401
    return decorated

def bombero_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Verificar JWT en request
            verify_jwt_in_request()
            
            # Obtener claims del JWT
            claims = get_jwt()
            
            # Verificar si es bombero
            if not claims.get('es_bombero', False):
                return jsonify({'error': 'Se requieren permisos de bombero'}), 403
                
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token inválido o expirado'}), 401
    return decorated