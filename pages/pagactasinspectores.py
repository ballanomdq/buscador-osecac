import streamlit as st
import pandas as pd
import folium
from supabase import create_client
from datetime import datetime
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

# ── FUNCIONES AGENDA ─────────────────────────────────────────────────────────
def sincronizar_agenda(df_empresas):
    """Sincroniza empresas del inspector con la agenda"""
    if df_empresas.empty:
        return 0
    
    contador = 0
    for _, row in df_empresas.iterrows():
        cuit = row.get('cuit')
        if not cuit:
            continue
        
        direccion = f"{row.get('calle', '')} {row.get('numero', '')}".strip()
        
        # Verificar si existe
        existente = supabase.table("agenda_telefonica").select("*").eq("cuit", str(cuit)).execute()
        
        if existente.data:
            # Actualizar solo si hay cambios
            cambios = False
            update_data = {"ultima_actualizacion": "now()"}
            
            if row.get('razon_social') and row.get('razon_social') != existente.data[0].get('razon_social'):
                update_data["razon_social"] = row.get('razon_social')
                cambios = True
            if row.get('tel_dom_legal') and row.get('tel_dom_legal') != existente.data[0].get('telefono_legal'):
                update_data["telefono_legal"] = row.get('tel_dom_legal')
                cambios = True
            if row.get('tel_dom_real') and row.get('tel_dom_real') != existente.data[0].get('telefono_real'):
                update_data["telefono_real"] = row.get('tel_dom_real')
                cambios = True
            if row.get('email') and row.get('email') != existente.data[0].get('email'):
                update_data["email"] = row.get('email')
                cambios = True
            if direccion and direccion != existente.data[0].get('direccion'):
                update_data["direccion"] = direccion
                cambios = True
            if row.get('localidad') and row.get('localidad') != existente.data[0].get('localidad'):
                update_data["localidad"] = row.get('localidad')
                cambios = True
            
            if cambios:
                supabase.table("agenda_telefonica").update(update_data).eq("cuit", str(cuit)).execute()
                contador += 1
        else:
            # Crear nuevo
            supabase.table("agenda_telefonica").insert({
                "cuit": str(cuit),
                "razon_social": row.get('razon_social', ''),
                "telefono_legal": row.get('tel_dom_legal', ''),
                "telefono_real": row.get('tel_dom_real', ''),
                "email": row.get('email', ''),
                "direccion": direccion,
                "localidad": row.get('localidad', '')
            }).execute()
            contador += 1
    
    return contador

def obtener_agenda():
    """Obtiene toda la agenda"""
    try:
        datos = supabase.table("agenda_telefonica").select("*").order("razon_social").execute()
        return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()
    except:
        return pd.DataFrame()

def agregar_telefono_extra(cuit, telefono):
    """Agrega/modifica teléfono extra"""
    try:
        supabase.table("agenda_telefonica").update({
            "telefono_extra": telefono,
            "ultima_actualizacion": "now()"
        }).eq("cuit", str(cuit)).execute()
        return True
    except:
        return False

def eliminar_telefono_extra(cuit):
    """Elimina teléfono extra"""
    try:
        supabase.table("agenda_telefonica").update({
            "telefono_extra": None,
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
        filtro_cuit = st.text_input("CUIT", placeholder="Buscar por CUIT")
    with col_f2:
        filtro_razon = st.text_input("Razón Social", placeholder="Buscar por razón social")
    
    df_filtrado = df_empresas.copy()
    if filtro_cuit:
        df_filtrado = df_filtrado[df_filtrado['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
    if filtro_razon:
        df_filtrado = df_filtrado[df_filtrado['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
    
    st.markdown(f"**Mostrando {len(df_filtrado)} de {total} registros**")
    
    # Tabla simplificada
    df_mostrar = df_filtrado[['cuit', 'razon_social', 'localidad', 'calle', 'numero', 'tel_dom_legal', 'tel_dom_real', 'vto']].copy()
    df_mostrar.columns = ['CUIT', 'RAZÓN SOCIAL', 'LOCALIDAD', 'CALLE', 'NÚMERO', 'TEL. LEGAL', 'TEL. REAL', 'VTO']
    
    if 'VTO' in df_mostrar.columns:
        df_mostrar['VTO'] = df_mostrar['VTO'].apply(lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else (str(x) if x else ""))
    
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

# ==================== TAB 3: AGENDA MINIMALISTA ====================
with tab_agenda:
    st.markdown("### 📞 Agenda de Contactos")
    st.caption("Los datos se actualizan desde sus empresas asignadas. Puede agregar un teléfono extra por empresa.")
    
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
    
    # Mostrar agenda
    df_agenda = obtener_agenda()
    
    if df_agenda.empty:
        st.info("Agenda vacía. Presione 'Actualizar agenda' para cargar sus empresas.")
    else:
        # Filtrar
        if buscar_cuit:
            df_agenda = df_agenda[df_agenda['cuit'].astype(str).str.contains(buscar_cuit, case=False, na=False)]
        if buscar_razon:
            df_agenda = df_agenda[df_agenda['razon_social'].str.contains(buscar_razon, case=False, na=False)]
        
        st.markdown(f"**📊 {len(df_agenda)} contactos**")
        
        # Mostrar como tabla interactiva simple
        for _, row in df_agenda.iterrows():
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
                
                col_extra1, col_extra2 = st.columns([3, 1])
                with col_extra1:
                    nuevo_extra = st.text_input("", value=extra_actual if extra_actual else "", 
                                                placeholder="Agregar teléfono extra", key=f"extra_{row['cuit']}",
                                                label_visibility="collapsed")
                with col_extra2:
                    if st.button("Guardar", key=f"guardar_{row['cuit']}"):
                        if nuevo_extra:
                            if agregar_telefono_extra(row['cuit'], nuevo_extra):
                                st.success("Guardado")
                                st.rerun()
                        else:
                            if extra_actual and eliminar_telefono_extra(row['cuit']):
                                st.success("Eliminado")
                                st.rerun()

st.markdown("---")
st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
