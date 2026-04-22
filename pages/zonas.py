import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("📍 MAPA FINAL OSECAC: MDP / MIRAMAR (4 ZONAS)")

# MAPA BASE DE GOOGLE (Calles nítidas)
m = folium.Map(
    location=[-38.050, -57.650], 
    zoom_start=11,
    tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attr='Google Maps'
)

zonas = [
    {
        "nombre": "RODRÍGUEZ (Norte)", "color": "#00BFFF", # Celeste
        "puntos": [[-37.94, -57.60], [-37.94, -57.51], [-38.0009, -57.53], [-37.9802, -57.5825]] 
    },
    {
        "nombre": "CARBAYO (Centro)", "color": "#DC143C", # Rosa
        "puntos": [[-37.9802, -57.5825], [-38.0009, -57.53], [-38.0407, -57.535], [-38.0003, -57.5958]]
    },
    {
        "nombre": "LÓPEZ (Oeste/Batán)", "color": "#FFD700", # Amarillo
        "puntos": [[-37.9802, -57.5825], [-38.0003, -57.5958], [-38.10, -57.75], [-37.96, -57.75]]
    },
    {
        "nombre": "GARCÍA (Sur/Miramar)", "color": "#FF8C00", # Naranja
        "puntos": [[-38.0003, -57.5958], [-38.0407, -57.535], [-38.12, -57.50], [-38.2650, -57.8400], [-38.10, -57.75]]
    }
]

for z in zonas:
    folium.Polygon(
        locations=z["puntos"],
        color="black", weight=2,
        fill=True, fill_color=z["color"], fill_opacity=0.3,
        tooltip=z["nombre"]
    ).add_to(m)

st_folium(m, width="100%", height=750)
