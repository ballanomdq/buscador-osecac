import folium

# 1. Centramos el mapa en una zona intermedia de las jurisdicciones de Rodríguez
mapa_rodriguez = folium.Map(location=[-38.005, -57.560], zoom_start=13)

# Estilo para Rodríguez
estilo = {'fillColor': '#00BFFF', 'color': '#00BFFF', 'weight': 2, 'fillOpacity': 0.5}

# --- ZONA 1 (Güemes / Bs. As. / Colón / J.B. Justo) ---
# Esquinas reales aproximadas:
z1 = [
    [-38.0058, -57.5434], # Colón y Güemes
    [-38.0101, -57.5381], # Colón y Buenos Aires
    [-38.0255, -57.5562], # J.B. Justo y Buenos Aires
    [-38.0210, -57.5615]  # J.B. Justo y Güemes
]
folium.Polygon(locations=z1, popup="Rodríguez - Zona 1", **estilo).add_to(mapa_rodriguez)

# --- ZONA 2 (Microcentro / La Perla) ---
# Usando Catamarca, Colón y el borde costero
z2 = [
    [-37.9942, -57.5435], # F.U. Camet y Catamarca
    [-38.0006, -57.5548], # Colón y Catamarca
    [-37.9976, -57.5592], # Colón y 20 de Septiembre
    [-37.9915, -57.5510]  # Costa y 20 de Septiembre
]
folium.Polygon(locations=z2, popup="Rodríguez - Zona 2", **estilo).add_to(mapa_rodriguez)

# --- ZONA 3 (San Juan / Bronzini - El Oeste) ---
# San Juan, Bronzini y el límite hacia Pehuajó
z3 = [
    [-37.9890, -57.5700], # Colón y San Juan
    [-37.9970, -57.5810], # Colón y T. Bronzini
    [-38.0050, -57.6100], # T. Bronzini y zona Pehuajó (estimado oeste)
    [-37.9950, -57.6150]  # San Juan y zona Pehuajó (estimado oeste)
]
folium.Polygon(locations=z3, popup="Rodríguez - Zona 3", **estilo).add_to(mapa_rodriguez)

# Marcador de control para que no te pierdas
folium.Marker([-38.0009, -57.5416], popup="Luro y Costa").add_to(mapa_rodriguez)

# Guardar
mapa_rodriguez.save('mapa_test.html')
