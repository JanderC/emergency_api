# app/routes/reportes_rapidos.py
from flask import Blueprint, request, jsonify, current_app
from app.schemas.reporte_rapido_schema import (
    ReporteRapidoSchema,
    AsignarBomberoReporteSchema,
    CompletarReporteSchema
)
from app.services.reporte_rapido_service import (
    crear_reporte_rapido,
    obtener_reportes_pendientes,
    obtener_reporte_por_id,
    asignar_bombero_a_reporte,
    marcar_reporte_atendido,
    obtener_reportes_por_usuario
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

reporte_rapido_bp = Blueprint('reporte_rapido', __name__, url_prefix='/api/reportes-rapidos')

@reporte_rapido_bp.route('', methods=['POST'])
def crear_reporte():
    """
    Endpoint para crear un reporte rápido de emergencia
    Puede ser usado CON o SIN autenticación
    """
    try:
        # Validar datos
        schema = ReporteRapidoSchema()
        datos = schema.load(request.json)
        
        # Obtener usuario_id si está autenticado
        usuario_id = None
        try:
            usuario_id = get_jwt_identity()
        except:
            pass  # No está autenticado, continuar sin usuario_id
        
        # Crear reporte
        resultado, codigo = crear_reporte_rapido(datos, usuario_id)
        
        return jsonify(resultado), codigo
        
    except ValidationError as ve:
        return jsonify({"error": "Datos inválidos", "detalles": ve.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Error al crear reporte rápido: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@reporte_rapido_bp.route('/pendientes', methods=['GET'])
@jwt_required()
def listar_pendientes():
    """
    Endpoint para obtener reportes pendientes
    Solo accesible por bomberos
    """
    try:
        reportes, codigo = obtener_reportes_pendientes()
        return jsonify(reportes), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener reportes pendientes: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@reporte_rapido_bp.route('/<reporte_id>', methods=['GET'])
@jwt_required()
def obtener_reporte(reporte_id):
    """
    Endpoint para obtener un reporte específico
    """
    try:
        reporte, codigo = obtener_reporte_por_id(reporte_id)
        return jsonify(reporte), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener reporte: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@reporte_rapido_bp.route('/<reporte_id>/asignar', methods=['POST'])
@jwt_required()
def asignar_bombero(reporte_id):
    """
    Endpoint para asignar un bombero a un reporte
    """
    try:
        schema = AsignarBomberoReporteSchema()
        datos = schema.load(request.json)
        
        resultado, codigo = asignar_bombero_a_reporte(reporte_id, datos['bombero_id'])
        
        return jsonify(resultado), codigo
        
    except ValidationError as ve:
        return jsonify({"error": "Datos inválidos", "detalles": ve.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Error al asignar bombero: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@reporte_rapido_bp.route('/<reporte_id>/completar', methods=['POST'])
@jwt_required()
def completar_reporte(reporte_id):
    """
    Endpoint para marcar un reporte como atendido
    """
    try:
        schema = CompletarReporteSchema()
        datos = schema.load(request.json)
        
        resultado, codigo = marcar_reporte_atendido(reporte_id, datos.get('notas'))
        
        return jsonify(resultado), codigo
        
    except ValidationError as ve:
        return jsonify({"error": "Datos inválidos", "detalles": ve.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Error al completar reporte: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@reporte_rapido_bp.route('/mis-reportes', methods=['GET'])
@jwt_required()
def mis_reportes():
    """
    Endpoint para obtener los reportes del usuario autenticado
    """
    try:
        usuario_id = get_jwt_identity()
        reportes, codigo = obtener_reportes_por_usuario(usuario_id)
        
        return jsonify(reportes), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener reportes del usuario: {str(e)}")
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500