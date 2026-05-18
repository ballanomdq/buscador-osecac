import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. GENERAMOS LOS PUNTOS DE LAS ZONAS EN UNA LISTA PLANA PARA EL MAPA NATIVO
# Ponemos las coordenadas que me pasaste organizadas por Inspector y Color
datos_mapa = [
    # --- ZONA GARCIA (Rojo/Naranja) ---
    {"lat": -38.0315, "lon": -57.5450, "Inspector": "GARCIA", "Color": "#ff7f0e"},
    {"lat": -38.0550, "lon": -57.5350, "Inspector": "GARCIA", "Color": "#ff7f0e"},
    {"lat": -38.0850, "lon": -57.5450, "Inspector": "GARCIA", "Color": "#ff7f0e"},
    {"lat": -38.0750, "lon": -57.5850, "Inspector": "GARCIA", "Color": "#ff7f0e"},
    {"lat": -38.0450, "lon": -57.5950, "Inspector": "GARCIA", "Color": "#ff7f0e"},
    
    # --- ZONA CARBAYO (Rosa) ---
    {"lat": -38.0050, "lon": -57.5420, "Inspector": "CARBAYO", "Color": "#e377c2"},
    {"lat": -38.0250, "lon": -57.5300, "Inspector": "CARBAYO", "Color": "#e377c2"},
    {"lat": -38.0450, "lon": -57.5500, "Inspector": "CARBAYO", "Color": "#e377c2"},
    {"lat": -38.0350, "lon": -57.5750, "Inspector": "CARBAYO", "Color": "#e377c2"},
    {"lat": -38.0100, "lon": -57.5650, "Inspector": "CARBAYO", "Color": "#e377c2"},
    
    # --- ZONA POLINESSI (Amarillo) ---
    {"lat": -37.9750, "lon": -57.5450, "Inspector": "POLINESSI", "Color": "#bcbd22"},
    {"lat": -38.0050, "lon": -57.5350, "Inspector": "POLINESSI", "Color": "#bcbd22"},
    {"lat": -38.0150, "lon": -57.5750, "Inspector": "POLINESSI", "Color": "#bcbd22"},
    {"lat": -37.9850, "lon": -57.5950, "Inspector": "POLINESSI", "Color": "#bcbd22"},
    {"lat": -37.9650, "lon": -57.5750, "Inspector": "POLINESSI", "Color": "#bcbd22"},
    
    # --- ZONA RODRIGUEZ (Azul) ---
    {"lat": -37.9950, "lon": -57.5550, "Inspector": "RODRIGUEZ", "Color": "#1f77b4"},
    {"lat": -38.0150, "lon": -57.5500, "Inspector": "RODRIGUEZ", "Color": "#1f77b4"},
    {"lat": -38.0250, "lon": -57.5850, "Inspector": "RODRIGUEZ", "Color": "#1f77b4"},
    {"lat": -38.0050, "lon": -57.5990, "Inspector": "RODRIGUEZ", "Color": "#1f77b4"},
    
    # --- ZONA LOPEZ (Morado) ---
    {"lat": -38.0150, "lon": -57.5850, "Inspector": "LOPEZ", "Color": "#9467bd"},
    {"lat": -38.0350, "lon": -57.5750, "Inspector": "LOPEZ", "Color": "#9467bd"},
    {"lat": -38.0550, "lon": -57.6150, "Inspector": "LOPEZ", "Color": "#9467bd"},
    {"lat": -38.0250, "lon": -57.6350, "Inspector": "LOPEZ", "Color": "#9467bd"}
]

# Convertimos la lista de datos a un DataFrame de Pandas (que ya lo tenés funcionando)
df = pd.DataFrame(datos_mapa)

# 2. DIBUJAMOS EL MAPA USANDO EL COMPONENTE SEGURO Y NATIVO DE STREAMLIT
# Este componente usa las librerías base de Streamlit y no requiere configuraciones externas
st.map(df, latitude="lat", longitude="lon", color="Color", size=200)

# 3. PANEL DE INFORMACIÓN COMPLEMENTARIO
st.markdown("---")
st.subheader("📋 Detalle de Zonas")
st.markdown("🟠 **Inspector GARCIA**: Punta Mogotes, Colinas, Juramento, Faro Norte.")
st.markdown("🌸 **Inspector CARBAYO**: Cerrito Sur, El Progreso, Chauvín, Plaza Mitre, Stella Maris.")
st.markdown("🟡 **Inspector POLINESSI**: Playa Grande, Los Troncos, San Carlos, San Cayetano, Libertad.")
st.markdown("🔵 **Inspector RODRIGUEZ**: Bernardino Rivadavia, Santa Mónica, San Juan, La Perla.")
st.markdown("🟣 **Inspector LOPEZ**: Regional, Belisario Roldán, Don Emilio, Las Américas.")
