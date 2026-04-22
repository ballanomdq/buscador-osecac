import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="Zonificación OSECAC MDP")

st.title("📍 Mapa de Jurisdicciones (Ajustado por Calle)")
st.markdown("---")

# Referencia de colores en columnas
col1, col2, col3, col4 = st.columns(4)
with col1: st.info("🔵 **RODRÍGUEZ**: Norte")
with col2: st.error("🔴 **CARBAYO**: Macrocentro")
with col3: st.warning("🟡 **LÓPEZ**: Oeste")
with col4: st.success("🟠 **GARCÍA**: Sur/Puerto")

# Centrado exacto en el centro de MDP
m = folium.Map(location=[-38.005, -57.555], zoom_start=13)

# --- COORDENADAS SIGUIENDO LA TRAZA URBANA ---

# RODRÍGUEZ (Norte: De Constitución a Luro)
zona_rodriguez = [
    [-37.975, -57.545], [-37.998, -57.545], # Costa hasta Luro
    [-37.998, -57.605], [-37.975, -57.605]  # Por Champagnat
]

# CARBAYO (Macrocentro: Entre Colón, J.B. Justo, Independencia y Jara)
zona_carbayo = [
    [-38.012, -57.552], [-38.038, -57.552], # Eje Independencia
    [-38.038, -57.585], [-38.012, -57.585]  # Eje Av. Jara
]

# LÓPEZ (Oeste: De Av. Jara hacia el fondo)
zona_lopez = [
    [-38.012, -57.585], [-38.038, -57.585], # Límite con Carbayo
    [-38.038, -57.650], [-38.012, -57.650]  # Fondo
]

# GARCÍA (Sur y Costa: El polígono más complejo)
# Sigue la curva de la costa y dobla en las avenidas
zona_garcia = [
    [-38.000, -57.535], [-38.012, -57.535], # Borde Colón
    [-38.012, -57.552], [-38.038, -57.552], # Baja por Independencia
    [-38.038, -57.540], [-38.060, -57.545], # Puerto
    [-38.150, -57.630], [-38.220, -57.750], # Camino a Miramar
    [-38.230, -57.700], [-38.000, -57.530]  # Cierre por costa
]

# Dibujar polígonos con opacidad baja para que se lea la calle abajo
folium.Polygon(zona_rodriguez, color="blue", weight=2, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_carbayo, color="red", weight=2, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_lopez, color="yellow", weight=2, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_garcia, color="orange", weight=2, fill=True, fill_opacity=0.3).add_to(m)

st_folium(m, width=1300, height=650)
