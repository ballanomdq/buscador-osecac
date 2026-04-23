import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Mapa de Jurisdicciones: Inspector RODRÍGUEZ")

mapa = folium.Map(location=[-38.018, -57.548], zoom_start=14)
estilo = {'fillColor': '#00BFFF', 'color': 'blue', 'weight': 4, 'fillOpacity': 0.6}

# --- ZONA 1: AJUSTE FINAL (UNA CUADRA MÁS Y CORTE RECTO) ---
# Se estiró el límite norte para llegar a Güemes y se enderezó el sur.
z1_finalisimo = [
    [-38.0045, -57.5448], # Esquina Colón y Güemes (Estirado 1 cuadra)
    [-38.0080, -57.5375], # Esquina Colón y Buenos Aires (Estirado 1 cuadra)
    [-38.0335, -57.5585], # Esquina Sur-Este (Corte recto en J.B. Justo)
    [-38.0300, -57.5655]  # Esquina Sur-Oeste (Corte recto en J.B. Justo)
]

folium.Polygon(
    locations=z1_finalisimo, 
    popup="Rodríguez - Zona 1 (Ajuste Final)", 
    **estilo
).add_to(mapa)

st_folium(mapa, width=1200, height=800)
