# app/schemas/usuario_schema.py
from marshmallow import Schema, fields, validate, validates, ValidationError

class RegistroSchema(Schema):
    """Schema para registro de usuario"""
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    apellido = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    cedula = fields.Str(required=True, validate=validate.Length(min=6, max=20))  # AGREGAR
    direccion = fields.Str(required=True, validate=validate.Length(min=5, max=500))  # AGREGAR
    password = fields.Str(required=True, validate=validate.Length(min=6))
    telefono = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    es_bombero = fields.Bool(missing=False)
    
    @validates('email')
    def validate_email(self, value):
        if not value or '@' not in value:
            raise ValidationError('Email inválido')
    
    @validates('cedula')
    def validate_cedula(self, value):
        if not value or not value.replace('-', '').isdigit():
            raise ValidationError('Cédula inválida. Solo se permiten números y guiones')

class LoginSchema(Schema):
    """Schema para login de usuario"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class ActualizarPerfilSchema(Schema):
    """Schema para actualizar perfil de usuario"""
    nombre = fields.Str(validate=validate.Length(min=2, max=100))
    apellido = fields.Str(validate=validate.Length(min=2, max=100))
    telefono = fields.Str(validate=validate.Length(min=10, max=15))
    direccion = fields.Str(validate=validate.Length(min=5, max=500))  # AGREGAR
    foto_perfil = fields.Str(allow_none=True)