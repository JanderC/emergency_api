# migration_script.py
"""
Script de migración para agregar campos nuevos a la base de datos
Ejecutar UNA SOLA VEZ después de actualizar el código
"""
from pymongo import MongoClient
from datetime import datetime

# Configuración de conexión (REEMPLAZA CON TUS DATOS)
MONGO_URI = "mongodb+srv://janderalexisc:GyeiWNwvGYUziNNw@emergencylinerubio.xqy43ih.mongodb.net/?retryWrites=true&w=majority&appName=emergencyLineRubio"
DB_NAME = "emergencia_linea_db"

def migrar_usuarios():
    """Agrega campos cedula y direccion a usuarios existentes"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Iniciando migración de usuarios...")
    
    # Actualizar usuarios que no tienen los nuevos campos
    result = db.usuarios.update_many(
        {
            "$or": [
                {"cedula": {"$exists": False}},
                {"direccion": {"$exists": False}},
                {"activo": {"$exists": False}}
            ]
        },
        {
            "$set": {
                "cedula": "",
                "direccion": "",
                "activo": True,
                "fecha_actualizacion": datetime.utcnow()
            }
        }
    )
    
    print(f"✅ {result.modified_count} usuarios actualizados con nuevos campos")
    
    client.close()

def migrar_bomberos():
    """Agrega campos de aprobación a bomberos existentes"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Iniciando migración de bomberos...")
    
    # Actualizar bomberos que no tienen los campos de aprobación
    result = db.bomberos.update_many(
        {
            "$or": [
                {"estado_aprobacion": {"$exists": False}},
                {"aprobado_por": {"$exists": False}},
                {"fecha_aprobacion": {"$exists": False}}
            ]
        },
        {
            "$set": {
                "estado_aprobacion": "aprobado",  # Los existentes se consideran aprobados
                "aprobado_por": None,
                "fecha_aprobacion": datetime.utcnow()
            }
        }
    )
    
    print(f"✅ {result.modified_count} bomberos actualizados con campos de aprobación")
    
    # Activar usuarios de bomberos existentes
    bomberos = db.bomberos.find({})
    for bombero in bomberos:
        db.usuarios.update_one(
            {"_id": bombero["usuario_id"]},
            {"$set": {"activo": True}}
        )
    
    print(f"✅ Usuarios de bomberos activados")
    
    client.close()

def crear_coleccion_jefes():
    """Crea la colección de jefes de bomberos si no existe"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Verificando colección de jefes_bomberos...")
    
    if "jefes_bomberos" not in db.list_collection_names():
        db.create_collection("jefes_bomberos")
        print("✅ Colección 'jefes_bomberos' creada")
    else:
        print("ℹ️  Colección 'jefes_bomberos' ya existe")
    
    client.close()

def crear_coleccion_reportes_rapidos():
    """Crea la colección de reportes rápidos si no existe"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Verificando colección de reportes_rapidos...")
    
    if "reportes_rapidos" not in db.list_collection_names():
        db.create_collection("reportes_rapidos")
        print("✅ Colección 'reportes_rapidos' creada")
    else:
        print("ℹ️  Colección 'reportes_rapidos' ya existe")
    
    client.close()

def crear_indices():
    """Crea índices para mejorar el rendimiento"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Creando índices...")
    
    # Índices en usuarios
    db.usuarios.create_index("email", unique=True)
    db.usuarios.create_index("cedula")
    print("✅ Índices creados en 'usuarios'")
    
    # Índices en bomberos
    db.bomberos.create_index("codigo_bombero", unique=True)
    db.bomberos.create_index("usuario_id")
    db.bomberos.create_index("estado_aprobacion")
    print("✅ Índices creados en 'bomberos'")
    
    # Índices en jefes
    db.jefes_bomberos.create_index("codigo_jefe", unique=True)
    db.jefes_bomberos.create_index("usuario_id")
    print("✅ Índices creados en 'jefes_bomberos'")
    
    # Índices en reportes rápidos
    db.reportes_rapidos.create_index("estado")
    db.reportes_rapidos.create_index("usuario_id")
    db.reportes_rapidos.create_index("fecha_reporte")
    print("✅ Índices creados en 'reportes_rapidos'")
    
    client.close()

if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT DE MIGRACIÓN DE BASE DE DATOS")
    print("=" * 60)
    print("")
    
    try:
        migrar_usuarios()
        print("")
        migrar_bomberos()
        print("")
        crear_coleccion_jefes()
        print("")
        crear_coleccion_reportes_rapidos()
        print("")
        crear_indices()
        print("")
        print("=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
    except Exception as e:
        print("")
        print("=" * 60)
        print(f"❌ ERROR EN LA MIGRACIÓN: {str(e)}")
        print("=" * 60)