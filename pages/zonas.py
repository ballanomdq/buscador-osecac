# PUNTOS CLAVE DE ENCASTRE (Las esquinas donde se tocan todos)
ESQUINA_COSTA = [-38.0009, -57.5416]     # Luro y Costa
ESQUINA_CHAMPAGNAT = [-37.9802, -57.5825] # Luro y Champagnat
ESQUINA_SUR_OESTE = [-38.0410, -57.5860]  # J.B. Justo y Champagnat
ESQUINA_SUR_COSTA = [-38.0350, -57.5500]  # J.B. Justo e Independencia

ZONAS_CALIBRADAS = {
    "RODRÍGUEZ": {
        "color": "#00BFFF", # Celeste
        "coords": [
            [-37.9650, -57.6000], [-37.9600, -57.5450], 
            ESQUINA_COSTA, ESQUINA_CHAMPAGNAT
        ]
    },
    "CARBAYO": {
        "color": "#DC143C", # Rosa/Rojo
        "coords": [
            ESQUINA_CHAMPAGNAT, ESQUINA_COSTA,
            ESQUINA_SUR_COSTA, ESQUINA_SUR_OESTE
        ]
    },
    "LÓPEZ": {
        "color": "#FFD700", # Amarillo
        "coords": [
            ESQUINA_CHAMPAGNAT, [-37.9900, -57.6800], 
            [-38.0500, -57.6800], ESQUINA_SUR_OESTE
        ]
    },
    "GARCÍA": {
        "color": "#FF8C00", # Naranja
        "coords": [
            ESQUINA_COSTA, ESQUINA_SUR_COSTA, 
            [-38.0900, -57.5500], [-38.1500, -57.5800],
            [-38.0300, -57.5300]
        ]
    }
}
