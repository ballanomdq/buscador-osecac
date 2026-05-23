import streamlit as st
import pandas as pd
import folium
from supabase import create_client
from datetime import datetime
import tempfile
import os
from folium.plugins import Fullscreen, HeatMap
import time
import math

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
    <p>Consulta de empresas | Agenda de contactos</p>
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

# ── FUNCIÓN LIMPIAR ──────────────────────────────────────────────────────────
def limpiar(valor):
    if valor is None:
        return None
    try:
        if isinstance(valor, float) and math.isnan(valor):
            return None
    except:
        pass
    try:
        import pandas as pd
        if pd.isna(valor):
            return None
    except:
        pass
    val_str = str(valor).strip()
    return val_str if val_str and val_str.lower() not in ('nan', 'nat', 'none', '') else None

# ── FUNCIONES AGENDA ─────────────────────────────────────────────────────────
def sincronizar_agenda(df_empresas, progress_bar, status_text):
    """Sincroniza usando UPSERT con barra de progreso"""
    if df_empresas.empty:
        return 0, 0
    
    total = len(df_empresas)
    contador = 0
    errores = 0
    
    for i, (_, row) in enumerate(df_empresas.iterrows()):
        progress = (i + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"Procesando {i+1} de {total}...")
        
        cuit = limpiar(row.get('cuit'))
        if not cuit:
            continue
        
        calle = limpiar(row.get('calle')) or ''
        numero = limpiar(row.get('numero')) or ''
        direccion = f"{calle} {numero}".strip() or None
        
        upsert_data = {
            "cuit": cuit,
            "razon_social": limpiar(row.get('razon_social')) or "",
            "telefono_legal": limpiar(row.get('tel_dom_legal')) or "",
            "telefono_real": limpiar(row.get('tel_dom_real')) or "",
            "email": limpiar(row.get('email')) or "",
            "direccion": direccion,
            "localidad": limpiar(row.get('localidad')) or "",
            "ultima_actualizacion": "now()"
        }
        
        try:
            supabase.table("agenda_telefonica").upsert(
                upsert_data,
                on_conflict="cuit"
            ).execute()
            contador += 1
        except Exception:
            errores += 1
        
        time.sleep(0.005)
    
    return contador, errores

def obtener_agenda():
    try:
        datos = supabase.table("agenda_telefonica").select("*").order("razon_social").execute()
        return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()
    except:
        return pd.DataFrame()

def guardar_telefono_extra(cuit, telefono):
    try:
        supabase.table("agenda_telefonica").update({
            "telefono_extra": telefono if telefono else None,
            "ultima_actualizacion": "now()"
        }).eq("cuit", str(cuit)).execute()
        return True
    except:
        return False

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
with st.spinner("Cargando sus empresas..."):
    df_empresas = cargar_empresas_por_inspector(legajo_seleccionado)
    coordenadas = cargar_coordenadas()

if df_empresas.empty:
    st.warning("No tiene empresas asignadas.")
    st.stop()

# ── Contadores ───────────────────────────────────────────────────────────────
total = len(df_empresas)
con_coords = sum(1 for _, row in df_empresas.iterrows() if coordenadas.get(row['id']))

c1, c2, c3 = st.columns(3)
c1.metric("📋 Total empresas", total)
c2.metric("📍 Con ubicación", con_coords)
c3.metric("⚠️ Sin ubicación", total - con_coords)

st.markdown("---")

# ── PESTAÑAS ─────────────────────────────────────────────────────────────────
t1, t2, t3 = st.tabs(["📋 Listado", "🗺️ Mapa", "📞 Agenda"])

# ==================== TAB 1: LISTADO ====================
with t1:
    st.markdown("### 📋 Listado de empresas")
    
    cf1, cf2 = st.columns(2)
    with cf1:
        f_cuit = st.text_input("CUIT", placeholder="Buscar por CUIT", key="f_cuit")
    with cf2:
        f_razon = st.text_input("Razón Social", placeholder="Buscar por razón social", key="f_razon")
    
    df_filtrado = df_empresas.copy()
    if f_cuit:
        df_filtrado = df_filtrado[df_filtrado['cuit'].astype(str).str.contains(f_cuit, case=False, na=False)]
    if f_razon:
        df_filtrado = df_filtrado[df_filtrado['razon_social'].astype(str).str.contains(f_razon, case=False, na=False)]
    
    st.markdown(f"**Mostrando {len(df_filtrado)} de {total} registros**")
    
    df_mostrar = df_filtrado[['cuit', 'razon_social', 'localidad', 'calle', 'numero', 'tel_dom_legal', 'tel_dom_real', 'vto']].copy()
    df_mostrar.columns = ['CUIT', 'RAZÓN SOCIAL', 'LOCALIDAD', 'CALLE', 'NÚMERO', 'TEL. LEGAL', 'TEL. REAL', 'VTO']
    
    if 'VTO' in df_mostrar.columns:
        df_mostrar['VTO'] = df_mostrar['VTO'].apply(
            lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else (str(x) if x else "")
        )
    
    st.dataframe(df_mostrar, use_container_width=True, height=500)

# ==================== TAB 2: MAPA ====================
with t2:
    st.markdown("### 🗺️ Mapa de ubicaciones")
    
    datos_mapa = []
    for _, row in df_empresas.iterrows():
        coords = coordenadas.get(row['id'])
        if coords:
            popup = f"<b>{limpiar(row.get('razon_social')) or ''}</b><br>CUIT: {limpiar(row.get('cuit')) or ''}"
            datos_mapa.append({"coords": coords, "popup": popup, "nombre": (limpiar(row.get('razon_social')) or '')[:35]})
    
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

# ==================== TAB 3: AGENDA ====================
with t3:
    st.markdown("### 📞 Agenda de Contactos")
    
    if st.button("🔄 ACTUALIZAR AGENDA", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        actualizados, errores = sincronizar_agenda(df_empresas, progress_bar, status_text)
        
        progress_bar.empty()
        status_text.empty()
        
        if actualizados > 0:
            st.success(f"✅ {actualizados} empresas sincronizadas")
        if errores > 0:
            st.warning(f"⚠️ {errores} errores (verifique la tabla)")
        if actualizados == 0 and errores == 0:
            st.info("Agenda al día")
        
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    
    # Buscador
    cb1, cb2 = st.columns(2)
    with cb1:
        buscar_cuit = st.text_input("Buscar por CUIT", placeholder="Ej: 30707685243", key="buscar_cuit")
    with cb2:
        buscar_razon = st.text_input("Buscar por Razón Social", placeholder="Ej: PEPSICO", key="buscar_razon")
    
    df_agenda = obtener_agenda()
    
    if df_agenda.empty:
        st.info("📭 Agenda vacía. Presione 'ACTUALIZAR AGENDA'")
    else:
        if buscar_cuit:
            df_agenda = df_agenda[df_agenda['cuit'].astype(str).str.contains(buscar_cuit, case=False, na=False)]
        if buscar_razon:
            df_agenda = df_agenda[df_agenda['razon_social'].str.contains(buscar_razon, case=False, na=False)]
        
        st.markdown(f"**📊 {len(df_agenda)} contactos**")
        
        for idx, (_, row) in enumerate(df_agenda.iterrows()):
            key = f"emp_{idx}_{row.get('cuit', idx)}"
            
            with st.expander(f"🏢 {row.get('razon_social', 'Sin nombre')}"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown(f"**CUIT:** {row.get('cuit', '—')}")
                    st.markdown(f"**Teléfono legal:** {row.get('telefono_legal', '—')}")
                    st.markdown(f"**Teléfono real:** {row.get('telefono_real', '—')}")
                    st.markdown(f"**Email:** {row.get('email', '—')}")
                
                with col_b:
                    st.markdown(f"**Dirección:** {row.get('direccion', '—')}")
                    st.markdown(f"**Localidad:** {row.get('localidad', '—')}")
                
                st.markdown("---")
                st.markdown("**📱 Teléfono adicional**")
                
                extra_actual = row.get('telefono_extra', '')
                nuevo_extra = st.text_input(
                    "", value=extra_actual or "", 
                    placeholder="Agregar teléfono extra", key=f"inp_{key}",
                    label_visibility="collapsed"
                )
                
                if st.button("Guardar", key=f"btn_{key}"):
                    if guardar_telefono_extra(row['cuit'], nuevo_extra):
                        st.success("Guardado")
                        st.rerun()

st.markdown("---")
st.caption(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
