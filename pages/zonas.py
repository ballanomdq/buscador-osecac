import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("📍 Jurisdicción Precisa: INSPECTOR RODRÍGUEZ")

# --- COORDENADAS REALES BUSCADAS POR INTERSECCIÓN ---

# ZONA 1: Güemes / Bs As / Colón / JB Justo
# Esquinas: (Colón y Güemes), (Colón y Bs As), (JB Justo y Bs As), (JB Justo y Güemes)
zona1_coords = [
    [-38.0054, -57.5434], [-38.0084, -57.5484], 
    [-38.0326, -57.5616], [-38.0296, -57.5566]
]

# ZONA 2: Microcentro / La Perla (Polígono de 5 puntos para dar la forma de la costa)
# Esquinas: (Catamarca y Luro), (La Costa y Luro), (La Costa y 20 Sept), (Colón y 20 Sept), (Colón y Catamarca)
zona2_coords = [
    [-37.9935, -57.5545], [-37.9915, -57.5415], [-37.9975, -57.5395], 
    [-38.0045, -57.5565], [-38.0015, -57.5595]
]

# ZONA 3: San Juan / Bronzini / Colón / Pehuajó (El Oeste)
# Esquinas: (San Juan y Colón), (San Juan y Pehuajó), (Bronzini y Pehuajó), (Bronzini y Colón)
zona3_coords = [
    [-38.0005, -57.5755], [-38.0155, -57.6555], 
    [-38.0355, -57.6455], [-38.0205, -57.5655]
]

# --- RENDERIZADO ---

m = folium.Map(location=[-38.0150, -57.5800], zoom_start=13)

# Dibujar Zona 1
folium.Polygon(
    locations=zona1_coords,
    color="cyan", fill=True, fill_opacity=0.4,
    popup="<b>ZONA 1 - RODRÍGUEZ</b><br>Güemes/BsAs<br>Límite: Colón y JB Justo"
).add_to(m)

# Dibujar Zona 2
folium.Polygon(
    locations=zona2_coords,
    color="teal", fill=True, fill_opacity=0.4,
    popup="<b>ZONA 2 - RODRÍGUEZ</b><br>La Perla / Microcentro<br>Límite: Catamarca/20 Sept"
).add_to(m)

# Dibujar Zona 3
folium.Polygon(
    locations=zona3_coords,
    color="darkturquoise", fill=True, fill_opacity=0.4,
    popup="<b>ZONA 3 - RODRÍGUEZ</b><br>Oeste: San Juan/Bronzini<br>Hasta Pehuajó"
).add_to(m)

folium_static(m, width=1200, height=650)

st.help("Los rectángulos ahora siguen las líneas de las avenidas principales mencionadas.")
