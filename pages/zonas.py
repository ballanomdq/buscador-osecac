import streamlit as st
import folium
from streamlit_folium import st_folium
import json

# Configuración de página ancha para que el mapa se vea grande
st.set_page_config(layout="wide", page_title="Mapa de Zonas OSECAC")

st.title("📍 Mapa de Jurisdicciones - Mar del Plata")
st.markdown("---")

# 1. CARGAR LOS DATOS (Asegurate que el archivo se llame mapa.json)
try:
    with open("mapa.json", "r") as f:
        datos_geo = json.load(f)
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'mapa.json'. Verificá el nombre.")
    st.stop()

# 2. CREAR EL MAPA BASE
# Centrado en el nudo de Colón e Independencia
m = folium.Map(location=[-38.005, -57.56], zoom_start=13, tiles="CartoDB positron")

# 3. DIBUJAR EL GEOJSON (Esto es lo que convierte el código en colores)
folium.GeoJson(
    datos_geo,
    style_function=lambda feature: {
        'fillColor': feature['properties']['color'],
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.4,
    },
    tooltip=folium.GeoJsonTooltip(fields=['nombre'], aliases=['Inspector:'])
).add_to(m)

# 4. RENDERIZAR EN STREAMLIT
#returned_objects=[] evita que la página se recargue cada vez que tocas el mapa
st_folium(m, width="100%", height=700, returned_objects=[])
