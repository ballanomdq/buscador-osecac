import streamlit as st
import folium
from streamlit_folium import st_folium
import json

# REGLA DE ORO: Si el punto A es el final de una zona, 
# DEBE ser el inicio de la siguiente. 

def main():
    st.set_page_config(layout="wide", page_title="OSECAC MDP - Mapa Maestro")
    
    # 1. Definición de Nodos (Esquinas exactas de Google Maps)
    # Estos puntos son los "clavos" donde se enganchan los hilos del mapa
    NUDO_COLON_INDEP = [-37.9995, -57.5459]
    NUDO_COLON_JARA  = [-38.0061, -57.5818]
    NUDO_LURO_COSTA   = [-38.0001, -57.5372]
    NUDO_LURO_CHAMP   = [-38.0062, -57.6119]
    
    m = folium.Map(location=[-38.005, -57.56], zoom_start=13, tiles="OpenStreetMap")

    # ESTRATEGIA RADICAL: Crear una función que dibuje para evitar errores de tipeo
    def dibujar_zona(puntos, color, nombre):
        folium.Polygon(
            locations=puntos,
            color=color,
            fill=True,
            fill_opacity=0.4,
            weight=3,
            tooltip=nombre
        ).add_to(m)

    # Dibujamos usando los NUDOS compartidos
    # ZONA 1
    dibujar_zona([[-37.969, -57.542], NUDO_LURO_COSTA, NUDO_LURO_CHAMP, [-37.975, -57.601]], "blue", "RODRÍGUEZ")
    
    # ZONA 2 (Usa los mismos nudos que la 1 para el borde norte)
    dibujar_zona([NUDO_COLON_INDEP, NUDO_COLON_JARA, [-38.041, -57.586], [-38.035, -57.550]], "red", "CARBAYO")

    st_folium(m, width="100%", height=600)

if __name__ == "__main__":
    main()
