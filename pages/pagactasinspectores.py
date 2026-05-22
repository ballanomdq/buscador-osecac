import streamlit as st
import pandas as pd
import folium
from supabase import create_client
from datetime import datetime
import re
import tempfile
import os
from folium.plugins import Fullscreen, HeatMap
import time

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
.filtro-titulo { font-size: 0.65rem; color: #64748b; margin-bottom: 0.2rem; }
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
    <p>Visualice sus empresas asignadas - Acceso solo de consulta</p>
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

# ── Cargar inspectores ───────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_inspectores():
    datos = supabase.table("inspectores").select("*").order("legajo").execute()
    return datos.data if datos.data else []

# ── Cargar coordenadas de empresas ───────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_coordenadas():
    datos = supabase.table("coordenadas_empresas").select("id_empresa, lat, lon").execute()
    if datos.data:
        return {d['id_empresa']: (d['lat'], d['lon']) for d in datos.data if d['lat'] is not None}
    return {}

# ── Cargar empresas por inspector ────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_empresas_por_inspector(legajo):
    datos = supabase.table("padron_deuda_presunta").select("*").eq("leg", legajo).execute()
    return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()

# ── Cargar inspectores ───────────────────────────────────────────────────────
inspectores = cargar_inspectores()

if not inspectores:
    st.warning("No hay inspectores cargados en el sistema.")
    st.stop()

# ── Selector de inspector ────────────────────────────────────────────────────
st.markdown("### 🔑 Seleccione su inspector")

# Crear opciones para el selector
opciones_inspectores = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores}

col_insp1, col_insp2 = st.columns([2, 1])
with col_insp1:
    inspector_seleccionado = st.selectbox(
        "Inspector",
        options=list(opciones_inspectores.keys()),
        key="selector_inspector"
    )

legajo_seleccionado = opciones_inspectores[inspector_seleccionado]
nombre_inspector = inspector_seleccionado.split(" (Legajo")[0]

st.success(f"✅ Bienvenido/a {nombre_inspector} - Visualizando sus empresas asignadas")

st.markdown("---")

# ── Cargar datos del inspector ───────────────────────────────────────────────
with st.spinner("Cargando sus empresas..."):
    df_empresas = cargar_empresas_por_inspector(legajo_seleccionado)
    coordenadas = cargar_coordenadas()

if df_empresas.empty:
    st.warning(f"No tiene empresas asignadas. {nombre_inspector} aún no tiene registros.")
    st.stop()

# ── Contadores ───────────────────────────────────────────────────────────────
total_registros = len(df_empresas)
con_coordenadas = 0
sin_coordenadas = 0
for _, row in df_empresas.iterrows():
    if coordenadas.get(row['id']) is not None:
        con_coordenadas += 1
    else:
        sin_coordenadas += 1

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    st.metric("📋 Total de empresas", total_registros)
with col_c2:
    st.metric("📍 Con ubicación", con_coordenadas)
with col_c3:
    st.metric("⚠️ Sin ubicación", sin_coordenadas)

st.markdown("---")

# ── Pestañas ─────────────────────────────────────────────────────────────────
tab_lista, tab_mapa = st.tabs(["📋 Listado de Empresas", "🗺️ Mapa de Ubicaciones"])

# ══════════════════════════════════════════════════════════════════
# TAB 1: LISTADO DE EMPRESAS (solo lectura)
# ══════════════════════════════════════════════════════════════════
with tab_lista:
    st.markdown("### 📋 Listado de sus empresas")
    st.caption("🔒 Modo solo consulta - No se pueden editar datos")
    
    # ── Filtros ──
    st.markdown("#### 🔎 Filtros de búsqueda")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown('<p class="filtro-titulo">CUIT</p>', unsafe_allow_html=True)
        filtro_cuit = st.text_input("CUIT", key="filtro_cuit_lista", placeholder="Ej: 30707685243", label_visibility="collapsed")
    with col_f2:
        st.markdown('<p class="filtro-titulo">RAZÓN SOCIAL</p>', unsafe_allow_html=True)
        filtro_razon = st.text_input("Razón Social", key="filtro_razon_lista", placeholder="Razón social", label_visibility="collapsed")
    with col_f3:
        st.markdown('<p class="filtro-titulo">CALLE</p>', unsafe_allow_html=True)
        filtro_calle = st.text_input("Calle", key="filtro_calle_lista", placeholder="Ej: San Luis", label_visibility="collapsed")
    
    # Aplicar filtros
    df_filtrado = df_empresas.copy()
    
    if filtro_cuit:
        df_filtrado = df_filtrado[df_filtrado['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
    if filtro_razon:
        df_filtrado = df_filtrado[df_filtrado['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
    if filtro_calle:
        df_filtrado = df_filtrado[df_filtrado['calle'].astype(str).str.contains(filtro_calle, case=False, na=False)]
    
    st.markdown(f"**📊 Mostrando {len(df_filtrado)} de {total_registros} registros**")
    
    # ── Preparar datos para mostrar ──
    df_mostrar = df_filtrado.copy()
    
    # Seleccionar columnas a mostrar
    columnas_mostrar = {
        'cuit': 'CUIT',
        'razon_social': 'RAZÓN SOCIAL',
        'localidad': 'LOCALIDAD',
        'calle': 'CALLE',
        'numero': 'NÚMERO',
        'vto': 'VENCIMIENTO',
        'estado_gestion': 'ESTADO',
        'acta': 'ACTA',
        'mail_enviado': 'MAIL'
    }
    
    df_tabla = pd.DataFrame()
    for col_orig, col_nuevo in columnas_mostrar.items():
        if col_orig in df_mostrar.columns:
            df_tabla[col_nuevo] = df_mostrar[col_orig]
    
    # Formatear fechas
    if 'VENCIMIENTO' in df_tabla.columns:
        df_tabla['VENCIMIENTO'] = df_tabla['VENCIMIENTO'].apply(
            lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else (str(x) if x else "")
        )
    
    # Mostrar tabla (sin edición)
    st.dataframe(df_tabla, use_container_width=True, height=500)
    
    # Botón para descargar CSV
    if st.button("📥 Descargar listado (CSV)", key="btn_descargar_csv"):
        csv_data = df_tabla.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="✅ Hacer clic para descargar",
            data=csv_data,
            file_name=f"empresas_{nombre_inspector.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ══════════════════════════════════════════════════════════════════
# TAB 2: MAPA DE UBICACIONES
# ══════════════════════════════════════════════════════════════════
with tab_mapa:
    st.markdown("### 🗺️ Ubicación de sus empresas")
    st.caption("💡 Los puntos muestran la ubicación aproximada de cada empresa")
    
    # ── Preparar datos para el mapa ──
    datos_mapa = []
    total_sin_coords_mapa = 0
    
    # Obtener color del inspector (amarillo para GARCIA, etc.)
    colores_inspectores = {
        "RODRIGUEZ": "#2563eb",   # Azul
        "POLINESSI": "#10b981",   # Verde
        "LOPEZ": "#f59e0b",       # Naranja
        "CARBAYO": "#8b5cf6",     # Morado
        "GARCIA": "#fcd34d",      # Amarillo
    }
    nombre_corto = nombre_inspector.split(',')[0].upper()
    color_inspector = colores_inspectores.get(nombre_corto, "#3b82f6")
    
    for _, row in df_empresas.iterrows():
        id_empresa = row['id']
        razon_social = row.get('razon_social', 'Sin nombre')
        calle = row.get('calle', '')
        numero = row.get('numero', '')
        localidad = row.get('localidad', '')
        cuit = row.get('cuit', '')
        legajo = row.get('leg', '')
        
        coords = coordenadas.get(id_empresa)
        
        if not coords:
            total_sin_coords_mapa += 1
            continue
        
        lat, lon = coords
        
        popup_text = f"""
        <div style="min-width: 220px;">
            <b>{razon_social}</b><br>
            <b>CUIT:</b> {cuit}<br>
            <b>Dirección:</b> {calle} {numero}<br>
            <b>Localidad:</b> {localidad}<br>
            <b>Legajo:</b> {legajo}
        </div>
        """
        
        datos_mapa.append({
            "coords": [lat, lon],
            "popup": popup_text,
            "razon_social": razon_social
        })
    
    if not datos_mapa:
        st.info(f"📌 No hay empresas con ubicación disponible para {nombre_inspector}. Algunas direcciones pueden no tener coordenadas cargadas.")
    else:
        st.info(f"📍 Mostrando {len(datos_mapa)} de {total_registros} empresas (las que tienen coordenadas cargadas)")
        
        # ── Crear el mapa ──
        # Calcular centro aproximado (promedio de coordenadas)
        centro_lat = sum(d["coords"][0] for d in datos_mapa) / len(datos_mapa)
        centro_lon = sum(d["coords"][1] for d in datos_mapa) / len(datos_mapa)
        
        m = folium.Map(location=[centro_lat, centro_lon], zoom_start=12, tiles="cartodbpositron")
        
        # Agregar marcadores
        for dato in datos_mapa:
            folium.CircleMarker(
                location=dato["coords"],
                radius=8,
                popup=folium.Popup(dato["popup"], max_width=350),
                color=color_inspector,
                fill=True,
                fill_color=color_inspector,
                fill_opacity=0.7,
                tooltip=dato["razon_social"][:35]
            ).add_to(m)
        
        # Agregar heatmap (opcional - muestra densidad)
        heat_data = [[d["coords"][0], d["coords"][1]] for d in datos_mapa]
        if len(heat_data) > 5:
            HeatMap(heat_data, radius=15, blur=10, max_zoom=13).add_to(m)
        
        # Controles
        Fullscreen(position="topleft", title="Pantalla completa", title_cancel="Salir").add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)
        
        # ── Guardar y mostrar el mapa ──
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            m.save(tmp.name)
            with open(tmp.name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            os.unlink(tmp.name)
        
        st.components.v1.html(html_content, height=550, width=None)
        
        # ── Mostrar resumen de la zona ──
        st.markdown("---")
        st.markdown("### 📊 Resumen de su zona")
        
        # Contar empresas por localidad
        localidades_count = df_empresas['localidad'].value_counts().head(10)
        st.markdown("**Distribución por localidad:**")
        for loc, count in localidades_count.items():
            st.markdown(f"- {loc}: {count} empresas")
        
        if total_sin_coords_mapa > 0:
            st.warning(f"⚠️ {total_sin_coords_mapa} empresas no tienen coordenadas cargadas y no aparecen en el mapa. Las direcciones pueden no estar correctamente geocodificadas.")

st.markdown("---")
st.caption(f"🔒 Acceso solo de consulta - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
