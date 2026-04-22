import folium

# Creamos el mapa centrado en Mar del Plata
m = folium.Map(location=[-38.0055, -57.5426], zoom_start=13)

# DIBUJAMOS LA ZONA DE GARCÍA (Ejemplo)
folium.Polygon(
    locations=[
        [-38.015, -57.54], # Esquina Independencia y Colon
        [-38.035, -57.54], # Esquina Independencia y JB Justo
        [-38.100, -57.65], # Arroyo Las Brusquitas
        [-38.015, -57.58]  # Cierre hacia Edison
    ],
    color='orange',
    fill=True,
    fill_opacity=0.3,
    popup='Zona Inspector García (Leg. 7952)'
).add_to(m)

# El mapa se guarda como un archivo que podés abrir en cualquier navegador
m.save("mapa_zonas.html")
