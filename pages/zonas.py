import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="Zonificación OSECAC MDP")

st.title("📍 Mapa de Jurisdicciones por Calle")
st.markdown("---")

# Referencia de colores
col1, col2, col3, col4 = st.columns(4)
with col1: st.info("🔵 **RODRÍGUEZ**: Norte")
with col2: st.error("🔴 **CARBAYO**: Macrocentro")
with col3: st.warning("🟡 **LÓPEZ**: Oeste")
with col4: st.success("🟠 **GARCÍA**: Sur")

m = folium.Map(location=[-38.0055, -57.5426], zoom_start=13)

# --- COORDINADAS AJUSTADAS A LAS CALLES ---

# GARCÍA: Sigue la línea de la costa y corta en Independencia/J.B.Justo
zona_garcia = [
    [-38.001, -57.531], [-38.016, -57.531], [-38.016, -57.550], # Borde Colón/Independencia
    [-38.036, -57.550], [-38.036, -57.580], # Baja por Independencia hasta J.B.Justo
    [-38.150, -57.650], [-38.220, -57.750], # Las Brusquitas
    [-38.230, -57.700], [-38.001, -57.525]
]

# CARBAYO: El cuadrado entre Colón, J.B. Justo, Independencia y Jara
zona_carbayo = [
    [-38.016, -57.550], [-38.036, -57.550], # Tramo Independencia
    [-38.036, -57.575], [-38.016, -57.575]  # Tramo Jara/Colón
]

# RODRÍGUEZ: Norte, cortando justo en Av. Luro y Av. Constitución
zona_rodriguez = [
    [-37.970, -57.540], [-38.000, -57.540], # De la costa a Luro
    [-38.000, -57.600], [-37.970, -57.600]  # Por Champagnat
]

# LÓPEZ: El área de Av. Colón hacia el fondo (Regional/Oeste)
zona_lopez = [
    [-38.000, -57.575], [-38.030, -57.575], # Límite con Carbayo (Jara)
    [-38.030, -57.680], [-38.000, -57.680]  # Hacia el fondo
]

# Dibujar con bordes más finos para que se vean las calles abajo
folium.Polygon(zona_garcia, color="orange", weight=1, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_rodriguez, color="blue", weight=1, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_lopez, color="yellow", weight=1, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_carbayo, color="red", weight=1, fill=True, fill_opacity=0.3).add_to(m)

st_folium(m, width=1300, height=600)
