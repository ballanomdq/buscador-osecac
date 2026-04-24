import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide", page_title="Mapa de Zonas")

st.title("Mapa de Jurisdicciones - Mar del Plata")

# 1. LA ZONA QUE SACASTE DE GEOJSON.IO (Corregida para que Folium la entienda)
# Corresponde a Colón / Independencia / J.B. Justo / Buenos Aires
zona_manual_1 = [
    (-38.0060, -57.5451),
    (-38.0262, -57.5614),
    (-38.0189, -57.5711),
    (-38.0003, -57.5561)
]

# 2. CREAR EL MAPA
m = folium.Map(location=[-38.0100, -57.5600], zoom_start=13, tiles='OpenStreetMap')

# 3. DIBUJAR EL POLÍGONO (Aquí estaba el NameError, ahora está dentro de la lógica correcta)
folium.Polygon(
    locations=zona_manual_1,
    color="blue",
    fill=True,
    fill_opacity=0.4,
    weight=3,
    popup="Zona: Colón / Independencia / J.B. Justo / Buenos Aires"
).add_to(m)

# 4. RENDERIZAR EN STREAMLIT
folium_static(m, width=1100, height=700)
