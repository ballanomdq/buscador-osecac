import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. DESCARGA DIRECTA DE LÍMITES OFICIALES (Sin inventar coordenadas)
# Usamos un repositorio público que tiene el mapa de barrios oficial de Mar del Plata extraído de OpenStreetMap
@st.cache_data
def cargar_mapa_oficial():
    url = "https://githubusercontent.com"
    # Si todavía no tenés ese archivo en tu repo, usamos este de respaldo con los polígonos reales de la provincia
    url_respaldo = "https://githubusercontent.com"
    try:
        r = requests.get(url_respaldo, timeout=10)
        return r.json()
    except:
        return None

geojson_oficial = cargar_mapa_oficial()

# 2. RELACIÓN REAL DE BARRIOS OFICIALES POR INSPECTOR
# Escribí los nombres tal cual figuran en los carteles del mapa de fondo
datos_barrios = [
    # --- ZONA GARCIA ---
    {"BarrioReal": "Punta Mogotes", "Inspector": "GARCIA"},
    {"BarrioReal": "Colinas de Peralta Ramos", "Inspector": "GARCIA"},
    {"BarrioReal": "Juramento", "Inspector": "GARCIA"},
    {"BarrioReal": "Termas Huinco", "Inspector": "GARCIA"},
    {"BarrioReal": "Faro Norte", "Inspector": "GARCIA"},
    
    # --- ZONA CARBAYO ---
    {"BarrioReal": "Cerrito Sur", "Inspector": "CARBAYO"},
    {"BarrioReal": "El Progreso", "Inspector": "CARBAYO"},
    {"BarrioReal": "Chauvín", "Inspector": "CARBAYO"},
    {"BarrioReal": "San José", "Inspector": "CARBAYO"},
    {"BarrioReal": "Plaza Mitre", "Inspector": "CARBAYO"},
    {"BarrioReal": "Stella Maris", "Inspector": "CARBAYO"},
    
    # --- ZONA POLINESSI ---
    {"BarrioReal": "Playa Grande", "Inspector": "POLINESSI"},
    {"BarrioReal": "Los Troncos", "Inspector": "POLINESSI"},
    {"BarrioReal": "San Carlos", "Inspector": "POLINESSI"},
    {"BarrioReal": "San Cayetano", "Inspector": "POLINESSI"},
    {"BarrioReal": "Libertad", "Inspector": "POLINESSI"},
    {"BarrioReal": "Constitución", "Inspector": "POLINESSI"},
    
    # --- ZONA RODRIGUEZ ---
    {"BarrioReal": "Bernardino Rivadavia", "Inspector": "RODRIGUEZ"},
    {"BarrioReal": "Santa Mónica", "Inspector": "RODRIGUEZ"},
    {"BarrioReal": "San Juan", "Inspector": "RODRIGUEZ"},
    {"BarrioReal": "La Perla", "Inspector": "RODRIGUEZ"},
    {"BarrioReal": "Nueva Pompeya", "Inspector": "RODRIGUEZ"},
    
    # --- ZONA LOPEZ ---
    {"BarrioReal": "Regional", "Inspector": "LOPEZ"},
    {"BarrioReal": "Belisario Roldán", "Inspector": "LOPEZ"},
    {"BarrioReal": "Don Emilio", "Inspector": "LOPEZ"},
    {"BarrioReal": "José Hernández", "Inspector": "LOPEZ"},
    {"BarrioReal": "Las Américas", "Inspector": "LOPEZ"}
]

df = pd.DataFrame(datos_barrios)

esquema_colores = {
    "GARCIA": "#ff7f0e",   # Naranja
    "CARBAYO": "#e377c2",  # Rosa
    "POLINESSI": "#bcbd22",# Amarillo
    "RODRIGUEZ": "#1f77b4",# Azul
    "LOPEZ": "#9467bd"     # Morado
}

# 3. DIBUJAR EL MAPA SI EL ARCHIVO CARGÓ CORRECTAMENTE
if geojson_oficial is not None:
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson_oficial,
        featureidkey="properties.name", # Mapea directo contra el nombre oficial del barrio
        locations="BarrioReal",      
        color="Inspector",
        color_discrete_map=esquema_colores,
        hover_name="BarrioReal",
        zoom=11.5,
        center={"lat": -38.0055, "lon": -57.5426},
        height=600
    )

    fig.update_traces(
        marker_opacity=0.45, 
        marker_line_width=1.5, 
        marker_line_color="black"
)

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0},
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("No se pudieron cargar los límites oficiales de Mar del Plata. Verifique la conexión.")

# 4. TABLA INFORMATIVA
st.markdown("---")
st.subheader("📋 Detalle de Zonas")
for inspector, col in esquema_colores.items():
    lista_barrios = df[df['Inspector'] == inspector]['BarrioReal'].tolist()
    st.markdown(f"🟢 **Inspector {inspector}**: {', '.join(lista_barrios)}")
