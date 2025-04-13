# app/utils/validators.py

def validar_coordenadas(lat, lng):
    """
    Valida que las coordenadas estén en un rango válido:
    - Latitud: -90 a 90
    - Longitud: -180 a 180
    """
    try:
        lat_float = float(lat)
        lng_float = float(lng)
        
        if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
            return True
        return False
    except (ValueError, TypeError):
        return False