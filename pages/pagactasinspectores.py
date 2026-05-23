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

# ── FUNCIÓN LIMPIAR (para evitar errores de serialización JSON) ──────────────
def limpiar(valor):
    """Convierte valores no serializables a string limpio o None."""
    if valor is None:
        return None
    try:
        if isinstance(valor, float) and math.isnan(valor):
            return None
    except:
        pass
    # Tipos numpy
    try:
        import numpy as np
        if isinstance(valor, (np.integer, np.int64, np.int32)):
            return int(valor)
        if isinstance(valor, (np.floating, np.float64)):
            return None if np.isnan(valor) else float(valor)
        if isinstance(valor, np.bool_):
            return bool(valor)
    except ImportError:
        pass
    # pandas NaT / NA
    try:
        import pandas as pd
        if pd.isna(valor):
            return None
    except:
        pass
    val_str = str(valor).strip()
    return val_str if val_str and val_str.lower() not in ('nan', 'nat', 'none', '') else None

# ── FUNCIONES AGENDA ─────────────────────────────────────────────────────────
def sincronizar_agenda(df_empresas):
    """Sincroniza empresas del inspector con la agenda"""
    if df_empresas.empty:
        return 0
    
    contador = 0
    for _, row in df_empresas.iterrows():
        cuit = limpiar(row.get('cuit'))
        if not cuit:
            continue
        
        direccion = f"{limpiar(row.get('calle')) or ''} {limpiar(row.get('numero')) or ''}".strip()
        
        existente = supabase.table("agenda_telefonica").select("*").eq("cuit", cuit).execute()
        
        if existente.data:
            update_data = {"ultima_actualizacion": "now()"}
            cambios = False
            
            # Razón social
            razon = limpiar(row.get('razon_social'))
            if razon and razon != existente.data[0].get('razon_social'):
                update_data["razon_social"] = razon
                cambios = True
            
            # Teléfono legal
            tel_legal = limpiar(row.get('tel_dom_legal'))
            if tel_legal and tel_legal != existente.data[0].get('telefono_legal'):
                update_data["telefono_legal"] = tel_legal
                cambios = True
            
            # Teléfono real
            tel_real = limpiar(row.get('tel_dom_real'))
            if tel_real and tel_real != existente.data[0].get('telefono_real'):
                update_data["telefono_real"] = tel_real
                cambios = True
            
            # Email
            email = limpiar(row.get('email'))
            if email and email != existente.data[0].get('email'):
                update_data["email"] = email
                cambios = True
            
            # Dirección
            if direccion and direccion != existente.data[0].get('direccion'):
                update_data["direccion"] = direccion
                cambios = True
            
            # Localidad
            localidad = limpiar(row.get('localidad'))
            if localidad and localidad != existente.data[0].get('localidad'):
                update_data["localidad"] = localidad
                cambios = True
            
            if cambios:
                supabase.table("agenda_telefonica").update(update_data).eq("cuit", cuit).execute()
                contador += 1
        else:
            insert_data = {
                "cuit": cuit,
                "razon_social": limpiar(row.get('razon_social')) or "",
                "telefono_legal": limpiar(row.get('tel_dom_legal')) or "",
                "telefono_real": limpiar(row.get('tel_dom_real')) or "",
                "email": limpiar(row.get('email')) or "",
                "direccion": direccion or None,
                "localidad": limpiar(row.get('localidad')) or "",
            }
            supabase.table("agenda_telefonica").insert(insert_data).execute()
            contador += 1
    
    return contador

def obtener_agenda():
    """Obtiene toda la agenda"""
    try:
        datos = supabase.table("agenda_telefonica").select("*").order("razon_social").execute()
        return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()
    except:
        return pd.DataFrame()

def guardar_telefono_extra(cuit, telefono):
    """Guarda teléfono extra"""
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
tab_lista, tab_mapa, tab_agenda = st.tabs(["📋 Listado", "🗺️ Mapa", "📞 Agenda"])

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
            popup = f"<b>{limpiar(row.get('razon_social')) or ''}</b><br>CUIT: {limpiar(row.get('cuit')) or ''}<br>{limpiar(row.get('calle')) or ''} {limpiar(row.get('numero')) or ''}"
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
with tab_agenda:
    st.markdown("### 📞 Agenda de Contactos")
    
    col_sync1, col_sync2 = st.columns([1, 3])
    with col_sync1:
        if st.button("🔄 Actualizar agenda", type="primary", use_container_width=True):
            with st.spinner("Sincronizando..."):
                actualizados = sincronizar_agenda(df_empresas)
                if actualizados > 0:
                    st.success(f"✅ {actualizados} empresas actualizadas")
                else:
                    st.info("Agenda al día")
                st.cache_data.clear()
                time.sleep(0.5)
                st.rerun()
    
    st.markdown("---")
    
    # Buscador
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        buscar_cuit = st.text_input("Buscar por CUIT", placeholder="Ej: 30707685243", key="buscar_cuit")
    with col_b2:
        buscar_razon = st.text_input("Buscar por Razón Social", placeholder="Ej: PEPSICO", key="buscar_razon")
    
    df_agenda = obtener_agenda()
    
    if df_agenda.empty:
        st.info("Agenda vacía. Presione 'Actualizar agenda' para cargar sus empresas.")
    else:
        if buscar_cuit:
            df_agenda = df_agenda[df_agenda['cuit'].astype(str).str.contains(buscar_cuit, case=False, na=False)]
        if buscar_razon:
            df_agenda = df_agenda[df_agenda['razon_social'].str.contains(buscar_razon, case=False, na=False)]
        
        st.markdown(f"**📊 {len(df_agenda)} contactos**")
        
        for idx, (_, row) in enumerate(df_agenda.iterrows()):
            unique_key = f"empresa_{idx}_{row.get('cuit', idx)}"
            
            with st.expander(f"🏢 {row.get('razon_social', 'Sin nombre')} - {row.get('cuit', 'N/D')}"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**📞 Teléfonos**")
                    st.markdown(f"- Legal: {row.get('telefono_legal', '—')}")
                    st.markdown(f"- Real: {row.get('telefono_real', '—')}")
                    st.markdown(f"✉️ Email: {row.get('email', '—')}")
                
                with col_b:
                    st.markdown("**📍 Dirección**")
                    st.markdown(f"{row.get('direccion', '—')}")
                    st.markdown(f"Localidad: {row.get('localidad', '—')}")
                
                st.markdown("---")
                st.markdown("**📱 Teléfono adicional**")
                
                extra_actual = row.get('telefono_extra', '')
                input_key = f"extra_input_{unique_key}"
                btn_key = f"extra_btn_{unique_key}"
                
                nuevo_extra = st.text_input(
                    "", 
                    value=extra_actual if extra_actual else "", 
                    placeholder="Agregar teléfono extra", 
                    key=input_key,
                    label_visibility="collapsed"
                )
                
                if st.button("Guardar", key=btn_key):
                    if guardar_telefono_extra(row['cuit'], nuevo_extra):
                        st.success("Guardado")
                        st.rerun()

st.markdown("---")
st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
