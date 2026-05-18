import streamlit as st
import folium
from supabase import create_client
import pandas as pd
import requests
import time
from urllib.parse import quote
import tempfile
import os

st.set_page_config(page_title="Mapa de Empresas - OSECAC", layout="wide")

st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
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
}
div[data-testid="stButton"] button:hover { background: #2563eb !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>🗺️ Mapa de Empresas por Inspector</h2>
    <p>Visualización geográfica de las empresas asignadas a cada inspector</p>
</div>
""", unsafe_allow_html=True)

# ── Conexión a Supabase ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

# ── Botón volver ─────────────────────────────────────────────────────────────
col_back, _ = st.columns([1, 11])
with col_back:
    if st.button("← Volver a Fiscalización"):
        st.switch_page("pages/actas.py")

st.markdown("---")

# ── Obtener datos de la base ─────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_empresas():
    datos = supabase.table("padron_deuda_presunta").select("*").execute()
    return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()

@st.cache_data(ttl=300)
def cargar_inspectores():
    datos = supabase.table("inspectores").select("*").order("legajo").execute()
    return datos.data if datos.data else []

# ── Función para geocodificar una dirección (obtener coordenadas reales) ─────
def geocodificar_direccion(calle, numero, localidad):
    """Obtiene coordenadas reales usando Nominatim (OpenStreetMap)"""
    if not calle or calle == "":
        return None
    
    # Construir dirección completa
    direccion = f"{calle} {numero}, {localidad}, Buenos Aires, Argentina"
    direccion_encoded = quote(direccion)
    
    url = f"https://nominatim.openstreetmap.org/search?q={direccion_encoded}&format=json&limit=1"
    
    try:
        # Respetar la política de uso de Nominatim
        time.sleep(0.5)
        
        response = requests.get(url, headers={"User-Agent": "OSECAC-Fiscalizacion/1.0"})
        data = response.json()
        
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return [lat, lon]
        else:
            return None
    except Exception as e:
        return None

# ── Cargar y geocodificar empresas con caché ─────────────────────────────────
@st.cache_data(ttl=86400)  # Cache por 24 horas
def cargar_empresas_con_coordenadas():
    df = cargar_empresas()
    
    if df.empty:
        return df
    
    # Agregar columnas de coordenadas
    df['lat'] = None
    df['lon'] = None
    
    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, row in df.iterrows():
        status_text.text(f"Geocodificando: {row.get('calle', '')} {row.get('numero', '')}")
        
        coords = geocodificar_direccion(
            row.get('calle', ''),
            row.get('numero', ''),
            row.get('localidad', 'MAR DEL PLATA')
        )
        
        if coords:
            df.at[idx, 'lat'] = coords[0]
            df.at[idx, 'lon'] = coords[1]
        
        progress_bar.progress((idx + 1) / len(df))
    
    progress_bar.empty()
    status_text.empty()
    
    return df

# ── Obtener datos ────────────────────────────────────────────────────────────
with st.spinner("Cargando datos y geocodificando direcciones..."):
    df_empresas = cargar_empresas_con_coordenadas()
    inspectores = cargar_inspectores()

if df_empresas.empty:
    st.warning("No hay empresas cargadas en la base de datos.")
    st.stop()

# ── Colores para inspectores ─────────────────────────────────────────────────
paleta_colores = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#F0B27A", "#85C1E9"]

color_por_legajo = {}
for idx, ins in enumerate(inspectores):
    color_por_legajo[ins['legajo']] = paleta_colores[idx % len(paleta_colores)]

# ── Filtros ──────────────────────────────────────────────────────────────────
st.markdown("### 🔍 Filtrar por Inspector")

opciones_inspectores = ["TODOS"] + [f"{ins['nombre']} (Legajo {ins['legajo']})" for ins in inspectores] + ["SIN LEGAJO"]
inspector_seleccionado = st.selectbox("Seleccionar inspector", opciones_inspectores)

# ── Preparar datos para el mapa ──────────────────────────────────────────────
datos_mapa = []
total_sin_coords = 0

for _, row in df_empresas.iterrows():
    legajo = row.get('leg')
    razon_social = row.get('razon_social', 'Sin nombre')
    calle = row.get('calle', '')
    numero = row.get('numero', '')
    localidad = row.get('localidad', '')
    cuit = row.get('cuit', '')
    lat = row.get('lat')
    lon = row.get('lon')
    
    # Solo mostrar empresas con coordenadas válidas
    if lat is None or lon is None:
        total_sin_coords += 1
        continue
    
    # Determinar color y grupo
    if pd.isna(legajo) or legajo is None:
        color = "#FF0000"  # ROJO para sin legajo
        grupo = "SIN LEGAJO"
        nombre_inspector = "Sin asignar"
    else:
        inspector = next((ins for ins in inspectores if ins['legajo'] == legajo), None)
        if inspector:
            nombre_inspector = inspector['nombre'].split(',')[0]
            color = color_por_legajo.get(legajo, "#888888")
            grupo = f"{nombre_inspector} (Legajo {legajo})"
        else:
            color = "#888888"
            nombre_inspector = "Desconocido"
            grupo = "Sin inspector"
    
    # Aplicar filtro
    if inspector_seleccionado == "TODOS":
        pasar = True
    elif inspector_seleccionado == "SIN LEGAJO":
        pasar = (grupo == "SIN LEGAJO")
    else:
        pasar = (grupo == inspector_seleccionado)
    
    if pasar:
        popup_text = f"""
        <div style="min-width: 200px;">
            <b>{razon_social}</b><br>
            <b>CUIT:</b> {cuit}<br>
            <b>Dirección:</b> {calle} {numero}<br>
            <b>Localidad:</b> {localidad}<br>
            <b>Inspector:</b> {nombre_inspector}<br>
            <b>Legajo:</b> {legajo if not pd.isna(legajo) else 'Sin asignar'}
        </div>
        """
        
        datos_mapa.append({
            "coords": [lat, lon],
            "popup": popup_text,
            "color": color,
            "razon_social": razon_social,
            "grupo": grupo
        })

# ── Mostrar estadísticas ─────────────────────────────────────────────────────
st.markdown("---")

if total_sin_coords > 0:
    st.warning(f"⚠️ {total_sin_coords} empresas no tienen coordenadas (dirección no encontrada)")

if not datos_mapa:
    st.info(f"No hay empresas para mostrar con el filtro '{inspector_seleccionado}'")
    st.stop()

col_stats1, col_stats2, col_stats3 = st.columns(3)
with col_stats1:
    st.metric("📍 Empresas en mapa", len(datos_mapa))
with col_stats2:
    con_legajo = sum(1 for d in datos_mapa if d["grupo"] != "SIN LEGAJO")
    st.metric("✅ Con legajo", con_legajo)
with col_stats3:
    sin_legajo = sum(1 for d in datos_mapa if d["grupo"] == "SIN LEGAJO")
    st.metric("❌ Sin legajo", sin_legajo)

st.markdown("---")
st.markdown("### 🗺️ Mapa interactivo")

# ── Crear el mapa ────────────────────────────────────────────────────────────
centro_mdp = [-38.0055, -57.5426]
m = folium.Map(location=centro_mdp, zoom_start=12, tiles="cartodbpositron")

# Agregar marcadores por grupo
grupos = {}
for dato in datos_mapa:
    grupo = dato["grupo"]
    if grupo not in grupos:
        grupos[grupo] = folium.FeatureGroup(name=grupo)
    
    folium.CircleMarker(
        location=dato["coords"],
        radius=6,
        popup=folium.Popup(dato["popup"], max_width=300),
        color=dato["color"],
        fill=True,
        fill_color=dato["color"],
        fill_opacity=0.7,
        tooltip=dato["razon_social"][:30]
    ).add_to(grupos[grupo])

for grupo, feature_group in grupos.items():
    feature_group.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
folium.Marker(location=centro_mdp, popup="<b>Mar del Plata</b><br>Centro", icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)

# ── Guardar y mostrar el mapa como HTML ──────────────────────────────────────
with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
    m.save(tmp.name)
    with open(tmp.name, 'r', encoding='utf-8') as f:
        html_content = f.read()
    os.unlink(tmp.name)

st.components.v1.html(html_content, height=600, width=1000)

# ── Leyenda ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎨 Leyenda de colores")

colores_mostrados = {}
for dato in datos_mapa:
    if dato["grupo"] != "SIN LEGAJO" and dato["grupo"] not in colores_mostrados:
        colores_mostrados[dato["grupo"]] = dato["color"]

cols_leyenda = st.columns(min(len(colores_mostrados) + 2, 4))
idx = 0
for grupo, color in colores_mostrados.items():
    with cols_leyenda[idx % 4]:
        st.markdown(f'<span style="display:inline-block; width:20px; height:20px; background:{color}; border-radius:50%; margin-right:8px;"></span> {grupo}', unsafe_allow_html=True)
    idx += 1

with cols_leyenda[idx % 4]:
    st.markdown('<span style="display:inline-block; width:20px; height:20px; background:#FF0000; border-radius:50%; margin-right:8px;"></span> ❌ Sin legajo', unsafe_allow_html=True)

st.caption(f"📊 Total de empresas en la base: {len(df_empresas)} | Mostradas en el mapa: {len(datos_mapa)} | Sin coordenadas: {total_sin_coords}")
