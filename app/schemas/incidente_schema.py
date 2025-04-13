"""
Schemas para validación y serialización de incidentes
"""
from marshmallow import Schema, fields, validate, pre_load, post_dump

class CoordenadasSchema(Schema):
    """Schema para validar y serializar coordenadas geográficas"""
    type = fields.Str(dump_only=True)
    coordinates = fields.List(fields.Float(), dump_only=True)

class ReporteIncidenteSchema(Schema):
    """Schema para validar la creación de un nuevo incidente"""
    tipo_emergencia = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    descripcion = fields.Str(required=True, validate=validate.Length(min=10))
    ubicacion = fields.Str(required=True, validate=validate.Length(min=5))
    coordenadas_lat = fields.Float(required=True)
    coordenadas_lng = fields.Float(required=True)
    nivel_urgencia = fields.Str(required=True, validate=validate.OneOf(['baja', 'media', 'alta', 'critica']))
    imagenes = fields.List(fields.Str(), required=False)

class IncidenteSchema(Schema):
    """Schema para serializar incidentes desde MongoDB"""
    _id = fields.Str(attribute="_id")
    usuario_id = fields.Str()
    bombero_asignado_id = fields.Str(allow_none=True)
    ambulancia_id = fields.Str(allow_none=True)
    tipo_emergencia = fields.Str()
    descripcion = fields.Str()
    ubicacion = fields.Str()
    coordenadas = fields.Nested(CoordenadasSchema)
    estado = fields.Str()
    nivel_urgencia = fields.Str()
    fecha_reporte = fields.DateTime()
    fecha_atencion = fields.DateTime(allow_none=True)
    imagenes = fields.List(fields.Str())
    
    @post_dump(pass_many=True)
    def convert_object_id(self, data, many, **kwargs):
        """Convierte ObjectId a string, si es necesario"""
        if many:
            for item in data:
                if item.get("_id") and not isinstance(item["_id"], str):
                    item["_id"] = str(item["_id"])
        else:
            if data.get("_id") and not isinstance(data["_id"], str):
                data["_id"] = str(data["_id"])
        return data