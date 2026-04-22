import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("📍 Mapa Final OSECAC - MDP / MIRAMAR")

# 1. PUNTOS MAESTROS (Tus referencias)
P_LURO_COSTA = [-38.0009, -57.5416]
P_LURO_CHAMP = [-37.9802, -57.5825]
P_JBJUSTO_COSTA = [-38.0407, -57.5423]
P_JBJUSTO_VIGNOLO = [-38.0003, -57.5958]
P_MIRAMAR = [-38.2650, -57.8400] # Punto de estiramiento para García

zonas = [
    {
        "nombre": "RODRÍGUEZ (Norte)",
        "color": "#00BFFF",
        "puntos": [[-37.9650, -57.6000], [-37.9600, -57.5450], P_LURO_COSTA, P_LURO_CHAMP]
    },
    {
        "nombre": "CARBAYO (Centro)",
        "color": "#DC143C",
        "puntos": [P_LURO_CHAMP, P_LURO_COSTA, P_JBJUSTO_COSTA, P_JBJUSTO_VIGNOLO]
    },
    {
        "nombre": "LÓPEZ (Oeste)",
        "color": "#FFD700",
        "puntos": [P_LURO_CHAMP, [-37.9800, -57.7500], [-38.0500, -57.7500], P_JBJUSTO_VIGNOLO]
    },
    {
        "nombre": "GARCÍA (Sur hasta Miramar)",
        "color": "#FF8C00",
        "puntos": [P_LURO_COSTA, P_JBJUSTO_COSTA, P_MIRAMAR, [-38.3000, -57.8000], [-38.1000, -57.5200]]
    }
]

m = folium.Map(location=[-38.100, -57.650], zoom_start=11, tiles="CartoDB positron")

for z in zonas:
    folium.Polygon(
        locations=z["puntos"],
        color="black", weight=2,
        fill=True, fill_color=z["color"], fill_opacity=0.4,
        tooltip=z["nombre"]
    ).add_to(m)

st_folium(m, width="100%", height=700, returned_objects=[])
