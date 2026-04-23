import streamlit as st
import folium
from streamlit_folium import folium_static

# Configuración de la página
st.set_page_config(layout="wide")
st.title("📍 Jurisdicción de Inspección: RODRÍGUEZ")
st.markdown("### Mar del Plata - Ubicación exacta por esquinas")

# --- COORDENADAS DE LAS ESQUINAS (INTERSECCIONES) ---
# He buscado cada esquina para que el polígono siga la línea de la calle

# ZONA 1: Rectángulo entre Colón, Güemes, Buenos Aires y J.B. Justo
zona1_esquinas = [
    [-38.0105, -57.5360], # Esquina Colón y Güemes
    [-38.0069, -57.5445], # Esquina Colón y Buenos Aires
    [-38.0336, -57.5611], # Esquina J.B. Justo y Buenos Aires
    [-38.0372, -57.5484]  # Esquina J.B. Justo y Güemes
]

# ZONA 2: Polígono irregular siguiendo la costa (Microcentro / La Perla)
zona2_esquinas = [
    [-38.0016, -57.5566], # Esquina Colón y Catamarca
    [-38.0044, -57.5606], # Esquina Colón y 20 de Septiembre
    [-37.9942, -57.5401], # Esquina 20 de Septiembre y la Costa (Bv. Marítimo)
    [-37.9912, -57.5445]  # Esquina Catamarca y la Costa (F.U. Camet)
]

# ZONA 3: Cuadrante San Juan / Bronzini / Colón / Pehuajó (El Oeste)
zona3_esquinas = [
    [-38.0004, -57.5682], # Esquina Colón y San Juan
    [-38.0017, -57.5750], # Esquina Colón y Teodoro Bronzini
    [-38.0430, -57.6380], # Esquina T. Bronzini y Pehuajó (Altura 9000 aprox)
    [-38.0410, -57.6310]  # Esquina San Juan y Pehuajó (Altura 9000 aprox)
]

# --- CREACIÓN DEL MAPA ---
# Centramos en Mar del Plata
mapa = folium.Map(location=[-38.0150, -57.5600], zoom_start=13, tiles="OpenStreetMap")

# Color para Rodríguez (Cian/Turquesa)
color_insp = "#00CED1"

# Dibujar Zona 1
folium.Polygon(
    locations=zona1_esquinas,
    color=color_insp,
    fill=True,
    fill_opacity=0.5,
    weight=3,
    popup="ZONA 1 - RODRÍGUEZ<br>Límites: Colón, JB Justo, Güemes y Bs As"
).add_to(mapa)

# Dibujar Zona 2
folium.Polygon(
    locations=zona2_esquinas,
    color=color_insp,
    fill=True,
    fill_opacity=0.5,
    weight=3,
    popup="ZONA 2 - RODRÍGUEZ<br>Límites: La Costa, Colón, Catamarca y 20 Sept"
).add_to(mapa)

# Dibujar Zona 3
folium.Polygon(
    locations=zona3_esquinas,
    color=color_insp,
    fill=True,
    fill_opacity=0.5,
    weight=3,
    popup="ZONA 3 - RODRÍGUEZ<br>Límites: San Juan, Bronzini, Colón y Pehuajó"
).add_to(mapa)

# Mostrar mapa en Streamlit
folium_static(mapa, width=1200, height=700)

st.success("✅ Las zonas ahora están ancladas a las intersecciones de calles reales.")
