import folium

# 1. Usamos un proveedor de mapas diferente (OpenStreetMap) y forzamos el renderizado
mapa = folium.Map(
    location=[-38.005, -57.555], 
    zoom_start=14,
    tiles="OpenStreetMap" # Forzamos el mapa estándar
)

# Estilo simple
estilo = {'fillColor': 'blue', 'color': 'red', 'weight': 5, 'fillOpacity': 0.7}

# --- ZONA 1 DE RODRÍGUEZ (Puntos de control exactos) ---
# Si esto no se ve, el problema es la instalación de la librería
zona1 = [
    [-38.0050, -57.5450], 
    [-38.0100, -57.5450], 
    [-38.0100, -57.5500], 
    [-38.0050, -57.5500]
]

folium.Polygon(locations=zona1, popup="TEST ZONA 1", **estilo).add_to(mapa)

# Marcador gigante para ver si aparece algo
folium.Marker([-38.005, -57.555], popup="ESTOY ACÁ").add_to(mapa)

# 2. Guardar
mapa.save('mapa_rodriguez.html')
print("Archivo guardado. Abrilo con Chrome o Edge.")
