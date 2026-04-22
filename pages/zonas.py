import streamlit as st
import folium
from streamlit_folium import st_folium

# Configuración de la página para que use todo el ancho
st.set_page_config(layout="wide", page_title="Sistema de Zonas OSECAC")

st.title("📍 Mapa de Jurisdicciones - Cuerpo de Inspectores")
st.markdown("---")

# 1. REFERENCIA DE COLORES (Títulos para los Inspectores)
# Esto ayuda a que el inspector identifique su color rápidamente
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.info("🔵 **RODRÍGUEZ** (Norte/Centro)")
with col2:
    st.error("🔴 **CARBAYO** (Macrocentro)")
with col3:
    st.warning("🟡 **LÓPEZ** (Oeste/Fondo)")
with col4:
    st.success("🟠 **GARCÍA** (Sur/Puerto)")

# 2. CONFIGURACIÓN DEL MAPA BASE
# Centrado en Mar del Plata
m = folium.Map(location=[-38.0055, -57.5426], zoom_start=12)

# 3. DEFINICIÓN DE POLÍGONOS (Basado en tus fotos y coordenadas reales)

# ZONA RODRÍGUEZ - Norte (Desde Constitución hasta Luro/Colón)
zona_rodriguez = [
    [-37.970, -57.545], [-37.995, -57.545], 
    [-37.995, -57.610], [-37.970, -57.610]
]

# ZONA CARBAYO - Centro (Cuadrante Plaza Mitre / San José)
zona_carbayo = [
    [-38.005, -57.555], [-38.035, -57.555], 
    [-38.035, -57.595], [-38.005, -57.595]
]

# ZONA LÓPEZ - Oeste (Corredor Colón 5800-9200 y Regional)
zona_lopez = [
    [-37.995, -57.595], [-38.040, -57.595], 
    [-38.040, -57.680], [-37.995, -57.680]
]

# ZONA GARCÍA - Sur (Puerto hasta Arroyo Las Brusquitas)
# Este es el polígono más largo que baja por la costa
zona_garcia = [
    [-38.015, -57.535], [-38.035, -57.540], [-38.060, -57.560], 
    [-38.150, -57.650], [-38.220, -57.750], # Límite Las Brusquitas
    [-38.230, -57.700], [-38.015, -57.530]
]

# 4. DIBUJAR LAS ZONAS EN EL MAPA
folium.Polygon(
    zona_rodriguez, color="blue", weight=2, fill=True, fill_opacity=0.4, 
    popup="RODRÍGUEZ - Zona Norte"
).add_to(m)

folium.Polygon(
    zona_carbayo, color="red", weight=2, fill=True, fill_opacity=0.4, 
    popup="CARBAYO - Macrocentro"
).add_to(m)

folium.Polygon(
    zona_lopez, color="yellow", weight=2, fill=True, fill_opacity=0.4, 
    popup="LÓPEZ - Zona Oeste"
).add_to(m)

folium.Polygon(
    zona_garcia, color="orange", weight=2, fill=True, fill_opacity=0.4, 
    popup="GARCÍA - Zona Sur / Puerto"
).add_to(m)

# 5. MOSTRAR MAPA EN LA WEB
st_folium(m, width=1300, height=650)

# 6. PIE DE PÁGINA INFORMATIVO
st.info("Hacé clic en cualquier área de color para confirmar el inspector responsable.")
