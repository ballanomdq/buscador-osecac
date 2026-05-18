import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. BASE DE DATOS REAL DE GEOMETRÍAS (Cerrando los polígonos por inspector)
datos_zonas = [
    # --- ZONA GARCIA (Naranja) ---
    {"lat": -38.0315, "lon": -57.5450, "Inspector": "GARCIA", "Color": "Naranja"},
    {"lat": -38.0550, "lon": -57.5350, "Inspector": "GARCIA", "Color": "Naranja"},
    {"lat": -38.0850, "lon": -57.5450, "Inspector": "GARCIA", "Color": "Naranja"},
    {"lat": -38.0750, "lon": -57.5850, "Inspector": "GARCIA", "Color": "Naranja"},
    {"lat": -38.0450, "lon": -57.5950, "Inspector": "GARCIA", "Color": "Naranja"},
    {"lat": -38.0315, "lon": -57.5450, "Inspector": "GARCIA", "Color": "Naranja"}, # Cierra el polígono
    
    # --- ZONA CARBAYO (Rosa) ---
    {"lat": -38.0050, "lon": -57.5420, "Inspector": "CARBAYO", "Color": "Rosa"},
    {"lat": -38.0250, "lon": -57.5300, "Inspector": "CARBAYO", "Color": "Rosa"},
    {"lat": -38.0450, "lon": -57.5500, "Inspector": "CARBAYO", "Color": "Rosa"},
    {"lat": -38.0350, "lon": -57.5750, "Inspector": "CARBAYO", "Color": "Rosa"},
    {"lat": -38.0100, "lon": -57.5650, "Inspector": "CARBAYO", "Color": "Rosa"},
    {"lat": -38.0050, "lon": -57.5420, "Inspector": "CARBAYO", "Color": "Rosa"}, # Cierra el polígono
    
    # --- ZONA POLINESSI (Amarillo) ---
    {"lat": -37.9750, "lon": -57.5450, "Inspector": "POLINESSI", "Color": "Amarillo"},
    {"lat": -38.0050, "lon": -57.5350, "Inspector": "POLINESSI", "Color": "Amarillo"},
    {"lat": -38.0150, "lon": -57.5750, "Inspector": "POLINESSI", "Color": "Amarillo"},
    {"lat": -37.9850, "lon": -57.5950, "Inspector": "POLINESSI", "Color": "Amarillo"},
    {"lat": -37.9650, "lon": -57.5750, "Inspector": "POLINESSI", "Color": "Amarillo"},
    {"lat": -37.9750, "lon": -57.5450, "Inspector": "POLINESSI", "Color": "Amarillo"}, # Cierra el polígono
    
    # --- ZONA RODRIGUEZ (Azul) ---
    {"lat": -37.9950, "lon": -57.5550, "Inspector": "RODRIGUEZ", "Color": "Azul"},
    {"lat": -38.0150, "lon": -57.5500, "Inspector": "RODRIGUEZ", "Color": "Azul"},
    {"lat": -38.0250, "lon": -57.5850, "Inspector": "RODRIGUEZ", "Color": "Azul"},
    {"lat": -38.0050, "lon": -57.5990, "Inspector": "RODRIGUEZ", "Color": "Azul"},
    {"lat": -37.9950, "lon": -57.5550, "Inspector": "RODRIGUEZ", "Color": "Azul"}, # Cierra el polígono
    
    # --- ZONA LOPEZ (Morado) ---
    {"lat": -38.0150, "lon": -57.5850, "Inspector": "LOPEZ", "Color": "Morado"},
    {"lat": -38.0350, "lon": -57.5750, "Inspector": "LOPEZ", "Color": "Morado"},
    {"lat": -38.0550, "lon": -57.6150, "Inspector": "LOPEZ", "Color": "Morado"},
    {"lat": -38.0250, "lon": -57.6350, "Inspector": "LOPEZ", "Color": "Morado"},
    {"lat": -38.0150, "lon": -57.5850, "Inspector": "LOPEZ", "Color": "Morado"}  # Cierra el polígono
]

df = pd.DataFrame(datos_zonas)

# Mapas de colores reales para Plotly
esquema_colores = {
    "GARCIA": "#ff7f0e",
    "CARBAYO": "#e377c2",
    "POLINESSI": "#bcbd22",
    "RODRIGUEZ": "#1f77b4",
    "LOPEZ": "#9467bd"
}

# 2. CREACIÓN DEL MAPA CON MAPBOX COMPUESTO (Dibuja áreas uniendo los puntos)
fig = px.line_mapbox(
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

# Truco geográfico: Actualizamos el trazo para que rellene el interior de los puntos con color transparente
fig.update_traces(fill="toself", fillopacity=0.35, line=dict(width=3))

# Usamos un estilo de mapa limpio basado en OpenStreetMap estándar que no requiere Tokens de Mapbox
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
)

# 3. RENDERIZAMOS EN STREAMLIT
st.plotly_chart(fig, use_container_width=True)

# 4. PANEL DE DETALLES
st.markdown("---")
st.subheader("📋 Detalle de Zonas")
st.markdown("🟠 **Inspector GARCIA**: Punta Mogotes, Colinas, Juramento, Faro Norte.")
st.markdown("🌸 **Inspector CARBAYO**: Cerrito Sur, El Progreso, Chauvín, Plaza Mitre, Stella Maris.")
st.markdown("🟡 **Inspector POLINESSI**: Playa Grande, Los Troncos, San Carlos, San Cayetano, Libertad.")
st.markdown("🔵 **Inspector RODRIGUEZ**: Bernardino Rivadavia, Santa Mónica, San Juan, La Perla.")
st.markdown("🟣 **Inspector LOPEZ**: Regional, Belisario Roldán, Don Emilio, Las Américas.")
