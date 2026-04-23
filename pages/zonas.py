import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Mapa de Jurisdicciones: Inspector RODRÍGUEZ")

mapa = folium.Map(location=[-38.016, -57.548], zoom_start=14)
estilo = {'fillColor': '#00BFFF', 'color': 'blue', 'weight': 4, 'fillOpacity': 0.6}

# --- ZONA 1: CALIBRACIÓN DE PRECISIÓN ---
# 1. Recuperamos el ancho hacia Güemes (2 cuadras más).
# 2. Recortamos arriba (Colón) y abajo (J.B. Justo) para que no sobre.
# 3. Mantenemos el ángulo paralelo a la cuadrícula.

z1_rectificado = [
    [-38.0065, -57.5455], # Esquina Colón y Güemes (Punto Norte-Oeste)
    [-38.0105, -57.5395], # Esquina Colón y Buenos Aires (Punto Norte-Este)
    [-38.0255, -57.5535], # Esquina J.B. Justo y Buenos Aires (Punto Sur-Este)
    [-38.0215, -57.5595]  # Esquina J.B. Justo y Güemes (Punto Sur-Oeste)
]

folium.Polygon(
    locations=z1_rectificado, 
    popup="Rodríguez - Zona 1 (Calibración Real)", 
    **estilo
).add_to(mapa)

st_folium(mapa, width=1200, height=800)
