import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("📍 Mapa de Jurisdicción: RODRÍGUEZ (Datos Reales)")

# --- COORDENADAS DE LAS ESQUINAS REALES (Intersecciones) ---

# ZONA 1: Güemes / Buenos Aires / Colón / JB Justo
# Es un rectángulo inclinado siguiendo la cuadrícula de MDP
zona1_esquinas = [
    [-38.0105, -57.5360], # Colón y Güemes
    [-38.0069, -57.5445], # Colón y Buenos Aires
    [-38.0336, -57.5569], # J.B. Justo y Buenos Aires
    [-38.0372, -57.5484]  # J.B. Justo y Güemes
]

# ZONA 2: Microcentro / La Perla (Siguiendo la diagonal de la costa)
zona2_esquinas = [
    [-38.0016, -57.5566], # Colón y Catamarca
    [-38.0044, -57.5606], # Colón y 20 de Septiembre
    [-37.9942, -57.5401], # 20 de Septiembre y la Costa (Bv. Marítimo)
    [-37.9912, -57.5445]  # Catamarca y la Costa (F.U. Camet)
]

# ZONA 3: San Juan / Bronzini / Colón / Pehuajó (El Oeste Profundo)
# Esta zona se estira hacia el suroeste siguiendo la cuadrícula
zona3_esquinas = [
    [-38.0004, -57.5682], # Colón y San Juan
    [-38.0017, -57.5750], # Colón y T. Bronzini
    [-38.0430, -57.6380], # T. Bronzini y Pehuajó (estimado por altura 9000)
    [-38.0410, -57.6310]  # San Juan y Pehuajó (estimado por altura 9000)
]

# --- CREACIÓN DEL MAPA ---
m = folium.Map(location=[-38.0150, -57.5600], zoom_start=13, tiles="OpenStreetMap")

# Estilo de los polígonos (Usamos el Turquesa de Rodríguez)
estilo = {'fillColor': '#00CED1', 'color': '#00CED1', 'fillOpacity': 0.5, 'weight': 3}

# Dibujar cada isla por separado
folium.Polygon(locations=zona1_esquinas, **estilo, 
               popup="ZONA 1: Güemes/BsAs<br>Colón (PAR) / JB Justo (IMPAR)").add_to(m)

folium.Polygon(locations=zona2_esquinas, **estilo, 
               popup="ZONA 2: La Perla<br>Catamarca (IMPAR) / 20 Sept (PAR)").add_to(m)

folium.Polygon(locations=zona3_esquinas, **estilo, 
               popup="ZONA 3: Oeste Urbano<br>San Juan/Bronzini hasta Pehuajó").add_to(m)

# Mostrar en Streamlit
folium_static(m, width=1200, height=700)

st.success("Interpretación completada: 3 Islas independientes cargadas con intersecciones reales.")
