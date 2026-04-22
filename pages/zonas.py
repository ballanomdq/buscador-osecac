import streamlit as st
import folium
from streamlit_folium import st_folium

# ──────────────────────────────────────────────
# CONFIGURACIÓN DE ZONAS CALIBRADAS
# ──────────────────────────────────────────────

ZONAS = {
    "RODRÍGUEZ": {
        "legajo": "Leg. 7713",
        "color": "#00BFFF", # Celeste
        "descripcion": "Norte: De Av. Constitución a Av. Colón/Luro. Límite Oeste: Av. Champagnat.",
        "coords": [
            [-37.9760, -57.6020], # Champagnat y Constitución
            [-37.9690, -57.5420], # Constitución y Costa
            [-38.0000, -57.5370], # Colón/Luro y Costa
            [-38.0060, -57.6120], # Colón/Luro y Champagnat
        ],
    },
    "CARBAYO": {
        "legajo": "Leg. 9220",
        "color": "#DC143C", # Rojo
        "descripcion": "Centro: Entre Av. Colón, J.B. Justo, Independencia y Jara.",
        "coords": [
            [-38.0140, -57.6140], # Colón y J.B. Justo (Punto de unión)
            [-37.9920, -57.6210], # Independencia y J.B. Justo
            [-37.9840, -57.5910], # Independencia y Jara
            [-38.0060, -57.5820], # Jara y Colón (Punto CRÍTICO de unión con LÓPEZ)
        ],
    },
    "LÓPEZ": {
        "legajo": "Leg. 9983",
        "color": "#FFD700", # Amarillo
        "descripcion": "Oeste: Desde Av. Jara hacia el fondo. Eje Av. Colón 5800-9200.",
        "coords": [
            [-38.0060, -57.5820], # Jara y Colón (MISMA COORDENADA que Carbayo para no encimarse)
            [-38.0520, -57.5960], # T. Bronzini y Jara
            [-38.0620, -57.6650], # Límite urbano Oeste
            [-38.0200, -57.6800], # Límite urbano Norte/Oeste
        ],
    },
    "GARCÍA": {
        "legajo": "Leg. 7952",
        "color": "#FF8C00", # Naranja
        "descripcion": "Sur: Desde Independencia y Colón hacia el sur (Puerto/Mogotes/Miramar).",
        "coords": [
            [-37.9995, -57.5460], # Independencia y Colón
            [-38.0020, -57.5310], # Costa y Colón
            [-38.0500, -57.5160], # Costa y J.B. Justo
            [-38.2200, -57.5350], # Límite sur
            [-38.2220, -57.5650], # Límite sur oeste
            [-38.0500, -57.5620], # Subida por Independencia
        ],
    }
}

def construir_mapa():
    mapa = folium.Map(location=[-38.0055, -57.5426], zoom_start=12, tiles="CartoDB positron")
    
    for nombre, zona in ZONAS.items():
        folium.Polygon(
            locations=zona["coords"],
            color=zona["color"],
            weight=2,
            fill=True,
            fill_opacity=0.3, # Transparencia para ver las calles
            tooltip=f"<b>{nombre}</b> - {zona['legajo']}",
            popup=zona["descripcion"]
        ).add_to(mapa)
    return mapa

def main():
    st.set_page_config(page_title="Zonas OSECAC MDP", layout="wide")
    st.title("🗺️ Mapa de Jurisdicciones Calibrado")
    
    # Leyenda simple
    cols = st.columns(4)
    for i, (nombre, zona) in enumerate(ZONAS.items()):
        cols[i].markdown(f"**{nombre}**")
        cols[i].caption(zona['legajo'])

    mapa_final = construir_mapa()
    st_folium(mapa_final, width="100%", height=600)

if __name__ == "__main__":
    main()
