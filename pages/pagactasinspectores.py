import streamlit as st
import pandas as pd
import folium
from supabase import create_client
from datetime import datetime
import tempfile
import os
from folium.plugins import Fullscreen, HeatMap

st.set_page_config(page_title="Panel de Inspector - OSECAC", layout="wide")

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
    border-radius: 6px !important;
}
div[data-testid="stButton"] button:hover { background: #2563eb !important; }
.stDataFrame { font-size: 0.75rem; }
iframe {
    width: 100% !important;
    height: 60vh !important;
    min-height: 450px !important;
    border: none !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>👤 Panel del Inspector</h2>
    <p>Consulta de empresas asignadas</p>
</div>
""", unsafe_allow_html=True)

col_volver, _ = st.columns([1, 11])
with col_volver:
    if st.button("← Volver al portal"):
        st.switch_page("main.py")

st.markdown("---")

# ── Conexión a Supabase ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

# ── Cargar datos ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_inspectores():
    datos = supabase.table("inspectores").select("*").order("legajo").execute()
    return datos.data if datos.data else []

@st.cache_data(ttl=300)
def cargar_coordenadas():
    datos = supabase.table("coordenadas_empresas").select("id_empresa, lat, lon").execute()
    if datos.data:
        return {d['id_empresa']: (d['lat'], d['lon']) for d in datos.data if d['lat'] is not None}
    return {}

@st.cache_data(ttl=300)
def cargar_empresas_por_inspector(legajo):
    datos = supabase.table("padron_deuda_presunta").select(
        "id", "cuit", "razon_social", "localidad", "calle", "numero", 
        "vto", "acta", "mail_enviado", "tel_dom_legal", "tel_dom_real", 
        "email", "fecha_carga"
    ).eq("leg", legajo).execute()
    return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()

# ── Cargar inspectores ───────────────────────────────────────────────────────
inspectores = cargar_inspectores()

if not inspectores:
    st.warning("No hay inspectores cargados.")
    st.stop()

# ── Selector de inspector ────────────────────────────────────────────────────
opciones_inspectores = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores}

inspector_seleccionado = st.selectbox(
    "Seleccione su inspector",
    options=list(opciones_inspectores.keys()),
    key="selector_inspector"
)

legajo_seleccionado = opciones_inspectores[inspector_seleccionado]
nombre_inspector = inspector_seleccionado.split(" (Legajo")[0]

st.success(f"✅ Bienvenido/a {nombre_inspector}")

st.markdown("---")

# ── Cargar datos ─────────────────────────────────────────────────────────────
with st.spinner("Cargando..."):
    df_empresas = cargar_empresas_por_inspector(legajo_seleccionado)
    coordenadas = cargar_coordenadas()

if df_empresas.empty:
    st.warning("No tiene empresas asignadas.")
    st.stop()

# ── Contadores ───────────────────────────────────────────────────────────────
total = len(df_empresas)
con_coords = sum(1 for _, row in df_empresas.iterrows() if coordenadas.get(row['id']))

col1, col2, col3 = st.columns(3)
col1.metric("📋 Total empresas", total)
col2.metric("📍 Con ubicación", con_coords)
col3.metric("⚠️ Sin ubicación", total - con_coords)

st.markdown("---")

# ── PESTAÑAS ─────────────────────────────────────────────────────────────────
tab_lista, tab_mapa = st.tabs(["📋 Listado", "🗺️ Mapa"])

# ==================== TAB 1: LISTADO ====================
with tab_lista:
    st.markdown("### 📋 Listado de empresas")
    st.caption("🔒 Solo consulta")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_cuit = st.text_input("CUIT", placeholder="Buscar por CUIT", key="filtro_cuit")
    with col_f2:
        filtro_razon = st.text_input("Razón Social", placeholder="Buscar por razón social", key="filtro_razon")
    
    df_filtrado = df_empresas.copy()
    if filtro_cuit:
        df_filtrado = df_filtrado[df_filtrado['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
    if filtro_razon:
        df_filtrado = df_filtrado[df_filtrado['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
    
    st.markdown(f"**Mostrando {len(df_filtrado)} de {total} registros**")
    
    df_mostrar = df_filtrado[['cuit', 'razon_social', 'localidad', 'calle', 'numero', 'tel_dom_legal', 'tel_dom_real', 'vto', 'fecha_carga']].copy()
    df_mostrar.columns = ['CUIT', 'RAZÓN SOCIAL', 'LOCALIDAD', 'CALLE', 'NÚMERO', 'TEL. LEGAL', 'TEL. REAL', 'VTO', 'FECHA CARGA']
    
    for col_fecha in ['VTO', 'FECHA CARGA']:
        if col_fecha in df_mostrar.columns:
            df_mostrar[col_fecha] = df_mostrar[col_fecha].apply(
                lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else (str(x) if x else "")
            )
    
    st.dataframe(df_mostrar, use_container_width=True, height=500)

# ==================== TAB 2: MAPA ====================
with tab_mapa:
    st.markdown("### 🗺️ Mapa de ubicaciones")
    
    datos_mapa = []
    for _, row in df_empresas.iterrows():
        coords = coordenadas.get(row['id'])
        if coords:
            popup = f"<b>{row.get('razon_social', '')}</b><br>CUIT: {row.get('cuit', '')}<br>{row.get('calle', '')} {row.get('numero', '')}"
            datos_mapa.append({"coords": coords, "popup": popup, "nombre": row.get('razon_social', '')[:35]})
    
    if not datos_mapa:
        st.info("No hay empresas con ubicación")
    else:
        centro_lat = sum(d["coords"][0] for d in datos_mapa) / len(datos_mapa)
        centro_lon = sum(d["coords"][1] for d in datos_mapa) / len(datos_mapa)
        
        m = folium.Map(location=[centro_lat, centro_lon], zoom_start=12, tiles="cartodbpositron")
        
        for d in datos_mapa:
            folium.CircleMarker(
                location=d["coords"], radius=8,
                popup=folium.Popup(d["popup"], max_width=300),
                color="#3b82f6", fill=True, fill_opacity=0.7,
                tooltip=d["nombre"]
            ).add_to(m)
        
        if len(datos_mapa) > 3:
            heat_data = [[d["coords"][0], d["coords"][1]] for d in datos_mapa]
            HeatMap(heat_data, radius=15, blur=10).add_to(m)
        
        Fullscreen().add_to(m)
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            m.save(tmp.name)
            with open(tmp.name, 'r') as f:
                st.components.v1.html(f.read(), height=550)
            os.unlink(tmp.name)

st.markdown("---")
st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
