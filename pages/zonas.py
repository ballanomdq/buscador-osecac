import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide", page_title="Zonas Inspector López")

st.title("Jurisdicción: LOPEZ, MARTÍN LEONARDO (Leg. 9983)")
st.write("Mapa rectificado: Los bordes siguen las calles del plano.")

# ESTE ES EL DICCIONARIO CON LAS COORDENADAS QUE FUNCIONAN
ZONAS_LOPEZ = [
    {
        "nombre": "Zona 1: Centro (Plaza Mitre / La Perla)",
        "calles": "Límites: 11 de Septiembre, Av. Colón, San Luis y Santiago del Estero.",
        "coords": [
            (-37.9961, -57.5492), # San Luis y 11 de Septiembre
            (-37.9995, -57.5475), # Diag. Alberdi y Santiago del Estero
            (-38.0062, -57.5507), # Av. Colón y Santiago del Estero
            (-38.0063, -57.5518), # Av. Colón y San Luis
        ]
    },
    {
        "nombre": "Zona 2: Noroeste (Bronzini)",
        "calles": "Límites: Av. Colón, Av. Juan B. Justo, T. Bronzini y Av. Champagnat.",
        "coords": [
            (-38.0069, -57.5755), # Av. Colón y T. Bronzini
            (-38.0067, -57.6081), # Av. Colón y Av. J.B. Justo
            (-38.0335, -57.6152), # Av. J.B. Justo y Reforma Universitaria
            (-38.0381, -57.5841), # Av. J.B. Justo y T. Bronzini
        ]
    },
    {
        "nombre": "Zona 3: Sur (J.B. Justo / Nuevo Golf)",
        "calles": "Límites: Av. Juan B. Justo, Calle Cerrito, Calle Acha y Av. Jorge Newbery.",
        "coords": [
            (-38.0338, -57.5562), # Av. J.B. Justo y Acha
            (-38.0415, -57.5812), # Av. J.B. Justo y Jorge Newbery
            (-38.0642, -57.5985), # Cerrito y Jorge Newbery
            (-38.0535, -57.5721)  # Cerrito y Acha
        ]
    }
]

# Mapa base
m = folium.Map(location=[-38.0150, -57.5650], zoom_start=13)

# Dibujar las 3 zonas en verde
for zona in ZONAS_LOPEZ:
    folium.Polygon(
        locations=zona["coords"],
        color="green",
        fill=True,
        fill_color="green",
        fill_opacity=0.4,
        weight=3,
        popup=f"{zona['nombre']}: {zona['calles']}"
    ).add_to(m)

folium_static(m, width=1100, height=700)
