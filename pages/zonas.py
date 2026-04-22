import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# MAPA BASE DE GOOGLE (Calles nítidas)
m = folium.Map(
    location=[-38.010, -57.550], 
    zoom_start=13,
    tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attr='Google Maps'
)

# AJUSTE DE LÍMITES PARA QUE NADA QUEDE AFUERA
zonas = [
    {
        "nombre": "RODRÍGUEZ", "color": "#00BFFF", 
        "puntos": [[-37.94, -57.6], [-37.94, -57.51], [-38.0009, -57.53], [-37.9802, -57.5825]] 
    },
    {
        "nombre": "CARBAYO", "color": "#DC143C", 
        "puntos": [
            [-37.9802, -57.5825], 
            [-38.0009, -57.53],    # Punto estirado hacia el mar (Luro y Costa)
            [-38.0450, -57.5350],  # Punto estirado hacia el mar (Puerto/Escollera)
            [-38.0003, -57.5958]
        ]
    },
    {
        "nombre": "GARCÍA", "color": "#FF8C00", 
        "puntos": [
            [-38.0003, -57.5958], 
            [-38.0450, -57.5350],  # Desde el Puerto
            [-38.12, -57.50],      # Cubre todo el Alfar y los Acantilados
            [-38.2650, -57.8400],  # Hasta Miramar
            [-38.15, -57.75]
        ]
    }
]

for z in zonas:
    folium.Polygon(
        locations=z["puntos"],
        color="black", weight=2,
        fill=True, fill_color=z["color"], fill_opacity=0.3
    ).add_to(m)

st_folium(m, width="100%", height=750)
