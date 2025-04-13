# app/services/notificacion_service.py
from flask import current_app
from app.models.notificacion import Notificacion
from datetime import datetime

def crear_notificacion(usuario_id, incidente_id, mensaje):
    """
    Crea una nueva notificación en el sistema
    """
    try:
        db = current_app.extensions['sqlalchemy'].db
        
        notificacion = Notificacion(
            usuario_id=usuario_id,
            incidente_id=incidente_id,
            mensaje=mensaje,
            fecha=datetime.utcnow(),
            leido=False
        )
        
        db.session.add(notificacion)
        db.session.commit()
        
        return notificacion.id
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al crear notificación: {str(e)}")
        return None