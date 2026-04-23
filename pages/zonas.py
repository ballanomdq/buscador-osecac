# --- ZONA 1 (RECTÁNGULO ROBUSTO Y LARGO) ---
# Se le dio más ancho hacia Independencia y más largo hacia San Carlos
z1_proporcional = [
    [-38.0050, -57.5435], # Esquina Colón y Güemes
    [-38.0090, -57.5370], # Esquina Colón y Buenos Aires (Más ancho)
    [-38.0320, -57.5585], # Esquina J.B. Justo y Buenos Aires (Mucho más largo)
    [-38.0280, -57.5650]  # Esquina J.B. Justo y Güemes (Mucho más largo)
]

folium.Polygon(
    locations=z1_proporcional, 
    popup="Rodríguez - Zona 1 (Calibrada)", 
    **estilo
).add_to(mapa)
