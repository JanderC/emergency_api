# app/schemas/bombero_schema.py
from marshmallow import Schema, fields, validate, validates, ValidationError

class RegistroBomberoSchema(Schema):
    # Datos de usuario
    nombre = fields.String(required=True, validate=validate.Length(min=2, max=100))
    apellido = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    telefono = fields.String(validate=validate.Length(max=20))
    
    # Datos específicos de bombero
    codigo_bombero = fields.String(required=True, validate=validate.Length(min=3, max=20))
    estacion_pertenencia = fields.String(required=True)
    carnet_foto = fields.String()

class BomberoSchema(Schema):
    id = fields.String(dump_only=True)
    usuario_id = fields.String(dump_only=True)
    codigo_bombero = fields.String()
    estacion_pertenencia = fields.String()
    estado_servicio = fields.String()
    carnet_foto = fields.String()

class ActualizarEstadoBomberoSchema(Schema):
    estado_servicio = fields.String(required=True, validate=validate.OneOf(
        ['disponible', 'ocupado', 'fuera_servicio', 'en_emergencia']
    ))