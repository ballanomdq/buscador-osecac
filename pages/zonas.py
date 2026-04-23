import streamlit as st
import folium
from streamlit_folium import folium_static

# Configuración de la página
st.set_page_config(layout="wide", page_title="Jurisdicción: RODRÍGUEZ")

st.title("🛡️ Jurisdicción de Inspección: RODRÍGUEZ")
st.markdown("### Mar del Plata - Control de Veredas y Alturas")

# --- DATA ESTRUCTURADA DE RODRÍGUEZ ---
RODRIGUEZ_ZONAS = [
    {
        "id": "R1",
        "nombre": "ZONA 1: Cuadrante Güemes / Buenos Aires",
        "color": "#00CED1",
        "descripcion": """
            <b>Límites y Paridad:</b><br>
            - <b>Norte:</b> Calle Güemes (2200-4800) - <b>VEREDA IMPAR</b><br>
            - <b>Sur:</b> Calle Buenos Aires (2200-4500) - <b>VEREDA PAR</b><br>
            - <b>Este:</b> Av. Colón (2000-1300) - <b>VEREDA PAR</b><br>
            - <b>Oeste:</b> Av. J.B. Justo (2000-1300) - <b>VEREDA IMPAR</b>
        """,
        # Coordenadas aproximadas según alturas MDP (Colón/JB Justo y Güemes/BsAs)
        "coords": [
            [-38.0055, -57.5430], [-38.0075, -57.5485], 
            [-38.0345, -57.5615], [-38.0325, -57.5560]
        ]
    },
    {
        "id": "R2",
        "nombre": "ZONA 2: Microcentro / La Perla (Polígono Costero)",
        "color": "#008B8B",
        "descripcion": """
            <b>Límites y Paridad:</b><br>
            - <b>Norte:</b> Calle Catamarca (500-2100) - <b>VEREDA IMPAR</b><br>
            - <b>Sur:</b> 20 de Septiembre (0-2100, PAR) y Charlone (300-0, PAR)<br>
            - <b>Este:</b> F.U. Camet (0-200) y Bv. Marítimo P. Ramos (0-600)<br>
            - <b>Oeste:</b> Av. Colón (3500-3100) - <b>VEREDA IMPAR</b>
        """,
        # Polígono irregular costero
        "coords": [
            [-37.9895, -57.5410], [-37.9940, -57.5385], [-37.9985, -57.5440],
            [-38.0015, -57.5560], [-37.9930, -57.5600], [-37.9880, -57.5490]
        ]
    },
    {
        "id": "R3",
        "nombre": "ZONA 3: Cuadrante San Juan / Bronzini (Oeste)",
        "color": "#20B2AA",
        "descripcion": """
            <b>Límites y Paridad:</b><br>
            - <b>Norte:</b> Calle San Juan (2200-4800) - <b>VEREDA IMPAR</b><br>
            - <b>Sur:</b> Calle T. Bronzini (2200-4800) - <b>VEREDA PAR</b><br>
            - <b>Este:</b> Av. Colón (5800-4200) - <b>VEREDA PAR</b><br>
            - <b>Oeste:</b> Pehuajó y Heguilor (0-Final) - Altura 9000-7500
        """,
        # Extensión hacia el Oeste
        "coords": [
            [-38.0100, -57.5850], [-38.0150, -57.6100], 
            [-38.0550, -57.6500], [-38.0450, -57.6150]
        ]
    }
]

# --- UI DE SELECCIÓN ---
st.info("💡 Interpretación de Veredas: El sistema valida Calle + Altura + Paridad.")

tabs = st.tabs([z["nombre"] for z in RODRIGUEZ_ZONAS])

for i, tab in enumerate(tabs):
    with tab:
        st.markdown(RODRIGUEZ_ZONAS[i]["descripcion"], unsafe_allow_html=True)

st.divider()

# --- MAPA ---
# Centramos el mapa para que abarque desde la costa hasta el extremo oeste (Pehuajó)
m = folium.Map(location=[-38.0200, -57.5800], zoom_start=13, tiles="OpenStreetMap")

for zona in RODRIGUEZ_ZONAS:
    folium.Polygon(
        locations=zona["coords"],
        color=zona["color"],
        fill=True,
        fill_color=zona["color"],
        fill_opacity=0.5,
        weight=3,
        popup=folium.Popup(f"<b>{zona['nombre']}</b><br>{zona['descripcion']}", max_width=350),
        tooltip=f"RODRÍGUEZ - {zona['id']}"
    ).add_to(m)

# Marcadores de referencia para orientación
folium.Marker([-38.0009, -57.5416], tooltip="Centro MDP", icon=folium.Icon(color='red')).add_to(m)
folium.Marker([-38.0550, -57.6500], tooltip="Límite Oeste (Pehuajó/Heguilor)", icon=folium.Icon(color='blue')).add_to(m)

folium_static(m, width=1200, height=650)

st.warning("Nota: Los polígonos son representaciones de área. La validación legal se realiza por la paridad de la vereda indicada en el texto.")
