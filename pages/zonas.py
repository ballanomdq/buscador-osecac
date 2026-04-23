import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Mapa de Jurisdicciones: Inspector RODRÍGUEZ")

# 1. Configuración del mapa base (OpenStreetMap)
# Centramos un poco más al sur para ver bien este cuadrante
mapa = folium.Map(location=[-38.014, -57.545], zoom_start=14)

# Estilo visual de Rodríguez
estilo = {'fillColor': '#00BFFF', 'color': 'blue', 'weight': 2, 'fillOpacity': 0.6}

# --- ZONA 1 (Güemes / Bs. As. / Colón / J.B. Justo) - COORDENADAS AJUSTADAS ---
# Estos son los puntos reales para encajar en el recuadro rojo:
z1_corregido = [
    [-38.0058, -57.5434], # Vértice Norte: Esquina Av. Colón y Güemes
    [-38.0101, -57.5381], # Vértice Este: Esquina Av. Colón y Buenos Aires
    [-38.0255, -57.5562], # Vértice Sur: Esquina Av. J.B. Justo y Buenos Aires
    [-38.0210, -57.5615]  # Vértice Oeste: Esquina Av. J.B. Justo y Güemes
]

folium.Polygon(
    locations=z1_corregido, 
    popup="Rodríguez - Zona 1 (Corregida)", 
    **estilo
).add_to(mapa)

# --- ZONAS 2 Y 3 (Por ahora no las toco, pero deberían seguir la misma lógica de "islas") ---
# ... (aquí iría el código de las otras dos zonas si ya te funcionan)

# 2. Mostramos el mapa en Streamlit
st_folium(mapa, width=800, height=600)
