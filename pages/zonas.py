import streamlit as st
import folium
from streamlit_folium import st_folium

# Configuración de la página
st.set_page_config(layout="wide")
st.title("Mapa de Jurisdicciones: Inspector RODRÍGUEZ")

# 1. Configuración del mapa base (Centrado para ver el estiramiento)
mapa = folium.Map(location=[-38.018, -57.550], zoom_start=14)

# Estilo visual de Rodríguez
estilo = {'fillColor': '#00BFFF', 'color': 'blue', 'weight': 4, 'fillOpacity': 0.5}

# --- ZONA 1 (ESTIRADA, ANCHA Y PARALELA A INDEPENDENCIA) ---
# He recalculado los puntos para que cubran desde Colón hasta bien pasado J.B. Justo
# El lateral sigue la línea de Buenos Aires/Independencia sin rotar de más.
z1_final_ajustada = [
    [-38.0055, -57.5435], # Esquina Colón y Güemes
    [-38.0098, -57.5385], # Esquina Colón y Buenos Aires
    [-38.0295, -57.5590], # Esquina J.B. Justo y Buenos Aires (MUCHO MÁS LARGO)
    [-38.0250, -57.5645]  # Esquina J.B. Justo y Güemes (MUCHO MÁS LARGO)
]

# Dibujamos el polígono asegurando que folium esté importado
folium.Polygon(
    locations=z1_final_ajustada, 
    popup="Rodríguez - Zona 1 (Ajuste Final)", 
    **estilo
).add_to(mapa)

# 2. Renderizado en Streamlit
st_folium(mapa, width=1100, height=700)
