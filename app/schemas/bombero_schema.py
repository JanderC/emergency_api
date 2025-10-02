# app/schemas/bombero_schema.py
from marshmallow import Schema, fields, validate, validates, ValidationError

class RegistroBomberoSchema(Schema):
    """Schema para registro de bombero"""
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    apellido = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
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

class BomberoSchema(Schema):
    """Schema para bombero completo"""
    _id = fields.Str(dump_only=True)
    usuario_id = fields.Str(required=True)
    codigo_bombero = fields.Str(required=True)
    estacion_pertenencia = fields.Str(required=True)
    rango = fields.Str(validate=validate.OneOf(['bombero', 'cabo', 'teniente', 'capitan', 'comandante']))
    especialidades = fields.List(fields.Str())
    certificaciones = fields.List(fields.Str())
    estado_servicio = fields.Str(
        validate=validate.OneOf(['disponible', 'en_servicio', 'fuera_servicio', 'descanso'])
    )
    carnet_foto = fields.Str(allow_none=True)
    experiencia_anos = fields.Int()
    contacto_emergencia = fields.Dict()
    ambulancia_id = fields.Str(allow_none=True)
    ubicacion_actual = fields.Dict(allow_none=True)
    turnos_completados = fields.Int()
    incidentes_atendidos = fields.Int()
    fecha_registro = fields.DateTime()

class ActualizarPerfilBomberoSchema(Schema):
    """Schema para actualizar perfil de bombero"""
    telefono = fields.Str(validate=validate.Length(min=10, max=15))
    especialidades = fields.List(fields.Str())
    certificaciones = fields.List(fields.Str())
    experiencia_anos = fields.Int(validate=validate.Range(min=0, max=50))
    contacto_emergencia = fields.Dict()
    rango = fields.Str(validate=validate.OneOf(['bombero', 'cabo', 'teniente', 'capitan', 'comandante']))
    foto_perfil = fields.Str(allow_none=True)

class CambiarEstadoBomberoSchema(Schema):
    """Schema para cambiar estado de bombero"""
    estado_servicio = fields.Str(
        required=True,
        validate=validate.OneOf(['disponible', 'en_servicio', 'fuera_servicio', 'descanso'])
    )

class ActualizarUbicacionSchema(Schema):
    """Schema para actualizar ubicación"""
    lat = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    lng = fields.Float(required=True, validate=validate.Range(min=-180, max=180))