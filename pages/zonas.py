import folium

# Centramos el mapa justo en Colón e Independencia
mapa = folium.Map(location=[-38.005, -57.555], zoom_start=14)

# Definimos el estilo de Rodríguez
estilo_rodriguez = {
    'fillColor': 'blue',
    'color': 'blue',
    'weight': 3,
    'fillOpacity': 0.6
}

# --- ZONA 1: Cuadrante Güemes ---
# Estas coordenadas forman un cuadrado real en Mar del Plata
zona1 = [
    [-38.0058, -57.5434], # Colón y Güemes
    [-38.0101, -57.5381], # Colón y Buenos Aires
    [-38.0195, -57.5468], # J.B. Justo y Buenos Aires
    [-38.0152, -57.5521]  # J.B. Justo y Güemes
]
folium.Polygon(locations=zona1, popup="Rodríguez Zona 1", **estilo_rodriguez).add_to(mapa)

# --- ZONA 2: La Perla / Microcentro ---
zona2 = [
    [-37.9945, -57.5438], # La Costa y Catamarca
    [-38.0010, -57.5540], # Colón y Catamarca
    [-37.9980, -57.5590], # Colón y 20 de Septiembre
    [-37.9910, -57.5500]  # La Costa y 20 de Septiembre
]
folium.Polygon(locations=zona2, popup="Rodríguez Zona 2", **estilo_rodriguez).add_to(mapa)

# --- ZONA 3: San Juan / Bronzini ---
zona3 = [
    [-37.9890, -57.5700], # Colón y San Juan
    [-37.9970, -57.5810], # Colón y T. Bronzini
    [-38.0040, -57.5950], # T. Bronzini y el oeste
    [-37.9940, -57.5850]  # San Juan y el oeste
]
folium.Polygon(locations=zona3, popup="Rodríguez Zona 3", **estilo_rodriguez).add_to(mapa)

# Marcador de prueba para ver si el mapa carga
folium.Marker([-38.000, -57.550], popup="Punto de Control").add_to(mapa)

# Guardar
mapa.save('mapa_rodriguez.html')
