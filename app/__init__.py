from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
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
    
    # Configurar MongoDB
    global mongo_client, db
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb+srv://janderalexisc:<mWtVaKwO3j6XfOOZ>@emergencylinerubio.xqy43ih.mongodb.net/?retryWrites=true&w=majority&appName=emergencyLineRubio"
    )

    try:
        mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        # Enviar un ping para verificar la conexión
        mongo_client.admin.command('ping')
        print("✅ Conexión a MongoDB Atlas establecida correctamente.")
        db = mongo_client[os.getenv("MONGO_DBNAME", "emergencia_linea_db")]
    except Exception as e:
        print("❌ Error al conectar con MongoDB Atlas:", e)

    # Inicializar extensiones con la app
    jwt.init_app(app)
    CORS(app)
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.bomberos import bombero_bp
    app.register_blueprint(bombero_bp)
    
    from app.routes.incidentes import incidente_bp
    app.register_blueprint(incidente_bp)

    # Crear directorio de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    @app.route('/')
    def hello():
        return "API de Emergencias funcionando correctamente con MongoDB"
    
    return app
