# app/services/ambulancia_service.py
from flask import current_app
from app.models.ambulancia import Ambulancia
from app.models.bombero import Bombero
from app.models.cambios_ambulancia import CambioAmbulancia
from datetime import datetime

def registrar_ambulancia(datos, bombero_id=None):
    """
    Registra una nueva ambulancia en el sistema y opcionalmente la asigna a un bombero
    """
    try:
        db = current_app.extensions['sqlalchemy'].db
        
        # Verificar si la placa ya existe
        ambulancia_existente = Ambulancia.query.filter_by(placa=datos['placa']).first()
        if ambulancia_existente:
            return {"error": "Ya existe una ambulancia con esa placa"}, 400
        
        # Crear nueva ambulancia
        nueva_ambulancia = Ambulancia(
            placa=datos['placa'],
            modelo=datos['modelo'],
            ano=datos['ano'],
            estado=datos.get('estado', 'operativa'),
            bombero_asignado_id=bombero_id,
            ubicacion_actual=datos.get('ubicacion_actual')
        )
        
        db.session.add(nueva_ambulancia)
        
        # Si hay un bombero asignado, actualizar su referencia a la ambulancia
        if bombero_id:
            bombero = Bombero.query.get(bombero_id)
            if bombero:
                bombero.ambulancia_id = nueva_ambulancia.id
                bombero.estado_servicio = 'disponible'
        
        db.session.commit()
        
        return {
            "mensaje": "Ambulancia registrada con éxito",
            "id": nueva_ambulancia.id
        }, 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al registrar ambulancia: {str(e)}")
        return {"error": "Error al registrar la ambulancia"}, 500

def asignar_ambulancia(ambulancia_id, bombero_id):
    """
    Asigna una ambulancia a un bombero
    """
    try:
        db = current_app.extensions['sqlalchemy'].db
        
        ambulancia = Ambulancia.query.get(ambulancia_id)
        if not ambulancia:
            return {"error": "Ambulancia no encontrada"}, 404
            
        bombero = Bombero.query.get(bombero_id)
        if not bombero:
            return {"error": "Bombero no encontrado"}, 404
            
        # Si la ambulancia ya está asignada a otro bombero, registrar el cambio
        if ambulancia.bombero_asignado_id and ambulancia.bombero_asignado_id != bombero_id:
            cambio = CambioAmbulancia(
                bombero_anterior_id=ambulancia.bombero_asignado_id,
                bombero_nuevo_id=bombero_id,
                ambulancia_id=ambulancia_id,
                estado='confirmado',
                razon_cambio='Reasignación de ambulancia'
            )
            db.session.add(cambio)
            
            # Actualizar el bombero anterior
            bombero_anterior = Bombero.query.get(ambulancia.bombero_asignado_id)
            if bombero_anterior:
                bombero_anterior.ambulancia_id = None
        
        # Asignar ambulancia al nuevo bombero
        ambulancia.bombero_asignado_id = bombero_id
        bombero.ambulancia_id = ambulancia_id
        
        db.session.commit()
        
        return {
            "mensaje": "Ambulancia asignada con éxito", 
            "ambulancia_id": ambulancia_id,
            "bombero_id": bombero_id
        }, 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al asignar ambulancia: {str(e)}")
        return {"error": "Error al asignar la ambulancia"}, 500

def actualizar_estado_ambulancia(ambulancia_id, nuevo_estado):
    """
    Actualiza el estado de una ambulancia
    """
    try:
        db = current_app.extensions['sqlalchemy'].db
        ambulancia = Ambulancia.query.get(ambulancia_id)
        
        if not ambulancia:
            return {"error": "Ambulancia no encontrada"}, 404
            
        ambulancia.estado = nuevo_estado
        db.session.commit()
        
        return {
            "mensaje": f"Estado de ambulancia actualizado a {nuevo_estado}",
            "ambulancia_id": ambulancia_id
        }, 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al actualizar estado de ambulancia {ambulancia_id}: {str(e)}")
        return {"error": "Error al actualizar el estado de la ambulancia"}, 500

def obtener_ambulancias(filtros=None):
    """
    Obtiene lista de ambulancias con filtros opcionales
    """
    try:
        query = Ambulancia.query
        
        if filtros:
            if 'estado' in filtros:
                query = query.filter(Ambulancia.estado == filtros['estado'])
            if 'disponible' in filtros and filtros['disponible']:
                query = query.filter(Ambulancia.bombero_asignado_id == None)
        
        ambulancias = query.all()
        return ambulancias, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener ambulancias: {str(e)}")
        return {"error": "Error al obtener ambulancias"}, 500