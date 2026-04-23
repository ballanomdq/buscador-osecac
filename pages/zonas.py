import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("📍 Mapa Jurisdiccional: RODRÍGUEZ (Ajuste por Esquinas)")

# --- COORDENADAS GPS REALES DE LAS ESQUINAS MENCIONADAS ---

# ZONA 1: El rectángulo entre Colón, Güemes, Buenos Aires y J.B. Justo
# Puntos: Esquina (Colón/BsAs), Esquina (Colón/Güemes), Esquina (JB Justo/Güemes), Esquina (JB Justo/BsAs)
z1_esquinas = [
    [-38.0068, -57.5484], # Av. Colón y Buenos Aires
    [-38.0104, -57.5358], # Av. Colón y Güemes
    [-38.0371, -57.5484], # Av. J.B. Justo y Güemes
    [-38.0335, -57.5611]  # Av. J.B. Justo y Buenos Aires
]

# ZONA 2: Microcentro / La Perla (Siguiendo la costa)
# Puntos: Esquina (Colón/Catamarca), Esquina (Colón/20 Sept), Esquina (20 Sept/Costa), Esquina (Catamarca/Costa)
z2_esquinas = [
    [-38.0016, -57.5566], # Av. Colón y Catamarca
    [-38.0044, -57.5606], # Av. Colón y 20 de Septiembre
    [-37.9892, -57.5512], # 20 de Septiembre y Felix U. Camet (La Costa)
    [-37.9912, -57.5445]  # Catamarca y Felix U. Camet (La Costa)
]

# ZONA 3: El Oeste (San Juan, Bronzini, Colón y Pehuajó)
# Puntos: Esquina (Colón/San Juan), Esquina (Colón/Bronzini), Esquina (Bronzini/Pehuajó), Esquina (San Juan/Pehuajó)
z3_esquinas = [
    [-38.0004, -57.5683], # Av. Colón y San Juan
    [-38.0017, -57.5750], # Av. Colón y Teodoro Bronzini
    [-38.0431, -57.6382], # T. Bronzini y Pehuajó (Altura 9000 aprox)
    [-38.0412, -57.6315]  # San Juan y Pehuajó (Altura 9000 aprox)
]

# --- CREACIÓN DEL MAPA ---
m = folium.Map(location=[-38.0150, -57.5600], zoom_start=13)

# Dibujamos las 3 zonas (Islas)
folium.Polygon(
    locations=z1_esquinas, 
    color="#00CED1", fill=True, fill_opacity=0.5, weight=4,
    popup="<b>RODRÍGUEZ - ZONA 1</b><br>Límites: Colón, JB Justo, Güemes y Bs As"
).add_to(m)

folium.Polygon(
    locations=z2_esquinas, 
    color="#00CED1", fill=True, fill_opacity=0.5, weight=4,
    popup="<b>RODRÍGUEZ - ZONA 2</b><br>Límites: La Costa, Colón, Catamarca y 20 Sept"
).add_to(m)

folium.Polygon(
    locations=z3_esquinas, 
    color="#00CED1", fill=True, fill_opacity=0.5, weight=4,
    popup="<b>RODRÍGUEZ - ZONA 3</b><br>Límites: San Juan, Bronzini, Colón y Pehuajó"
).add_to(m)

folium_static(m, width=1200, height=700)
