import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide") # Para que el mapa se vea grande

st.title("Mapa de Jurisdicciones: Inspector RODRÍGUEZ")

# 1. Configuración del mapa base
# Centramos el mapa en el medio del cuadrante
mapa = folium.Map(location=[-38.016, -57.548], zoom_start=14)

# Estilo visual de Rodríguez
estilo = {'fillColor': '#00BFFF', 'color': 'blue', 'weight': 4, 'fillOpacity': 0.6}

# --- ZONA 1 (RE-ESTIRADA Y EN ESCUADRA TOTAL) ---
# Coordenadas calculadas para que sea LARGO y RECTO
z1_final = [
    [-38.0058, -57.5435], # Esquina 1: Av. Colón y Güemes
    [-38.0099, -57.5384], # Esquina 2: Av. Colón y Buenos Aires
    [-38.0265, -57.5568], # Esquina 3: Av. J.B. Justo y Buenos Aires (Estirado)
    [-38.0224, -57.5619]  # Esquina 4: Av. J.B. Justo y Güemes (Estirado)
]

# Dibujamos el polígono
folium.Polygon(
    locations=z1_final, 
    popup="Rodríguez - Zona 1 (Escuadra Final)", 
    **estilo
).add_to(mapa)

# 2. Mostramos el mapa en Streamlit
st_folium(mapa, width=1000, height=700)
