# app/models/cambios_ambulancia.py
from datetime import datetime
from app import db

class CambioAmbulancia(db.Model):
    __tablename__ = 'cambios_ambulancia'
    
    id = db.Column(db.Integer, primary_key=True)
    bombero_anterior_id = db.Column(db.Integer, db.ForeignKey('bomberos.id'))
    bombero_nuevo_id = db.Column(db.Integer, db.ForeignKey('bomberos.id'))
    ambulancia_id = db.Column(db.Integer, db.ForeignKey('ambulancias.id'))
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), nullable=False)
    razon_cambio = db.Column(db.Text)
    
    # Relaciones
    bombero_anterior = db.relationship('Bombero', foreign_keys=[bombero_anterior_id])
    bombero_nuevo = db.relationship('Bombero', foreign_keys=[bombero_nuevo_id])
    ambulancia = db.relationship('Ambulancia')
    
    def __repr__(self):
        return f'<CambioAmbulancia {self.id}>'