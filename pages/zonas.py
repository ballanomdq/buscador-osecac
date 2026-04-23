import streamlit as st
import folium
from streamlit_folium import folium_static

# Configuración de página
st.set_page_config(layout="wide", page_title="Jurisdicciones Inspectores MDP")

st.title("📋 Sistema de Gestión Territorial de Inspectores")
st.markdown("### Mar del Plata - Batán - Miramar")

# --- DEFINICIÓN DE COLORES POR INSPECTOR ---
COLORES = {
    "CARBAYO": "#FF1493",    # Rosa Fucsia
    "RODRÍGUEZ": "#00CED1",  # Turquesa
    "LÓPEZ": "#00008B",      # Azul Oscuro
    "GARCÍA": "#FF8C00"      # Naranja
}

# --- ESTRUCTURA DE DATOS (ISLAS INDEPENDIENTES) ---
# He usado tus puntos de referencia para proyectar los polígonos
ZONAS_DATA = [
    # --- INSPECTOR CARBAYO ---
    {
        "inspector": "CARBAYO",
        "nombre": "ZONA 1: Triángulo Costero",
        "detalles": "Av. Colón (PAR), Corrientes (PAR), Bv. Marítimo.",
        "coords": [[-38.0009, -57.5416], [-38.0050, -57.5416], [-38.0030, -57.5350]],
    },
    {
        "inspector": "CARBAYO",
        "nombre": "ZONA 2: Cuadrante Independencia",
        "detalles": "Colón (PAR 2199-3199), Independencia (PAR 2201-4499), J.B. Justo (IMPAR 2199-3199), Buenos Aires (IMPAR 2201-4499).",
        "coords": [[-38.0050, -57.5600], [-38.0050, -57.5800], [-38.0350, -57.5800], [-38.0350, -57.5600]],
    },
    {
        "inspector": "CARBAYO",
        "nombre": "ZONA 3: Cuadrante Puerto",
        "detalles": "J.B. Justo (PAR 3199-4400), Don Orione (IMPAR), J. Peralta Ramos (PAR), Edison.",
        "coords": [[-38.0350, -57.5450], [-38.0350, -57.5650], [-38.0550, -57.5650], [-38.0550, -57.5450]],
    },

    # --- INSPECTOR RODRÍGUEZ ---
    {
        "inspector": "RODRÍGUEZ",
        "nombre": "ZONA 1: Casco Urbano Norte",
        "detalles": "Luro (IMPAR), Champagnat (IMPAR), Constitución, La Costa.",
        "coords": [[-37.9802, -57.5825], [-37.9802, -57.5450], [-37.9600, -57.5450], [-37.9600, -57.5825]],
    },
    {
        "inspector": "RODRÍGUEZ",
        "nombre": "ZONA 2: Santa Clara / Camet",
        "detalles": "Ruta 11 (Límite Norte), Av. Constitución (Hacia el Norte).",
        "coords": [[-37.9500, -57.5300], [-37.9600, -57.5300], [-37.9600, -57.5600], [-37.9500, -57.5600]],
    },

    # --- INSPECTOR LÓPEZ ---
    {
        "inspector": "LÓPEZ",
        "nombre": "ZONA 1: Oeste Urbano",
        "detalles": "Champagnat (PAR), Luro (Oeste), J.B. Justo (Oeste).",
        "coords": [[-37.9802, -57.5825], [-38.0003, -57.5958], [-38.0200, -57.6200], [-37.9802, -57.6200]],
    },
    {
        "inspector": "LÓPEZ",
        "nombre": "ZONA 2: Isla Batán",
        "detalles": "Ruta 88 (Traza urbana), Calle 35, Calle 155 (Parque Industrial).",
        "coords": [[-38.0000, -57.7500], [-38.0100, -57.7400], [-38.0200, -57.7600], [-38.0100, -57.7700]],
    },

    # --- INSPECTOR GARCÍA ---
    {
        "inspector": "GARCÍA",
        "nombre": "ZONA 1: Mogotes / Faro",
        "detalles": "J.B. Justo (PAR), Martínez de Hoz (Costa Sur), Mario Bravo.",
        "coords": [[-38.0407, -57.5423], [-38.0700, -57.5423], [-38.0700, -57.5800], [-38.0407, -57.5800]],
    },
    {
        "inspector": "GARCÍA",
        "nombre": "ZONA 2: Acantilados / Alfar",
        "detalles": "Mario Bravo (Hacia el Sur), Ruta 11 (Límite Acantilados).",
        "coords": [[-38.0700, -57.5423], [-38.1500, -57.6000], [-38.1500, -57.6500], [-38.0700, -57.6000]],
    },
    {
        "inspector": "GARCÍA",
        "nombre": "ZONA 3: Isla Miramar",
        "detalles": "Av. 9, Av. 12, Av. 40, Costanera Miramar.",
        "coords": [[-38.2650, -57.8400], [-38.2750, -57.8300], [-38.2850, -57.8500], [-38.2750, -57.8600]],
    }
]

# --- RENDERIZADO DE INFORMACIÓN ---
st.info("⚠️ REGLA CRÍTICA: En calles límite, validar PARIDAD (Par/Impar) según la descripción del inspector.")

# Mostrar tarjetas informativas
inspectores = list(COLORES.keys())
cols = st.columns(len(inspectores))

for i, insp in enumerate(inspectores):
    with cols[i]:
        st.markdown(f"**Inspector: {insp}**")
        for zona in ZONAS_DATA:
            if zona['inspector'] == insp:
                with st.expander(f"📍 {zona['nombre']}"):
                    st.write(zona['detalles'])

st.markdown("---")

# --- GENERACIÓN DEL MAPA ---
# Centrado en MDP pero con zoom que permita ver Batán y Miramar
m = folium.Map(location=[-38.0500, -57.6500], zoom_start=11, tiles="OpenStreetMap")

for zona in ZONAS_DATA:
    color = COLORES[zona['inspector']]
    
    # Crear Polígono
    folium.Polygon(
        locations=zona['coords'],
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.4,
        weight=2,
        popup=folium.Popup(f"<b>Inspector: {zona['inspector']}</b><br>{zona['nombre']}<br><i>{zona['detalles']}</i>", max_width=300),
        tooltip=f"{zona['inspector']} - {zona['nombre']}"
    ).add_to(m)

# Mostrar mapa
folium_static(m, width=1200, height=650)

st.success("Mapa cargado con éxito. Las 'islas' son independientes para evitar solapamientos visuales.")
