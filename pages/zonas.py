# --- ZONA 1 (LARGA, ANCHA Y ALINEADA A INDEPENDENCIA) ---
# Se estiró la longitud hacia el Sur y se ensanchó para cubrir el área real.

z1_ajuste_final = [
    [-38.0050, -57.5440], # Esquina Norte (Cerca de Colón y Güemes)
    [-38.0095, -57.5375], # Esquina Este (Cerca de Colón y Buenos Aires)
    [-38.0310, -57.5610], # Esquina Sur (Pasando J.B. Justo para dar longitud)
    [-38.0265, -57.5675]  # Esquina Oeste (Pasando J.B. Justo para dar longitud)
]

folium.Polygon(
    locations=z1_ajuste_final, 
    popup="Rodríguez - Zona 1 (Ajuste de Escala)", 
    fillColor='#00BFFF', 
    color='blue', 
    weight=3, 
    fillOpacity=0.5
).add_to(mapa)
