import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. GEOJSON CON FORMATO CORRECTO (Estructura exacta que lee Plotly)
geojson_barrios = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature", 
            "id": "ZONA_POLINESSI", 
            "properties": {"name": "POLINESSI"},
            "geometry": {"type": "Polygon", "coordinates": [[[-57.595, -37.985], [-57.545, -37.975], [-57.535, -38.005], [-57.575, -38.015], [-57.595, -37.985]]]}}
        },
        {
            "type": "Feature", 
            "id": "ZONA_RODRIGUEZ", 
            "properties": {"name": "RODRIGUEZ"},
            "geometry": {"type": "Polygon", "coordinates": [[[-57.570, -38.005], [-57.545, -37.990], [-57.535, -38.005], [-57.550, -38.015], [-57.570, -38.005]]]}}
        },
        {
            "type": "Feature", 
            "id": "ZONA_CARBAYO", 
            "properties": {"name": "CARBAYO"},
            "geometry": {"type": "Polygon", "coordinates": [[[-57.565, -38.010], [-57.542, -38.005], [-57.530, -38.025], [-57.550, -38.045], [-57.565, -38.010]]]}}
        },
        {
            "type": "Feature", 
            "id": "ZONA_LOPEZ", 
            "properties": {"name": "LOPEZ"},
            "geometry": {"type": "Polygon", "coordinates": [[[-57.635, -38.025], [-57.570, -38.005], [-57.565, -38.010], [-57.575, -38.035], [-57.615, -38.055], [-57.635, -38.025]]]}}
        },
        {
            "type": "Feature", 
            "id": "ZONA_GARCIA", 
            "properties": {"name": "GARCIA"},
            "geometry": {"type": "Polygon", "coordinates": [[[-57.595, -38.045], [-57.550, -38.045], [-57.530, -38.025], [-57.535, -38.055], [-57.545, -38.085], [-57.585, -38.075], [-57.595, -38.045]]]}}
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

# 3. CONSTRUCCIÓN DEL MAPA COROPLÉTICO FIJO
fig = px.choropleth_mapbox(
    df,
    geojson=geojson_barrios,
    locations="ZonaID",      # Apunta al campo 'id' de arriba
    color="Inspector",
    color_discrete_map=esquema_colores,
    hover_name="Inspector",
    hover_data={"Detalle": True, "ZonaID": False},
    zoom=11,
    center={"lat": -38.0055, "lon": -57.5426},
    height=600
)

# Forzamos que se pinte el área transparente y se marque el borde de cada zona
fig.update_traces(
    marker_opacity=0.5, 
    marker_line_width=2, 
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
    detalle_ins = df[df['Inspector'] == inspector]['Detalle'].values[0]
    st.markdown(f"🟢 **Inspector {inspector}**: {detalle_ins}")
