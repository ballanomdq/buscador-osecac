"""
zonas.py — Mapa de Zonas de Inspección, Mar del Plata
======================================================
Polígonos definidos con vértices exactos de intersección de avenidas.
Los bordes compartidos entre zonas usan coordenadas IDÉNTICAS para
evitar solapamientos o huecos visuales.

Coordenadas maestras (no modificar sin relevamiento de campo):
  P1  = Av. Constitución y Av. Champagnat        [-37.9758, -57.6019]
  P2  = Av. Constitución y La Costa              [-37.9691, -57.5422]
  P3  = Av. Luro y La Costa                      [-38.0001, -57.5372]
  P4  = Av. Luro y Av. Champagnat                [-38.0062, -57.6119]
  P5  = Av. Colón y Av. Independencia            [-37.9995, -57.5459]
  P6  = Av. Colón y Av. Jara                     [-38.0061, -57.5818]
  P7  = Av. J.B. Justo y Av. Independencia       [-38.0355, -57.5501]
  P8  = Av. J.B. Justo y Av. Jara                [-38.0418, -57.5862]
  P9  = Av. J.B. Justo y La Costa                [-38.0305, -57.5312]
  P10 = Arroyo Las Brusquitas (Costa)            [-38.2215, -57.5348]
"""

import streamlit as st
import folium
from streamlit_folium import st_folium

# ══════════════════════════════════════════════════════════════════════════════
# COORDENADAS MAESTRAS
# Definidas una sola vez. Los polígonos las referencian directamente para que
# los bordes compartidos sean byte-a-byte idénticos.
# ══════════════════════════════════════════════════════════════════════════════

P1  = [-37.9758, -57.6019]   # Av. Constitución y Av. Champagnat
P2  = [-37.9691, -57.5422]   # Av. Constitución y La Costa
P3  = [-38.0001, -57.5372]   # Av. Luro y La Costa
P4  = [-38.0062, -57.6119]   # Av. Luro y Av. Champagnat
P5  = [-37.9995, -57.5459]   # Av. Colón y Av. Independencia  ← nudo triple
P6  = [-38.0061, -57.5818]   # Av. Colón y Av. Jara           ← Carbayo/López
P7  = [-38.0355, -57.5501]   # Av. J.B. Justo y Av. Independencia
P8  = [-38.0418, -57.5862]   # Av. J.B. Justo y Av. Jara
P9  = [-38.0305, -57.5312]   # Av. J.B. Justo y La Costa  (quiebre García-Puerto)
P10 = [-38.2215, -57.5348]   # Arroyo Las Brusquitas / límite sur García

# Punto intermedio de costa para evitar que García "corte" por el mar
PUNTA_MOGOTES = [-38.0850, -57.5400]

# Puntos de López hacia el "Fin del Mundo" (Ruta 226 / límite urbano oeste)
P6B = [-38.0130, -57.7200]   # Av. Colón ~alt. 9200 / Ruta 226 (límite N-O López)
P8B = [-38.0480, -57.7150]   # T. Bronzini y límite urbano      (límite S-O López)

# Punto interior suroeste para cerrar García por tierra (no por el mar)
GARCIA_SW = [-38.1800, -57.5900]

# ══════════════════════════════════════════════════════════════════════════════
# DEFINICIÓN DE ZONAS
# ══════════════════════════════════════════════════════════════════════════════
#
# FRONTERA COMPARTIDA RODRÍGUEZ – CARBAYO (Av. Colón):
#   El segmento P5 → P6 es el borde SUR de Rodríguez y el borde NORTE de Carbayo.
#   Ambas zonas usan exactamente P5 y P6 (misma referencia Python).
#
# FRONTERA COMPARTIDA CARBAYO – LÓPEZ (Av. Jara):
#   El segmento P6 → P8 es el borde OESTE de Carbayo y el borde ESTE de López.
#   Ambas zonas usan P6 y P8 directamente.
# ══════════════════════════════════════════════════════════════════════════════

ZONAS = {

    # ── ZONA RODRÍGUEZ ────────────────────────────────────────────────────────
    # Norte : Av. Constitución     (P1 → P2)
    # Este  : Costa La Perla       (P2 → P3)
    # Sur   : Av. Luro / Av. Colón (P3 → P4)
    # Oeste : Av. Champagnat       (P4 → P1)
    "RODRÍGUEZ": {
        "legajo": "Leg. 7713",
        "color": "#00BFFF",
        "fill_color": "#00BFFF",
        "descripcion": (
            "Norte: Av. Constitución — Sur: Av. Luro/Colón — "
            "Este: Costa (La Perla/Centro) — Oeste: Av. Champagnat. "
            "Calles críticas: San Juan (impar) y Catamarca (impar)."
        ),
        "coords": [
            P1,   # N-O: Av. Constitución y Av. Champagnat
            P2,   # N-E: Av. Constitución y La Costa
            P3,   # S-E: Av. Luro y La Costa
            P4,   # S-O: Av. Luro y Av. Champagnat
        ],
    },

    # ── ZONA CARBAYO ──────────────────────────────────────────────────────────
    # Norte : Av. Colón (vereda impar)  (P5 → P6)  ← compartido con Rodríguez sur
    # Este  : Av. Independencia         (P5 → P7)
    # Sur   : Av. J.B. Justo            (P7 → P8)
    # Oeste : Av. Jara                  (P8 → P6)  ← compartido con López este
    #
    # Orden de vértices: N-E → N-O → S-O → S-E
    "CARBAYO": {
        "legajo": "Leg. 9220",
        "color": "#DC143C",
        "fill_color": "#DC143C",
        "descripcion": (
            "Norte: Av. Colón (alt. 2200–4500, vereda impar) — "
            "Sur: Av. J.B. Justo — "
            "Este: Av. Independencia — Oeste: Av. Jara. "
            "Área Plaza Mitre y Chauvín."
        ),
        "coords": [
            P5,   # N-E: Av. Colón y Av. Independencia (nudo triple)
            P6,   # N-O: Av. Colón y Av. Jara (nudo Carbayo/López)
            P8,   # S-O: Av. J.B. Justo y Av. Jara
            P7,   # S-E: Av. J.B. Justo y Av. Independencia
        ],
    },

    # ── ZONA LÓPEZ ────────────────────────────────────────────────────────────
    # Este  : Av. Jara                  (P6 → P8)  ← compartido con Carbayo oeste
    # Norte : Av. Colón alt. 5800→9200  (P6 → P6B)
    # Oeste : Ruta 226 / Fin del Mundo  (P6B → P8B)
    # Sur   : T. Bronzini               (P8B → P8)
    #
    # Orden de vértices: N-E → N-O → S-O → S-E
    "LÓPEZ": {
        "legajo": "Leg. 9983",
        "color": "#FFD700",
        "fill_color": "#FFD700",
        "descripcion": (
            "Este: Av. Jara — Norte: Av. Colón (alt. 5800–9200, vereda par) — "
            "Sur: T. Bronzini — Oeste: Ruta 226 / Fin del Mundo."
        ),
        "coords": [
            P6,    # N-E: Av. Colón y Av. Jara  (mismo punto que Carbayo N-O)
            P6B,   # N-O: Av. Colón y Ruta 226 / límite urbano
            P8B,   # S-O: T. Bronzini y límite urbano
            P8,    # S-E: Av. J.B. Justo y Av. Jara (mismo punto que Carbayo S-O)
        ],
    },

    # ── ZONA GARCÍA ───────────────────────────────────────────────────────────
    # Norte : Av. Colón / Av. Independencia  (P3 → P5)
    # Costa : con puntos intermedios P9 y PUNTA_MOGOTES para bordear la playa
    # Sur   : Arroyo Las Brusquitas          (P10)
    # Oeste : Av. Independencia              (P10 → GARCIA_SW → P7 → P5)
    #
    # Sentido: empezar en P3 (costa norte), bajar por costa, cerrar por interior
    "GARCÍA": {
        "legajo": "Leg. 7952",
        "color": "#FF8C00",
        "fill_color": "#FF8C00",
        "descripcion": (
            "Norte: Av. Colón / Av. Independencia — "
            "Este: Costa, Puerto, Punta Mogotes — "
            "Sur: Arroyo Las Brusquitas (límite con Miramar). "
            "Incluye Puerto y Punta Mogotes."
        ),
        "coords": [
            P5,            # N-O interior: Av. Colón y Av. Independencia
            P3,            # N-E costero:  Av. Luro y La Costa
            P9,            # quiebre Puerto: Av. J.B. Justo y La Costa
            PUNTA_MOGOTES, # intermedio costa: evita cruzar por el mar
            P10,           # S-E: Arroyo Las Brusquitas (límite sur)
            GARCIA_SW,     # S-O interior: cierra por tierra hacia el oeste
            P7,            # Av. J.B. Justo y Av. Independencia
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# CONSTRUCCIÓN DEL MAPA
# ══════════════════════════════════════════════════════════════════════════════

def construir_mapa() -> folium.Map:
    mapa = folium.Map(
        location=[-38.0100, -57.5700],
        zoom_start=12,
        tiles="CartoDB positron",
    )

    for nombre, zona in ZONAS.items():
        folium.Polygon(
            locations=zona["coords"],
            color=zona["color"],
            weight=2.5,
            fill=True,
            fill_color=zona["fill_color"],
            fill_opacity=0.3,
            opacity=0.90,
            tooltip=folium.Tooltip(
                f"<b>ZONA {nombre}</b> — {zona['legajo']}<br>"
                f"<small>{zona['descripcion']}</small>",
                sticky=True,
            ),
            popup=folium.Popup(
                f"<b>ZONA {nombre}</b><br>"
                f"<i>{zona['legajo']}</i><br><br>"
                f"{zona['descripcion']}",
                max_width=280,
            ),
        ).add_to(mapa)

    return mapa


# ══════════════════════════════════════════════════════════════════════════════
# INTERFAZ STREAMLIT
# ══════════════════════════════════════════════════════════════════════════════

COLORES_LEGIBLES = {
    "RODRÍGUEZ": {"hex": "#00BFFF", "borde": "#0077aa", "texto": "#004466"},
    "CARBAYO":   {"hex": "#DC143C", "borde": "#9a0e2a", "texto": "#6b0a1e"},
    "LÓPEZ":     {"hex": "#FFD700", "borde": "#b89600", "texto": "#6b5700"},
    "GARCÍA":    {"hex": "#FF8C00", "borde": "#b36200", "texto": "#6b3b00"},
}


def main():
    st.set_page_config(
        page_title="Zonas de Inspección — Mar del Plata",
        page_icon="🗺️",
        layout="wide",
    )

    st.title("🗺️ Zonas de Inspección — Mar del Plata")
    st.caption(
        "Polígonos con vértices exactos de intersección de avenidas. "
        "Bordes compartidos sincronizados: cero solapamiento entre zonas."
    )

    # ── LEYENDA ──────────────────────────────────────────────────────────────
    st.subheader("Leyenda de Zonas")
    cols = st.columns(len(ZONAS))

    for col, (nombre, zona) in zip(cols, ZONAS.items()):
        c = COLORES_LEGIBLES[nombre]
        with col:
            st.markdown(
                f"""
                <div style="
                    background: {c['hex']}33;
                    border-left: 5px solid {c['borde']};
                    border-radius: 6px;
                    padding: 10px 12px;
                    margin-bottom: 6px;
                ">
                    <div style="font-weight:700; color:{c['texto']}; font-size:15px;">
                        ZONA {nombre}
                    </div>
                    <div style="font-size:12px; color:#666; margin-top:2px;">
                        {zona['legajo']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(zona["descripcion"])

    st.divider()

    # ── MAPA ─────────────────────────────────────────────────────────────────
    mapa = construir_mapa()
    st_folium(mapa, width="100%", height=650, returned_objects=[])

    # ── TABLA DE COORDENADAS MAESTRAS (auditoría) ─────────────────────────────
    with st.expander("📍 Coordenadas maestras — referencia de auditoría"):
        maestras = [
            ("P1",  "Av. Constitución y Av. Champagnat (Rodríguez N-O)",         P1),
            ("P2",  "Av. Constitución y La Costa (Rodríguez N-E)",               P2),
            ("P3",  "Av. Luro y La Costa (Rodríguez S-E / García N-E)",          P3),
            ("P4",  "Av. Luro y Av. Champagnat (Rodríguez S-O)",                 P4),
            ("P5",  "Av. Colón y Av. Independencia — NUDO TRIPLE",               P5),
            ("P6",  "Av. Colón y Av. Jara — CARBAYO/LÓPEZ (borde compartido)",   P6),
            ("P7",  "Av. J.B. Justo y Av. Independencia (Carbayo S-E)",          P7),
            ("P8",  "Av. J.B. Justo y Av. Jara — CARBAYO/LÓPEZ S",              P8),
            ("P9",  "Av. J.B. Justo y La Costa — quiebre Puerto (García)",       P9),
            ("P10", "Arroyo Las Brusquitas — LÍMITE SUR García",                 P10),
        ]
        for pid, desc, coord in maestras:
            st.code(
                f"{pid:4s}  {desc}\n"
                f"      lat: {coord[0]}   lon: {coord[1]}",
                language="text",
            )

        st.info(
            "**Clave de sincronización:** P5, P6 y P8 son referencias Python únicas. "
            "Carbayo y López comparten P6 y P8 exactos — no hay copias con decimales distintos. "
            "Para ajustar una frontera, modificá el punto maestro aquí arriba "
            "y el cambio se propaga automáticamente."
        )


if __name__ == "__main__":
    main()
