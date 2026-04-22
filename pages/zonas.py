"""
zonas.py — Mapa de zonas de inspección, Mar del Plata
Polígonos alineados a la cuadrícula urbana (~35° respecto al Norte).
Cada zona se define con vértices que siguen las avenidas perimetrales.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium

# ──────────────────────────────────────────────
# CONFIGURACIÓN DE ZONAS
# ──────────────────────────────────────────────
# Cada zona tiene:
#   color      → color de borde y relleno
#   fill_color → puede diferir del borde (aquí son iguales para simplificar)
#   opacity    → 0.3 para transparencia requerida
#   coords     → lista de [lat, lon] que sigue las avenidas perimetrales
#
# Criterio de los vértices:
#   – Se ubican en las INTERSECCIONES de las avenidas que delimitan cada zona.
#   – El orden es antihorario/horario consistente (Folium cierra el polígono
#     automáticamente uniendo el último punto con el primero).
#   – La cuadrícula de MDP está rotada ~35° NE, por lo que los vértices
#     NO forman un rectángulo cartesiano; se definen con coordenadas reales
#     de cada esquina de avenida.
# ──────────────────────────────────────────────

ZONAS = {
    "GARCÍA": {
        "legajo": "Leg. 7952",
        "color": "#FF8C00",          # Naranja
        "fill_color": "#FF8C00",
        "descripcion": "Desde Av. Independencia (vereda impar) hacia la costa, "
                       "Av. Colón al sur hasta Arroyo Las Brusquitas. "
                       "Incluye Puerto y Punta Mogotes.",
        # Perímetro: Av. Independencia (borde O) → costa (borde E) →
        #            Límite con Miramar/Arroyo Las Brusquitas (borde S) →
        #            cierra por el norte en Av. Independencia/Av. Colón
        "coords": [
            # Vértice N-O: Av. Independencia y Av. Colón (zona puerto)
            [-37.9995, -57.5460],
            # Vértice N-E: Bajada a la costa / Puerto de Mar del Plata
            [-38.0020, -57.5310],
            # Costa hacia el sur — siguiendo la línea costera
            [-38.0500, -57.5160],
            [-38.1000, -57.5120],
            [-38.1500, -57.5150],
            [-38.1900, -57.5200],
            # Vértice S-E: Punta Mogotes / Límite sur costero
            [-38.2200, -57.5350],
            # Vértice S-O: Arroyo Las Brusquitas (límite con Miramar)
            [-38.2220, -57.5650],
            # Borde O remontando hacia el norte por Av. Independencia
            [-38.1800, -57.5800],
            [-38.1200, -57.5720],
            [-38.0500, -57.5620],
        ],
    },

    "RODRÍGUEZ": {
        "legajo": "Leg. 7713",
        "color": "#00BFFF",          # Celeste
        "fill_color": "#00BFFF",
        "descripcion": "Delimitada por Av. Luro/Av. Colón al sur, "
                       "Av. Constitución al norte, costa al este "
                       "y Av. Champagnat al oeste. "
                       "Calles críticas: San Juan (impar) y Catamarca (impar).",
        # Recorrido: inicio en intersección Av. Constitución – Av. Champagnat (N-O)
        #            → hacia el este por Av. Constitución hasta la costa (N-E)
        #            → bajando por la costa (E)
        #            → Av. Colón / Av. Luro hacia el oeste (S)
        #            → sube por Av. Champagnat (O)
        "coords": [
            # N-O: Av. Constitución y Av. Champagnat
            [-37.9760, -57.6020],
            # N-E: Av. Constitución y costanera
            [-37.9690, -57.5420],
            # S-E: Av. Colón / Av. Luro y costanera (altura Punta Iglesia)
            [-38.0000, -57.5370],
            # S-O: Av. Luro / Av. Colón y Av. Champagnat
            [-38.0060, -57.6120],
        ],
    },

    "CARBAYO": {
        "legajo": "Leg. 9220",
        "color": "#DC143C",          # Rojo
        "fill_color": "#DC143C",
        "descripcion": "Cuadrante entre Av. Colón (alt. 2200–4500), "
                       "Av. Juan B. Justo, Av. Independencia y Av. Jara. "
                       "Área de Plaza Mitre y Chauvín.",
        # Recorrido: esquina Av. Independencia – Av. Juan B. Justo (N-O)
        #            → Av. Independencia hacia el este hasta Av. Jara (N-E)
        #            → Av. Jara hacia el sur hasta Av. Colón ~4500 (S-E)
        #            → Av. Colón hacia el oeste hasta Av. Juan B. Justo ~2200 (S-O)
        "coords": [
            # N-O: Av. Independencia y Av. Juan B. Justo
            [-37.9920, -57.6210],
            # N-E: Av. Independencia y Av. Jara
            [-37.9840, -57.5910],
            # S-E: Av. Jara y Av. Colón (altura ~4500)
            [-38.0060, -57.5820],
            # S-O: Av. Colón (altura ~2200) y Av. Juan B. Justo
            [-38.0140, -57.6140],
        ],
    },

    "LÓPEZ": {
        "legajo": "Leg. 9983",
        "color": "#FFD700",          # Amarillo
        "fill_color": "#FFD700",
        "descripcion": "Desde Av. Jara hacia el oeste hasta el límite urbano. "
                       "Eje: Av. Colón (alt. 5800–9200, vereda par) "
                       "y tramos de T. Bronzini.",
        # Recorrido: inicio N-E en Av. Jara / borde norte (calle paralela a Av. Colón)
        #            → hacia el oeste hasta el límite urbano ("Fin del Mundo") (N-O)
        #            → límite urbano bajando al sur (O)
        #            → Av. Colón alt. 9200 cerrando por el sur (S-O → S-E)
        #            → T. Bronzini / calle sur hasta Av. Jara (S-E)
        "coords": [
            # N-E: Av. Jara y línea norte de la zona (~Av. Colón 5800 par)
            [-38.0060, -57.5820],
            # N-O: Límite urbano oeste y calle norte
            [-38.0200, -57.6800],
            # S-O: Límite urbano oeste y Av. Colón alt. ~9200
            [-38.0620, -57.6650],
            # S-E: Av. Colón alt. ~9200 / T. Bronzini y Av. Jara
            [-38.0520, -57.5960],
        ],
    },
}

# ──────────────────────────────────────────────
# HELPER: construir el mapa
# ──────────────────────────────────────────────

def construir_mapa() -> folium.Map:
    """Devuelve el mapa Folium con todas las zonas dibujadas."""
    mapa = folium.Map(
        location=[-38.0055, -57.5426],  # Centro aproximado de MDP
        zoom_start=12,
        tiles="CartoDB positron",       # Fondo claro que deja leer calles
    )

    for nombre, zona in ZONAS.items():
        tooltip_html = (
            f"<b>{nombre}</b> — {zona['legajo']}<br>"
            f"<small>{zona['descripcion']}</small>"
        )
        folium.Polygon(
            locations=zona["coords"],
            color=zona["color"],
            weight=2.5,
            fill=True,
            fill_color=zona["fill_color"],
            fill_opacity=0.3,
            opacity=0.85,
            tooltip=tooltip_html,
            popup=folium.Popup(
                f"<b>{nombre}</b><br>{zona['legajo']}<br>{zona['descripcion']}",
                max_width=260,
            ),
        ).add_to(mapa)

    return mapa


# ──────────────────────────────────────────────
# INTERFAZ STREAMLIT
# ──────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Zonas de Inspección — Mar del Plata",
        page_icon="🗺️",
        layout="wide",
    )

    st.title("🗺️ Zonas de Inspección — Mar del Plata")
    st.caption("Polígonos alineados a la cuadrícula urbana (~35° respecto al Norte)")

    # ── LEYENDA DE COLORES ──────────────────────────────────
    st.subheader("Leyenda de Zonas")

    cols = st.columns(len(ZONAS))
    for col, (nombre, zona) in zip(cols, ZONAS.items()):
        with col:
            # Cuadrado de color usando HTML inline
            color_box = (
                f'<div style="'
                f'background:{zona["color"]};'
                f'opacity:0.85;'
                f'width:28px;height:28px;'
                f'border-radius:5px;'
                f'border:1.5px solid #555;'
                f'display:inline-block;'
                f'vertical-align:middle;'
                f'margin-right:8px;'
                f'"></div>'
            )
            st.markdown(
                f'{color_box} <b>ZONA {nombre}</b><br>'
                f'<small style="color:#555">{zona["legajo"]}</small>',
                unsafe_allow_html=True,
            )
            st.caption(zona["descripcion"])

    st.divider()

    # ── MAPA ──────────────────────────────────────────────
    mapa = construir_mapa()

    st_folium(
        mapa,
        width="100%",
        height=620,
        returned_objects=[],   # Evita rerun innecesario al hacer clic
    )

    # ── NOTA TÉCNICA ──────────────────────────────────────
    with st.expander("ℹ️ Nota sobre los polígonos"):
        st.markdown(
            """
            **Por qué los vértices no forman rectángulos cartesianos**

            La cuadrícula de Mar del Plata está rotada aproximadamente **35° respecto
            al Norte verdadero** (orientación NE-SO). Si se usaran solo dos puntos
            (esquinas opuestas) para definir un rectángulo alineado a los ejes
            geográficos, el relleno cruzaría las manzanas en diagonal.

            Estos polígonos se definen con los vértices en las **intersecciones reales**
            de las avenidas perimetrales, de modo que cada lado del polígono sigue
            la trayectoria de la avenida correspondiente.

            **Para afinar los vértices:** usá Google Maps o QGIS para obtener las
            coordenadas exactas de cada esquina y reemplazalas en la lista `coords`
            de cada zona en este archivo.
            """,
            unsafe_allow_html=False,
        )


if __name__ == "__main__":
    main()
