import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="OSECAC MDP - Final")
st.title("📍 Mapa de Jurisdicciones Calibrado")

# 1. TUS PUNTOS DE REFERENCIA (Exactos según tus coordenadas)
P_LURO_COSTA = [-38.0009, -57.5416] 
P_LURO_CHAMP = [-37.9802, -57.5825] 
P_JBJUSTO_COSTA = [-38.0407, -57.5423]
P_JBJUSTO_CHAMP = [-38.0250, -57.5950] # Ajustado para cerrar el cuadro

zonas = [
    {
        "nombre": "RODRÍGUEZ (Norte)",
        "color": "#00BFFF", # Celeste
        "puntos": [
            [-37.9750, -57.5450], [-37.9650, -57.5950], 
            P_LURO_CHAMP, P_LURO_COSTA
        ]
    },
    {
        "nombre": "CARBAYO (Centro)",
        "color": "#DC143C", # Rosa
        "puntos": [
            P_LURO_COSTA, P_LURO_CHAMP, 
            P_JBJUSTO_CHAMP, P_JBJUSTO_COSTA
        ]
    },
    {
        "nombre": "LÓPEZ (Oeste)",
        "color": "#FFD700", # Amarillo
        "puntos": [
            P_LURO_CHAMP, [-37.9850, -57.6800], 
            [-38.0300, -57.6800], P_JBJUSTO_CHAMP
        ]
    },
    {
        "nombre": "GARCÍA (Sur/Puerto)",
        "color": "#FF8C00", # Naranja
        "puntos": [
            P_JBJUSTO_COSTA, P_JBJUSTO_CHAMP, 
            [-38.0800, -57.5800], [-38.1200, -57.5500], [-38.0500, -57.5300]
        ]
    }
]

m = folium.Map(location=[-38.005, -57.56], zoom_start=13, tiles="CartoDB positron")

for z in zonas:
    folium.Polygon(
        locations=z["puntos"],
        color="black", weight=2,
        fill=True, fill_color=z["color"], fill_opacity=0.4,
        tooltip=z["nombre"]
    ).add_to(m)

st_folium(m, width="100%", height=700, returned_objects=[])
