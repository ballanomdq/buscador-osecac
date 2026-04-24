import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(page_title="Mapa de Inspectores - Osecac", layout="wide")
st.title("🗺️ Mapa de Inspectores por Zona - Mar del Plata")
st.markdown("Zonas delimitadas por calles reales. Hacé clic en cualquier polígono para ver los detalles completos.")

# ==============================================================================
# COORDENADAS EXACTAS (relevamiento completo)
# ==============================================================================

coord = {
    # RODRIGUEZ - Zona Güemes/JBJusto
    "COLON_GUEMES": [-38.0076, -57.5451],
    "COLON_BAIRES": [-38.0055, -57.5458],
    "JBJUSTO_GUEMES": [-38.0315, -57.5471],
    "JBJUSTO_BAIRES": [-38.0298, -57.5482],
    
    # RODRIGUEZ - Zona La Perla/Catamarca
    "COLON_CATAMARCA": [-38.0062, -57.5532],
    "COLON_CHARLONE": [-38.0074, -57.5684],
    "BV_CATAMARCA": [-37.9942, -57.5455],
    "BV_CHARLONE": [-37.9855, -57.5531],
    
    # RODRIGUEZ - Zona San Juan/Bronzini
    "COLON_SANJUAN": [-38.0065, -57.5552],
    "COLON_BRONZINI": [-38.0069, -57.5755],
    "PEHUAJO_SANJUAN": [-38.0165, -57.5568],
    "PEHUAJO_BRONZINI": [-38.0171, -57.5772],
    
    # GARCIA - Zona Costa/Colón
    "SANLUIS_COSTA": [-38.0044, -57.5428],
    "YRIGOYEN_COSTA": [-38.0019, -57.5412],
    "COLON_SANLUIS": [-38.0063, -57.5518],
    "COLON_YRIGOYEN": [-38.0064, -57.5542],
    
    # GARCIA - Zona JBJusto/PeraltaRamos
    "JBJUSTO_PERALTARAMOS": [-38.0211, -57.5768],
    "JBJUSTO_POLONIA": [-38.0163, -57.5956],
    "VERTIZ_PERALTARAMOS": [-38.0312, -57.5815],
    "VERTIZ_POLONIA": [-38.0255, -57.6012],
    
    # GARCIA - Zona Microcentro/SanJuan
    "COLON_INDEP": [-38.0066, -57.5562],
    "JBJUSTO_INDEP": [-38.0215, -57.5638],
    "JBJUSTO_SANJUAN": [-38.0214, -57.5622],
    
    # CARBAYO - Zona Costa Triangular
    "COLON_COSTA": [-38.0031, -57.5405],
    
    # CARBAYO - Zona Microcentro Independencia
    "JBJUSTO_BAIRES": [-38.0298, -57.5482],
    
    # LOPEZ - Centro Plaza Mitre
    "COLON_SANTIAGO": [-38.0062, -57.5507],
    "FALUCHO_SANLUIS": [-38.0094, -57.5522],
    "FALUCHO_SANTIAGO": [-38.0093, -57.5511],
    
    # LOPEZ - Noroeste Bronzini
    "COLON_JBJUSTO": [-38.0067, -57.6081],
    "JBJUSTO_REFORMA": [-38.0335, -57.6152],
    "JBJUSTO_BRONZINI": [-38.0381, -57.5841],
    
    # POLINESSI - Champagnat
    "COLON_CHAMPAGNAT": [-38.0075, -57.5862],
    "COLON_RUTA2": [-38.0076, -57.5912],
    "CHAMPAGNAT_LIBERTAD": [-37.9868, -57.5772],
    
    # POLINESSI - Microcentro Catamarca
    "CATAMARCA_JUJUY": [-37.9949, -57.5478],
    "YRIGOYEN_JUJUY": [-38.0031, -57.5471],
    
    # POLINESSI - Sur Puerto
    "GÜEMES_MARTINEZ": [-38.0338, -57.5342],
    "COSTA_PLAYA": [-38.0268, -57.5312],
}

# ==============================================================================
# DEFINICIÓN DE ZONAS (usando las coordenadas exactas)
# ==============================================================================

zonas_inspectores = [

    {   # RODRIGUEZ
        "inspector": "RODRIGUEZ, Maximiliano",
        "legajo": "7713",
        "color": "#FF0000",
        "zonas": [
            {
                "nombre": "Zona 1 - Güemes / J.B. Justo",
                "limites": "Norte: Av. Colón | Sur: Av. Juan B. Justo | Este: Güemes | Oeste: Buenos Aires",
                "poligono": [
                    coord["COLON_GUEMES"], coord["COLON_BAIRES"],
                    coord["JBJUSTO_BAIRES"], coord["JBJUSTO_GUEMES"],
                    coord["COLON_GUEMES"]
                ]
            },
            {
                "nombre": "Zona 2 - La Perla / Catamarca",
                "limites": "Norte: Av. Colón | Sur: Bv. Marítimo | Este: Catamarca | Oeste: Charlone",
                "poligono": [
                    coord["COLON_CATAMARCA"], coord["COLON_CHARLONE"],
                    coord["BV_CHARLONE"], coord["BV_CATAMARCA"],
                    coord["COLON_CATAMARCA"]
                ]
            },
            {
                "nombre": "Zona 3 - San Juan / Bronzini",
                "limites": "Norte: Av. Colón | Sur: Pehuajó | Este: San Juan | Oeste: Bronzini",
                "poligono": [
                    coord["COLON_SANJUAN"], coord["COLON_BRONZINI"],
                    coord["PEHUAJO_BRONZINI"], coord["PEHUAJO_SANJUAN"],
                    coord["COLON_SANJUAN"]
                ]
            }
        ]
    },

    {   # GARCIA
        "inspector": "GARCÍA, Juan Paulo",
        "legajo": "7852",
        "color": "#FFA500",
        "zonas": [
            {
                "nombre": "Zona 1 - Costa / Colón",
                "limites": "Norte: La Costa | Sur: Av. Colón | Este: San Luis | Oeste: Yrigoyen",
                "poligono": [
                    coord["SANLUIS_COSTA"], coord["YRIGOYEN_COSTA"],
                    coord["COLON_YRIGOYEN"], coord["COLON_SANLUIS"],
                    coord["SANLUIS_COSTA"]
                ]
            },
            {
                "nombre": "Zona 2 - J.B. Justo / Peralta Ramos",
                "limites": "Norte: Av. Juan B. Justo | Sur: Calle Vértiz | Este: Peralta Ramos | Oeste: Polonia",
                "poligono": [
                    coord["JBJUSTO_PERALTARAMOS"], coord["JBJUSTO_POLONIA"],
                    coord["VERTIZ_POLONIA"], coord["VERTIZ_PERALTARAMOS"],
                    coord["JBJUSTO_PERALTARAMOS"]
                ]
            },
            {
                "nombre": "Zona 3 - Microcentro / San Juan",
                "limites": "Norte: Av. Colón | Sur: Av. Juan B. Justo | Este: Independencia | Oeste: San Juan",
                "poligono": [
                    coord["COLON_INDEP"], coord["COLON_SANJUAN"],
                    coord["JBJUSTO_SANJUAN"], coord["JBJUSTO_INDEP"],
                    coord["COLON_INDEP"]
                ]
            }
        ]
    },

    {   # CARBAYO
        "inspector": "CARBAYO, Víctor Hugo",
        "legajo": "9220",
        "color": "#FFFF00",
        "zonas": [
            {
                "nombre": "Zona 1 - Costa Triangular",
                "limites": "Triángulo entre La Costa, Av. Colón y San Luis",
                "poligono": [
                    coord["SANLUIS_COSTA"], coord["COLON_SANLUIS"],
                    coord["COLON_COSTA"], coord["SANLUIS_COSTA"]
                ]
            },
            {
                "nombre": "Zona 2 - Microcentro Independencia",
                "limites": "Norte: Av. Colón | Sur: Av. Juan B. Justo | Este: Independencia | Oeste: Buenos Aires",
                "poligono": [
                    coord["COLON_INDEP"], coord["COLON_BAIRES"],
                    coord["JBJUSTO_BAIRES"], coord["JBJUSTO_INDEP"],
                    coord["COLON_INDEP"]
                ]
            }
        ]
    },

    {   # LOPEZ
        "inspector": "LOPEZ, Martín Leonardo",
        "legajo": "9983",
        "color": "#00FF00",
        "zonas": [
            {
                "nombre": "Zona 1 - Centro Plaza Mitre",
                "limites": "Norte: San Luis | Sur: Santiago del Estero | Este: Av. Colón | Oeste: Falucho",
                "poligono": [
                    coord["COLON_SANLUIS"], coord["COLON_SANTIAGO"],
                    coord["FALUCHO_SANTIAGO"], coord["FALUCHO_SANLUIS"],
                    coord["COLON_SANLUIS"]
                ]
            },
            {
                "nombre": "Zona 2 - Noroeste Bronzini",
                "limites": "Norte: Av. Colón | Sur: Av. Juan B. Justo | Este: Bronzini | Oeste: Reforma Universitaria",
                "poligono": [
                    coord["COLON_BRONZINI"], coord["COLON_JBJUSTO"],
                    coord["JBJUSTO_REFORMA"], coord["JBJUSTO_BRONZINI"],
                    coord["COLON_BRONZINI"]
                ]
            }
        ]
    },

    {   # POLINESSI
        "inspector": "POLINESSI, Juan José",
        "legajo": "9513",
        "color": "#0000FF",
        "zonas": [
            {
                "nombre": "Zona 1 - Champagnat",
                "limites": "Triángulo entre Av. Colón, Av. Champagnat y Ruta 2",
                "poligono": [
                    coord["COLON_CHAMPAGNAT"], coord["COLON_RUTA2"],
                    coord["CHAMPAGNAT_LIBERTAD"], coord["COLON_CHAMPAGNAT"]
                ]
            },
            {
                "nombre": "Zona 2 - Microcentro Catamarca",
                "limites": "Norte: Catamarca | Sur: Yrigoyen | Este: Bv. Marítimo | Oeste: Jujuy",
                "poligono": [
                    coord["BV_CATAMARCA"], coord["CATAMARCA_JUJUY"],
                    coord["YRIGOYEN_JUJUY"], coord["YRIGOYEN_COSTA"],
                    coord["BV_CATAMARCA"]
                ]
            },
            {
                "nombre": "Zona 3 - Sur Puerto",
                "limites": "Norte: Güemes | Sur: Bv. Marítimo | Este: Mar | Oeste: J.B. Justo",
                "poligono": [
                    coord["JBJUSTO_GUEMES"], coord["GÜEMES_MARTINEZ"],
                    coord["COSTA_PLAYA"], coord["COLON_GUEMES"],
                    coord["JBJUSTO_GUEMES"]
                ]
            }
        ]
    }
]

# ==============================================================================
# CREAR MAPA CON FOLIUM
# ==============================================================================

mapa_centro = [-38.0055, -57.5426]
mapa = folium.Map(location=mapa_centro, zoom_start=13, tiles="CartoDB positron")

# Agregar zonas
for inspector in zonas_inspectores:
    color = inspector["color"]
    nombre_inspector = inspector["inspector"]
    legajo = inspector["legajo"]
    
    for zona in inspector["zonas"]:
        folium.Polygon(
            locations=zona["poligono"],
            color=color,
            weight=2,
            fill=True,
            fill_opacity=0.4,
            popup=folium.Popup(
                f"""
                <b>Inspector:</b> {nombre_inspector}<br>
                <b>Legajo:</b> {legajo}<br>
                <b>Zona:</b> {zona['nombre']}<br>
                <hr>
                <b>Límites:</b><br>{zona['limites']}
                """,
                max_width=300
            ),
            tooltip=f"{nombre_inspector} - {zona['nombre']}"
        ).add_to(mapa)

# ==============================================================================
# MOSTRAR EN STREAMLIT
# ==============================================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📍 Mapa de Zonas por Inspector")
    st_folium(mapa, width=800, height=650)

with col2:
    st.subheader("📋 Leyenda")
    for inspector in zonas_inspectores:
        with st.expander(f"🎨 {inspector['inspector']} (Leg. {inspector['legajo']})"):
            st.markdown(f"**Color:** `{inspector['color']}`")
            st.markdown("**Zonas:**")
            for zona in inspector["zonas"]:
                st.markdown(f"- {zona['nombre']}")

# ==============================================================================
# TABLA RESUMEN
# ==============================================================================

st.subheader("📊 Tabla completa de Zonas")

tabla_datos = []
for inspector in zonas_inspectores:
    for zona in inspector["zonas"]:
        tabla_datos.append({
            "Inspector": inspector["inspector"],
            "Legajo": inspector["legajo"],
            "Zona": zona["nombre"],
            "Límites": zona["limites"]
        })

df = pd.DataFrame(tabla_datos)
st.dataframe(df, use_container_width=True)

st.success("✅ Mapa generado con todas las zonas delimitadas por calles reales de Mar del Plata")
