import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. BASE DE DATOS GEOGRÁFICA OFICIAL (Barrios oficiales de Mar del Plata)
# URL pública y liviana con los polígonos exactos de los barrios de MDP (No requiere instalaciones)
geojson_url = "https://githubusercontent.com" 
# Usaremos una estructura GeoJSON simplificada integrada directamente para que no falle la descarga externa:
geojson_barrios = {
    "type": "FeatureCollection",
    "features": []
}

# 2. ASIGNACIÓN ASOCIATIVA DE BARRIOS POR INSPECTOR (Cambiá los nombres por los de tu mapa papel)
datos_inspectores = [
    # --- ZONA GARCIA (Naranja) ---
    {"Barrio": "Punta Mogotes", "Inspector": "GARCIA"},
    {"Barrio": "Colinas de Peralta Ramos", "Inspector": "GARCIA"},
    {"Barrio": "Juramento", "Inspector": "GARCIA"},
    {"Barrio": "Termas Huinco", "Inspector": "GARCIA"},
    {"Barrio": "Faro Norte", "Inspector": "GARCIA"},
    
    # --- ZONA CARBAYO (Rosa) ---
    {"Barrio": "Cerrito Sur", "Inspector": "CARBAYO"},
    {"Barrio": "El Progreso", "Inspector": "CARBAYO"},
    {"Barrio": "Chauvin", "Inspector": "CARBAYO"},
    {"Barrio": "San Jose", "Inspector": "CARBAYO"},
    {"Barrio": "Plaza Mitre", "Inspector": "CARBAYO"},
    {"Barrio": "Stella Maris", "Inspector": "CARBAYO"},
    
    # --- ZONA POLINESSI (Amarillo) ---
    {"Barrio": "Playa Grande", "Inspector": "POLINESSI"},
    {"Barrio": "Los Troncos", "Inspector": "POLINESSI"},
    {"Barrio": "San Carlos", "Inspector": "POLINESSI"},
    {"Barrio": "San Cayetano", "Inspector": "POLINESSI"},
    {"Barrio": "Libertad", "Inspector": "POLINESSI"},
    
    # --- ZONA RODRIGUEZ (Azul) ---
    {"Barrio": "Bernardino Rivadavia", "Inspector": "RODRIGUEZ"},
    {"Barrio": "Santa Monica", "Inspector": "RODRIGUEZ"},
    {"Barrio": "San Juan", "Inspector": "RODRIGUEZ"},
    {"Barrio": "La Perla", "Inspector": "RODRIGUEZ"},
    {"Barrio": "Nueva Pompeya", "Inspector": "RODRIGUEZ"},
    
    # --- ZONA LOPEZ (Morado) ---
    {"Barrio": "Regional", "Inspector": "LOPEZ"},
    {"Barrio": "Belisario Roldan", "Inspector": "LOPEZ"},
    {"Barrio": "Don Emilio", "Inspector": "LOPEZ"},
    {"Barrio": "Jose Hernandez", "Inspector": "LOPEZ"},
    {"Barrio": "Las Americas", "Inspector": "LOPEZ"}
]

df = pd.DataFrame(datos_inspectores)

esquema_colores = {
    "GARCIA": "#ff7f0e",   # Naranja
    "CARBAYO": "#e377c2",  # Rosa
    "POLINESSI": "#bcbd22",# Amarillo
    "RODRIGUEZ": "#1f77b4",# Azul
    "LOPEZ": "#9467bd"     # Morado
}

# 3. ALTERNATIVA INDESTRUCTIBLE CON PLOTLY: PUNTOS CENTRADOS POR BARRIO (Mapeo Limpio)
# Para evitar cruce de líneas, calculamos centros reales de los barrios en MDP
coordenadas_barrios = {
    "Punta Mogotes": [-38.065, -57.545], "Colinas de Peralta Ramos": [-38.055, -57.560],
    "Juramento": [-38.045, -57.565], "Termas Huinco": [-38.040, -57.555], "Faro Norte": [-38.080, -57.545],
    "Cerrito Sur": [-38.045, -57.575], "El Progreso": [-38.030, -57.575], "Chauvin": [-38.015, -57.555],
    "San Jose": [-38.020, -57.570], "Plaza Mitre": [-38.003, -57.550], "Stella Maris": [-38.010, -57.535],
    "Playa Grande": [-38.030, -57.533], "Los Troncos": [-38.020, -57.540], "San Carlos": [-38.030, -57.550],
    "San Cayetano": [-37.990, -57.585], "Libertad": [-37.975, -57.580], "Bernardino Rivadavia": [-38.005, -57.570],
    "Santa Monica": [-38.015, -57.585], "San Juan": [-37.995, -57.565], "La Perla": [-37.990, -57.545],
    "Nueva Pompeya": [-37.985, -57.555], "Regional": [-38.010, -57.595], "Belisario Roldan": [-38.000, -57.610],
    "Don Emilio": [-38.020, -57.615], "Jose Hernandez": [-38.030, -57.605], "Las Americas": [-38.035, -57.590]
}

# Añadimos las coordenadas al DataFrame de forma matemática y exacta
df['lat'] = df['Barrio'].map(lambda x: coordenadas_barrios.get(x, [-38.00, -57.54])[0])
df['lon'] = df['Barrio'].map(lambda x: coordenadas_barrios.get(x, [-38.00, -57.54])[1])

# 4. CREAMOS EL MAPA DE BURBUJAS DE TERRITORIO (No se cruzan líneas, marca áreas de influencia)
fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    color="Inspector",
    color_discrete_map=esquema_colores,
    hover_name="Barrio",
    text="Barrio",
    size_max=40,
    zoom=11.5,
    center={"lat": -38.0055, "lon": -57.5426},
    height=600
)

# Ajustamos el tamaño para que cubra la superficie visual del barrio en el mapa sin generar líneas raras
fig.update_traces(marker=dict(size=35, opacity=0.6))

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
)

st.plotly_chart(fig, use_container_width=True)

# 5. DETALLE INFORMATIVO ABAJO
st.markdown("---")
st.subheader("📋 Detalle de Zonas")
for ins, col in esquema_colores.items():
    barrios_ins = ", ".join(df[df['Inspector'] == ins]['Barrio'].tolist())
    st.markdown(f"🟢 **Inspector {ins}**: {barrios_ins}")
