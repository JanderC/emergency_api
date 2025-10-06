# crear_jefe_bomberos.py
"""
Script para crear el primer jefe de bomberos en el sistema
Ejecutar después de la migración
"""
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime

# Configuración (REEMPLAZA CON TUS DATOS)
MONGO_URI = "mongodb+srv://janderalexisc:GyeiWNwvGYUziNNw@emergencylinerubio.xqy43ih.mongodb.net/?retryWrites=true&w=majority&appName=emergencyLineRubio"
DB_NAME = "emergencia_linea_db"

# Datos del jefe de bomberos
JEFE_DATA = {
    "nombre": "Carlos",
    "apellido": "Rodriguez",
    "email": "jefe@bomberos.com",
    "cedula": "0000000000",
    "direccion": "Estación Central de Bomberos",
    "password": "jefe123456",  # CAMBIAR DESPUÉS
    "telefono": "0999999999",
    "codigo_jefe": "JEFE001",
    "estacion_asignada": "estacion central"
}

def crear_jefe_bomberos():
    """Crea el usuario jefe de bomberos en el sistema"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Creando jefe de bomberos...")
    
    # Verificar si ya existe
    existe = db.usuarios.find_one({"email": JEFE_DATA["email"]})
    if existe:
        print(f"⚠️  El email {JEFE_DATA['email']} ya está registrado")
        
        # Verificar si ya tiene registro de jefe
        jefe_existente = db.jefes_bomberos.find_one({"usuario_id": str(existe["_id"])})
        if jefe_existente:
            print(f"ℹ️  Ya existe un jefe con código: {jefe_existente['codigo_jefe']}")
            client.close()
            return
        else:
            usuario_id = str(existe["_id"])
            print(f"ℹ️  Usuario existe, creando registro de jefe...")
    else:
        # Crear usuario
        usuario_data = {
            "nombre": JEFE_DATA["nombre"],
            "apellido": JEFE_DATA["apellido"],
            "email": JEFE_DATA["email"],
            "cedula": JEFE_DATA["cedula"],
            "direccion": JEFE_DATA["direccion"],
            "password_hash": generate_password_hash(JEFE_DATA["password"]),
            "telefono": JEFE_DATA["telefono"],
            "es_bombero": True,
            "foto_perfil": "",
            "fecha_registro": datetime.utcnow(),
            "activo": True
        }
        
        result = db.usuarios.insert_one(usuario_data)
        usuario_id = str(result.inserted_id)
        print(f"✅ Usuario jefe creado con ID: {usuario_id}")
    
    # Crear registro en jefes_bomberos
    jefe_data = {
        "usuario_id": usuario_id,
        "codigo_jefe": JEFE_DATA["codigo_jefe"],
        "estacion_asignada": JEFE_DATA["estacion_asignada"],
        "fecha_asignacion": datetime.utcnow(),
        "activo": True
    }
    
    result = db.jefes_bomberos.insert_one(jefe_data)
    print(f"✅ Jefe de bomberos creado exitosamente")
    print(f"   Código: {JEFE_DATA['codigo_jefe']}")
    print(f"   Email: {JEFE_DATA['email']}")
    print(f"   Password: {JEFE_DATA['password']}")
    print(f"   ⚠️  IMPORTANTE: Cambiar la contraseña después del primer login")
    
    client.close()

if __name__ == "__main__":
    print("=" * 60)
    print("CREAR JEFE DE BOMBEROS")
    print("=" * 60)
    print("")
    
    try:
        crear_jefe_bomberos()
        print("")
        print("=" * 60)
        print("✅ PROCESO COMPLETADO")
        print("=" * 60)
    except Exception as e:
        print("")
        print("=" * 60)
        print(f"❌ ERROR: {str(e)}")
        print("=" * 60)