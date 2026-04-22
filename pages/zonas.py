import streamlit as st
import folium
from streamlit_folium import st_folium

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(layout="wide", page_title="Zonas OSECAC MDP - Calibrado")
st.title("📍 Mapa de Inspección Calibrado por Eje Real")
st.caption("Ajustado mediante los puntos de referencia Luro-Costa y Champagnat.")

# 1. TUS PUNTOS DE REFERENCIA (Calibradores)
# P_COSTA: Luro y La Costa (mano alejada del mar)
# P_ROTONDA: Centro de la rotonda Champagnat y Luro
P_COSTA = [-38.0009, -57.5416]
P_ROTONDA = [-37.9802, -57.5825]

# 2. DEFINICIÓN DE POLÍGONOS BASADOS EN EL EJE
# He proyectado los puntos para que sigan la rotación que marcaste
ZONAS_CALIBRADAS = {
    "RODRÍGUEZ": {
        "color": "#00BFFF",
        "coords": [
            [-37.9650, -57.5600], [-37.9850, -57.5300], 
            P_COSTA, P_ROTONDA
        ]
    },
    "CARBAYO": {
        "color": "#DC143C",
        "coords": [
            P_ROTONDA, P_COSTA,
            [-38.0350, -57.5500], [-38.0410, -57.5860]
        ]
    },
    "LÓPEZ": {
        "color": "#FFD700",
        "coords": [
            P_ROTONDA, [-37.9650, -57.6500], 
            [-38.0400, -57.6800], [-38.0410, -57.5860]
        ]
    },
    "GARCÍA": {
        "color": "#FF8C00",
        "coords": [
            P_COSTA, [-38.0350, -57.5500], 
            [-38.1500, -57.5400], [-38.2200, -57.5350],
            [-38.1800, -57.6000]
        ]
    }
}

# 3. CREACIÓN DEL MAPA
m = folium.Map(location=[-38.005, -57.56], zoom_start=13, tiles="CartoDB positron")

for nombre, data in ZONAS_CALIBRADAS.items():
    folium.Polygon(
        locations=data["coords"],
        color="black",
        weight=1,
        fill=True,
        fill_color=data["color"],
        fill_opacity=0.4,
        tooltip=f"Zona {nombre}"
    ).add_to(m)

# 4. RENDERIZAR
st_folium(m, width="100%", height=700, returned_objects=[])
