import streamlit as st
import folium
from streamlit_folium import st_folium

# --- COORDENADAS MAESTRAS (Intersecciones Reales de MDP) ---
# Estas coordenadas obligan al mapa a seguir la inclinación de las avenidas
P_LURO_COSTA = [-38.0001, -57.5372]
P_LURO_CHAMPAGNAT = [-38.0062, -57.6119]
P_CONST_CHAMPAGNAT = [-37.9758, -57.6019]
P_CONST_COSTA = [-37.9691, -57.5422]
P_COLON_INDEP = [-37.9995, -57.5459]
P_COLON_JARA = [-38.0061, -57.5818]
P_JBJUSTO_INDEP = [-38.0355, -57.5501]
P_JBJUSTO_JARA = [-38.0418, -57.5862]

def main():
    st.set_page_config(layout="wide", page_title="Zonas OSECAC MDP")
    st.title("🗺️ Mapa de Inspección Calibrado")
    st.caption("Polígonos alineados a la cuadrícula real (Avenidas)")

    # Crear el mapa centrado en MDP
    m = folium.Map(location=[-38.005, -57.56], zoom_start=13, tiles="CartoDB positron")

    # 1. ZONA RODRÍGUEZ (Celeste) - Entre Constitución y Luro
    folium.Polygon(
        locations=[P_CONST_CHAMPAGNAT, P_CONST_COSTA, P_LURO_COSTA, P_LURO_CHAMPAGNAT],
        color="blue", weight=2, fill=True, fill_opacity=0.3,
        tooltip="ZONA RODRÍGUEZ (Norte)"
    ).add_to(m)

    # 2. ZONA CARBAYO (Rojo) - Entre Colón y J.B. Justo (Centro)
    # Usamos P_COLON_JARA y P_JBJUSTO_JARA para que pegue perfecto con LÓPEZ
    folium.Polygon(
        locations=[P_COLON_INDEP, P_COLON_JARA, P_JBJUSTO_JARA, P_JBJUSTO_INDEP],
        color="red", weight=2, fill=True, fill_opacity=0.3,
        tooltip="ZONA CARBAYO (Centro)"
    ).add_to(m)

    # 3. ZONA LÓPEZ (Amarillo) - De Av. Jara hacia el Oeste
    folium.Polygon(
        locations=[P_COLON_JARA, [-38.015, -57.680], [-38.055, -57.675], P_JBJUSTO_JARA],
        color="orange", weight=2, fill=True, fill_opacity=0.3,
        tooltip="ZONA LÓPEZ (Oeste)"
    ).add_to(m)

    # 4. ZONA GARCÍA (Naranja) - Sur y Puerto
    folium.Polygon(
        locations=[P_COLON_INDEP, P_JBJUSTO_INDEP, [-38.100, -57.540], [-38.100, -57.580]],
        color="darkorange", weight=2, fill=True, fill_opacity=0.3,
        tooltip="ZONA GARCÍA (Sur)"
    ).add_to(m)

    st_folium(m, width="100%", height=600)

if __name__ == "__main__":
    main()
