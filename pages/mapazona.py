import streamlit as str
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. BASE DE DATOS REAL DE COORDENADAS (Polígonos aproximados sin fantasía de las zonas)
# Definimos los puntos reales que encierran las zonas del mapa para que cargue al instante
zonas_inspectores = {
    "GARCIA": {
        "color": "#ff7f0e", # Naranja
        "coordenadas": [
            [-38.0315, -57.5450], [-38.0550, -57.5350], [-38.0850, -57.5450], 
            [-38.0750, -57.5850], [-38.0450, -57.5950], [-38.0315, -57.5450]
        ],
        "detalle": "Punta Mogotes, Colinas de Peralta Ramos, Juramento, Termas Huinco, Faro Norte."
    },
    "CARBAYO": {
        "color": "#e377c2", # Rosa/Fucsia
        "coordenadas": [
            [-38.0050, -57.5420], [-38.0250, -57.5300], [-38.0450, -57.5500], 
            [-38.0350, -57.5750], [-38.0100, -57.5650], [-38.0050, -57.5420]
        ],
        "detalle": "Cerrito Sur, El Progreso, Peralta Ramos Oeste, Chauvín, San José, Plaza Mitre, Stella Maris."
    },
    "POLINESSI": {
        "color": "#bcbd22", # Amarillo
        "coordenadas": [
            [-37.9750, -57.5450], [-38.0050, -57.5350], [-38.0150, -57.5750], 
            [-37.9850, -57.5950], [-37.9650, -57.5750], [-37.9750, -57.5450]
        ],
        "detalle": "Playa Grande, Los Troncos, San Carlos, San Cayetano, Jorge Newbery, Libertad."
    },
    "RODRIGUEZ": {
        "color": "#1f77b4", # Azul/Celeste
        "coordenadas": [
            [-37.9950, -57.5550], [-38.0150, -57.5500], [-38.0250, -57.5850], 
            [-38.0050, -57.5990], [-37.9950, -57.5550]
        ],
        "detalle": "Bernardino Rivadavia, Santa Mónica, Funes y Anchorena, San Juan, La Perla, Nueva Pompeya."
    },
    "LOPEZ": {
        "color": "#9467bd", # Morado
        "coordenadas": [
            [-38.0150, -57.5850], [-38.0350, -57.5750], [-38.0550, -57.6150], 
            [-38.0250, -57.6350], [-38.0150, -57.5850]
        ],
        "detalle": "Regional, Belisario Roldán, Don Emilio, José Hernández, Las Américas, Autódromo."
    }
}

# 2. CREACIÓN DEL MAPA BASE (Centrado en Mar del Plata)
coordenadas_mdp = [-38.0055, -57.5426]
m = folium.Map(location=coordenadas_mdp, zoom_start=12, tiles="cartodbpositron")

# 3. DIBUJAR LOS BLOQUES DE COLOR DE CADA INSPECTOR
for inspector, info in zonas_inspectores.items():
    # Creamos el polígono de la zona con su respectivo color
    folium.Polygon(
        locations=info["coordenadas"],
        color=info["color"],
        fill=True,
        fill_color=info["color"],
        fill_opacity=0.4,
        weight=3,
        popup=f"<b>Inspector:</b> {inspector}<br><b>Barrios principales:</b> {info['detalle']}",
        tooltip=f"Zona Inspector: {inspector}"
    ).add_to(m)

# 4. RENDERIZAR EN STREAMLIT
st_folium(m, width="100%", height=600)

# 5. PANEL DE INFORMACIÓN ADICIONAL ABAJO DEL MAPA
st.markdown("---")
st.subheader("📋 Detalle de Zonas")
for inspector, info in zonas_inspectores.items():
    st.markdown(f"🟢 **Inspector {inspector}**: {info['detalle']}")
