import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="Zonificación OSECAC MDP")

st.title("📍 Mapa de Jurisdicciones (Ajustado por Avenida)")
st.markdown("---")

# Referencia de colores en columnas (Leyenda)
col1, col2, col3, col4 = st.columns(4)
with col1: st.info("🔵 **RODRÍGUEZ**: Norte")
with col2: st.error("🔴 **CARBAYO**: Macrocentro")
with col3: st.warning("🟡 **LÓPEZ**: Oeste")
with col4: st.success("🟠 **GARCÍA**: Sur")

# Centrado exacto en el microcentro de MDP
m = folium.Map(location=[-38.005, -57.555], zoom_start=13)

# --- COORDINADAS DETALLADAS (Surcando las Avenidas) ---

# RODRÍGUEZ (Norte: De Constitución a Luro/Colón, siguiendo Champagnat)
# Estos puntos están alineados con la cuadrícula de MDP
zona_rodriguez = [
    [-37.972, -57.540], [-38.000, -57.540], # De la costa por Av. Luro
    [-38.000, -57.600], [-37.972, -57.600]  # Por Champagnat hasta Constitución
]

# CARBAYO (Macrocentro: Cuadrante entre Colón, J.B. Justo, Independencia y Jara)
zona_carbayo = [
    [-38.016, -57.552], [-38.038, -57.552], # Baja por Independencia
    [-38.038, -57.585], [-38.016, -57.585]  # Vuelve por Jara (Límite Oeste)
]

# LÓPEZ (Oeste: Regional/Industrial, de Jara hacia el fondo)
zona_lopez = [
    [-38.016, -57.585], [-38.038, -57.585], # Límite con Carbayo
    [-38.038, -57.650], [-38.016, -57.650]  # Hacia el fondo (Campo)
]

# GARCÍA (Sur/Costa: Puerto hasta Las Brusquitas)
# Sigue la curva de la costa y corta justo en Independencia
zona_garcia = [
    [-38.000, -57.535], [-38.016, -57.535], # Borde Colón/Costa
    [-38.016, -57.552], [-38.038, -57.552], # Dobla en Independencia/J.B. Justo
    [-38.038, -57.540], [-38.100, -57.600], # Puerto/Punta Mogotes
    [-38.210, -57.780], [-38.220, -57.700], # Las Brusquitas
    [-38.000, -57.530]  # Cierre por costa
]

# Dibujar polígonos con baja opacidad para que se vea la calle por debajo
folium.Polygon(zona_rodriguez, color="blue", weight=2, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_carbayo, color="red", weight=2, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_lopez, color="yellow", weight=2, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_garcia, color="orange", weight=2, fill=True, fill_opacity=0.3).add_to(m)

# Mostramos el mapa
st_folium(m, width=1300, height=650)
