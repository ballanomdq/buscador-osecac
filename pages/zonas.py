import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("📍 Jurisdicción Real: RODRÍGUEZ")

# --- BUSQUEDA DE INTERSECCIONES REALES PARA RODRÍGUEZ ---

# ZONA 1: Güemes / Buenos Aires / Colón / JB Justo
# Buscamos los 4 puntos donde estas calles se cruzan entre sí:
z1_esquinas = [
    [-38.0055, -57.5431], # Av. Colón y Güemes
    [-38.0084, -57.5484], # Av. Colón y Buenos Aires
    [-38.0327, -57.5617], # Av. J.B. Justo y Buenos Aires
    [-38.0298, -57.5564]  # Av. J.B. Justo y Güemes
]

# ZONA 2: Microcentro / La Perla (Polígono irregular)
# Usamos las esquinas donde las calles tocan la costa
z2_esquinas = [
    [-38.0016, -57.5567], # Av. Colón y Catamarca
    [-38.0045, -57.5606], # Av. Colón y 20 de Septiembre
    [-37.9943, -57.5403], # 20 de Septiembre y Bv. Marítimo (Costa)
    [-37.9912, -57.5447]  # Catamarca y F.U. Camet (Costa)
]

# ZONA 3: San Juan / Bronzini / Colón / Pehuajó
# Esta zona es gigante, buscamos los puntos extremos
z3_esquinas = [
    [-38.0004, -57.5683], # Av. Colón y San Juan
    [-38.0017, -57.5751], # Av. Colón y T. Bronzini
    [-38.0336, -57.6253], # T. Bronzini y Pehuajó (Cerca de Av. Tetamanti)
    [-38.0315, -57.6180]  # San Juan y Pehuajó
]

# --- DIBUJO EN EL MAPA ---

m = folium.Map(location=[-38.0150, -57.5600], zoom_start=13)

# Color único para Rodríguez
color_rod = "#00CED1" 

# Dibujamos las 3 Islas
folium.Polygon(locations=z1_esquinas, color=color_rod, fill=True, fill_opacity=0.5, 
               popup="Rodríguez - Zona 1").add_to(m)

folium.Polygon(locations=z2_esquinas, color=color_rod, fill=True, fill_opacity=0.5, 
               popup="Rodríguez - Zona 2").add_to(m)

folium.Polygon(locations=z3_esquinas, color=color_rod, fill=True, fill_opacity=0.5, 
               popup="Rodríguez - Zona 3").add_to(m)

folium_static(m, width=1200, height=700)
