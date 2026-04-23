# --- ZONA 1 (RE-ESTIRADA Y EN ESCUADRA TOTAL) ---
# Se ajustaron los 4 vértices para que cierren en ángulo recto
# y cubran toda la extensión desde Colón hasta Juan B. Justo.

z1_final = [
    [-38.0058, -57.5435], # Esquina 1: Av. Colón y Güemes
    [-38.0099, -57.5384], # Esquina 2: Av. Colón y Buenos Aires (Vértice Norte)
    [-38.0265, -57.5568], # Esquina 3: Av. J.B. Justo y Buenos Aires (Vértice Sur - Estirado)
    [-38.0224, -57.5619]  # Esquina 4: Av. J.B. Justo y Güemes (Vértice Oeste - Estirado)
]

folium.Polygon(
    locations=z1_final, 
    popup="Rodríguez - Zona 1 (Escuadra y Proporción Final)", 
    fillColor='#00BFFF', 
    color='blue', 
    weight=4, 
    fillOpacity=0.6
).add_to(mapa)
