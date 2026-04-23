import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Mapa de Jurisdicciones: Inspector RODRÍGUEZ")

mapa = folium.Map(location=[-38.014, -57.545], zoom_start=14)
estilo = {'fillColor': '#00BFFF', 'color': 'blue', 'weight': 4, 'fillOpacity': 0.6}

# --- ZONA 1: AJUSTE DE DIMENSIONES REALES ---
# 1. Se achicó arriba (Norte) 2 cuadras.
# 2. Se achicó abajo (Sur) 4 cuadras.
# 3. Se ensanchó hacia Güemes para cubrir las 2 cuadras que faltaban.

z1_ajustado = [
    [-38.0075, -57.5465], # Esquina Norte-Oeste (Güemes y Colón aprox)
    [-38.0105, -57.5405], # Esquina Norte-Este (Buenos Aires y Colón aprox)
    [-38.0260, -57.5510], # Esquina Sur-Este (Buenos Aires y J.B. Justo aprox - RECORTE 4 CUADRAS)
    [-38.0230, -57.5570]  # Esquina Sur-Oeste (Güemes y J.B. Justo aprox - RECORTE 4 CUADRAS)
]

folium.Polygon(
    locations=z1_ajustado, 
    popup="Rodríguez - Zona 1 (Ajuste Preciso)", 
    **estilo
).add_to(mapa)

st_folium(mapa, width=1200, height=800)
