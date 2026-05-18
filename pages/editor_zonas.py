import streamlit as st
import folium
from supabase import create_client
import json
import tempfile
import os
from folium.plugins import Draw
import requests

st.set_page_config(page_title="Editor de Zonas - OSECAC", layout="wide")

st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    border-left: 4px solid #3b82f6;
}
.main-header h2 { color: white; margin: 0; font-size: 1.3rem; }
.main-header p { color: #94a3b8; margin: 0; font-size: 0.8rem; }
div[data-testid="stButton"] button {
    background: #3b82f6 !important;
    color: white !important;
    border: none !important;
    padding: 0.3rem 1rem !important;
    font-size: 0.8rem !important;
    border-radius: 6px !important;
}
div[data-testid="stButton"] button:hover { background: #2563eb !important; }
div[data-testid="stButton"] button[kind="secondary"] {
    background: #10b981 !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    background: #059669 !important;
}
div[data-testid="stButton"] button[kind="primary"] {
    background: #ef4444 !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: #dc2626 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>🎨 Editor de Zonas por Inspector</h2>
    <p>Dibujá las zonas geográficas de cada inspector directamente en el mapa</p>
</div>
""", unsafe_allow_html=True)

# ── Botones superiores ───────────────────────────────────────────────────────
col_volver, col_guardar, col_eliminar = st.columns([1, 1, 4])

with col_volver:
    if st.button("← Volver a Zonas"):
        st.switch_page("pages/zonas.py")

with col_guardar:
    guardar_click = st.button("💾 GUARDAR ZONA ACTUAL", type="secondary")

with col_eliminar:
    eliminar_click = st.button("🗑️ ELIMINAR ZONA SELECCIONADA", type="primary")

st.markdown("---")

# ── Conexión a Supabase ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

# ── Obtener inspectores ──────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_inspectores():
    datos = supabase.table("inspectores").select("*").order("legajo").execute()
    return datos.data if datos.data else []

inspectores = cargar_inspectores()

if not inspectores:
    st.warning("No hay inspectores cargados")
    st.stop()

# ── Colores por inspector ────────────────────────────────────────────────────
colores_inspectores = {
    "RODRIGUEZ": "#2563eb",
    "POLINESSI": "#10b981",
    "LOPEZ": "#f59e0b",
    "CARBAYO": "#8b5cf6",
    "GARCIA": "#fcd34d",
}

# ── Seleccionar inspector ────────────────────────────────────────────────────
st.markdown("### 1. Seleccionar Inspector")
opciones = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores}
inspector_seleccionado = st.selectbox("Inspector", options=list(opciones.keys()))

legajo_seleccionado = opciones[inspector_seleccionado]
nombre_corto = inspector_seleccionado.split('(')[0].strip().split(',')[0]
color_seleccionado = colores_inspectores.get(nombre_corto.upper(), "#6b7280")

st.markdown(f'<span style="display:inline-block; width:20px; height:20px; background:{color_seleccionado}; border-radius:4px; margin-right:8px;"></span> Color: {color_seleccionado}', unsafe_allow_html=True)

st.markdown("---")

# ── Cargar zona existente ────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_zona(legajo):
    datos = supabase.table("zonas_inspectores_geojson").select("*").eq("legajo", legajo).execute()
    if datos.data and len(datos.data) > 0:
        return datos.data[0].get("geojson")
    return None

zona_existente = cargar_zona(legajo_seleccionado)

# ── Centro de Mar del Plata ──────────────────────────────────────────────────
centro_mdp = [-38.0055, -57.5426]

# ── Crear mapa con herramienta de dibujo ─────────────────────────────────────
st.markdown("### 2. Dibujar la zona en el mapa")
st.caption("💡 Hacé clic en el mapa para marcar los puntos del polígono. Cerrá el polígono haciendo clic en el primer punto.")

m = folium.Map(location=centro_mdp, zoom_start=12, tiles="cartodbpositron")

# Si ya existe una zona, mostrarla en el mapa
if zona_existente:
    try:
        geojson_data = json.loads(zona_existente)
        folium.GeoJson(
            geojson_data,
            style_function=lambda x: {
                'fillColor': color_seleccionado,
                'color': color_seleccionado,
                'weight': 3,
                'fillOpacity': 0.3
            },
            tooltip=f"Zona: {nombre_corto}"
        ).add_to(m)
        st.info(f"📌 Zona existente cargada. Podés dibujar una nueva para reemplazarla.")
    except:
        pass

# Agregar herramienta de dibujo
draw = Draw(
    draw_options={
        'polygon': True,
        'polyline': False,
        'rectangle': False,
        'circle': False,
        'marker': False,
        'circlemarker': False
    },
    edit_options={'edit': True}
)
draw.add_to(m)

# Agregar control de pantalla completa
from folium.plugins import Fullscreen
Fullscreen(position="topleft").add_to(m)

# Guardar el mapa como HTML
with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
    m.save(tmp.name)
    with open(tmp.name, 'r', encoding='utf-8') as f:
        html_content = f.read()
    os.unlink(tmp.name)

st.components.v1.html(html_content, height=600, width=None)

st.markdown("---")
st.markdown("### 3. Instrucciones")
st.markdown("""
1. **Dibujar:** Hacé clic en el ícono de polígono (⏺) en la esquina superior izquierda del mapa
2. **Marcar puntos:** Hacé clic en el mapa para marcar cada vértice del polígono
3. **Cerrar:** Hacé clic en el primer punto para cerrar el polígono
4. **Editar:** Podés arrastrar los puntos después de dibujar
5. **Guardar:** Apretá el botón "💾 GUARDAR ZONA ACTUAL" en la parte superior
""")

# ── Capturar el dibujo del usuario (necesita JavaScript) ─────────────────────
st.markdown("---")
st.markdown("### 4. Datos de la zona dibujada")

# Input para pegar el GeoJSON dibujado
geojson_input = st.text_area(
    "Pegá aquí el GeoJSON del polígono que dibujaste (se genera automáticamente al dibujar)",
    height=150,
    placeholder='{"type":"FeatureCollection","features":[...]}'
)

# Si hay input, mostrar resumen
if geojson_input and geojson_input.strip():
    try:
        geojson_data = json.loads(geojson_input)
        features = geojson_data.get('features', [])
        if features:
            coords = features[0]['geometry']['coordinates'][0]
            st.success(f"✅ Polígono detectado con {len(coords)} puntos")
    except:
        st.warning("GeoJSON inválido")

# ── Guardar zona ─────────────────────────────────────────────────────────────
if guardar_click:
    if not geojson_input or not geojson_input.strip():
        st.error("❌ Primero dibujá una zona en el mapa y copiá el GeoJSON generado")
    else:
        try:
            geojson_data = json.loads(geojson_input)
            
            # Verificar si ya existe
            existente = supabase.table("zonas_inspectores_geojson").select("*").eq("legajo", legajo_seleccionado).execute()
            
            if existente.data:
                supabase.table("zonas_inspectores_geojson").update({
                    "geojson": json.dumps(geojson_data),
                    "color": color_seleccionado,
                    "ultima_actualizacion": "now()"
                }).eq("legajo", legajo_seleccionado).execute()
                st.success(f"✅ Zona de {inspector_seleccionado} actualizada correctamente")
            else:
                supabase.table("zonas_inspectores_geojson").insert({
                    "legajo": legajo_seleccionado,
                    "inspector_nombre": inspector_seleccionado,
                    "geojson": json.dumps(geojson_data),
                    "color": color_seleccionado,
                    "ultima_actualizacion": "now()"
                }).execute()
                st.success(f"✅ Zona de {inspector_seleccionado} guardada correctamente")
            
            st.cache_data.clear()
            st.balloons()
        except Exception as e:
            st.error(f"Error al guardar: {e}")

# ── Eliminar zona ────────────────────────────────────────────────────────────
if eliminar_click:
    supabase.table("zonas_inspectores_geojson").delete().eq("legajo", legajo_seleccionado).execute()
    st.success(f"🗑️ Zona de {inspector_seleccionado} eliminada")
    st.cache_data.clear()
    st.rerun()
