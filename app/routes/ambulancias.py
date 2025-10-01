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
from bson.objectid import ObjectId

ambulancia_bp = Blueprint('ambulancia', __name__, url_prefix='/api/ambulancias')

@ambulancia_bp.route('', methods=['POST'])
@token_required
@bombero_required
def crear_ambulancia():
    """
    Endpoint para registrar una nueva ambulancia
    """
    try:
        current_app.logger.info("=== INICIO REGISTRO AMBULANCIA ===")
        
        if not hasattr(g, 'usuario_id'):
            current_app.logger.error("No se encontró usuario_id")
            return jsonify({"error": "No autorizado"}), 401
        
        bombero_id = g.usuario_id
        current_app.logger.info(f"Bombero ID: {bombero_id}")
        current_app.logger.info(f"Datos recibidos: {request.json}")
        
        schema = RegistroAmbulanciaSchema()
        try:
            datos = schema.load(request.json)
            current_app.logger.info(f"Datos validados: {datos}")
        except Exception as schema_error:
            current_app.logger.error(f"Error de validación: {str(schema_error)}")
            return jsonify({"error": f"Datos inválidos: {str(schema_error)}"}), 400
        
        resultado, codigo = registrar_ambulancia(datos, bombero_id)
        current_app.logger.info(f"Resultado: {resultado}")
        
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
    """
    try:
        filtros = {}
        if 'estado' in request.args:
            filtros['estado'] = request.args.get('estado')
        if 'disponible' in request.args:
            filtros['disponible'] = request.args.get('disponible').lower() == 'true'
        
        ambulancias, codigo = obtener_ambulancias(filtros)
        
        if isinstance(ambulancias, list):
            schema = AmbulanciaSchema(many=True)
            return jsonify(schema.dump(ambulancias)), codigo
        else:
            return jsonify(ambulancias), codigo
            
    except Exception as e:
        current_app.logger.error(f"Error en listar_ambulancias: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('/<string:ambulancia_id>/asignar', methods=['PUT'])
@token_required
@bombero_required
def asignar_a_bombero(ambulancia_id):
    """
    Endpoint para asignar una ambulancia a un bombero
    """
    try:
        bombero_id = g.usuario_id
        
        try:
            ObjectId(ambulancia_id)
        except Exception as e:
            return jsonify({"error": f"ID inválido: {str(e)}"}), 400
        
        resultado, codigo = asignar_ambulancia(ambulancia_id, bombero_id)
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en asignar_a_bombero: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('/<string:ambulancia_id>/estado', methods=['PUT'])
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
        
        try:
            ObjectId(ambulancia_id)
        except Exception as e:
            return jsonify({"error": f"ID inválido: {str(e)}"}), 400
        
        resultado, codigo = actualizar_estado_ambulancia(ambulancia_id, datos['estado'])
        return jsonify(resultado), codigo
        
    except Exception as e:
        current_app.logger.error(f"Error en cambiar_estado_ambulancia: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500

@ambulancia_bp.route('/<string:ambulancia_id>', methods=['GET'])
@token_required
def obtener_ambulancia_detalle(ambulancia_id):
    """
    Endpoint para obtener detalles de una ambulancia
    """
    try:
        from app import db
        
        try:
            object_id = ObjectId(ambulancia_id)
        except Exception as e:
            return jsonify({"error": f"ID inválido: {str(e)}"}), 400
        
        ambulancia = db.ambulancias.find_one({"_id": object_id})
        
        if not ambulancia:
            return jsonify({"error": "Ambulancia no encontrada"}), 404
        
        ambulancia["_id"] = str(ambulancia["_id"])
        
        schema = AmbulanciaSchema()
        return jsonify(schema.dump(ambulancia)), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener ambulancia: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500