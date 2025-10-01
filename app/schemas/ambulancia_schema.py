# app/schemas/ambulancia_schema.py
from marshmallow import Schema, fields, validate

class RegistroAmbulanciaSchema(Schema):
    placa = fields.Str(required=True)
    modelo = fields.Str(required=False, allow_none=True)
    tipo = fields.Str(required=False, allow_none=True)  # AGREGAR
    capacidad = fields.Int(required=False, allow_none=True)  # AGREGAR
    ano = fields.Int(required=False, allow_none=True)
    estado = fields.Str(
        required=False,
        validate=validate.OneOf(['operativa', 'en_servicio', 'mantenimiento', 'fuera_de_servicio']),
        missing='operativa'
    )
    estacion_pertenencia = fields.Str(required=False, allow_none=True)  # AGREGAR

class AmbulanciaSchema(Schema):
    _id = fields.Str(dump_only=True)
    placa = fields.Str()
    modelo = fields.Str()
    tipo = fields.Str()  # AGREGAR
    capacidad = fields.Int()  # AGREGAR
    ano = fields.Int()
    estado = fields.Str()
    estacion_pertenencia = fields.Str()  # AGREGAR
    bombero_asignado_id = fields.Str(allow_none=True)
    ubicacion_actual = fields.Dict(allow_none=True)
    fecha_registro = fields.DateTime()
    fecha_asignacion = fields.DateTime(allow_none=True)
    bombero_info = fields.Dict(allow_none=True)