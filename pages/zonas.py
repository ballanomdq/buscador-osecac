import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide", page_title="Mapa de Inspectores - MDP")

st.title("Mapa de Jurisdicciones de Inspectores Municipales")
st.write("Visualización basada en el mapa oficial de cuadrantes. Haz clic en las zonas para ver detalles.")

# Definición de Colores y Datos según tu foto
INSPECTORES = {
    "RODRIGUEZ": {"color": "#FF0000", "legajo": "7713"},  # Rojo
    "GARCIA": {"color": "#FFA500", "legajo": "7852"},     # Naranja
    "CARBAYO": {"color": "#FFFF00", "legajo": "9220"},    # Amarillo
    "LOPEZ": {"color": "#00FF00", "legajo": "9983"},      # Verde
    "POLINESSI": {"color": "#0000FF", "legajo": "9513"}   # Azul
}

# Coordenadas procesadas de la foto (Cierre de polígonos exacto)
ZONAS = [
    # RODRIGUEZ (Rojo)
    {"insp": "RODRIGUEZ", "nombre": "Güemes / J.B. Justo", "coords": [(-38.0076, -57.5451), (-38.0315, -57.5471), (-38.0298, -57.5482), (-38.0055, -57.5458)]},
    {"insp": "RODRIGUEZ", "nombre": "La Perla / Catamarca", "coords": [(-38.0062, -57.5532), (-37.9942, -57.5455), (-37.9855, -57.5531), (-38.0074, -57.5684)]},
    
    # GARCIA (Naranja)
    {"insp": "GARCIA", "nombre": "Microcentro / San Juan", "coords": [(-38.0066, -57.5562), (-38.0065, -57.5552), (-38.0214, -57.5622), (-38.0215, -57.5638)]},
    {"insp": "GARCIA", "nombre": "Sur / Alfar", "coords": [(-38.0338, -57.5342), (-38.0955, -57.5612), (-38.1155, -57.5912), (-38.0415, -57.5812)]},

    # CARBAYO (Amarillo)
    {"insp": "CARBAYO", "nombre": "Microcentro Independencia", "coords": [(-38.0066, -57.5562), (-38.0055, -57.5458), (-38.0298, -57.5482), (-38.0215, -57.5638)]},
    {"insp": "CARBAYO", "nombre": "Costa Triangular", "coords": [(-38.0044, -57.5428), (-38.0031, -57.5405), (-38.0063, -57.5518)]},

    # LOPEZ (Verde - Corregido por fotos)
    {"insp": "LOPEZ", "nombre": "Centro / Plaza Mitre", "coords": [(-37.9961, -57.5492), (-37.9995, -57.5475), (-38.0062, -57.5507), (-38.0063, -57.5518)]},
    {"insp": "LOPEZ", "nombre": "Noroeste / Bronzini", "coords": [(-38.0069, -57.5755), (-38.0067, -57.6081), (-38.0335, -57.6152), (-38.0381, -57.5841)]},
    {"insp": "LOPEZ", "nombre": "Sur / Puerto / Golf", "coords": [(-38.0338, -57.5562), (-38.0535, -57.5721), (-38.0642, -57.5985), (-38.0415, -57.5812)]},

    # POLINESSI (Azul)
    {"insp": "POLINESSI", "nombre": "Franja Catamarca", "coords": [(-37.9942, -57.5455), (-37.9949, -57.5478), (-38.0031, -57.5471), (-38.0019, -57.5412)]},
    {"insp": "POLINESSI", "nombre": "Puerto / Reserva", "coords": [(-38.0315, -57.5471), (-38.0076, -57.5451), (-38.0338, -57.5342), (-38.0268, -57.5312)]}
]

# Mapa base con CartoDB Positron (es el más nítido para leer nombres de calles)
m = folium.Map(location=[-38.0100, -57.5600], zoom_start=13, tiles='CartoDB positron')

# Dibujar todas las zonas con transparencia
for z in ZONAS:
    inspector = z["insp"]
    folium.Polygon(
        locations=z["coords"],
        color=INSPECTORES[inspector]["color"],
        fill=True,
        fill_color=INSPECTORES[inspector]["color"],
        fill_opacity=0.35, # Transparencia justa para leer calles
        weight=2,
        popup=f"<b>Inspector:</b> {inspector}<br><b>Legajo:</b> {INSPECTORES[inspector]['legajo']}<br><b>Zona:</b> {z['nombre']}",
        tooltip=f"{inspector}: {z['nombre']}"
    ).add_to(m)

# Leyenda en el Sidebar para que sea profesional
st.sidebar.title("Referencia de Colores")
for nombre, info in INSPECTORES.items():
    st.sidebar.markdown(f'<p style="color:{info["color"]}; font-weight:bold;">■ {nombre} (Leg. {info["legajo"]})</p>', unsafe_allow_html=True)

# Renderizar mapa
folium_static(m, width=1100, height=750)
