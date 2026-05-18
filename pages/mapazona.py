import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🗺️ Mapa de Inspectores - Mar del Plata")

# 1. GEOJSON DE LOS BARRIOS REALES (Fronteras exactas para que NO se encimen)
geojson_barrios = {
    "type": "FeatureCollection",
    "features": [
        # ZONA POLINESSI (Norte / Constitución / Libertad)
        {"type": "Feature", "id": "ZONA_POLINESSI", "geometry": {"type": "Polygon", "coordinates": [[[-57.545, -37.975], [-57.535, -38.005], [-57.575, -38.015], [-57.595, -37.985], [-57.575, -37.965], [-57.545, -37.975]]]}},
        # ZONA RODRIGUEZ (Macrocentro Norte / La Perla / San Juan)
        {"type": "Feature", "id": "ZONA_RODRIGUEZ", "geometry": {"type": "Polygon", "coordinates": [[[-57.545, -37.990], [-57.555, -37.995], [-57.550, -38.015], [-57.570, -38.005], [-57.545, -37.990]]]}},
        # ZONA CARBAYO (Centro / Plaza Mitre / Stella Maris / Chauvín)
        {"type": "Feature", "id": "ZONA_CARBAYO", "geometry": {"type": "Polygon", "coordinates": [[[-57.542, -38.005], [-57.530, -38.025], [-57.550, -38.045], [-57.575, -38.035], [-57.565, -38.010], [-57.542, -38.005]]]}},
        # ZONA LOPEZ (Oeste / Regional / Las Américas)
        {"type": "Feature", "id": "ZONA_LOPEZ", "geometry": {"type": "Polygon", "coordinates": [[[-57.570, -38.005], [-57.585, -38.015], [-57.575, -38.035], [-57.615, -38.055], [-57.635, -38.025], [-57.570, -38.005]]]}},
        # ZONA GARCIA (Puerto / Punta Mogotes / Colinas / Faro)
        {"type": "Feature", "id": "ZONA_GARCIA", "geometry": {"type": "Polygon", "coordinates": [[[-57.530, -38.025], [-57.545, -38.031], [-57.535, -38.055], [-57.545, -38.085], [-57.585, -38.075], [-57.595, -38.045], [-57.550, -38.045], [-57.530, -38.025]]]}}
    ]
}

# 2. RELACIÓN DE INSPECTORES CON SUS RESPECTIVAS ZONAS GEOJSON
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

# 3. MAPA COROPLÉTICO (Dibuja áreas cerradas perfectas con división real)
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

# Ajustamos la opacidad para que el bloque de color pinte el área de forma transparente y se vean las calles abajo
fig.update_traces(marker_opacity=0.45, marker_line_width=2, marker_line_color="white")

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
)

st.plotly_chart(fig, use_container_width=True)

# 4. PANEL INFORMATIVO COMPLEMENTARIO
st.markdown("---")
st.subheader("📋 Detalle de Zonas")
for inspector, info in esquema_colores.items():
    detalle_ins = df[df['Inspector'] == inspector]['Detalle'].values[0]
    st.markdown(f"🟢 **Inspector {inspector}**: {detalle_ins}")
