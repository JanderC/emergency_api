from marshmallow import Schema, fields, validate, validates, ValidationError

class RegistroSchema(Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=2, max=100))
    apellido = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    telefono = fields.String(validate=validate.Length(max=20))
    es_bombero = fields.Boolean(default=False)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class UsuarioSchema(Schema):
    id = fields.String(dump_only=True)  # Changed from Integer to String for MongoDB ObjectId
    nombre = fields.String()
    apellido = fields.String()
    email = fields.Email()
    telefono = fields.String()
    foto_perfil = fields.String()
    es_bombero = fields.Boolean()
    fecha_registro = fields.DateTime(dump_only=True)