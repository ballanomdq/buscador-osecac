import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="OSECAC MDP - Mapa Maestro")
st.title("📍 Mapa de Jurisdicciones Calibrado (Versión Final)")

# 1. TUS PUNTOS REALES (Los "Clavos" del Mapa)
P_LURO_COSTA = [-38.0009, -57.5416] 
P_LURO_CHAMP = [-37.9802, -57.5825] 
P_JBJUSTO_COSTA = [-38.0407, -57.5423]
P_JBJUSTO_VIGNOLO = [-38.0003, -57.5958] # Tu punto en Vignolo/JBJusto

# 2. DEFINICIÓN DE ZONAS POR VÉRTICES COMPARTIDOS
# Esto garantiza que las zonas encastren como un modelo 3D perfecto
zonas = [
    {
        "nombre": "RODRÍGUEZ (Celeste)",
        "color": "#00BFFF",
        "puntos": [[-37.9650, -57.6000], [-37.9600, -57.5450], P_LURO_COSTA, P_LURO_CHAMP]
    },
    {
        "nombre": "CARBAYO (Rosa)",
        "color": "#DC143C",
        "puntos": [P_LURO_CHAMP, P_LURO_COSTA, P_JBJUSTO_COSTA, P_JBJUSTO_VIGNOLO]
    },
    {
        "nombre": "LÓPEZ (Amarillo)",
        "color": "#FFD700",
        "puntos": [P_LURO_CHAMP, [-37.9850, -57.6800], [-38.0300, -57.6800], P_JBJUSTO_VIGNOLO]
    },
    {
        "nombre": "GARCÍA (Naranja)",
        "color": "#FF8C00",
        "puntos": [P_LURO_COSTA, P_JBJUSTO_COSTA, [-38.1500, -57.5500], [-38.2500, -57.7000], [-38.0800, -57.5300]]
    }
]

# 3. CONSTRUCCIÓN DEL MAPA
m = folium.Map(location=[-38.005, -57.56], zoom_start=13, tiles="CartoDB positron")

for z in zonas:
    folium.Polygon(
        locations=z["puntos"],
        color="black",
        weight=1,
        fill=True,
        fill_color=z["color"],
        fill_opacity=0.4,
        tooltip=z["nombre"]
    ).add_to(m)

# 4. RENDERIZADO
st_folium(m, width="100%", height=700, returned_objects=[])
