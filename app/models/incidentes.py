"""
Este módulo define la estructura de documentos para incidentes en MongoDB.
No utilizamos clases como en SQLAlchemy, sino funciones que crean la estructura
de documentos.
"""
from datetime import datetime

def crear_documento_incidente(
    usuario_id, 
    tipo_emergencia, 
    descripcion, 
    ubicacion, 
    coordenadas_lat, 
    coordenadas_lng,
    nivel_urgencia, 
    imagenes=None
):
    """
    Crea un nuevo documento de incidente para MongoDB.
    """
    return {
        "usuario_id": usuario_id,
        "bombero_asignado_id": None,
        "ambulancia_id": None,
        "tipo_emergencia": tipo_emergencia,
        "descripcion": descripcion,
        "ubicacion": ubicacion,
        "coordenadas": {
            "type": "Point",
            "coordinates": [float(coordenadas_lng), float(coordenadas_lat)]
        },
        "estado": "reportado",
        "nivel_urgencia": nivel_urgencia,
        "fecha_reporte": datetime.utcnow(),
        "fecha_atencion": None,
        "imagenes": imagenes or []
    }