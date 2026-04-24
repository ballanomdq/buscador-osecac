import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide", page_title="Zonas Inspector López")

st.title("Jurisdicción: LOPEZ, MARTÍN LEONARDO (Leg. 9983)")
st.write("Mapa corregido: Los bordes ahora siguen las calles del plano.")

# Coordenadas REORDENADAS para evitar el error de pantalla blanca
ZONAS_LOPEZ = [
    {
        "nombre": "Zona 1: Centro (Plaza Mitre / La Perla)",
        "coords": [
            (-38.0063, -57.5518), # 1. Av. Colón y San Luis
            (-37.9961, -57.5492), # 2. San Luis y 11 de Septiembre
            (-37.9995, -57.5475), # 3. Diag. Alberdi y Santiago del Estero
            (-38.0062, -57.5507), # 4. Av. Colón y Santiago del Estero
        ]
    },
    {
        "nombre": "Zona 2: Noroeste (Bronzini)",
        "coords": [
            (-38.0069, -57.5755), # 1. Av. Colón y T. Bronzini
            (-38.0067, -57.6081), # 2. Av. Colón y Av. J.B. Justo
            (-38.0335, -57.6152), # 3. Av. J.B. Justo y Reforma Universitaria
            (-38.0381, -57.5841), # 4. Av. J.B. Justo y T. Bronzini
        ]
    },
    {
        "nombre": "Zona 3: Sur (J.B. Justo / Nuevo Golf)",
        "coords": [
            (-38.0338, -57.5562), # 1. J.B. Justo y Acha
            (-38.0415, -57.5812), # 2. J.B. Justo y Jorge Newbery
            (-38.0642, -57.5985), # 3. Cerrito y Jorge Newbery
            (-38.0535, -57.5721), # 4. Cerrito y Acha
        ]
    }
]

# Crear el mapa (Usamos 'OpenStreetMap' que es más estable si falla CartoDB)
m = folium.Map(location=[-38.0200, -57.5600], zoom_start=13)

# Dibujar las zonas
for zona in ZONAS_LOPEZ:
    folium.Polygon(
        locations=zona["coords"],
        color="green",
        fill=True,
        fill_color="green",
        fill_opacity=0.4,
        weight=3,
        popup=zona["nombre"]
    ).add_to(m)

folium_static(m, width=1100, height=700)
