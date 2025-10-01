# app/routes/usuarios.py
from flask import Blueprint, request, jsonify, current_app, g
from app.middlewares.auth import token_required, bombero_required
from app.services.usuario_service import (
    obtener_perfil_usuario,
    actualizar_perfil_usuario,
    cambiar_password_usuario,
    obtener_historial_incidentes_usuario,
    obtener_notificaciones_usuario,
    marcar_notificacion_leida,
    obtener_usuarios_sistema,
    eliminar_usuario
)
from bson.objectid import ObjectId

usuario_bp = Blueprint('usuario', __name__, url_prefix='/api/usuarios')

@usuario_bp.route('/perfil', methods=['GET'])
@token_required
def obtener_perfil():
    """
    Obtiene el perfil completo del usuario autenticado
    """
    try:
        usuario_id = g.usuario_id
        current_app.logger.info(f"Obteniendo perfil para usuario: {usuario_id}")
        
        perfil, codigo = obtener_perfil_usuario(usuario_id)
        return jsonify(perfil), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint obtener_perfil: {str(e)}")
        return jsonify({"error": "Error al obtener el perfil"}), 500

@usuario_bp.route('/perfil', methods=['PUT'])
@token_required
def actualizar_perfil():
    try:
        usuario_id = g.usuario_id
        datos = request.json
        
        if not datos:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400
        
        # Validar y corregir formato de foto_perfil
        if 'foto_perfil' in datos:
            foto = datos['foto_perfil']
            if foto:
                # Si ya tiene el formato correcto, dejarlo
                if not foto.startswith('data:image/'):
                    # Si es base64 puro, agregar el prefijo
                    datos['foto_perfil'] = f'data:image/jpeg;base64,{foto}'
                # Si tiene formato incorrecto como "data:image//9j/", corregirlo
                elif foto.startswith('data:image/') and ';base64,' not in foto:
                    # Extraer solo el base64
                    base64_data = foto.replace('data:image/', '')
                    datos['foto_perfil'] = f'data:image/jpeg;base64,{base64_data}'
        
        resultado, codigo = actualizar_perfil_usuario(usuario_id, datos)
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint actualizar_perfil: {str(e)}")
        return jsonify({"error": "Error al actualizar el perfil"}), 500

@usuario_bp.route('/cambiar-password', methods=['POST'])
@token_required
def cambiar_password():
    """
    Cambia la contraseña del usuario autenticado
    Requiere: password_actual, password_nueva
    """
    try:
        usuario_id = g.usuario_id
        datos = request.json
        
        if not datos or 'password_actual' not in datos or 'password_nueva' not in datos:
            return jsonify({"error": "Se requiere password_actual y password_nueva"}), 400
        
        password_actual = datos['password_actual']
        password_nueva = datos['password_nueva']
        
        # Validar longitud de nueva contraseña
        if len(password_nueva) < 6:
            return jsonify({"error": "La nueva contraseña debe tener al menos 6 caracteres"}), 400
        
        current_app.logger.info(f"Cambiando contraseña para usuario: {usuario_id}")
        
        resultado, codigo = cambiar_password_usuario(usuario_id, password_actual, password_nueva)
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint cambiar_password: {str(e)}")
        return jsonify({"error": "Error al cambiar la contraseña"}), 500

@usuario_bp.route('/historial-incidentes', methods=['GET'])
@token_required
def historial_incidentes():
    """
    Obtiene el historial de incidentes reportados por el usuario
    Query params opcionales: estado, fecha_desde, fecha_hasta
    """
    try:
        usuario_id = g.usuario_id
        
        # Construir filtros desde query params
        filtros = {}
        if 'estado' in request.args:
            filtros['estado'] = request.args.get('estado')
        if 'fecha_desde' in request.args:
            try:
                from datetime import datetime
                filtros['fecha_desde'] = datetime.fromisoformat(request.args.get('fecha_desde'))
            except:
                return jsonify({"error": "Formato de fecha_desde inválido. Use YYYY-MM-DD"}), 400
        if 'fecha_hasta' in request.args:
            try:
                from datetime import datetime
                filtros['fecha_hasta'] = datetime.fromisoformat(request.args.get('fecha_hasta'))
            except:
                return jsonify({"error": "Formato de fecha_hasta inválido. Use YYYY-MM-DD"}), 400
        
        current_app.logger.info(f"Obteniendo historial de incidentes para usuario: {usuario_id}")
        
        incidentes, codigo = obtener_historial_incidentes_usuario(usuario_id, filtros)
        return jsonify(incidentes), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint historial_incidentes: {str(e)}")
        return jsonify({"error": "Error al obtener historial"}), 500

@usuario_bp.route('/notificaciones', methods=['GET'])
@token_required
def listar_notificaciones():
    """
    Obtiene las notificaciones del usuario
    Query param opcional: solo_no_leidas (true/false)
    """
    try:
        usuario_id = g.usuario_id
        solo_no_leidas = request.args.get('solo_no_leidas', 'false').lower() == 'true'
        
        current_app.logger.info(f"Obteniendo notificaciones para usuario: {usuario_id}")
        
        notificaciones, codigo = obtener_notificaciones_usuario(usuario_id, solo_no_leidas)
        return jsonify(notificaciones), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint listar_notificaciones: {str(e)}")
        return jsonify({"error": "Error al obtener notificaciones"}), 500

@usuario_bp.route('/notificaciones/<string:notificacion_id>/marcar-leida', methods=['POST'])
@token_required
def marcar_notificacion_como_leida(notificacion_id):
    """
    Marca una notificación específica como leída
    """
    try:
        usuario_id = g.usuario_id
        
        # Validar que el ID sea válido
        try:
            ObjectId(notificacion_id)
        except:
            return jsonify({"error": "ID de notificación inválido"}), 400
        
        current_app.logger.info(f"Marcando notificación {notificacion_id} como leída para usuario: {usuario_id}")
        
        resultado, codigo = marcar_notificacion_leida(usuario_id, notificacion_id)
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint marcar_notificacion_como_leida: {str(e)}")
        return jsonify({"error": "Error al marcar notificación"}), 500

@usuario_bp.route('/sistema', methods=['GET'])
@token_required
@bombero_required
def listar_usuarios_sistema():
    """
    Lista todos los usuarios del sistema (solo para bomberos/administradores)
    Query params opcionales: es_bombero (true/false), nombre
    """
    try:
        admin_id = g.usuario_id
        
        # Construir filtros desde query params
        filtros = {}
        if 'es_bombero' in request.args:
            filtros['es_bombero'] = request.args.get('es_bombero').lower() == 'true'
        if 'nombre' in request.args:
            filtros['nombre'] = request.args.get('nombre')
        
        current_app.logger.info(f"Administrador {admin_id} listando usuarios del sistema")
        
        usuarios, codigo = obtener_usuarios_sistema(admin_id, filtros)
        return jsonify(usuarios), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint listar_usuarios_sistema: {str(e)}")
        return jsonify({"error": "Error al obtener usuarios"}), 500

@usuario_bp.route('/<string:usuario_id>', methods=['DELETE'])
@token_required
@bombero_required
def eliminar_usuario_sistema(usuario_id):
    """
    Elimina un usuario del sistema (solo para bomberos/administradores)
    """
    try:
        admin_id = g.usuario_id
        
        # Validar que el ID sea válido
        try:
            ObjectId(usuario_id)
        except:
            return jsonify({"error": "ID de usuario inválido"}), 400
        
        # No permitir que un usuario se elimine a sí mismo
        if usuario_id == admin_id:
            return jsonify({"error": "No puedes eliminarte a ti mismo"}), 400
        
        current_app.logger.info(f"Administrador {admin_id} eliminando usuario: {usuario_id}")
        
        resultado, codigo = eliminar_usuario(usuario_id, admin_id)
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en endpoint eliminar_usuario_sistema: {str(e)}")
        return jsonify({"error": "Error al eliminar usuario"}), 500