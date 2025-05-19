from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conexión a MongoDB (se inicializará con la app)
mongo_client = None
db = None

# Inicializar extensiones que se mantienen
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # Configuración
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    
    # Obtener las variables de entorno para la conexión a MongoDB
    mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME', 'mongo')
    mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD', 'CvnQaghnRxuwqITNEpeKRilLCNsMZZgU')
    mongo_host = os.getenv('RAILWAY_PRIVATE_DOMAIN', 'tramway.proxy.rlwy.net')  # Usando el proxy correcto
    mongo_port = os.getenv('RAILWAY_TCP_PROXY_PORT', 40148)  # El puerto para el proxy

    # Construir la URI de conexión usando las variables de entorno
    uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/?connectTimeoutMS=30000&socketTimeoutMS=30000"
    
    # Configurar MongoDB
    global mongo_client, db
    try:
        # Establecer la conexión con MongoDB
        mongo_client = MongoClient(uri, server_api=ServerApi('1'))
        mongo_client.admin.command('ping')  # Hacer un ping para verificar la conexión
        db = mongo_client.get_database('emergencia_linea_db')  # Especifica el nombre de tu base de datos aquí
        print("Conexión exitosa a MongoDB!")
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        db = None  # Asegurarse de que db sea None si hay un error en la conexión
        return None  # Si la conexión falla, detener la ejecución de la app

    # Inicializar extensiones con la app
    jwt.init_app(app)
    CORS(app)

    # Registrar blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Registrar blueprint para bomberos
    from app.routes.bomberos import bombero_bp
    app.register_blueprint(bombero_bp)
    
    # Registrar blueprint para incidentes
    from app.routes.incidentes import incidente_bp
    app.register_blueprint(incidente_bp)

    # Crear directorio de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    @app.route('/')
    def hello():
        return "API de Emergencias funcionando correctamente con MongoDB"
    
    return app
