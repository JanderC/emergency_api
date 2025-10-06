# app/schemas/reporte_rapido_schema.py
from marshmallow import Schema, fields, validate, validates, ValidationError

class ReporteRapidoSchema(Schema):
    """Schema para reporte rápido de emergencia"""
    tipo_emergencia = fields.Str(
        required=True, 
        validate=validate.OneOf([
            'choque_fuerte',
            'incendio',
            'inundacion',
            'deslizamiento',
            'accidente_multiple',
            'explosion',
            'otro'
        ])
    )
    foto = fields.Str(required=True)  # Base64 de la imagen
    nombre_foto = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    direccion = fields.Str(required=True, validate=validate.Length(min=5, max=500))
    lat = fields.Float(required=False, validate=validate.Range(min=-90, max=90))
    lng = fields.Float(required=False, validate=validate.Range(min=-180, max=180))
    
    @validates('foto')
    def validate_foto(self, value):
        if not value.startswith('data:image/'):
            raise ValidationError('La foto debe estar en formato base64 válido')

class AsignarBomberoReporteSchema(Schema):
    """Schema para asignar bombero a reporte rápido"""
    bombero_id = fields.Str(required=True)

class CompletarReporteSchema(Schema):
    """Schema para marcar reporte como atendido"""
    notas = fields.Str(required=False, validate=validate.Length(max=1000))