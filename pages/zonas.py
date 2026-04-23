import streamlit as st
import folium
from streamlit_folium import st_folium

# Configuración para que el mapa ocupe toda la pantalla
st.set_page_config(layout="wide")
st.title("Mapa de Jurisdicciones: Inspector RODRÍGUEZ")

# 1. Configuración del mapa base
# Centramos un poco más al sur para ver el estiramiento completo
mapa = folium.Map(location=[-38.018, -57.548], zoom_start=14)

# Estilo visual: Celeste fuerte para Rodríguez
estilo = {'fillColor': '#00BFFF', 'color': 'blue', 'weight': 4, 'fillOpacity': 0.6}

# --- ZONA 1: EL MOLDE MAESTRO (LARGO, ANCHO Y PARALELO) ---
# He estirado los puntos hacia el sur (San Carlos) y ensanchado hacia Buenos Aires
z1_molde = [
    [-38.0050, -57.5440], # Esquina Colón y Güemes
    [-38.0085, -57.5365], # Esquina Colón y Buenos Aires
    [-38.0330, -57.5580], # Esquina J.B. Justo y Buenos Aires (MUCHO MÁS LARGO)
    [-38.0290, -57.5655]  # Esquina J.B. Justo y Güemes (MUCHO MÁS LARGO)
]

# Dibujamos el polígono (usando folium. explicitamente para evitar el NameError)
folium.Polygon(
    locations=z1_molde, 
    popup="Rodríguez - Zona 1 (Calibración Final)", 
    **estilo
).add_to(mapa)

# 2. Renderizado para Streamlit
st_folium(mapa, width=1200, height=800)
