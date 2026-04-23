import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd

# Configuración de la página
st.set_page_config(layout="wide", page_title="Mapa de Inspectores - Mar del Plata")

st.title("📍 Distribución de Zonas de Inspectores - Mar del Plata")

# --- BASE DE DATOS DE ZONAS (Aquí debes ajustar las coordenadas y límites) ---
# Nota: Las coordenadas son ejemplos ilustrativos. Debes buscar los puntos en Google Maps.
ZONAS_DATA = {
    "LOPEZ, MARTIN LEONARDO": {
        "color": "#FF5733", # Naranja
        "limites": "Av. Colón, Av. Independencia, Av. Juan B. Justo, La Costa",
        "indicaciones": "Calle Colón (Vereda Impar), Santiago del Estero (Vereda Impar).",
        "calles_internas": "San Luis, Mitre, Hipólito Yrigoyen, entre otras.",
        "coordenadas": [
            [-38.005, -57.545], [-38.005, -57.560], 
            [-38.020, -57.560], [-38.020, -57.545]
        ]
    },
    "GARCIA, JUAN PAULO": {
        "color": "#33FF57", # Verde
        "limites": "J.B. Justo, Av. Vértiz, Av. Edison, Av. Antártida Argentina",
        "indicaciones": "Comparte J.B. Justo (Vereda Par) con Lopez.",
        "calles_internas": "Cerrito, Acha, Juramento, Magallanes.",
        "coordenadas": [
            [-38.025, -57.565], [-38.025, -57.585], 
            [-38.040, -57.585], [-38.040, -57.565]
        ]
    },
    "CARBAYO, VICTOR HUGO": {
        "color": "#3357FF", # Azul
        "limites": "Av. Juan B. Justo, Av. Independencia, Av. Paso, Av. Jara",
        "indicaciones": "Toma vereda par en Av. Independencia.",
        "calles_internas": "Matheu, Formosa, Quintana, Saavedra.",
        "coordenadas": [
            [-38.015, -57.570], [-38.015, -57.590], 
            [-38.030, -57.590], [-38.030, -57.570]
        ]
    },
    "RODRIGUEZ, MAXIMILIANO": {
        "color": "#F333FF", # Rosa/Púrpura
        "limites": "Charlone, 20 de Septiembre, Av. Colón, Bv. Maritimo",
        "indicaciones": "Zona céntrica y comercial.",
        "calles_internas": "Félix U. Camet, Catamarca, La Rioja.",
        "coordenadas": [
            [-37.990, -57.540], [-37.990, -57.555], 
            [-38.000, -57.555], [-38.000, -57.540]
        ]
    }
}

# --- SECCIÓN SUPERIOR: INFORMACIÓN DETALLADA ---
st.markdown("### 📋 Listado de Responsabilidades y Límites")

# Mostramos la info en columnas o expansores para que sea ordenado
cols = st.columns(len(ZONAS_DATA))

for i, (nombre, data) in enumerate(ZONAS_DATA.items()):
    with st.expander(f"👤 {nombre}"):
        st.markdown(f"**Límites:** {data['limites']}")
        st.markdown(f"**Indicaciones Especiales:** {data['indicaciones']}")
        st.markdown(f"**Calles principales internas:** {data['calles_internas']}")
        st.write(f"Color en mapa: 🟦" if data['color'] == "#3357FF" else "🟧") # Representación visual simple

# --- SECCIÓN DEL MAPA ---
st.markdown("---")
st.subheader("🗺️ Visualización Espacial")

# Crear el mapa base centrado en Mar del Plata
m = folium.Map(location=[-38.005, -57.555], zoom_start=13, tiles="OpenStreetMap")

# Dibujar cada zona
for nombre, data in ZONAS_DATA.items():
    # Creamos el polígono
    folium.Polygon(
        locations=data['coordenadas'],
        color=data['color'],
        fill=True,
        fill_color=data['color'],
        fill_opacity=0.4,
        weight=2,
        popup=folium.Popup(f"<b>Inspector:</b> {nombre}<br><b>Límites:</b> {data['limites']}", max_width=300),
        tooltip=nombre
    ).add_to(m)

# Mostrar el mapa en Streamlit
folium_static(m, width=1000, height=600)

st.info("💡 Haz clic en cada zona coloreada para ver más detalles del inspector.")
