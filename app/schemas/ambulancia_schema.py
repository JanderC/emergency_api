from marshmallow import Schema, fields, validate, validates, ValidationError

class AmbulanciaSchema(Schema):
    id = fields.Integer(dump_only=True)
    placa = fields.String(required=True, validate=validate.Length(min=5, max=20))
    modelo = fields.String(validate=validate.Length(max=100))
    ano = fields.Integer(validate=[validate.Range(min=1990, max=2030)])
    estado = fields.String(
        validate=validate.OneOf(['operativa', 'mantenimiento', 'fuera_de_servicio']), 
        default='operativa'
    )
    bombero_asignado_id = fields.Integer(allow_none=True)
    ubicacion_actual = fields.String(allow_none=True)

class RegistroAmbulanciaSchema(Schema):
    placa = fields.String(required=True, validate=validate.Length(min=5, max=20))
    modelo = fields.String(required=True, validate=validate.Length(max=100))
    ano = fields.Integer(required=True, validate=[validate.Range(min=1990, max=2030)])
    estado = fields.String(
        validate=validate.OneOf(['operativa', 'mantenimiento', 'fuera_de_servicio']), 
        default='operativa'
    )
    ubicacion_actual = fields.String(allow_none=True)