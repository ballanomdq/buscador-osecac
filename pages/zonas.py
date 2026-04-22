import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("📍 Mapa de Jurisdicciones - VISTA SATELITAL")

# PUNTOS CLAVE
P_LURO_COSTA = [-38.0009, -57.5416]
P_LURO_CHAMP = [-37.9802, -57.5825]
P_JBJUSTO_COSTA = [-38.0407, -57.5423]
P_JBJUSTO_VIGNOLO = [-38.0003, -57.5958]
P_MIRAMAR = [-38.2650, -57.8400]

# Usamos Google Satellite para que las calles se vean perfectas
m = folium.Map(
    location=[-38.120, -57.680], 
    zoom_start=11, 
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attr='Google'
)

zonas = [
    {"n": "RODRÍGUEZ", "c": "#00BFFF", "p": [[-37.9500, -57.6000], [-37.9500, -57.5300], P_LURO_COSTA, P_LURO_CHAMP]},
    {"n": "CARBAYO", "c": "#DC143C", "p": [P_LURO_CHAMP, P_LURO_COSTA, P_JBJUSTO_COSTA, P_JBJUSTO_VIGNOLO]},
    {"n": "LÓPEZ", "c": "#FFD700", "p": [P_LURO_CHAMP, [-37.9500, -57.8000], [-38.1000, -57.8000], P_JBJUSTO_VIGNOLO]},
    {"n": "GARCÍA", "c": "#FF8C00", "p": [P_JBJUSTO_VIGNOLO, P_JBJUSTO_COSTA, [-38.1000, -57.5200], P_MIRAMAR, [-38.2000, -57.8000]]}
]

for z in zonas:
    folium.Polygon(
        locations=z["p"],
        color="white", # Borde blanco para que resalte en el satélite
        weight=3,
        fill=True,
        fill_color=z["c"],
        fill_opacity=0.3 # Bien clarito para ver las calles abajo
    ).add_to(m)

st_folium(m, width="100%", height=750)
