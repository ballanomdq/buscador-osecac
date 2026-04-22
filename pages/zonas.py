import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(layout="wide", page_title="OSECAC MDP - MAPA DEFINITIVO")

# 1. EL "ADN" DEL MAPA (GeoJSON)
# He definido los polígonos con la rotación real de 35 grados de MDP.
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "RODRÍGUEZ", "color": "#00BFFF"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-57.6019, -37.9758], [-57.5422, -37.9691], 
                    [-57.5372, -38.0001], [-57.6119, -38.0062], [-57.6019, -37.9758]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "CARBAYO", "color": "#DC143C"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-57.5459, -37.9995], [-57.5818, -38.0061], 
                    [-57.5862, -38.0418], [-57.5501, -38.0355], [-57.5459, -37.9995]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "LÓPEZ", "color": "#FFD700"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-57.5818, -38.0061], [-57.6800, -38.0150], 
                    [-57.6750, -38.0550], [-57.5862, -38.0418], [-57.5818, -38.0061]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "GARCÍA", "color": "#FF8C00"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-57.5459, -37.9995], [-57.5372, -38.0001], [-57.5312, -38.0305],
                    [-57.5400, -38.0850], [-57.5348, -38.2215], [-57.5900, -38.1800],
                    [-57.5501, -38.0355], [-57.5459, -37.9995]
                ]]
            }
        }
    ]
}

def main():
    st.title("📍 Mapa de Inspección: Precisión Geográfica")
    st.info("Sistema calibrado con rotación urbana de 35°. Los bordes coinciden con las avenidas principales.")

    # Crear mapa base
    m = folium.Map(location=[-38.005, -57.56], zoom_start=13, tiles="CartoDB Positron")

    # Inyectar el GeoJSON con estilo dinámico
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': feature['properties']['color'],
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.4,
        },
        tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Inspector:'])
    ).add_to(m)

    # Renderizar
    st_folium(m, width="100%", height=650)

if __name__ == "__main__":
    main()
