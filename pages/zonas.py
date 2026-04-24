import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide", page_title="Mapa de Inspectores")

# Sidebar para filtrar
st.sidebar.header("Filtros de Búsqueda")
inspector_seleccionado = st.sidebar.multiselect(
    "Seleccionar Inspector/es:",
    options=["RODRIGUEZ", "GARCIA", "CARBAYO", "LOPEZ", "POLINESSI"],
    default=["RODRIGUEZ", "GARCIA", "CARBAYO", "LOPEZ", "POLINESSI"]
)

st.title("Mapa Interactivo de Jurisdicciones")
st.write("Usa el menú lateral para filtrar y evitar la superposición de zonas.")

# Diccionario de Datos (Mantenemos tus coordenadas ordenadas)
ZONAS_DATA = {
    "RODRIGUEZ": {
        "color": "#FF0000", # Rojo
        "zonas": [
            {"nombre": "Güemes / J.B. Justo", "coords": [(-38.0076, -57.5451), (-38.0315, -57.5471), (-38.0298, -57.5482), (-38.0055, -57.5458)]},
            {"nombre": "La Perla / Catamarca", "coords": [(-38.0062, -57.5532), (-37.9942, -57.5455), (-37.9855, -57.5531), (-38.0074, -57.5684)]},
            {"nombre": "San Juan / Bronzini", "coords": [(-38.0065, -57.5552), (-38.0069, -57.5755), (-38.0171, -57.5772), (-38.0165, -57.5568)]}
        ]
    },
    "GARCIA": {
        "color": "#FFA500", # Naranja
        "zonas": [
            {"nombre": "Costa / Colón", "coords": [(-38.0044, -57.5428), (-38.0019, -57.5412), (-38.0064, -57.5542), (-38.0063, -57.5518)]},
            {"nombre": "J.B. Justo / Peralta Ramos", "coords": [(-38.0211, -57.5768), (-38.0163, -57.5956), (-38.0255, -57.6012), (-38.0312, -57.5815)]},
            {"nombre": "Microcentro / San Juan", "coords": [(-38.0066, -57.5562), (-38.0065, -57.5552), (-38.0214, -57.5622), (-38.0215, -57.5638)]}
        ]
    },
    "CARBAYO": {
        "color": "#E5E500", # Amarillo oscuro para que se vea
        "zonas": [
            {"nombre": "Costa Triangular", "coords": [(-38.0044, -57.5428), (-38.0031, -57.5405), (-38.0063, -57.5518)]},
            {"nombre": "Microcentro Independencia", "coords": [(-38.0066, -57.5562), (-38.0055, -57.5458), (-38.0298, -57.5482), (-38.0215, -57.5638)]}
        ]
    },
    "LOPEZ": {
        "color": "#008000", # Verde
        "zonas": [
            {"nombre": "Plaza Mitre", "coords": [(-38.0063, -57.5518), (-38.0062, -57.5507), (-38.0093, -57.5511), (-38.0094, -57.5522)]},
            {"nombre": "Noroeste Bronzini", "coords": [(-38.0069, -57.5755), (-38.0067, -57.6081), (-38.0335, -57.6152), (-38.0381, -57.5841)]}
        ]
    },
    "POLINESSI": {
        "color": "#0000FF", # Azul
        "zonas": [
            {"nombre": "Champagnat", "coords": [(-38.0075, -57.5862), (-38.0076, -57.5912), (-37.9868, -57.5772)]},
            {"nombre": "Microcentro Catamarca", "coords": [(-37.9942, -57.5455), (-37.9949, -57.5478), (-38.0031, -57.5471), (-38.0019, -57.5412)]}
        ]
    }
}

m = folium.Map(location=[-38.0060, -57.5550], zoom_start=13, tiles='CartoDB positron')

# Solo dibujar lo seleccionado en la barra lateral
for insp in inspector_seleccionado:
    info = ZONAS_DATA[insp]
    for zona in info["zonas"]:
        folium.Polygon(
            locations=zona["coords"],
            color=info["color"],
            fill=True,
            fill_opacity=0.3, # Menos opacidad ayuda a ver la superposición si existe
            weight=3,
            popup=f"Inspector: {insp} - {zona['nombre']}"
        ).add_to(m)

folium_static(m, width=1000, height=600)
