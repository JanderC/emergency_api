# app/models/notificacion.py
from datetime import datetime
from app import db

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    incidente_id = db.Column(db.Integer, db.ForeignKey('incidentes.id'))
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='notificaciones')
    
    def __repr__(self):
        return f'<Notificacion {self.id}>'