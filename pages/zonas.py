import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("📍 MAPA FINAL OSECAC: MDP / MIRAMAR")

# MAPA DE GOOGLE (Aquí se ven todas las calles, nombres y números de ruta)
m = folium.Map(
    location=[-38.120, -57.680], 
    zoom_start=11,
    tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attr='Google Maps'
)

# Límites (Ordenados para que no se crucen)
zonas = [
    {"n": "RODRÍGUEZ", "c": "#00BFFF", "p": [[-37.95, -57.6], [-37.95, -57.53], [-38.0009, -57.5416], [-37.9802, -57.5825]]},
    {"n": "CARBAYO", "c": "#DC143C", "p": [[-37.9802, -57.5825], [-38.0009, -57.5416], [-38.0407, -57.5423], [-38.0003, -57.5958]]},
    {"n": "LÓPEZ", "c": "#FFD700", "p": [[-37.9802, -57.5825], [-37.96, -57.75], [-38.06, -57.75], [-38.0003, -57.5958]]},
    {"n": "GARCÍA", "c": "#FF8C00", "p": [[-38.0003, -57.5958], [-38.0407, -57.5423], [-38.1, -57.52], [-38.2650, -57.8400], [-38.15, -57.75]]}
]

for z in zonas:
    folium.Polygon(locations=z["p"], color="black", weight=2, fill=True, fill_color=z["c"], fill_opacity=0.3).add_to(m)

st_folium(m, width="100%", height=700)
