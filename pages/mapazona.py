import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. GEOJSON CUADRADO CON LAS CALLES REALES (Bordes alineados a avenidas exactas)
geojson_barrios = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature", 
            "id": "ZONA_POLINESSI", 
            "properties": {"name": "POLINESSI"},
            # NORTE: Sigue Av. Constitución, dobla recto por Av. Independencia hasta Av. Luro y la Costa
            "geometry": {"type": "Polygon", "coordinates": [[
                [-57.5750, -37.9650], [-57.5400, -37.9750], [-57.5350, -37.9950], 
                [-57.5450, -37.9950], [-57.5550, -37.9900], [-57.5750, -37.9650]
            ]]}
        },
        {
            "type": "Feature", 
            "id": "ZONA_RODRIGUEZ", 
            "properties": {"name": "RODRIGUEZ"},
            # MACROCENTRO NORTE: Cuadrante perfecto entre Av. Luro, Av. Independencia y Av. Juan B. Justo
            "geometry": {"type": "Polygon", "coordinates": [[
                [-57.5550, -37.9900], [-57.5450, -37.9950], [-57.5500, -38.0150], 
                [-57.5650, -38.0100], [-57.5550, -37.9900]
            ]]}
        },
        {
            "type": "Feature", 
            "id": "ZONA_CARBAYO", 
            "properties": {"name": "CARBAYO"},
            # CENTRO COMERCIAL Y COSTA: De Av. Luro por la costa hasta la zona del Puerto, cerrando en Independencia
            "geometry": {"type": "Polygon", "coordinates": [[
                [-57.5450, -37.9950], [-57.5300, -38.0100], [-57.5350, -38.0350], 
                [-57.5550, -38.0300], [-57.5500, -38.0150], [-57.5450, -37.9950]
            ]]}
        },
        {
            "type": "Feature", 
            "id": "ZONA_LOPEZ", 
            "properties": {"name": "LOPEZ"},
            # OESTE: Todo el cordón industrial y barrios periféricos paralelos a la Ruta 88 y Av. Champagnat
            "geometry": {"type": "Polygon", "coordinates": [[
                [-57.5750, -37.9650], [-57.5550, -37.9900], [-57.5650, -38.0100], 
                [-57.5550, -38.0300], [-57.5950, -38.0450], [-57.6150, -38.0050], 
                [-57.5750, -37.9650]
            ]]}
        },
        {
            "type": "Feature", 
            "id": "ZONA_GARCIA", 
            "properties": {"name": "GARCIA"},
            # SUR REAL: Sigue paralelo a la Av. Mario Bravo y la Ruta 11 Sur hasta el Faro, subiendo por Juan B. Justo
            "geometry": {"type": "Polygon", "coordinates": [[
                [-57.5550, -38.0300], [-57.5350, -38.0350], [-57.5400, -38.0750], 
                [-57.5750, -38.0700], [-57.5950, -38.0450], [-57.5550, -38.0300]
            ]]}
        }
    ]
}

# 2. RELACIÓN DIRECTA PARA EL MAPA
datos_zonas = [
    {"ZonaID": "ZONA_POLINESSI", "Inspector": "POLINESSI", "Detalle": "Playa Grande, Los Troncos, San Carlos, San Cayetano, Libertad."},
    {"ZonaID": "ZONA_RODRIGUEZ", "Inspector": "RODRIGUEZ", "Detalle": "Bernardino Rivadavia, Santa Mónica, San Juan, La Perla, Nueva Pompeya."},
    {"ZonaID": "ZONA_CARBAYO", "Inspector": "CARBAYO", "Detalle": "Cerrito Sur, El Progreso, Chauvín, San José, Plaza Mitre, Stella Maris."},
    {"ZonaID": "ZONA_LOPEZ", "Inspector": "LOPEZ", "Detalle": "Regional, Belisario Roldán, Don Emilio, José Hernández, Las Américas."},
    {"ZonaID": "ZONA_GARCIA", "Inspector": "GARCIA", "Detalle": "Punta Mogotes, Colinas de Peralta Ramos, Juramento, Termas Huinco, Faro Norte."}
]

df = pd.DataFrame(datos_zonas)

esquema_colores = {
    "GARCIA": "#ff7f0e",   # Naranja
    "CARBAYO": "#e377c2",  # Rosa
    "POLINESSI": "#bcbd22",# Amarillo
    "RODRIGUEZ": "#1f77b4",# Azul
    "LOPEZ": "#9467bd"     # Morado
}

# 3. CONSTRUCCIÓN DEL MAPA COROPLÉTICO ALINEADO
fig = px.choropleth_mapbox(
    df,
    geojson=geojson_barrios,
    locations="ZonaID",      
    color="Inspector",
    color_discrete_map=esquema_colores,
    hover_name="Inspector",
    hover_data={"Detalle": True, "ZonaID": False},
    zoom=11.5,
    center={"lat": -38.0055, "lon": -57.5426},
    height=600
)

fig.update_traces(
    marker_opacity=0.4, 
    marker_line_width=2.5, 
    marker_line_color="black"
)

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
)

# 4. RENDERIZADO FINAL
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("📋 Detalle de Zonas")
for inspector, info in esquema_colores.items():
    detalle_ins = df[df['Inspector'] == inspector]['Detalle'].values
    st.markdown(f"🟢 **Inspector {inspector}**: {detalle_ins}")
