import streamlit as st
import folium
from streamlit_folium import folium_static

# Configuración de la página
st.set_page_config(layout="wide", page_title="Zonas Inspector López")

st.title("Jurisdicción: LOPEZ, MARTÍN LEONARDO (Leg. 9983)")
st.write("Mapa corregido según relevamiento gráfico (Fotos del mapa manual).")

# Diccionario exclusivo para López con los cierres de polígono correctos
ZONAS_LOPEZ = [
    {
        "nombre": "Zona 1: Sector Centro (Plaza Mitre / La Perla)",
        "descripcion": "Límite: San Luis, Colón (2100-2600), Santiago del Estero y Diag. Alberdi.",
        "coords": [
            (-37.9961, -57.5492), # San Luis y 11 de Septiembre
            (-38.0063, -57.5518), # San Luis y Av. Colón (Vereda Par)
            (-38.0062, -57.5507), # Santiago del Estero y Av. Colón (Vereda Impar)
            (-37.9995, -57.5475)  # Santiago del Estero y Diag. Alberdi Sur
        ]
    },
    {
        "nombre": "Zona 2: Sector Noroeste (Bronzini / Colón Alta)",
        "descripcion": "Triángulo entre Av. Colón (5800-2200) y Teodoro Bronzini (Vereda Impar).",
        "coords": [
            (-38.0069, -57.5755), # Av. Colón y T. Bronzini (Inicio)
            (-38.0076, -57.5912), # Av. Colón y Champagnat / Ruta 226
            (-38.0381, -57.5841)  # T. Bronzini y Av. Juan B. Justo (Cierre)
        ]
    },
    {
        "nombre": "Zona 3: Sector Sur (J.B. Justo / Puerto / Nuevo Golf)",
        "descripcion": "Límites: J.B. Justo, Acha, Cerrito y Av. Jorge Newbery (Ambas manos).",
        "coords": [
            (-38.0338, -57.5562), # J.B. Justo y Acha
            (-38.0535, -57.5721), # Cerrito y Acha
            (-38.0642, -57.5985), # Cerrito y Jorge Newbery
            (-38.0415, -57.5812)  # J.B. Justo y Jorge Newbery
        ]
    }
]

# Crear el mapa centrado en el punto medio de sus zonas
m = folium.Map(location=[-38.0200, -57.5600], zoom_start=13, tiles='CartoDB positron')

# Dibujar las 3 zonas de López
for zona in ZONAS_LOPEZ:
    folium.Polygon(
        locations=zona["coords"],
        color="#00FF00",      # Color Verde
        fill=True,
        fill_color="#00FF00",
        fill_opacity=0.4,     # Transparencia para ver las calles
        weight=2,
        popup=f"<b>{zona['nombre']}</b><br>{zona['descripcion']}",
        tooltip=zona["nombre"]
    ).add_to(m)

# Mostrar el mapa en la app de Streamlit
folium_static(m, width=1100, height=700)

# Tabla resumen debajo del mapa
st.subheader("Detalle de Cobertura")
st.table(ZONAS_LOPEZ)
