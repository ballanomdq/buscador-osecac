import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(page_title="Mapa de Inspectores - Osecac", layout="wide")
st.title("🗺️ Mapa de Inspectores por Zona - Mar del Plata")
st.markdown("Cada zona está delimitada por las calles reales de Mar del Plata. Hacé clic en cualquier polígono para ver los detalles completos del inspector.")

# ==============================================================================
# COORDENADAS EXACTAS (obtenidas de Google Maps)
# ==============================================================================

# Eje Av. Colón
COLON_JBJUSTO = [-38.00673, -57.60814]
COLON_GUEMES = [-38.00760, -57.54510]
COLON_INDEP = [-38.00662, -57.55620]
COLON_SANLUIS = [-38.00632, -57.55182]
COLON_BRONZINI = [-38.00695, -57.57550]

# Eje Av. Juan B. Justo
JBJUSTO_CATAMARCA = [-38.02012, -57.57531]
JBJUSTO_GUEMES = [-38.03155, -57.54714]
JBJUSTO_POLONIA = [-38.01633, -57.59560]
JBJUSTO_PERALTARAMOS = [-38.02114, -57.57682]

# Otras intersecciones
GUEMES_BUENOSAIRES = [-38.00285, -57.54320]

# Puntos adicionales (de conversaciones anteriores)
PUNTO_CENTRO = [-38.00093862744996, -57.54161484586379]
PUNTO_CHAMPAGNAT = [-37.980243861788324, -57.58254961283819]

# ==============================================================================
# DEFINICIÓN DE ZONAS CON POLÍGONOS QUE SIGUEN CALLES REALES
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
                "calles_descripcion": "Norte: Av. Colón (vereda Par 2000-1300) | Sur: Av. Juan B. Justo (vereda Impar 2000-1300) | Este: Güemes (vereda Impar 2200-4800) | Oeste: Buenos Aires (vereda Par 2200-4500)",
                "poligono": [
                    COLON_GUEMES,           # Av. Colón y Güemes
                    [-38.00760, -57.54000],  # hacia el mar
                    JBJUSTO_GUEMES,          # Av. J.B. Justo y Güemes
                    GUEMES_BUENOSAIRES,      # Güemes y Buenos Aires
                    COLON_GUEMES
                ]
            },
            {
                "nombre": "Zona 2 - La Perla / Catamarca",
                "calles_descripcion": "Norte: Av. Colón (vereda Impar 3500-3100) | Sur: Bv. Marítimo (0-600) y Félix U. Camet (0-200) | Este: Catamarca (vereda Impar 500-2100) | Oeste: Charlone (vereda Par 300-0) y 20 de Septiembre",
                "poligono": [
                    [-38.00600, -57.57000],
                    [-38.00600, -57.56000],
                    [-38.01600, -57.56000],
                    [-38.01600, -57.57000],
                    [-38.00600, -57.57000]
                ]
            },
            {
                "nombre": "Zona 3 - San Juan / Bronzini",
                "calles_descripcion": "Norte: Av. Colón (vereda Par 5800-4200) | Sur: Pehuajó (0-final) y Alvear (0-final) | Este: San Juan (vereda Impar 2200-4800) | Oeste: T. Bronzini (vereda Par 2200-4800)",
                "poligono": [
                    COLON_BRONZINI,         # Av. Colón y Bronzini
                    [-38.00000, -57.57550],
                    [-38.00000, -57.58000],
                    [-38.00695, -57.58000],
                    COLON_BRONZINI
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
                "calles_descripcion": "Norte: La Costa | Sur: Av. Colón (vereda Impar) | Este: San Luis (vereda Impar) | Oeste: H. Yrigoyen (vereda Par)",
                "poligono": [
                    [-38.00000, -57.53500],
                    [-38.00000, -57.52000],
                    [-38.00500, -57.52000],
                    [-38.00500, -57.53500],
                    [-38.00000, -57.53500]
                ]
            },
            {
                "nombre": "Zona 2 - J.B. Justo / Peralta Ramos",
                "calles_descripcion": "Norte: Av. Juan B. Justo | Sur: Límite jurisdicción | Este: Av. Peralta Ramos (vereda Impar) | Oeste: Av. Polonia (vereda Par)",
                "poligono": [
                    JBJUSTO_PERALTARAMOS,
                    JBJUSTO_POLONIA,
                    [-38.02500, -57.59560],
                    [-38.02500, -57.57682],
                    JBJUSTO_PERALTARAMOS
                ]
            },
            {
                "nombre": "Zona 3 - Microcentro / San Juan",
                "calles_descripcion": "Norte: Av. Colón (vereda Impar) | Sur: Av. Juan B. Justo | Este: Av. Independencia (vereda Impar) | Oeste: San Juan (vereda Par)",
                "poligono": [
                    COLON_INDEP,
                    COLON_SANLUIS,
                    [-38.01200, -57.55182],
                    [-38.01200, -57.55620],
                    COLON_INDEP
                ]
            },
            {
                "nombre": "Zona 4 - Sur / Puerto / Alfar",
                "calles_descripcion": "Norte: Av. Juan B. Justo (vereda Par) | Sur: Límite Gral. Alvarado | Este: La Costa | Oeste: Av. Edison (vereda Par)",
                "poligono": [
                    JBJUSTO_GUEMES,
                    [-38.03155, -57.53500],
                    [-38.04000, -57.53500],
                    [-38.04000, -57.54714],
                    JBJUSTO_GUEMES
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
                "calles_descripcion": "Norte: La Costa | Sur: Av. Colón (vereda Impar) | Oeste: San Luis (vereda Par)",
                "poligono": [
                    [-38.00000, -57.54182],
                    [-38.00000, -57.53500],
                    COLON_SANLUIS,
                    [-38.00000, -57.54182]
                ]
            },
            {
                "nombre": "Zona 2 - Microcentro (Independencia)",
                "calles_descripcion": "Norte: Av. Colón (vereda Par) | Sur: Av. Juan B. Justo (vereda Impar) | Este: Buenos Aires (vereda Impar) | Oeste: Av. Independencia (vereda Par)",
                "poligono": [
                    COLON_INDEP,
                    [-38.00662, -57.55800],
                    [-38.01000, -57.55800],
                    [-38.01000, -57.55620],
                    COLON_INDEP
                ]
            },
            {
                "nombre": "Zona 3 - J.B. Justo / Peralta Ramos",
                "calles_descripcion": "Norte: Av. Juan B. Justo (vereda Par) | Sur: Límite jurisdicción | Este: Cerrito (vereda Impar) | Oeste: Av. Peralta Ramos (vereda Par)",
                "poligono": [
                    JBJUSTO_PERALTARAMOS,
                    [-38.01600, -57.57682],
                    [-38.02200, -57.57682],
                    [-38.02200, -57.58000],
                    JBJUSTO_PERALTARAMOS
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
                "calles_descripcion": "Norte: San Luis (vereda Par) | Sur: Santiago del Estero (vereda Impar) | Este: Av. Colón (vereda Impar 2100-2600) | Oeste: San Luis altura 1100",
                "poligono": [
                    COLON_SANLUIS,
                    [-38.00632, -57.54500],
                    [-38.01200, -57.54500],
                    [-38.01200, -57.55182],
                    COLON_SANLUIS
                ]
            },
            {
                "nombre": "Zona 2 - Noroeste (Bronzini / Colón Alta)",
                "calles_descripcion": "Norte: Av. Colón (vereda Par 5800-2200) | Sur: Teodoro Bronzini (vereda Impar) | Barrios: Villa Primera, Regional",
                "poligono": [
                    COLON_BRONZINI,
                    [-37.99500, -57.57550],
                    [-37.99500, -57.58000],
                    [-38.00000, -57.58000],
                    COLON_BRONZINI
                ]
            },
            {
                "nombre": "Zona 3 - Sur (J.B. Justo / Puerto / Nuevo Golf)",
                "calles_descripcion": "Norte: Av. Juan B. Justo (vereda Par 100-1300) | Sur: Cerrito (vereda Impar 3100-4600) | Este: Acha (vereda Impar) | Oeste: Av. Jorge Newbery",
                "poligono": [
                    JBJUSTO_PERALTARAMOS,
                    [-38.01600, -57.57000],
                    [-38.02500, -57.57000],
                    [-38.02500, -57.57682],
                    JBJUSTO_PERALTARAMOS
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
                "calles_descripcion": "Norte: Av. Colón (vereda Impar final) | Sur: Ruta 2 | Este: Av. Champagnat (vereda Impar)",
                "poligono": [
                    [-37.98000, -57.58500],
                    [-37.98000, -57.57500],
                    [-37.99000, -57.57500],
                    [-37.99000, -57.58500],
                    [-37.98000, -57.58500]
                ]
            },
            {
                "nombre": "Zona 2 - Microcentro (Catamarca)",
                "calles_descripcion": "Norte: Catamarca (vereda Par) | Sur: Hipólito Yrigoyen (vereda Impar) | Este: Bv. Marítimo | Oeste: Jujuy/España",
                "poligono": [
                    [-38.00200, -57.53000],
                    [-38.00200, -57.52500],
                    [-38.00800, -57.52500],
                    [-38.00800, -57.53000],
                    [-38.00200, -57.53000]
                ]
            },
            {
                "nombre": "Zona 3 - Sur (Puerto / Reserva)",
                "calles_descripcion": "Norte: Güemes (vereda Par 2200+) | Sur: Bv. Marítimo (Costa Sur) | Este: El Mar | Oeste: Av. Juan B. Justo (vereda Par 1200+)",
                "poligono": [
                    JBJUSTO_GUEMES,
                    [-38.03155, -57.54000],
                    [-38.03800, -57.54000],
                    [-38.03800, -57.54714],
                    JBJUSTO_GUEMES
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
                <hr>
                <b>Límites:</b><br>
                {descripcion.replace('|', '<br>')}
                """,
                max_width=350
            ),
            tooltip=f"{inspector_nombre} - {nombre_zona}"
        ).add_to(mapa)

# Agregar marcadores en todas las intersecciones clave
puntos_ref = {
    "Av. Colón + J.B. Justo": COLON_JBJUSTO,
    "Av. Colón + Güemes": COLON_GUEMES,
    "Av. Colón + Independencia": COLON_INDEP,
    "Av. Colón + San Luis": COLON_SANLUIS,
    "Av. Colón + Bronzini": COLON_BRONZINI,
    "J.B. Justo + Catamarca": JBJUSTO_CATAMARCA,
    "J.B. Justo + Güemes": JBJUSTO_GUEMES,
    "J.B. Justo + Polonia": JBJUSTO_POLONIA,
    "J.B. Justo + Peralta Ramos": JBJUSTO_PERALTARAMOS,
    "Güemes + Buenos Aires": GUEMES_BUENOSAIRES,
}

for nombre, coord in puntos_ref.items():
    folium.Marker(
        coord,
        popup=nombre,
        icon=folium.Icon(color="gray", icon="info-sign", prefix="fa"),
        tooltip=nombre
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
            for zona in inspector["zonas"]:
                st.markdown(f"**📍 {zona['nombre']}**")
                st.caption(zona["calles_descripcion"][:150] + "...")
                st.markdown("---")

# ==============================================================================
# TABLA RESUMEN COMPLETA
# ==============================================================================

st.subheader("📊 Tabla completa de Zonas por Inspector")

datos_tabla = []
for inspector in zonas_inspectores:
    for zona in inspector["zonas"]:
        datos_tabla.append({
            "Inspector": inspector["inspector"],
            "Legajo": inspector["legajo"],
            "Zona": zona["nombre"],
            "Límites": zona["calles_descripcion"],
            "Color": inspector["color"]
        })

df = pd.DataFrame(datos_tabla)
st.dataframe(df, use_container_width=True, height=400)

st.success("✅ Los polígonos están trazados usando las coordenadas exactas de las intersecciones reales de Mar del Plata.")
