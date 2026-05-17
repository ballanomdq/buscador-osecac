import streamlit as st
import folium
from supabase import create_client
import random
import tempfile
import os

st.set_page_config(page_title="Mapa de Zonas - OSECAC", layout="wide", initial_sidebar_state="collapsed")

# ── Conexión a Supabase ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

st.markdown("""
<style>
.main-header { background-color: #1e293b; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #3b82f6; }
.main-header h2 { color: #ffffff; margin: 0; font-size: 1.2rem; }
.main-header p { color: #94a3b8; margin: 0; font-size: 0.75rem; }
div[data-testid="stButton"] button { background-color: #3b82f6; color: white; border: none; padding: 0.2rem 0.5rem; font-size: 0.75rem; border-radius: 4px; }
div[data-testid="stButton"] button:hover { background-color: #2563eb; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>🗺️ Mapa de Zonas por Inspector</h2>
    <p>Visualización geográfica de las zonas asignadas a cada inspector en Mar del Plata</p>
</div>
""", unsafe_allow_html=True)

col_back, _ = st.columns([1, 11])
with col_back:
    if st.button("← Volver"):
        st.switch_page("pages/zonas.py")

st.markdown("---")

# ── Obtener inspectores desde Supabase ───────────────────────────────────────
inspectores_db = supabase.table("inspectores").select("*").order("legajo").execute()
inspectores = inspectores_db.data if inspectores_db.data else []

if not inspectores:
    st.warning("No hay inspectores cargados en la base de datos")
    st.stop()

# ── Obtener calles por inspector ──────────────────────────────────────────────
def get_calles_por_inspector(legajo):
    calles = supabase.table("zonas_inspectores").select("*").eq("legajo", legajo).execute()
    return calles.data if calles.data else []

# ── Colores para cada inspector ───────────────────────────────────────────────
colores = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#F0B27A", "#85C1E9"]

colores_inspectores = {}
for i, ins in enumerate(inspectores):
    colores_inspectores[ins['legajo']] = colores[i % len(colores)]

# ── Centro de Mar del Plata ──────────────────────────────────────────────────
centro_mdp = [-38.0055, -57.5426]

# ── Diccionario de calles principales con coordenadas aproximadas ─────────────
calles_coordenadas = {
    "AV COLON": [-38.0000, -57.5600],
    "CATAMARCA": [-37.9980, -57.5550],
    "AV JARA": [-37.9950, -57.5480],
    "AV TEJEDOR": [-38.0020, -57.5700],
    "HIPOLITO YRIGOYEN": [-38.0030, -57.5400],
    "SAN LUIS": [-38.0050, -57.5450],
    "SANTA FE": [-38.0020, -57.5500],
    "AV PATRICIO PERALTA RAMOS": [-38.0100, -57.5600],
    "AV MARIO BRAVO": [-38.0200, -57.5800],
    "ACHA": [-37.9900, -57.5300],
    "AV JUAN B JUSTO": [-37.9850, -57.5350],
    "AV DE LOS TRABAJADORES": [-38.0150, -57.5900],
}

# ── Crear el mapa ────────────────────────────────────────────────────────────
st.info("🗺️ Generando mapa interactivo...")

m = folium.Map(location=centro_mdp, zoom_start=13, tiles="cartodbpositron")

# Marcador centro
folium.Marker(
    location=centro_mdp,
    popup="<b>Mar del Plata</b><br>Centro",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)

# ── Para cada inspector, agregar sus calles al mapa ──────────────────────────
for ins in inspectores:
    legajo = ins['legajo']
    nombre_corto = ins['nombre'].split(',')[0]
    color = colores_inspectores[legajo]
    calles = get_calles_por_inspector(legajo)
    
    if calles:
        grupo = folium.FeatureGroup(name=f"👤 {nombre_corto} (Legajo {legajo})")
        
        for calle in calles:
            nombre_calle = calle['calle']
            lado = calle['lado']
            desde = calle['altura_desde']
            hasta = calle['altura_hasta']
            
            if nombre_calle in calles_coordenadas:
                coords = calles_coordenadas[nombre_calle]
            else:
                coords = [centro_mdp[0] + random.uniform(-0.05, 0.05), 
                          centro_mdp[1] + random.uniform(-0.05, 0.05)]
            
            popup_text = f"""
            <b>Inspector:</b> {nombre_corto}<br>
            <b>Calle:</b> {nombre_calle}<br>
            <b>Lado:</b> {lado}<br>
            <b>Alturas:</b> {desde} a {hasta}
            """
            
            folium.CircleMarker(
                location=coords,
                radius=8,
                popup=folium.Popup(popup_text, max_width=300),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                tooltip=f"{nombre_calle} ({lado})"
            ).add_to(grupo)
        
        folium.Circle(
            location=centro_mdp,
            radius=2000,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.1,
            popup=f"Zona aproximada: {nombre_corto}"
        ).add_to(grupo)
        
        grupo.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

# ── Guardar y mostrar el mapa como HTML ──────────────────────────────────────
with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
    m.save(tmp.name)
    with open(tmp.name, 'r', encoding='utf-8') as f:
        html_content = f.read()
    os.unlink(tmp.name)

st.components.v1.html(html_content, height=650, width=900)

st.markdown("---")
st.caption("📌 Los marcadores representan las calles asignadas a cada inspector. Use el ☰ arriba a la derecha para ocultar/mostrar inspectores.")
