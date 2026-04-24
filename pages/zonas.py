import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Mapa Oficial de Jurisdicciones - OSECAC MDP")

# Centramos el mapa en Mar del Plata
m = folium.Map(location=[-38.005, -57.56], zoom_start=13)

# --- DEFINICIÓN DE ZONAS SEGÚN MAPA FÍSICO ---

# 1. RODRÍGUEZ (Celeste) - Zona Chauvin / San José
folium.Polygon(
    locations=[[-38.006, -57.545], [-38.010, -57.539], [-38.026, -57.554], [-38.022, -57.560]],
    color='blue', fill_color='#00BFFF', fill_opacity=0.5,
    popup="Inspector RODRÍGUEZ"
).add_to(m)

# 2. CARBAYO (Rosa) - Zona Centro / Plaza Mitre
folium.Polygon(
    locations=[[-37.998, -57.555], [-38.005, -57.546], [-38.015, -57.560], [-38.008, -57.568]],
    color='deeppink', fill_color='#FF69B4', fill_opacity=0.5,
    popup="Inspector CARBAYO"
).add_to(m)

# 3. GARCÍA (Naranja) - Zona Norte / Constitución
folium.Polygon(
    locations=[[-37.975, -57.560], [-37.985, -57.545], [-38.000, -57.555], [-37.990, -57.575]],
    color='orange', fill_color='#FFA500', fill_opacity=0.5,
    popup="Inspector GARCÍA"
).add_to(m)

# 4. LOPEZ (Violeta) - Zona Puerto / Cerrito
folium.Polygon(
    locations=[[-38.025, -57.570], [-38.035, -57.550], [-38.060, -57.580], [-38.050, -57.600]],
    color='purple', fill_color='#8A2BE2', fill_opacity=0.5,
    popup="Inspector LÓPEZ"
).add_to(m)

# 5. POLINESSI (Verde) - Zona Playa Grande
folium.Polygon(
    locations=[[-38.020, -57.540], [-38.030, -57.530], [-38.045, -57.545], [-38.035, -57.555]],
    color='green', fill_color='#7FFF00', fill_opacity=0.5,
    popup="Inspector POLINESSI"
).add_to(m)

# Renderizado
st_folium(m, width=1200, height=800)
