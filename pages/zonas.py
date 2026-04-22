import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="Zonas OSECAC MDP")

st.title("📍 Mapa de Jurisdicciones - Mar del Plata")
st.markdown("---")

# 1. COORDENADAS MAESTRAS (Basadas en tus puntos reales)
# Luro y la Costa
P1 = [-38.0009, -57.5416] 
# Luro y Champagnat (Rotonda)
P2 = [-37.9802, -57.5825] 
# J.B. Justo y Champagnat
P3 = [-38.0410, -57.5860] 
# J.B. Justo e Independencia
P4 = [-38.0350, -57.5500] 

# 2. DEFINICIÓN DE LAS 4 ZONAS
# Cada zona es un polígono que comparte puntos con la vecina para que no haya huecos
zonas = [
    {
        "nombre": "RODRÍGUEZ (Celeste)",
        "color": "#00BFFF",
        "puntos": [[-37.9650, -57.6000], [-37.9600, -57.5450], P1, P2]
    },
    {
        "nombre": "CARBAYO (Rosa)",
        "color": "#DC143C",
        "puntos": [P2, P1, P4, P3]
    },
    {
        "nombre": "LÓPEZ (Amarillo)",
        "color": "#FFD700",
        "puntos": [P2, [-37.9900, -57.6800], [-38.0500, -57.6800], P3]
    },
    {
        "nombre": "GARCÍA (Naranja)",
        "color": "#FF8C00",
        "puntos": [P1, P4, [-38.0900, -57.5500], [-38.1500, -57.5800], [-38.0300, -57.5300]]
    }
]

# 3. CREACIÓN DEL MAPA
m = folium.Map(location=[-38.005, -57.56], zoom_start=13, tiles="CartoDB positron")

# Añadir cada zona al mapa
for zona in zonas:
    folium.Polygon(
        locations=zona["puntos"],
        color="black",
        weight=1,
        fill=True,
        fill_color=zona["color"],
        fill_opacity=0.4,
        tooltip=zona["nombre"]
    ).add_to(m)

# 4. MOSTRAR EN STREAMLIT
# Agregamos returned_objects=[] para evitar que la página se limpie al tocar el mapa
st_folium(m, width="100%", height=700, returned_objects=[])
