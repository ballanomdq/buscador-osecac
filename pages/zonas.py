import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Configurar la página
st.set_page_config(page_title="Mapa de Inspectores - Osecac", layout="wide")
st.title("🗺️ Mapa de Inspectores por Zona - Mar del Plata")
st.markdown("Hacé clic en las zonas para ver los detalles completos.")

# ==============================================================================
# 1. DEFINICIÓN DE ZONAS CON COORDENADAS REALES
# ==============================================================================

zonas_inspectores = [

    # ========== RODRIGUEZ ==========
    {
        "inspector": "RODRIGUEZ, Maximiliano",
        "legajo": "7713",
        "color": "#FF0000",
        "zonas": [
            {
                "nombre": "Zona 1 - Güemes / J.B. Justo",
                "calles_descripcion": "Límites: Av. Colón (vereda Par, del 2000 al 1300) | Av. Juan B. Justo (vereda Impar, del 2000 al 1300) | Güemes (vereda Impar, del 2200 al 4800) | Buenos Aires (vereda Par, del 2200 al 4500)",
                "poligono": [
                    [-38.0075, -57.5480],
                    [-38.0075, -57.5400],
                    [-38.0200, -57.5400],
                    [-38.0200, -57.5480],
                    [-38.0075, -57.5480]
                ]
            }
        ]
    },

    # ========== GARCIA ==========
    {
        "inspector": "GARCÍA, Juan Paulo",
        "legajo": "7852",
        "color": "#FFA500",
        "zonas": [
            {
                "nombre": "Zona 1 - Costa / Colón",
                "calles_descripcion": "Límites: La Costa (norte) | Av. Colón (vereda Impar) | San Luis (vereda Impar) | H. Yrigoyen (vereda Par)",
                "poligono": [
                    [-38.0000, -57.5350],
                    [-38.0000, -57.5200],
                    [-38.0050, -57.5200],
                    [-38.0050, -57.5350],
                    [-38.0000, -57.5350]
                ]
            },
            {
                "nombre": "Zona 2 - J.B. Justo / Peralta Ramos",
                "calles_descripcion": "Límites: Av. Juan B. Justo (norte) | Av. Jacinto Peralta Ramos (vereda Impar) | Av. Polonia (vereda Par) | al fondo límite jurisdicción",
                "poligono": [
                    [-38.0160, -57.5760],
                    [-38.0160, -57.5680],
                    [-38.0250, -57.5680],
                    [-38.0250, -57.5760],
                    [-38.0160, -57.5760]
                ]
            },
            {
                "nombre": "Zona 3 - Microcentro / San Juan",
                "calles_descripcion": "Límites: Av. Colón (vereda Impar) | Av. Juan B. Justo (sur) | Av. Independencia (vereda Impar) | San Juan (vereda Par)",
                "poligono": [
                    [-38.0065, -57.5600],
                    [-38.0065, -57.5520],
                    [-38.0120, -57.5520],
                    [-38.0120, -57.5600],
                    [-38.0065, -57.5600]
                ]
            },
            {
                "nombre": "Zona 4 - Sur / Puerto / Alfar",
                "calles_descripcion": "Límites: Av. Juan B. Justo (vereda Par) | límite Gral. Alvarado (sur) | La Costa (este) | Av. Edison (vereda Par)",
                "poligono": [
                    [-38.0200, -57.5500],
                    [-38.0200, -57.5300],
                    [-38.0400, -57.5300],
                    [-38.0400, -57.5500],
                    [-38.0200, -57.5500]
                ]
            }
        ]
    },

    # ========== CARBAYO ==========
    {
        "inspector": "CARBAYO, Víctor Hugo",
        "legajo": "9220",
        "color": "#FFFF00",
        "zonas": [
            {
                "nombre": "Zona 1 - Costa / Colón (Triangular)",
                "calles_descripcion": "Límites: La Costa (norte) | Av. Colón (vereda Impar) | San Luis (vereda Par)",
                "poligono": [
                    [-38.0000, -57.5410],
                    [-38.0000, -57.5350],
                    [-38.0050, -57.5410],
                    [-38.0000, -57.5410]
                ]
            },
            {
                "nombre": "Zona 2 - Microcentro (Independencia)",
                "calles_descripcion": "Límites: Av. Colón (vereda Par) | Av. Juan B. Justo (vereda Impar) | Buenos Aires (vereda Impar) | Av. Independencia (vereda Par)",
                "poligono": [
                    [-38.0065, -57.5580],
                    [-38.0065, -57.5560],
                    [-38.0100, -57.5560],
                    [-38.0100, -57.5580],
                    [-38.0065, -57.5580]
                ]
            },
            {
                "nombre": "Zona 3 - J.B. Justo / Peralta Ramos",
                "calles_descripcion": "Límites: Av. Juan B. Justo (vereda Par) | Cerrito (vereda Impar) | Av. Jacinto Peralta Ramos (vereda Par)",
                "poligono": [
                    [-38.0160, -57.5720],
                    [-38.0160, -57.5680],
                    [-38.0220, -57.5680],
                    [-38.0220, -57.5720],
                    [-38.0160, -57.5720]
                ]
            }
        ]
    },

    # ========== LOPEZ ==========
    {
        "inspector": "LOPEZ, Martín Leonardo",
        "legajo": "9983",
        "color": "#00FF00",
        "zonas": [
            {
                "nombre": "Zona 1 - Centro (Plaza Mitre / La Perla)",
                "calles_descripcion": "Límites: San Luis (vereda Par) | Santiago del Estero (vereda Impar) | Av. Colón (vereda Impar, entre altura 2100 y 2600) | San Luis (Altura 1100) hacia La Perla",
                "poligono": [
                    [-38.0050, -57.5500],
                    [-38.0050, -57.5450],
                    [-38.0120, -57.5450],
                    [-38.0120, -57.5500],
                    [-38.0050, -57.5500]
                ]
            },
            {
                "nombre": "Zona 2 - Noroeste (Bronzini / Colón Alta)",
                "calles_descripcion": "Límites: Av. Colón (vereda Par, desde altura 5800 hacia el 2200) | Teodoro Bronzini (vereda Impar). Barrios: Villa Primera, Regional.",
                "poligono": [
                    [-37.9950, -57.5650],
                    [-37.9950, -57.5550],
                    [-38.0050, -57.5550],
                    [-38.0050, -57.5650],
                    [-37.9950, -57.5650]
                ]
            },
            {
                "nombre": "Zona 3 - Sur (J.B. Justo / Puerto / Nuevo Golf)",
                "calles_descripcion": "Límites: Av. Juan B. Justo (vereda Par, desde altura 100 hasta el 1300) | Cerrito (vereda Impar, alturas 3100 a 4600) | Acha (vereda Impar) | Av. Jorge Newbery (ambas manos, desde altura 3400 hacia el Fin del Mundo)",
                "poligono": [
                    [-38.0160, -57.5550],
                    [-38.0160, -57.5480],
                    [-38.0250, -57.5480],
                    [-38.0250, -57.5550],
                    [-38.0160, -57.5550]
                ]
            }
        ]
    },

    # ========== POLINESSI ==========
    {
        "inspector": "POLINESSI, Juan José",
        "legajo": "9513",
        "color": "#0000FF",
        "zonas": [
            {
                "nombre": "Zona 1 - Noroeste (Champagnat)",
                "calles_descripcion": "Límites: Av. Colón (vereda Impar al final) | hasta Ruta 2 | Av. Champagnat (vereda Impar)",
                "poligono": [
                    [-37.9800, -57.5850],
                    [-37.9800, -57.5750],
                    [-37.9900, -57.5750],
                    [-37.9900, -57.5850],
                    [-37.9800, -57.5850]
                ]
            },
            {
                "nombre": "Zona 2 - Microcentro (Catamarca)",
                "calles_descripcion": "Límites: Catamarca (vereda Par) | Hipólito Yrigoyen (vereda Impar) | Blvd. Marítimo (La Costa) | Jujuy/España (cierre)",
                "poligono": [
                    [-38.0020, -57.5300],
                    [-38.0020, -57.5250],
                    [-38.0080, -57.5250],
                    [-38.0080, -57.5300],
                    [-38.0020, -57.5300]
                ]
            },
            {
                "nombre": "Zona 3 - Sur (Puerto / Reserva)",
                "calles_descripcion": "Límites: Güemes (vereda Par desde el 2200) | Blvd. Marítimo (Costa Sur) | El Mar | Av. Juan B. Justo (vereda Par desde el 1200)",
                "poligono": [
                    [-38.0250, -57.5450],
                    [-38.0250, -57.5350],
                    [-38.0380, -57.5350],
                    [-38.0380, -57.5450],
                    [-38.0250, -57.5450]
                ]
            }
        ]
    }
]

# ==============================================================================
# 2. CREAR MAPA CON FOLIUM
# ==============================================================================
mapa_centro = [-38.0055, -57.5426]
mapa = folium.Map(location=mapa_centro, zoom_start=13, tiles="CartoDB positron")

# Agregar cada zona como polígono
for inspector_data in zonas_inspectores:
    color = inspector_data["color"]
    inspector_nombre = inspector_data["inspector"]
    legajo = inspector_data["legajo"]
    
    for zona in inspector_data["zonas"]:
        nombre_zona = zona["nombre"]
        descripcion = zona["calles_descripcion"]
        vertices = zona["poligono"]
        
        folium.Polygon(
            locations=vertices,
            color=color,
            weight=2,
            fill=True,
            fill_opacity=0.4,
            popup=folium.Popup(
                f"""
                <b>Inspector:</b> {inspector_nombre}<br>
                <b>Legajo:</b> {legajo}<br>
                <b>Zona:</b> {nombre_zona}<br>
                <b>Límites:</b><br>{descripcion}
                """,
                max_width=300
            ),
            tooltip=f"{inspector_nombre} - {nombre_zona}"
        ).add_to(mapa)

# Agregar puntos de referencia
puntos_ref = {
    "Colón + J.B. Justo": [-38.0068, -57.6083],
    "Colón + Güemes": [-38.0076, -57.5451],
    "Colón + Independencia": [-38.0066, -57.5562],
    "Colón + San Luis": [-38.0063, -57.5518],
    "J.B. Justo + Catamarca": [-38.0201, -57.5753],
    "J.B. Justo + Güemes": [-38.0315, -57.5471],
    "J.B. Justo + Polonia": [-38.0163, -57.5956],
    "J.B. Justo + Peralta Ramos": [-38.0211, -57.5768],
}

for nombre, coord in puntos_ref.items():
    folium.Marker(
        coord,
        popup=nombre,
        icon=folium.Icon(color="gray", icon="info-sign", prefix="fa"),
        tooltip=nombre
    ).add_to(mapa)

# ==============================================================================
# 3. MOSTRAR EN STREAMLIT
# ==============================================================================
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📍 Mapa de Zonas por Inspector")
    output = st_folium(mapa, width=800, height=600)

with col2:
    st.subheader("📋 Leyenda de Inspectores")
    for inspector in zonas_inspectores:
        with st.expander(f"🎨 {inspector['inspector']} (Leg. {inspector['legajo']})"):
            st.markdown(f"**Color:** `{inspector['color']}`")
            for zona in inspector["zonas"]:
                st.markdown(f"**📍 {zona['nombre']}**")
                st.caption(zona["calles_descripcion"])
                st.markdown("---")

# ==============================================================================
# 4. TABLA RESUMEN
# ==============================================================================
st.subheader("📊 Resumen de Zonas por Inspector")
datos_tabla = []
for inspector in zonas_inspectores:
    for zona in inspector["zonas"]:
        datos_tabla.append({
            "Inspector": inspector["inspector"],
            "Legajo": inspector["legajo"],
            "Zona": zona["nombre"],
            "Límites": zona["calles_descripcion"]
        })
df = pd.DataFrame(datos_tabla)
st.dataframe(df, use_container_width=True)

st.info("💡 Los polígonos son aproximaciones basadas en las descripciones de límites. Para una geolocalización exacta cuadra por cuadra, se necesita un servicio de geocodificación.")
