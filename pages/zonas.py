import folium

# 1. Configuración base del mapa centrado en Mar del Plata
# Coordenadas: -38.000, -57.550 (Centro aproximado)
mapa_rodriguez = folium.Map(location=[-38.000, -57.550], zoom_start=13)

# Estilo visual para el Inspector RODRÍGUEZ (Celeste)
estilo_rodriguez = {
    'fillColor': '#00BFFF',
    'color': '#00BFFF',
    'weight': 2,
    'fillOpacity': 0.4
}

# --- INSPECTOR RODRÍGUEZ: ZONA 1 (Güemes / Buenos Aires) ---
# Límites: Av. Colón, J.B. Justo, Güemes y Buenos Aires
zona1_coords = [
    [-38.0055, -57.5425], # Esquina Colón y Güemes
    [-38.0120, -57.5490], # Esquina J.B. Justo y Güemes
    [-38.0160, -57.5430], # Esquina J.B. Justo y Buenos Aires
    [-38.0095, -57.5370]  # Esquina Colón y Buenos Aires
]
folium.Polygon(
    locations=zona1_coords, 
    popup="RODRÍGUEZ - Zona 1 (Güemes/BsAs)", 
    **estilo_rodriguez
).add_to(mapa_rodriguez)

# --- INSPECTOR RODRÍGUEZ: ZONA 2 (Microcentro / La Perla) ---
# Límites: Catamarca, 20 de Septiembre, Bv. Marítimo y Colón
zona2_coords = [
    [-37.9950, -57.5480], # Catamarca y la costa
    [-38.0010, -57.5550], # Catamarca y Colón
    [-37.9980, -57.5610], # 20 de Septiembre y Colón
    [-37.9920, -57.5530]  # Bv. Marítimo
]
folium.Polygon(
    locations=zona2_coords, 
    popup="RODRÍGUEZ - Zona 2 (La Perla)", 
    **estilo_rodriguez
).add_to(mapa_rodriguez)

# --- INSPECTOR RODRÍGUEZ: ZONA 3 (San Juan / Bronzini) ---
# Límites: San Juan, T. Bronzini, Av. Colón y Pehuajó/Heguilor
zona3_coords = [
    [-37.9850, -57.5750], # San Juan y Colón
    [-37.9750, -57.6000], # San Juan y Pehuajó
    [-37.9850, -57.6100], # Bronzini y Pehuajó
    [-37.9950, -57.5850]  # Bronzini y Colón
]
folium.Polygon(
    locations=zona3_coords, 
    popup="RODRÍGUEZ - Zona 3 (Oeste Urbano)", 
    **estilo_rodriguez
).add_to(mapa_rodriguez)

# 2. Marcador de referencia para posicionamiento (Luro y Costa)
folium.Marker(
    [-38.0009, -57.5416], 
    popup="Referencia: Luro y Costa",
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(mapa_rodriguez)

# 3. Guardar o mostrar el mapa
# mapa_rodriguez.save('mapa_rodriguez.html')
