# app/routes/ambulancias.py
from flask import Blueprint, request, jsonify, current_app, g
from app.schemas.ambulancia_schema import RegistroAmbulanciaSchema, AmbulanciaSchema
from app.services.ambulancia_service import (
    registrar_ambulancia, 
    asignar_ambulancia, 
    actualizar_estado_ambulancia, 
    obtener_ambulancias,
    desasignar_ambulancia,
    obtener_ambulancia_por_id
)
from app.middlewares.auth import token_required, bombero_required
from bson.objectid import ObjectId

ambulancia_bp = Blueprint('ambulancia', __name__, url_prefix='/api/ambulancias')

@ambulancia_bp.route('', methods=['POST'])
@token_required
@bombero_required
def crear_ambulancia():
    """
    Endpoint para registrar una nueva ambulancia
    Solo bomberos pueden registrar ambulancias
    """
    try:
        current_app.logger.info("=== INICIO REGISTRO AMBULANCIA ===")
        
        if not hasattr(g, 'usuario_id'):
            current_app.logger.error("No se encontró usuario_id en el token")
            return jsonify({"error": "No autorizado"}), 401
        
        bombero_id = g.usuario_id
        current_app.logger.info(f"Bombero ID: {bombero_id}")
        current_app.logger.info(f"Datos recibidos: {request.json}")
        
        # Validar datos con schema
        schema = RegistroAmbulanciaSchema()
        try:
            datos = schema.load(request.json)
            current_app.logger.info(f"Datos validados correctamente")
        except Exception as schema_error:
            current_app.logger.error(f"Error de validación: {str(schema_error)}")
            return jsonify({"error": f"Datos inválidos: {str(schema_error)}"}), 400
        
        # Registrar ambulancia
        resultado, codigo = registrar_ambulancia(datos, bombero_id)
        current_app.logger.info(f"Resultado del registro: {resultado}")
        
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en crear_ambulancia: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('', methods=['GET'])
@token_required
def listar_ambulancias():
    """
    Endpoint para obtener lista de ambulancias
    Query params opcionales:
    - estado: filtrar por estado (operativa, en_servicio, mantenimiento, fuera_de_servicio)
    - disponible: true para obtener solo disponibles
    """
    try:
        filtros = {}
        
        # Procesar filtros de query params
        if 'estado' in request.args:
            filtros['estado'] = request.args.get('estado')
            current_app.logger.info(f"Filtro de estado: {filtros['estado']}")
        
        if 'disponible' in request.args:
            disponible_str = request.args.get('disponible').lower()
            filtros['disponible'] = disponible_str == 'true'
            current_app.logger.info(f"Filtro de disponible: {filtros['disponible']}")
        
        # Obtener ambulancias
        ambulancias, codigo = obtener_ambulancias(filtros)
        
        if isinstance(ambulancias, list):
            schema = AmbulanciaSchema(many=True)
            return jsonify(schema.dump(ambulancias)), codigo
        else:
            return jsonify(ambulancias), codigo
            
    except Exception as e:
        current_app.logger.error(f"Error en listar_ambulancias: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('/<string:ambulancia_id>', methods=['GET'])
@token_required
def obtener_ambulancia_detalle(ambulancia_id):
    """
    Endpoint para obtener detalles de una ambulancia específica
    """
    try:
        current_app.logger.info(f"Obteniendo detalles de ambulancia: {ambulancia_id}")
        
        # Validar que el ID es válido
        try:
            ObjectId(ambulancia_id)
        except Exception as e:
            return jsonify({"error": f"ID inválido: {str(e)}"}), 400
        
        # Obtener ambulancia
        ambulancia, codigo = obtener_ambulancia_por_id(ambulancia_id)
        
        if codigo == 200:
            schema = AmbulanciaSchema()
            return jsonify(schema.dump(ambulancia)), 200
        else:
            return jsonify(ambulancia), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener ambulancia: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('/<string:ambulancia_id>/asignar', methods=['PUT'])
@token_required
@bombero_required
def asignar_a_bombero(ambulancia_id):
    """
    Endpoint para asignar una ambulancia al bombero autenticado
    """
    try:
        bombero_id = g.usuario_id
        current_app.logger.info(f"Asignando ambulancia {ambulancia_id} a bombero {bombero_id}")
        
        # Validar ID
        try:
            ObjectId(ambulancia_id)
        except Exception as e:
            return jsonify({"error": f"ID inválido: {str(e)}"}), 400
        
        # Asignar ambulancia
        resultado, codigo = asignar_ambulancia(ambulancia_id, bombero_id)
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en asignar_a_bombero: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('/<string:ambulancia_id>/liberar', methods=['PUT'])
@token_required
@bombero_required
def liberar_ambulancia(ambulancia_id):
    """
    Endpoint para liberar una ambulancia (desasignarla del bombero)
    """
    try:
        current_app.logger.info(f"Liberando ambulancia {ambulancia_id}")
        
        # Validar ID
        try:
            ObjectId(ambulancia_id)
        except Exception as e:
            return jsonify({"error": f"ID inválido: {str(e)}"}), 400
        
        # Liberar ambulancia
        resultado, codigo = desasignar_ambulancia(ambulancia_id)
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en liberar_ambulancia: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('/<string:ambulancia_id>/estado', methods=['PUT'])
@token_required
@bombero_required
def cambiar_estado_ambulancia(ambulancia_id):
    """
    Endpoint para actualizar el estado de una ambulancia
    Body JSON: {"estado": "operativa|en_servicio|mantenimiento|fuera_de_servicio"}
    """
    try:
        datos = request.json
        current_app.logger.info(f"Cambiando estado de ambulancia {ambulancia_id}: {datos}")
        
        # Validar que se envió el estado
        if 'estado' not in datos:
            return jsonify({"error": "El campo 'estado' es requerido"}), 400
        
        # Validar ID
        try:
            ObjectId(ambulancia_id)
        except Exception as e:
            return jsonify({"error": f"ID inválido: {str(e)}"}), 400
        
        # Actualizar estado
        resultado, codigo = actualizar_estado_ambulancia(ambulancia_id, datos['estado'])
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en cambiar_estado_ambulancia: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500