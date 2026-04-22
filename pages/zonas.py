import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("📍 Mapa Jurisdicciones OSECAC: MDP - MIRAMAR")

# PUNTOS DE CONTROL CALIBRADOS
P_LURO_COSTA = [-38.0009, -57.5416]
P_LURO_CHAMP = [-37.9802, -57.5825]
P_JBJUSTO_COSTA = [-38.0407, -57.5423]
P_JBJUSTO_VIGNOLO = [-38.0003, -57.5958]
P_ENTRADA_MIRAMAR = [-38.2650, -57.8400]

zonas = [
    {
        "nombre": "RODRÍGUEZ",
        "color": "#00BFFF", # Celeste
        "puntos": [[-37.9650, -57.6000], [-37.9550, -57.5400], P_LURO_COSTA, P_LURO_CHAMP]
    },
    {
        "nombre": "CARBAYO",
        "color": "#DC143C", # Rosa
        "puntos": [P_LURO_CHAMP, P_LURO_COSTA, P_JBJUSTO_COSTA, P_JBJUSTO_VIGNOLO]
    },
    {
        "nombre": "LÓPEZ",
        "color": "#FFD700", # Amarillo
        "puntos": [P_LURO_CHAMP, [-37.9600, -57.7200], [-38.0600, -57.7200], P_JBJUSTO_VIGNOLO]
    },
    {
        "nombre": "GARCÍA",
        "color": "#FF8C00", # Naranja
        "puntos": [P_JBJUSTO_COSTA, [-38.0500, -57.5200], [-38.2300, -57.7800], P_ENTRADA_MIRAMAR, [-38.1000, -57.7000], P_JBJUSTO_VIGNOLO]
    }
]

m = folium.Map(location=[-38.120, -57.680], zoom_start=11, tiles="CartoDB positron")

for z in zonas:
    folium.Polygon(
        locations=z["puntos"],
        color="black", weight=2, fill=True, fill_color=z["color"], fill_opacity=0.4,
        tooltip=z["nombre"]
    ).add_to(m)

st_folium(m, width="100%", height=700, returned_objects=[])
