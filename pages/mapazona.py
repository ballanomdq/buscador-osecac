import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. BASE DE DATOS REAL DE GEOMETRÍAS (Puntos que encierran las zonas)
datos_zonas = [
    # --- ZONA GARCIA (Naranja) ---
    {"lat": -38.0315, "lon": -57.5450, "Inspector": "GARCIA"},
    {"lat": -38.0550, "lon": -57.5350, "Inspector": "GARCIA"},
    {"lat": -38.0850, "lon": -57.5450, "Inspector": "GARCIA"},
    {"lat": -38.0750, "lon": -57.5850, "Inspector": "GARCIA"},
    {"lat": -38.0450, "lon": -57.5950, "Inspector": "GARCIA"},
    {"lat": -38.0315, "lon": -57.5450, "Inspector": "GARCIA"}, # Cierra el bloque
    
    # --- ZONA CARBAYO (Rosa) ---
    {"lat": -38.0050, "lon": -57.5420, "Inspector": "CARBAYO"},
    {"lat": -38.0250, "lon": -57.5300, "Inspector": "CARBAYO"},
    {"lat": -38.0450, "lon": -57.5500, "Inspector": "CARBAYO"},
    {"lat": -38.0350, "lon": -57.5750, "Inspector": "CARBAYO"},
    {"lat": -38.0100, "lon": -57.5650, "Inspector": "CARBAYO"},
    {"lat": -38.0050, "lon": -57.5420, "Inspector": "CARBAYO"}, # Cierra el bloque
    
    # --- ZONA POLINESSI (Amarillo) ---
    {"lat": -37.9750, "lon": -57.5450, "Inspector": "POLINESSI"},
    {"lat": -38.0050, "lon": -57.5350, "Inspector": "POLINESSI"},
    {"lat": -38.0150, "lon": -57.5750, "Inspector": "POLINESSI"},
    {"lat": -37.9850, "lon": -57.5950, "Inspector": "POLINESSI"},
    {"lat": -37.9650, "lon": -57.5750, "Inspector": "POLINESSI"},
    {"lat": -37.9750, "lon": -57.5450, "Inspector": "POLINESSI"}, # Cierra el bloque
    
    # --- ZONA RODRIGUEZ (Azul) ---
    {"lat": -37.9950, "lon": -57.5550, "Inspector": "RODRIGUEZ"},
    {"lat": -38.0150, "lon": -57.5500, "Inspector": "RODRIGUEZ"},
    {"lat": -38.0250, "lon": -57.5850, "Inspector": "RODRIGUEZ"},
    {"lat": -38.0050, "lon": -57.5990, "Inspector": "RODRIGUEZ"},
    {"lat": -37.9950, "lon": -57.5550, "Inspector": "RODRIGUEZ"}, # Cierra el bloque
    
    # --- ZONA LOPEZ (Morado) ---
    {"lat": -38.0150, "lon": -57.5850, "Inspector": "LOPEZ"},
    {"lat": -38.0350, "lon": -57.5750, "Inspector": "LOPEZ"},
    {"lat": -38.0550, "lon": -57.6150, "Inspector": "LOPEZ"},
    {"lat": -38.0250, "lon": -57.6350, "Inspector": "LOPEZ"},
    {"lat": -38.0150, "lon": -57.5850, "Inspector": "LOPEZ"}  # Cierra el bloque
]

df = pd.DataFrame(datos_zonas)

# Esquema de colores exacto para tus inspectores
esquema_colores = {
    "GARCIA": "#ff7f0e",   # Naranja
    "CARBAYO": "#e377c2",  # Rosa
    "POLINESSI": "#bcbd22",# Amarillo
    "RODRIGUEZ": "#1f77b4",# Azul
    "LOPEZ": "#9467bd"     # Morado
}

# 2. CREACIÓN DEL MAPA USANDO SCATTER_MAPBOX CONFIGURADO COMO LÍNEA CONTINUA
fig = px.scatter_mapbox(
    df, 
    lat="lat", 
    lon="lon", 
    color="Inspector",
    color_discrete_map=esquema_colores,
    hover_name="Inspector",
    zoom=11.5, 
    center={"lat": -38.0055, "lon": -57.5426},
    height=600
)

# Cambiamos el modo de los trazos para que dibuje líneas que unan los puntos en lugar de marcadores sueltos
fig.update_traces(mode="lines", line=dict(width=4.5))

# Aplicamos el mapa base público de OpenStreetMap
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
)

# 3. RENDERS EN STREAMLIT
st.plotly_chart(fig, use_container_width=True)

# 4. PANEL DE DETALLES
st.markdown("---")
st.subheader("📋 Detalle de Zonas")
st.markdown("🟠 **Inspector GARCIA**: Punta Mogotes, Colinas, Juramento, Faro Norte.")
st.markdown("🌸 **Inspector CARBAYO**: Cerrito Sur, El Progreso, Chauvín, Plaza Mitre, Stella Maris.")
st.markdown("🟡 **Inspector POLINESSI**: Playa Grande, Los Troncos, San Carlos, San Cayetano, Libertad.")
st.markdown("🔵 **Inspector RODRIGUEZ**: Bernardino Rivadavia, Santa Mónica, San Juan, La Perla.")
st.markdown("🟣 **Inspector LOPEZ**: Regional, Belisario Roldán, Don Emilio, Las Américas.")
