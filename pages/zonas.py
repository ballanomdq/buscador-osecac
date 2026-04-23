import streamlit as st
import folium
from streamlit_folium import folium_static

# Configuración de página ancha
st.set_page_config(layout="wide", page_title="Sistema de Inspectores MDP")

# --- ESTILOS ---
st.markdown("""
    <style>
    .inspector-card {
        padding: 15px;
        border-radius: 10px;
        border-left: 10px solid;
        margin-bottom: 10px;
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🗺️ Mapa de Zonas de Inspección - Mar del Plata")
st.info("Haga clic en las zonas del mapa para ver detalles o consulte el listado superior.")

# --- BASE DE DATOS EXTENDIDA (Basada en tus 9 fotos) ---
# Aquí es donde pondrás las coordenadas exactas que tengas.
ZONAS = [
    {
        "inspector": "LOPEZ, MARTIN LEONARDO",
        "color": "#00008B", # Azul Oscuro (Foto 7/8/9)
        "limites": "Av. Colón (Par), Santiago del Estero (Impar), J.B. Justo (Par) 100-1300",
        "instrucciones": "Zona Centro y Villa Lourdes. Cuidado con veredas compartidas en Colón.",
        "calles": "Belisario Roldán, Coronel Dorrego, San Luis, Mitre, Yrigoyen.",
        "coords": [[-38.000, -57.540], [-38.000, -57.555], [-38.020, -57.555], [-38.020, -57.540]]
    },
    {
        "inspector": "GARCIA, JUAN PAULO",
        "color": "#FF8C00", # Naranja (Foto 7)
        "limites": "Av. Vértiz, Av. Edison, Antártida Argentina, J.B. Justo (Impar)",
        "instrucciones": "Zona Gral. Pueyrredón y El Martillo. Ver detalle de veredas en J.B. Justo.",
        "calles": "Cerrito, Acha, Juramento, Magallanes, Ramos, Pelícano.",
        "coords": [[-38.025, -57.575], [-38.025, -57.595], [-38.045, -57.595], [-38.045, -57.575]]
    },
    {
        "inspector": "CARBAYO, VICTOR HUGO",
        "color": "#FF1493", # Rosa Fucsia (Foto 7/9)
        "limites": "Av. Colón (Par) 2199-4499, San Juan (Impar) 2201-4499, Independencia (Par)",
        "instrucciones": "Zona Chauvín y San José. Límites precisos en Independencia.",
        "calles": "Matheu, Formosa, Quintana, Saavedra, Primera Junta.",
        "coords": [[-38.010, -57.560], [-38.010, -57.580], [-38.025, -57.580], [-38.025, -57.560]]
    },
    {
        "inspector": "RODRIGUEZ, MAXIMILIANO",
        "color": "#00CED1", # Turquesa/Cian (Foto 7)
        "limites": "Charlone (Par), 20 de Septiembre (Par), Bv. Marítimo, Colón (Impar) 3500-3100",
        "instrucciones": "Zona Regional y El Gaucho. Incluye faja costera norte.",
        "calles": "Félix U. Camet, Catamarca, La Rioja, San Juan, Pehuajó.",
        "coords": [[-37.985, -57.545], [-37.985, -57.565], [-37.998, -57.565], [-37.998, -57.545]]
    },
    {
        "inspector": "POLINESSI",
        "color": "#9400D3", # Violeta (Foto 7 Arriba Izquierda)
        "limites": "Zona Noroeste: Libertad, Don Emilio, Belgrano.",
        "instrucciones": "Límites rurales y barrios periféricos norte.",
        "calles": "Av. Libertad, Av. Champagnat (parte), Malvinas Argentinas.",
        "coords": [[-37.970, -57.570], [-37.970, -57.600], [-37.990, -57.600], [-37.990, -57.570]]
    },
    {
        "inspector": "POLINESSI (Sur)",
        "color": "#ADFF2F", # Verde Amarillento (Foto 7 Abajo)
        "limites": "Playa Grande, Los Troncos, San Carlos.",
        "instrucciones": "Zona de alta densidad residencial.",
        "calles": "Juan B. Justo, Alem, Aristóbulo del Valle, Formosa.",
        "coords": [[-38.025, -57.535], [-38.025, -57.550], [-38.040, -57.550], [-38.040, -57.535]]
    },
    {
        "inspector": "MOREA",
        "color": "#228B22", # Verde Bosque (Foto 7 Derecha)
        "limites": "Villa Primera, Nueva Pompeya, Parque Luro.",
        "instrucciones": "Veredas compartidas con Rodríguez en zonas costeras.",
        "calles": "Av. Tejedor, Estrada, Av. Constitución.",
        "coords": [[-37.965, -57.545], [-37.965, -57.565], [-37.980, -57.565], [-37.980, -57.545]]
    },
    {
        "inspector": "GARCIA (Puerto/Mogotes)",
        "color": "#CD853F", # Marrón claro/Tan (Foto 7 Abajo Izquierda)
        "limites": "Puerto, Colinas de Peralta Ramos, Punta Mogotes.",
        "instrucciones": "Seguimiento de zona portuaria y balnearios.",
        "calles": "Av. de los Trabajadores, Av. Martínez de Hoz.",
        "coords": [[-38.050, -57.550], [-38.050, -57.580], [-38.080, -57.580], [-38.080, -57.550]]
    },
    {
        "inspector": "BOVONE",
        "color": "#808080", # Gris (Foto 7 Fondo)
        "limites": "Mar Argentino / Extremo Sur.",
        "instrucciones": "Límite sur del partido.",
        "calles": "Ruta 11, Alfar, Playas del Sur.",
        "coords": [[-38.090, -57.560], [-38.090, -57.600], [-38.120, -57.600], [-38.120, -57.560]]
    }
]

# --- RENDERIZADO DE INFORMACIÓN SUPERIOR ---
st.subheader("📋 Detalle de Inspectores y Calles")
cols = st.columns(3) # Dividimos en 3 columnas para que no sea muy largo hacia abajo

for i, zona in enumerate(ZONAS):
    with cols[i % 3]:
        st.markdown(f"""
            <div class="inspector-card" style="border-left-color: {zona['color']};">
                <strong>{zona['inspector']}</strong><br>
                <small>📍 <i>{zona['limites']}</i></small><br>
                <b>Instrucciones:</b> {zona['instrucciones']}<br>
                <b>Calles Internas:</b> {zona['calles']}
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# --- RENDERIZADO DEL MAPA ---
st.subheader("🗺️ Visualización de Islas MDP")
m = folium.Map(location=[-38.005, -57.565], zoom_start=12, tiles="OpenStreetMap")

for zona in ZONAS:
    folium.Polygon(
        locations=zona['coords'],
        color=zona['color'],
        fill=True,
        fill_color=zona['color'],
        fill_opacity=0.5,
        weight=3,
        popup=f"<b>Inspector:</b> {zona['inspector']}<br><b>Límites:</b> {zona['limites']}",
        tooltip=zona['inspector']
    ).add_to(m)

folium_static(m, width=1200, height=700)
