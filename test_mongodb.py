# test_mongodb.py
# Run this with: python test_mongodb.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_connection():
    try:
        # Configurar MongoDB
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        mongo_client = MongoClient(mongo_uri)
        db_name = os.getenv("MONGO_DBNAME", "emergencia_linea_db")
        db = mongo_client[db_name]
        
        # Test the connection
        db.command('ping')
        print(f"✅ Successfully connected to MongoDB at {mongo_uri}")
        print(f"✅ Using database: {db_name}")
        
        # Check if the usuarios collection exists, if not create it
        if "usuarios" not in db.list_collection_names():
            db.create_collection("usuarios")
            print("✅ Created 'usuarios' collection")
        else:
            print("✅ 'usuarios' collection already exists")
        
        # Count documents in usuarios collection
        count = db.usuarios.count_documents({})
        print(f"✅ Found {count} documents in usuarios collection")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB connection error: {str(e)}")
        return False
    finally:
        if 'mongo_client' in locals():
            mongo_client.close()
            print("✅ Connection closed")

if __name__ == "__main__":
    test_connection()