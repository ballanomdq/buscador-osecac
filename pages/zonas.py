import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="Sistema de Zonas OSECAC MDP")

st.title("📍 Mapa de Jurisdicciones Calibrado (Ajuste por Avenida)")
st.markdown("---")

# 1. REFERENCIA DE COLORES Y TÍTULOS (Leyenda)
col1, col2, col3, col4 = st.columns(4)
with col1: st.info("🔵 **RODRÍGUEZ** (Leg. 7713) - Norte")
with col2: st.error("🔴 **CARBAYO** (Leg. 9220) - Macrocentro")
with col3: st.warning("🟡 **LÓPEZ** (Leg. 9983) - Oeste")
with col4: st.success("🟠 **GARCÍA** (Leg. 7952) - Sur/Puerto")

# 2. CONFIGURACIÓN DEL MAPA BASE
# Centrado exacto en la cuadrícula de Mar del Plata
m = folium.Map(location=[-38.0055, -57.5426], zoom_start=13)

# --- COORDINADAS CALIBRADAS PARA SEGUIR LA TRAZA URBANA ---

# RODRÍGUEZ (Norte: De Constitución a Luro)
zona_rodriguez = [
    [-37.9750, -57.5450], [-37.9980, -57.5450], # Costa desde Constitución a Luro
    [-37.9980, -57.6050], [-37.9750, -57.6050]  # Por Champagnat (Límite Oeste)
]

# CARBAYO (Macrocentro: Cuadrante entre Colón, J.B. Justo, Independencia y Jara)
zona_carbayo = [
    [-38.0120, -57.5520], [-38.0380, -57.5520], # Baja por Av. Independencia
    [-38.0380, -57.5850], [-38.0120, -57.5850]  # Vuelve por Av. Jara (Límite Oeste)
]

# LÓPEZ (Oeste: De Av. Jara hacia el fondo)
# Estos puntos están alineados con Carbayo para no encimarse
zona_lopez = [
    [-38.0120, -57.5850], [-38.0380, -57.5850], # Límite CRÍTICO con Carbayo (Av. Jara)
    [-38.0380, -57.6500], [-38.0120, -57.6500]  # Hacia el fondo (Campo)
]

# GARCÍA (Sur/Costa: Puerto hasta Las Brusquitas)
# Sigue la curva de la costa y dobla en las avenidas
zona_garcia = [
    [-38.0000, -57.5350], [-38.0120, -57.5350], # Borde Colón/Costa
    [-38.0120, -57.5520], [-38.0380, -57.5520], # Dobla en Independencia/J.B. Justo
    [-38.0380, -57.5400], [-38.0600, -57.5450], # Puerto
    [-38.1500, -57.6300], [-38.2200, -57.7500], # Camino a Miramar
    [-38.2300, -57.7000], [-38.0000, -57.5300]  # Cierre por costa
]

# 3. DIBUJAR LOS POLÍGONOS CON ALTA OPACIDAD
# Usamos weight=1 y fill_opacity=0.3 para que se lean las calles debajo
folium.Polygon(zona_rodriguez, color="blue", weight=1, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_carbayo, color="red", weight=1, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_lopez, color="yellow", weight=1, fill=True, fill_opacity=0.3).add_to(m)
folium.Polygon(zona_garcia, color="orange", weight=1, fill=True, fill_opacity=0.3).add_to(m)

# 4. MOSTRAR EL MAPA
st_folium(m, width=1300, height=650)
