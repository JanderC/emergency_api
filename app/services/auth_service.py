# app/services/auth_service.py
from app.models.usuarios import Usuario
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

class AuthService:
    @staticmethod
    def registrar_usuario(datos):
        print("Entrando en registro de usuarios")
        
        # Verificar si el email ya existe
        usuario_existente = Usuario.find_by_email(datos['email'])
        if usuario_existente:
            return {'error': 'El email ya está registrado'}, 400
        
        # NUEVO: Verificar si la cédula ya existe
        cedula_existente = Usuario.find_by_cedula(datos['cedula'])
        if cedula_existente:
            return {'error': 'La cédula ya está registrada'}, 400
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            email=datos['email'],
            cedula=datos['cedula'],  # NUEVO
            direccion=datos['direccion'],  # NUEVO
            telefono=datos.get('telefono', ''),
            es_bombero=datos.get('es_bombero', False)
        )
        
        # Establecer contraseña
        nuevo_usuario.set_password(datos['password'])
        
        print(f"Nuevo usuario: {nuevo_usuario.nombre} {nuevo_usuario.apellido} ({nuevo_usuario.email})")
        
        # Guardar en la base de datos
        try:
            if nuevo_usuario.save():
                return {
                    'mensaje': 'Usuario registrado exitosamente',
                    'usuario_id': nuevo_usuario.id
                }, 201
            else:
                return {'error': 'Error al guardar el usuario'}, 500
        except Exception as e:
            print(f"Error al registrar usuario: {str(e)}")
            return {'error': f'Error al registrar usuario: {str(e)}'}, 500
    
    @staticmethod
    def login(datos):
        # Buscar usuario por email
        usuario = Usuario.find_by_email(datos['email'])
        
        # Verificar si existe y la contraseña es correcta
        if not usuario or not usuario.check_password(datos['password']):
            return {'error': 'Credenciales inválidas'}, 401
        
        # Verificar si el usuario está activo
        if not usuario.activo:
            return {'error': 'Usuario inactivo. Contacte al administrador'}, 403
        
        # Generar tokens de acceso y refresh
        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                'es_bombero': usuario.es_bombero,
                'usuario_id': str(usuario.id)
            },
            expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            identity=str(usuario.id),
            additional_claims={
                'usuario_id': str(usuario.id)
            },
            expires_delta=timedelta(days=30)
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'usuario': usuario.to_dict()
        }, 200
    
    @staticmethod
    def refresh_token(usuario_id):
        usuario = Usuario.find_by_id(usuario_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        
        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                'es_bombero': usuario.es_bombero,
                'usuario_id': str(usuario.id)
            },
            expires_delta=timedelta(hours=1)
        )
        
        return {'access_token': access_token}, 200