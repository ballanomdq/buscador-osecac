import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Mapa de Jurisdicciones - Inspector RODRÍGUEZ")

# 1. Creamos el mapa base (OpenStreetMap no requiere configuración extra)
mapa = folium.Map(location=[-38.005, -57.555], zoom_start=13)

# Estilo para Rodríguez
estilo = {'fillColor': '#00BFFF', 'color': 'blue', 'weight': 2, 'fillOpacity': 0.5}

# --- ZONA 1 (Güemes / Bs. As.) ---
z1 = [
    [-38.0058, -57.5434], [-38.0101, -57.5381], 
    [-38.0255, -57.5562], [-38.0210, -57.5615]
]
folium.Polygon(locations=z1, popup="Rodríguez - Zona 1", **estilo).add_to(mapa)

# --- ZONA 2 (La Perla) ---
z2 = [
    [-37.9942, -57.5435], [-38.0006, -57.5548], 
    [-37.9976, -57.5592], [-37.9915, -57.5510]
]
folium.Polygon(locations=z2, popup="Rodríguez - Zona 2", **estilo).add_to(mapa)

# --- ZONA 3 (San Juan / Bronzini) ---
z3 = [
    [-37.9890, -57.5700], [-37.9970, -57.5810], 
    [-38.0050, -57.6100], [-37.9950, -57.6150]
]
folium.Polygon(locations=z3, popup="Rodríguez - Zona 3", **estilo).add_to(mapa)

# 2. ESTO ES LO MÁS IMPORTANTE PARA STREAMLIT
# En lugar de mapa.save(), usamos st_folium para mostrarlo en la web
st_folium(mapa, width=700, height=500)
