import streamlit as st
import folium
from supabase import create_client
import pandas as pd
import requests
import time
from urllib.parse import quote
import tempfile
import os
import hashlib

st.set_page_config(page_title="Mapa de Empresas - OSECAC", layout="wide")

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
iframe {
    width: 100% !important;
    height: 70vh !important;
    min-height: 500px !important;
    border: none !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>🗺️ Mapa de Empresas por Inspector</h2>
    <p>Visualización geográfica de las empresas asignadas a cada inspector</p>
</div>
""", unsafe_allow_html=True)

# ── Botones superiores ───────────────────────────────────────────────────────
col_actas, col_actualizar, col_volver = st.columns([1, 1, 4])

with col_actas:
    if st.button("📋 IR A ACTAS", type="primary"):
        st.switch_page("pages/actas.py")

with col_actualizar:
    actualizar_click = st.button("🔄 ACTUALIZAR COORDENADAS", type="secondary")

with col_volver:
    if st.button("← Volver a Fiscalización"):
        st.switch_page("pages/actas.py")

st.markdown("---")

# ── Conexión a Supabase ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

# ── Obtener datos de la base ─────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_empresas():
    datos = supabase.table("padron_deuda_presunta").select("*").execute()
    return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()

@st.cache_data(ttl=300)
def cargar_inspectores():
    datos = supabase.table("inspectores").select("*").order("legajo").execute()
    return datos.data if datos.data else []

def obtener_hash_direccion(calle, numero, localidad):
    """Genera un hash único para la dirección"""
    direccion = f"{calle}|{numero}|{localidad}".upper().strip()
    return hashlib.md5(direccion.encode()).hexdigest()

# ── Coordenadas de fallback por localidad ────────────────────────────────────
FALLBACK_LOCALIDADES = {
    "MAR DEL PLATA": (-38.0055, -57.5426),
    "BATAN": (-37.9333, -57.7333),
    "SIERRA DE LOS PADRES": (-37.9167, -57.6833),
    "CHAPADMALAL": (-38.1500, -57.6167),
    "MIRAMAR": (-38.2750, -57.8417),
    "NECOCHEA": (-38.5550, -58.7374),
    "BALCARCE": (-37.8400, -58.2550),
}

def geocodificar_direccion(calle, numero, localidad):
    """
    Geocodifica usando tres fuentes en cascada:
    1. API georef del gobierno argentino (mejor cobertura local)
    2. Nominatim (OpenStreetMap) como fallback global
    3. Coordenadas aproximadas de la localidad si todo falla
    """
    if not calle or str(calle).strip() == "":
        return None

    calle_str = str(calle).strip()
    numero_str = str(numero).strip() if numero and str(numero).strip() != "" else ""
    localidad_str = str(localidad).strip().upper() if localidad else "MAR DEL PLATA"

    # ── 1. API georef (Argentina) ────────────────────────────────────────────
    try:
        direccion_completa = f"{calle_str} {numero_str}".strip()
        params = {
            "direccion": direccion_completa,
            "provincia": "Buenos Aires",
            "localidad": localidad_str.title(),
            "max": 1,
            "formato": "json"
        }
        url = "https://apis.datos.gob.ar/georef/api/direcciones"
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if (data.get("direcciones") 
                and len(data["direcciones"]) > 0
                and data["direcciones"][0].get("ubicacion")):
            ub = data["direcciones"][0]["ubicacion"]
            return (float(ub["lat"]), float(ub["lon"]))
    except Exception:
        pass

    time.sleep(0.5)

    # ── 2. Nominatim (OpenStreetMap) ─────────────────────────────────────────
    try:
        query = f"{calle_str} {numero_str}, {localidad_str.title()}, Buenos Aires, Argentina"
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 1, "countrycodes": "ar"}
        headers = {"User-Agent": "OSECAC-Fiscalizacion/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()

        if data and len(data) > 0:
            return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass

    time.sleep(1.0)

    # ── 3. Fallback: centro de la localidad ──────────────────────────────────
    for key, coords in FALLBACK_LOCALIDADES.items():
        if key in localidad_str:
            return coords

    return FALLBACK_LOCALIDADES["MAR DEL PLATA"]

def actualizar_coordenadas(empresas_df, progress_bar, status_text):
    """Actualiza coordenadas en Supabase usando georef + Nominatim + fallback"""
    
    # Obtener coordenadas existentes
    existentes = supabase.table("coordenadas_empresas").select("id_empresa, direccion_hash").execute()
    existentes_dict = {e['id_empresa']: e.get('direccion_hash', '') for e in existentes.data} if existentes.data else {}
    
    actualizados = 0
    no_encontrados = 0
    total = len(empresas_df)
    
    for idx, row in empresas_df.iterrows():
        progreso = (idx + 1) / total
        progress_bar.progress(progreso, text=f"Geocodificando {idx+1} de {total}...")
        
        id_empresa = row['id']
        calle = row.get('calle', '')
        numero = row.get('numero', '')
        localidad = row.get('localidad', 'MAR DEL PLATA')
        
        # Generar hash de la dirección actual
        hash_actual = obtener_hash_direccion(calle, numero, localidad)
        
        # Verificar si necesita actualización
        necesita_actualizar = True
        if id_empresa in existentes_dict:
            if existentes_dict[id_empresa] == hash_actual:
                necesita_actualizar = False
        
        if necesita_actualizar:
            status_text.markdown(f"📍 Procesando: {calle} {numero} - {row.get('razon_social', '')[:35]}...")
            coords = geocodificar_direccion(calle, numero, localidad)
            
            if coords:
                supabase.table("coordenadas_empresas").upsert({
                    "id_empresa": id_empresa,
                    "lat": coords[0],
                    "lon": coords[1],
                    "direccion_hash": hash_actual,
                    "ultima_actualizacion": "now()"
                }).execute()
                actualizados += 1
            else:
                no_encontrados += 1
                supabase.table("coordenadas_empresas").upsert({
                    "id_empresa": id_empresa,
                    "lat": None,
                    "lon": None,
                    "direccion_hash": hash_actual,
                    "ultima_actualizacion": "now()"
                }).execute()
    
    return actualizados, no_encontrados

def cargar_coordenadas():
    """Carga coordenadas desde Supabase"""
    datos = supabase.table("coordenadas_empresas").select("id_empresa, lat, lon").execute()
    if datos.data:
        return {d['id_empresa']: (d['lat'], d['lon']) for d in datos.data if d['lat'] is not None}
    return {}

# ── Cargar datos ─────────────────────────────────────────────────────────────
with st.spinner("Cargando empresas..."):
    df_empresas = cargar_empresas()
    inspectores = cargar_inspectores()

if df_empresas.empty:
    st.warning("No hay empresas cargadas en la base de datos.")
    st.stop()

# ── Actualizar coordenadas si se pide ────────────────────────────────────────
if actualizar_click:
    with st.spinner("Preparando actualización..."):
        st.info("⏳ Geocodificando direcciones usando georef + Nominatim... puede tomar varios minutos.")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        actualizados, no_encontrados = actualizar_coordenadas(df_empresas, progress_bar, status_text)
        
        progress_bar.empty()
        status_text.empty()
        
        if actualizados > 0:
            st.success(f"✅ {actualizados} coordenadas actualizadas correctamente.")
        if no_encontrados > 0:
            st.warning(f"⚠️ {no_encontrados} direcciones no se encontraron.")
        
        st.cache_data.clear()
        st.rerun()

# ── Cargar coordenadas guardadas ─────────────────────────────────────────────
with st.spinner("Cargando coordenadas..."):
    coordenadas = cargar_coordenadas()

# ── Colores fijos para inspectores ───────────────────────────────────────────
colores_inspectores = {
    "RODRIGUEZ": "#2563eb",   # Azul
    "POLINESSI": "#10b981",   # Verde
    "LOPEZ": "#f59e0b",       # Naranja
    "CARBAYO": "#8b5cf6",     # Morado
    "GARCIA": "#fcd34d",      # Amarillo
}
color_sin_legajo = "#ef4444"  # Rojo

color_por_legajo = {}
for ins in inspectores:
    nombre_corto = ins['nombre'].split(',')[0].upper()
    color_por_legajo[ins['legajo']] = colores_inspectores.get(nombre_corto, "#6b7280")

# ── Filtros ──────────────────────────────────────────────────────────────────
st.markdown("### 🔍 Filtrar por Inspector")

opciones_inspectores = ["TODOS"] + [f"{ins['nombre']} (Legajo {ins['legajo']})" for ins in inspectores] + ["SIN LEGAJO"]
inspector_seleccionado = st.selectbox("Seleccionar inspector", opciones_inspectores)

# ── Preparar datos para el mapa ──────────────────────────────────────────────
datos_mapa = []
total_sin_coords = 0
total_sin_legajo_mapa = 0

for _, row in df_empresas.iterrows():
    id_empresa = row['id']
    legajo = row.get('leg')
    razon_social = row.get('razon_social', 'Sin nombre')
    calle = row.get('calle', '')
    numero = row.get('numero', '')
    localidad = row.get('localidad', '')
    cuit = row.get('cuit', '')
    
    coords = coordenadas.get(id_empresa)
    
    if not coords:
        total_sin_coords += 1
        continue
    
    lat, lon = coords
    
    if pd.isna(legajo) or legajo is None:
        color = color_sin_legajo
        grupo = "SIN LEGAJO"
        nombre_inspector = "Sin asignar"
        total_sin_legajo_mapa += 1
    else:
        inspector = next((ins for ins in inspectores if ins['legajo'] == legajo), None)
        if inspector:
            nombre_inspector = inspector['nombre'].split(',')[0]
            color = color_por_legajo.get(legajo, "#6b7280")
            grupo = f"{nombre_inspector} (Legajo {legajo})"
        else:
            color = "#6b7280"
            nombre_inspector = "Desconocido"
            grupo = "Sin inspector"
    
    if inspector_seleccionado == "TODOS":
        pasar = True
    elif inspector_seleccionado == "SIN LEGAJO":
        pasar = (grupo == "SIN LEGAJO")
    else:
        pasar = (grupo == inspector_seleccionado)
    
    if pasar:
        popup_text = f"""
        <div style="min-width: 220px;">
            <b>{razon_social}</b><br>
            <b>CUIT:</b> {cuit}<br>
            <b>Dirección:</b> {calle} {numero}<br>
            <b>Localidad:</b> {localidad}<br>
            <b style="color:{color}">●</b> <b>Inspector:</b> {nombre_inspector}<br>
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

col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
with col_stats1:
    st.metric("📍 Empresas en mapa", len(datos_mapa))
with col_stats2:
    con_legajo = sum(1 for d in datos_mapa if d["grupo"] != "SIN LEGAJO")
    st.metric("✅ Con legajo", con_legajo)
with col_stats3:
    st.metric("❌ Sin legajo", total_sin_legajo_mapa)
with col_stats4:
    st.metric("⚠️ Sin coordenadas", total_sin_coords)

if total_sin_coords > 0:
    st.warning(f"⚠️ {total_sin_coords} empresas sin coordenadas. Usá 'ACTUALIZAR COORDENADAS'.")

st.markdown("---")

if not datos_mapa:
    st.info(f"No hay empresas para mostrar con el filtro '{inspector_seleccionado}'")
    st.stop()

st.markdown("### 🗺️ Mapa interactivo")
st.caption("💡 Zoom, arrastrar, clic para detalles. Pantalla completa (☐ arriba a la izquierda)")

# ── Crear el mapa ────────────────────────────────────────────────────────────
centro_mdp = [-38.0055, -57.5426]
m = folium.Map(location=centro_mdp, zoom_start=12, tiles="cartodbpositron")

grupos = {}
for dato in datos_mapa:
    grupo = dato["grupo"]
    if grupo not in grupos:
        grupos[grupo] = folium.FeatureGroup(name=grupo)
    
    folium.CircleMarker(
        location=dato["coords"],
        radius=7,
        popup=folium.Popup(dato["popup"], max_width=350),
        color=dato["color"],
        fill=True,
        fill_color=dato["color"],
        fill_opacity=0.7,
        tooltip=dato["razon_social"][:35]
    ).add_to(grupos[grupo])

for grupo, feature_group in grupos.items():
    feature_group.add_to(m)

from folium.plugins import Fullscreen
Fullscreen(position="topleft", title="Pantalla completa", title_cancel="Salir").add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

folium.Marker(
    location=centro_mdp,
    popup="<b>Mar del Plata</b><br>Centro",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)

# ── Guardar y mostrar el mapa ────────────────────────────────────────────────
with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
    m.save(tmp.name)
    with open(tmp.name, 'r', encoding='utf-8') as f:
        html_content = f.read()
    os.unlink(tmp.name)

st.components.v1.html(html_content, height=600, width=None)

# ── Leyenda de colores ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎨 Leyenda de inspectores")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f'<span style="display:inline-block; width:20px; height:20px; background:#2563eb; border-radius:50%; margin-right:8px;"></span> RODRIGUEZ', unsafe_allow_html=True)
with col2:
    st.markdown(f'<span style="display:inline-block; width:20px; height:20px; background:#10b981; border-radius:50%; margin-right:8px;"></span> POLINESSI', unsafe_allow_html=True)
with col3:
    st.markdown(f'<span style="display:inline-block; width:20px; height:20px; background:#f59e0b; border-radius:50%; margin-right:8px;"></span> LOPEZ', unsafe_allow_html=True)
with col4:
    st.markdown(f'<span style="display:inline-block; width:20px; height:20px; background:#8b5cf6; border-radius:50%; margin-right:8px;"></span> CARBAYO', unsafe_allow_html=True)
with col5:
    st.markdown(f'<span style="display:inline-block; width:20px; height:20px; background:#fcd34d; border-radius:50%; margin-right:8px;"></span> GARCIA', unsafe_allow_html=True)
with col6:
    st.markdown(f'<span style="display:inline-block; width:20px; height:20px; background:#ef4444; border-radius:50%; margin-right:8px;"></span> ❌ Sin legajo', unsafe_allow_html=True)

st.caption(f"📊 Total: {len(df_empresas)} empresas | En mapa: {len(datos_mapa)} | Sin coordenadas: {total_sin_coords}")
