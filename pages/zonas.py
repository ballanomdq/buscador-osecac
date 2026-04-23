# --- ZONA 1 (ESTIRADA Y ALINEADA A BUENOS AIRES) ---
# He ajustado los puntos para que el lateral pase exacto por la calle Buenos Aires
# y los extremos toquen Colón y J.B. Justo sin torcerse.

z1_estirado = [
    [-38.0058, -57.5435], # Esquina 1: Av. Colón y Güemes
    [-38.0098, -57.5385], # Esquina 2: Av. Colón y Buenos Aires (Lateral exacto)
    [-38.0260, -57.5565], # Esquina 3: Av. J.B. Justo y Buenos Aires (Estirado al Sur)
    [-38.0215, -57.5618]  # Esquina 4: Av. J.B. Justo y Güemes (Estirado al Sur)
]

folium.Polygon(
    locations=z1_estirado, 
    popup="Rodríguez - Zona 1 (Alineación Final)", 
    fillColor='#00BFFF', 
    color='blue', 
    weight=4, # Línea más gruesa para que veas si pisa la calle
    fillOpacity=0.5
).add_to(mapa)
