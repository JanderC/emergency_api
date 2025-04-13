# app/services/bombero_service.py
from flask import current_app
from app import db
from werkzeug.security import generate_password_hash
from app.models.usuarios import Usuario
from app.models.bombero import Bombero
from datetime import datetime

def registrar_bombero(datos):
    """
    Registra un nuevo bombero en el sistema
    """
    try:
        print("entro en registar bombero")

        #db = current_app.extensions['sqlalchemy'].db
        print("entro en registar bombero 2")
        
        # Verificar si el email ya existe
        usuario_existente = Usuario.query.filter_by(email=datos['email']).first()
        if usuario_existente:
            return {"error": "El correo electrónico ya está registrado"}, 400
        
        # Verificar si el código de bombero ya existe
        bombero_existente = Bombero.query.filter_by(codigo_bombero=datos['codigo_bombero']).first()
        if bombero_existente:
            return {"error": "El código de bombero ya está registrado"}, 400
        
        # Crear nuevo usuario 
        nuevo_usuario = Usuario(
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            email=datos['email'],
            contrasena=generate_password_hash(datos['password']),
            telefono=datos.get('telefono'),
            es_bombero=True,
            fecha_registro=datetime.utcnow()
        )
        db.session.add(nuevo_usuario)
        db.session.flush()  # Para obtener el ID del usuario antes de hacer commit
        
        # Crear registro de bombero
        nuevo_bombero = Bombero(
            usuario_id=nuevo_usuario.id,
            codigo_bombero=datos['codigo_bombero'],
            estacion_pertenencia=datos['estacion_pertenencia'],
            carnet_foto=datos.get('carnet_foto'),
            estado_servicio='disponible'
        )
        
        db.session.add(nuevo_bombero)
        db.session.commit()
        
        return {
            "mensaje": "Bombero registrado con éxito",
            "id": nuevo_usuario.id,
            "bombero_id": nuevo_bombero.id
        }, 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al registrar bombero: {str(e)}")
        return {"error": "Error al registrar el bombero"}, 500

def obtener_bombero(bombero_id):
    """
    Obtiene información de un bombero específico
    """
    try:
        bombero = Bombero.query.get(bombero_id)
        if not bombero:
            return {"error": "Bombero no encontrado"}, 404
            
        return bombero, 200
    
    except Exception as e:
        current_app.logger.error(f"Error al obtener bombero {bombero_id}: {str(e)}")
        return {"error": "Error al obtener información del bombero"}, 500

def actualizar_estado_bombero(bombero_id, nuevo_estado):
    """
    Actualiza el estado de servicio de un bombero
    """
    try:
        db = current_app.extensions['sqlalchemy'].db
        bombero = Bombero.query.get(bombero_id)
        
        if not bombero:
            return {"error": "Bombero no encontrado"}, 404
            
        bombero.estado_servicio = nuevo_estado
        db.session.commit()
        
        return {
            "mensaje": f"Estado actualizado a {nuevo_estado}",
            "bombero_id": bombero_id
        }, 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al actualizar estado del bombero {bombero_id}: {str(e)}")
        return {"error": "Error al actualizar el estado del bombero"}, 500