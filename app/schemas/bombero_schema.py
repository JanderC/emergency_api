# app/schemas/bombero_schema.py
from marshmallow import Schema, fields, validate, validates, ValidationError

class RegistroBomberoSchema(Schema):
    """Schema para registro de bombero"""
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    apellido = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    cedula = fields.Str(required=True, validate=validate.Length(min=6, max=20))  # AGREGAR
    direccion = fields.Str(required=True, validate=validate.Length(min=5, max=500))  # AGREGAR
    password = fields.Str(required=True, validate=validate.Length(min=6))
    telefono = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    
    # Campos específicos de bombero
    codigo_bombero = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    estacion_pertenencia = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    rango = fields.Str(
        missing='bombero',
        validate=validate.OneOf(['bombero', 'cabo', 'teniente', 'capitan', 'comandante'])
    )
    especialidades = fields.List(fields.Str(), missing=[])
    certificaciones = fields.List(fields.Str(), missing=[])
    experiencia_anos = fields.Int(missing=0, validate=validate.Range(min=0, max=50))
    carnet_foto = fields.Str(missing=None, allow_none=True)
    contacto_emergencia = fields.Dict(missing={})
    
    @validates('email')
    def validate_email(self, value):
        if not value or '@' not in value:
            raise ValidationError('Email inválido')
    
    @validates('cedula')
    def validate_cedula(self, value):
        if not value or not value.replace('-', '').isdigit():
            raise ValidationError('Cédula inválida. Solo se permiten números y guiones')    