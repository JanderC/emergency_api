from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
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
    
    # Configurar MongoDB
    global mongo_client, db
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:CvnQaghnRxuwqITNEpeKRilLCNsMZZgU@tramway.proxy.rlwy.net:40148")
    mongo_client = MongoClient(mongo_uri)
    db = mongo_client[os.getenv("MONGO_DBNAME", "emergencia_linea_db")]
    
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
    
    # NO CERRAR la conexión a MongoDB para evitar el error
    # Este es un workaround temporal
    
    return app