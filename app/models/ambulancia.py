# app/models/ambulancia.py
from bson.objectid import ObjectId

# Funciones para crear y manipular documentos de ambulancias
def create_ambulancia(placa, modelo=None, ano=None, estado="operativa", 
                      bombero_asignado_id=None, ubicacion_actual=None):
    """Crea un documento de ambulancia para MongoDB"""
    # Convertir ID a ObjectId si es string
    if bombero_asignado_id and not isinstance(bombero_asignado_id, ObjectId):
        try:
            bombero_asignado_id = ObjectId(bombero_asignado_id)
        except:
            bombero_asignado_id = None
    
    return {
        "placa": placa,
        "modelo": modelo,
        "ano": ano,
        "estado": estado,
        "bombero_asignado_id": bombero_asignado_id,
        "ubicacion_actual": ubicacion_actual
    }

def to_dict(ambulancia, include_bombero=False, db=None):
    """Convierte el documento de ambulancia a un diccionario para respuesta JSON"""
    if not ambulancia:
        return None
    
    ambulancia_dict = {
        'id': str(ambulancia.get('_id')),
        'placa': ambulancia.get('placa'),
        'modelo': ambulancia.get('modelo'),
        'ano': ambulancia.get('ano'),
        'estado': ambulancia.get('estado'),
        'bombero_asignado_id': str(ambulancia.get('bombero_asignado_id')) if ambulancia.get('bombero_asignado_id') else None,
        'ubicacion_actual': ambulancia.get('ubicacion_actual')
    }
    
    # Incluir información del bombero si se solicita y se proporciona db
    if include_bombero and db and ambulancia.get('bombero_asignado_id'):
        from app.models.bombero import to_dict as bombero_to_dict
        bombero = db.bomberos.find_one({"_id": ambulancia.get('bombero_asignado_id')})
        if bombero:
            ambulancia_dict['bombero'] = bombero_to_dict(bombero)
    
    return ambulancia_dict

# Funciones para acceder a la colección de ambulancias
class AmbulanciaRepository:
    def __init__(self, db):
        self.collection = db.ambulancias
        self.db = db
    
    def find_by_id(self, id):
        """Busca una ambulancia por su ID"""
        if not isinstance(id, ObjectId):
            try:
                id = ObjectId(id)
            except:
                return None
        return self.collection.find_one({"_id": id})
    
    def find_by_placa(self, placa):
        """Busca una ambulancia por su placa"""
        return self.collection.find_one({"placa": placa})
    
    def create(self, ambulancia_data):
        """Crea una nueva ambulancia en la base de datos"""
        result = self.collection.insert_one(ambulancia_data)
        
        # Si hay bombero asignado, actualizar el bombero también
        if ambulancia_data.get('bombero_asignado_id'):
            self.db.bomberos.update_one(
                {"_id": ambulancia_data['bombero_asignado_id']},
                {"$set": {"ambulancia_id": result.inserted_id}}
            )
        
        return result.inserted_id
    
    def update(self, id, update_data):
        """Actualiza una ambulancia existente"""
        if not isinstance(id, ObjectId):
            try:
                id = ObjectId(id)
            except:
                return False
        
        # Si cambia el bombero asignado, hay que manejar las referencias en ambos lados
        prev_ambulancia = self.find_by_id(id)
        prev_bombero_id = prev_ambulancia.get('bombero_asignado_id') if prev_ambulancia else None
        new_bombero_id = update_data.get('bombero_asignado_id')
        
        # Si el bombero cambió
        if new_bombero_id != prev_bombero_id:
            # Si había un bombero previo, quitar referencia a esta ambulancia
            if prev_bombero_id:
                self.db.bomberos.update_one(
                    {"_id": prev_bombero_id},
                    {"$set": {"ambulancia_id": None}}
                )
            
            # Si hay un nuevo bombero, actualizar su referencia a esta ambulancia
            if new_bombero_id:
                if not isinstance(new_bombero_id, ObjectId):
                    try:
                        new_bombero_id = ObjectId(new_bombero_id)
                        update_data['bombero_asignado_id'] = new_bombero_id
                    except:
                        update_data.pop('bombero_asignado_id', None)
                
                if update_data.get('bombero_asignado_id'):
                    self.db.bomberos.update_one(
                        {"_id": update_data['bombero_asignado_id']},
                        {"$set": {"ambulancia_id": id}}
                    )
        
        result = self.collection.update_one(
            {"_id": id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete(self, id):
        """Elimina una ambulancia por su ID"""
        if not isinstance(id, ObjectId):
            try:
                id = ObjectId(id)
            except:
                return False
        
        # Buscar primero para obtener el bombero_id
        ambulancia = self.find_by_id(id)
        if ambulancia and ambulancia.get('bombero_asignado_id'):
            # Actualizar bombero para quitar referencia a esta ambulancia
            self.db.bomberos.update_one(
                {"_id": ambulancia['bombero_asignado_id']},
                {"$set": {"ambulancia_id": None}}
            )
        
        result = self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
    
    def list_all(self, limit=100, skip=0):
        """Lista todas las ambulancias"""
        cursor = self.collection.find().limit(limit).skip(skip)
        return list(cursor)
    
    def list_operational(self):
        """Lista las ambulancias operativas"""
        cursor = self.collection.find({"estado": "operativa"})
        return list(cursor)
    
    def update_location(self, id, ubicacion):
        """Actualiza la ubicación de una ambulancia"""
        if not isinstance(id, ObjectId):
            try:
                id = ObjectId(id)
            except:
                return False
        
        result = self.collection.update_one(
            {"_id": id},
            {"$set": {"ubicacion_actual": ubicacion}}
        )
        return result.modified_count > 0