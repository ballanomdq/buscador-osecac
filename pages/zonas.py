import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="OSECAC - Mapa Maestro")

st.title("📍 Jurisdicciones de Inspección: Mar del Plata - Miramar")

# PUNTOS CLAVE (Tus referencias)
P_LURO_COSTA = [-38.0009, -57.5416]
P_LURO_CHAMP = [-37.9802, -57.5825]
P_JBJUSTO_COSTA = [-38.0407, -57.5423]
P_JBJUSTO_VIGNOLO = [-38.0003, -57.5958]
P_MIRAMAR = [-38.2650, -57.8400]

# Mapa base claro (OpenStreetMap) donde se ven todas las calles
m = folium.Map(location=[-38.120, -57.650], zoom_start=11)

zonas = [
    {"n": "RODRÍGUEZ (Celeste)", "c": "#00BFFF", "p": [[-37.9500, -57.6000], [-37.9500, -57.5300], P_LURO_COSTA, P_LURO_CHAMP]},
    {"n": "CARBAYO (Rosa)", "c": "#DC143C", "p": [P_LURO_CHAMP, P_LURO_COSTA, P_JBJUSTO_COSTA, P_JBJUSTO_VIGNOLO]},
    {"n": "LÓPEZ (Amarillo)", "c": "#FFD700", "p": [P_LURO_CHAMP, [-37.9500, -57.8000], [-38.1000, -57.8000], P_JBJUSTO_VIGNOLO]},
    {"n": "GARCÍA (Naranja)", "c": "#FF8C00", "p": [P_JBJUSTO_VIGNOLO, P_JBJUSTO_COSTA, [-38.0800, -57.5200], P_MIRAMAR, [-38.2000, -57.8000]]}
]

for z in zonas:
    # Dibujamos solo la línea del contorno para no tapar nada
    folium.PolyLine(
        locations=z["p"] + [z["p"][0]], # Cerramos la línea volviendo al primer punto
        color=z["c"],
        weight=6, # Línea gruesa para que se note el límite
        opacity=0.8,
        tooltip=z["n"]
    ).add_to(m)

st_folium(m, width="100%", height=750)
