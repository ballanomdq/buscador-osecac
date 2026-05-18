import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. COORDENADAS OFICIALES ALINEADAS A LAS AVENIDAS (Sin cruzar manzanas al medio)
datos_zonas = [
    # --- ZONA POLINESSI (Norte: Desde Constitución hasta Luro/Costa) ---
    {"lat": -37.9750, "lon": -57.5400, "Inspector": "POLINESSI"}, # Constitución y la Costa
    {"lat": -37.9850, "lon": -57.5800, "Inspector": "POLINESSI"}, # Constitución y Champagnat
    {"lat": -38.0000, "lon": -57.5700, "Inspector": "POLINESSI"}, # Luro y Champagnat
    {"lat": -37.9930, "lon": -57.5420, "Inspector": "POLINESSI"}, # Luro y la Costa
    {"lat": -37.9750, "lon": -57.5400, "Inspector": "POLINESSI"}, # Cierre Norte
    
    # --- ZONA RODRIGUEZ (Centro-Norte: Cuadrante Independencia / Colón / Luro) ---
    {"lat": -37.9930, "lon": -57.5420, "Inspector": "RODRIGUEZ"}, # Luro y la Costa
    {"lat": -38.0000, "lon": -57.5700, "Inspector": "RODRIGUEZ"}, # Luro y Champagnat
    {"lat": -38.0120, "lon": -57.5650, "Inspector": "RODRIGUEZ"}, # Colón y Champagnat
    {"lat": -38.0050, "lon": -57.5380, "Inspector": "RODRIGUEZ"}, # Colón y la Costa
    {"lat": -37.9930, "lon": -57.5420, "Inspector": "RODRIGUEZ"}, # Cierre
    
    # --- ZONA CARBAYO (Centro-Sur: Desde Colón hasta Juan B. Justo) ---
    {"lat": -38.0050, "lon": -57.5380, "Inspector": "CARBAYO"}, # Colón y la Costa
    {"lat": -38.0120, "lon": -57.5650, "Inspector": "CARBAYO"}, # Colón y Champagnat
    {"lat": -38.0300, "lon": -57.5600, "Inspector": "CARBAYO"}, # Juan B. Justo y Champagnat
    {"lat": -38.0250, "lon": -57.5300, "Inspector": "CARBAYO"}, # Juan B. Justo y la Costa
    {"lat": -38.0050, "lon": -57.5380, "Inspector": "CARBAYO"}, # Cierre
    
    # --- ZONA LOPEZ (Oeste Periférico: Paralelo externo a Champagnat / Ruta 88) ---
    {"lat": -37.9850, "lon": -57.5800, "Inspector": "LOPEZ"}, # Constitución y Champagnat
    {"lat": -38.0300, "lon": -57.5600, "Inspector": "LOPEZ"}, # Juan B. Justo y Champagnat
    {"lat": -38.0400, "lon": -57.6100, "Inspector": "LOPEZ"}, # Av. Perón (Ruta 88) Oeste
    {"lat": -38.0000, "lon": -57.6200, "Inspector": "LOPEZ"}, # Luro Oeste Periferia
    {"lat": -37.9850, "lon": -57.5800, "Inspector": "LOPEZ"}, # Cierre
    
    # --- ZONA GARCIA (Sur Completo: De Juan B. Justo hacia el Puerto y Mario Bravo) ---
    {"lat": -38.0250, "lon": -57.5300, "Inspector": "GARCIA"}, # Juan B. Justo y la Costa
    {"lat": -38.0300, "lon": -57.5600, "Inspector": "GARCIA"}, # Juan B. Justo y Champagnat
    {"lat": -38.0550, "lon": -57.5800, "Inspector": "GARCIA"}, # Mario Bravo y Edison
    {"lat": -38.0700, "lon": -57.5450, "Inspector": "GARCIA"}, # Faro / Ruta 11 Sur
    {"lat": -38.0250, "lon": -57.5300, "Inspector": "GARCIA"}  # Cierre
]

df = pd.DataFrame(datos_zonas)

esquema_colores = {
    "GARCIA": "#ff7f0e",   # Naranja
    "CARBAYO": "#e377c2",  # Rosa
    "POLINESSI": "#bcbd22",# Amarillo
    "RODRIGUEZ": "#1f77b4",# Azul
    "LOPEZ": "#9467bd"     # Morado
}

# 2. CONSTRUCCIÓN CON MOTOR MAPBOX (Trazado continuo perimetral)
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

# Cambiamos el comportamiento visual para trazar bordes gruesos paralelos que delimitan los sectores
fig.update_traces(mode="lines", line=dict(width=5.5))

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
)

# 3. RENDER FINAL DIRECTO (Sin descargas externas que causen errores)
st.plotly_chart(fig, use_container_width=True)

# 4. CUADRO DE REFERENCIAS
st.markdown("---")
st.subheader("📋 Detalle de Zonas")
st.markdown("🟠 **Inspector GARCIA**: Puerto, Punta Mogotes, Colinas, Faro Norte (Eje Av. Juan B. Justo al Sur).")
st.markdown("🌸 **Inspector CARBAYO**: Cerrito Sur, El Progreso, Chauvín, Plaza Mitre, Stella Maris (Entre Colón y Juan B. Justo).")
st.markdown("🟡 **Inspector POLINESSI**: Playa Grande, Los Troncos, San Carlos, San Cayetano, Libertad (Eje Constitución a Luro).")
st.markdown("🔵 **Inspector RODRIGUEZ**: Bernardino Rivadavia, Santa Mónica, San Juan, La Perla (Eje Luro a Colón).")
st.markdown("🟣 **Inspector LOPEZ**: Cordón Periférico Oeste, Regional, Belisario Roldán, Don Emilio (Eje Oeste Champagnat).")
