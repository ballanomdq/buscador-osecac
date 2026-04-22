import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("📍 Mapa de Zonificación - Inspectores OSECAC")

# 1. Creamos el mapa centrado en Mar del Plata
m = folium.Map(location=[-38.0055, -57.5426], zoom_start=12)

# 2. DEFINICIÓN DE POLÍGONOS (ZONAS)
# Coordenadas aproximadas según tus apuntes y el mapa de colores

# ZONA GARCÍA (Naranja) - Centro y Sur hasta Las Brusquitas
zona_garcia = [
    [-38.001, -57.540], [-38.035, -57.540], # Centro
    [-38.035, -57.580], [-38.210, -57.780], # Hacia Las Brusquitas
    [-38.220, -57.700], [-38.001, -57.530]  # Costa
]

# ZONA CARBAYO (Fucsia) - Plaza Mitre / San José
zona_carbayo = [
    [-38.005, -57.555], [-38.035, -57.555], 
    [-38.035, -57.585], [-38.005, -57.585]
]

# ZONA LÓPEZ (Amarillo) - Oeste y tramos específicos
zona_lopez = [
    [-37.990, -57.590], [-38.030, -57.590],
    [-38.030, -57.650], [-37.990, -57.650]
]

# 3. DIBUJAR EN EL MAPA
folium.Polygon(zona_garcia, color="orange", fill=True, fill_opacity=0.4, popup="GARCÍA - Leg. 7952").add_to(m)
folium.Polygon(zona_carbayo, color="deeppink", fill=True, fill_opacity=0.4, popup="CARBAYO - Leg. 9220").add_to(m)
folium.Polygon(zona_lopez, color="yellow", fill=True, fill_opacity=0.4, popup="LÓPEZ - Leg. 9983").add_to(m)

# 4. MOSTRAR EL MAPA EN STREAMLIT
st_folium(m, width=1200, height=600)

st.info("💡 Hacé clic sobre cada color para ver el nombre del Inspector responsable.")
