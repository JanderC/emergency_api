from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv


# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones que se mantienen
jwt = JWTManager()
mongo_client = None
db = None

def create_app():
    app = Flask(__name__)
    
    # Configuración
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    
    # Configurar MongoDB
    global mongo_client, db
    
    # Obtener la URI de MongoDB desde las variables de entorno
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DBNAME", "emergencia_linea_db")
    print(f"Conectando a la base de datos '{db_name}' en MongoDB Atlas...", "mongo_uri", mongo_uri)
    
    # Establecer conexión con MongoDB Atlas usando Server API v1
    try:
        mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        # Verificar la conexión con un ping
        mongo_client.admin.command('ping')
        print("¡Conexión exitosa a MongoDB Atlas!")
        
        # Obtener la base de datos
        db = mongo_client[db_name]
        print(f"Base de datos '{db_name}' seleccionada correctamente")
        
    except Exception as e:
        print(f"Error al conectar a MongoDB Atlas: {e}")
    
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

    # Registrar blueprint para usuarios
    from app.routes.usuarios import usuario_bp
    app.register_blueprint(usuario_bp)

    # Registrar blueprint para emergencias
    from app.routes.emergency import emergencia_bp
    app.register_blueprint(emergencia_bp)

    from app.routes.ambulancias import ambulancia_bp
    app.register_blueprint(ambulancia_bp)


    from app.routes.reportes_rapidos import reporte_rapido_bp
    app.register_blueprint(reporte_rapido_bp)
    
    # Crear directorio de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    @app.route('/')
    def hello():
        return "API de Emergencias funcionando correctamente con MongoDB Atlas"
    
    return app

# Función para obtener la instancia de la base de datos 
# (útil para usarla en otros módulos)
def get_db():
    return db