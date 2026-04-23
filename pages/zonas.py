import folium

# 1. Creamos el mapa SIN mapa base (todo negro/gris) para que no dependa de internet
mapa = folium.Map(location=[-38.005, -57.555], zoom_start=14, tiles=None)

# Agregamos una capa de color sólido de fondo para ver si el lienzo funciona
folium.TileLayer('stamenwatercolor', name='Prueba de Fondo').add_to(mapa)

# Estilo fuerte: Rojo para que resalte
estilo = {'fillColor': 'red', 'color': 'black', 'weight': 5, 'fillOpacity': 0.8}

# ZONA DE PRUEBA (Un cuadrado grande en el centro)
zona_test = [
    [-38.000, -57.550], 
    [-38.010, -57.550], 
    [-38.010, -57.560], 
    [-38.000, -57.560]
]

folium.Polygon(locations=zona_test, popup="SI VES ESTO, EL CODIGO FUNCIONA", **estilo).add_to(mapa)

# Marcador simple
folium.Marker([-38.005, -57.555], popup="CENTRO").add_to(mapa)

# 2. Guardar con un nombre nuevo
mapa.save('prueba_final.html')
print("Archivo 'prueba_final.html' creado. Abrilo ahora.")
