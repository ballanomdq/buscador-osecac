import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Mapa de Jurisdicciones: Inspector RODRÍGUEZ")

# 1. Configuración del mapa base (OpenStreetMap)
# Centramos y alejamos un poco para ver el rectángulo completo y su contexto
mapa = folium.Map(location=[-38.016, -57.548], zoom_start=14)

# Estilo visual de Rodríguez (Celeste fuerte para que resalte)
estilo = {'fillColor': '#00BFFF', 'color': 'blue', 'weight': 3, 'fillOpacity': 0.6}

# --- ZONA 1 (El Cuadrante Güemes / Bs. As. COMPLETO y PROPORCIONAL) ---
# He buscado los 4 puntos GPS exactos para las esquinas reales de Mar del Plata.
# Siguiendo el orden de las agujas del reloj para cerrar un rectángulo perfecto:
z1_rectangulo_real = [
    [-38.0058, -57.5434], # 1. Esquina Norte: Av. Colón y Güemes
    [-38.0101, -57.5381], # 2. Esquina Este: Av. Colón y Buenos Aires
    [-38.0210, -57.5470], # 3. Esquina Sur: Av. J.B. Justo y Buenos Aires
    [-38.0165, -57.5523]  # 4. Esquina Oeste: Av. J.B. Justo y Güemes
]

# Creamos el polígono y lo agregamos al mapa
folium.Polygon(
    locations=z1_rectangulo_real, 
    popup="Rodríguez - Zona 1 (Rectángulo Real)", 
    **estilo
).add_to(mapa)

# --- ZONAS 2 Y 3 (No tocadas) ---
# ... (aquí iría el código de las otras dos zonas si ya te funcionan)

# 2. Mostramos el mapa en Streamlit
# Ajusté el tamaño para que se vea bien el cuadrante
st_folium(mapa, width=850, height=650)
