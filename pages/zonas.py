import streamlit as st
import pandas as pd
from supabase import create_client
import re

st.set_page_config(page_title="Zonas de Inspectores - OSECAC", layout="wide", initial_sidebar_state="collapsed")

SUPABASE_URL_ACTAS = st.secrets["SUPABASE_URL_ACTAS"]
SUPABASE_KEY_ACTAS = st.secrets["SUPABASE_KEY_ACTAS"]
supabase = create_client(SUPABASE_URL_ACTAS, SUPABASE_KEY_ACTAS)

st.markdown("""
<style>
.main-header { background-color: #1e293b; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #3b82f6; }
div[data-testid="stButton"] button { background-color: #3b82f6; color: white; border: none; padding: 0.2rem 0.5rem; font-size: 0.75rem; }
div[data-testid="stButton"] button:hover { background-color: #2563eb; }
.stDataFrame { font-size: 0.75rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2 style="color: #ffffff; margin: 0; font-size: 1.2rem;">🗺️ Zonas de Inspectores</h2>
</div>
""", unsafe_allow_html=True)

col_back, _ = st.columns([1, 5])
with col_back:
    if st.button("← Volver", key="btn_volver_zonas"):
        st.switch_page("main.py")

st.markdown("---")

def normalizar_localidad(loc):
    """Normaliza localidad para GUARDAR: MAYÚSCULAS, sin puntos, sin espacios dobles"""
    if not loc:
        return ""
    loc = loc.upper().strip()
    loc = loc.replace('.', '')
    loc = re.sub(r'\s+', ' ', loc)
    # Reemplazos comunes
    reemplazos = {
        "GRAL": "GENERAL", "CNEL": "CORONEL", "CTE": "COMANDANTE", "CMTE": "COMANDANTE",
        "DR": "DOCTOR", "ING": "INGENIERO", "PTE": "PRESIDENTE", "STA": "SANTA",
        "BLNRIO": "BALNEARIO", "BALNEARIO": "BALNEARIO"
    }
    for abrev, completo in reemplazos.items():
        loc = loc.replace(abrev, completo)
    return loc.strip()

def normalizar_calle(calle):
    if not calle:
        return ""
    calle = calle.upper().strip()
    parentesis = re.search(r'\(([^)]+)\)', calle)
    if parentesis:
        calle = parentesis.group(1)
    for prefijo in ['AV ', 'AV.', 'AVENIDA ', 'CALLE ', 'C/', 'RUTA ', 'RP ']:
        if calle.startswith(prefijo):
            calle = calle[len(prefijo):]
    calle = re.sub(r'^\d+\s+', '', calle)
    calle = calle.replace('.', '')
    calle = calle.replace("SETIEMBRE", "SEPTIEMBRE")
    return calle.strip()

# 🔥 FUNCIÓN PARA FORZAR RECARGA DEL CACHÉ DE ACTAS.PY
def forzar_recarga_cache_actas():
    """Fuerza la recarga de las funciones cacheadas en actas.py"""
    try:
        import sys
        if 'actas' in sys.modules:
            import actas
            if hasattr(actas, 'cargar_inspectores_localidad'):
                actas.cargar_inspectores_localidad.clear()
            if hasattr(actas, 'cargar_zonas_inspectores'):
                actas.cargar_zonas_inspectores.clear()
            if hasattr(actas, 'forzar_recarga_cache'):
                actas.forzar_recarga_cache()
    except Exception as e:
        pass

tab1, tab2, tab3 = st.tabs(["👥 Inspectores", "📍 Localidades", "📍 Calles (MDQ)"])

# ==================== TAB 1: INSPECTORES ====================
with tab1:
    st.markdown("### 👥 Inspectores")
    
    with st.expander("➕ Agregar inspector"):
        with st.form("form_inspector"):
            nombre = st.text_input("Nombre", key="nombre_inspector")
            legajo = st.text_input("Legajo", key="legajo_inspector")
            if st.form_submit_button("Guardar"):
                if nombre and legajo:
                    supabase.table("inspectores").insert({"nombre": nombre, "legajo": legajo}).execute()
                    forzar_recarga_cache_actas()
                    st.success("Agregado")
                    st.rerun()
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if inspectores.data:
        for ins in inspectores.data:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{ins['nombre']}**")
            col2.write(f"Legajo: {ins['legajo']}")
            if col3.button("🗑️", key=f"del_insp_{ins['id']}"):
                supabase.table("inspectores").delete().eq("id", ins['id']).execute()
                forzar_recarga_cache_actas()
                st.rerun()
    else:
        st.info("No hay inspectores")

# ==================== TAB 2: LOCALIDADES ====================
with tab2:
    st.markdown("### 📍 Localidades")
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if not inspectores.data:
        st.warning("Primero cargá inspectores en TAB 1")
    else:
        opts = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        legajo_sel = st.selectbox("Seleccionar inspector", options=list(opts.values()), format_func=lambda x: [k for k, v in opts.items() if v == x][0], key="sel_legajo_localidad")
        
        with st.expander("➕ Agregar localidad (separar variantes con /)"):
            with st.form("form_localidad"):
                st.caption("⚠️ Podés usar paréntesis, ej: SAN BERNARDO (MAR DEL PLATA)")
                localidades = st.text_area("Localidades (ej: BATAN / BARRIO BATAN / MDP)", key="nuevas_localidades")
                if st.form_submit_button("Guardar"):
                    if localidades:
                        for loc in localidades.split('/'):
                            loc = loc.strip()
                            if loc:
                                supabase.table("inspectores_localidad").insert({
                                    "legajo": legajo_sel,
                                    "localidad": normalizar_localidad(loc)
                                }).execute()
                        forzar_recarga_cache_actas()
                        st.success("Localidades agregadas")
                        st.rerun()
        
        localidades = supabase.table("inspectores_localidad").select("*").eq("legajo", legajo_sel).order("localidad").execute()
        if localidades.data:
            for loc in localidades.data:
                col1, col2 = st.columns([4, 1])
                col1.write(loc['localidad'])
                if col2.button("🗑️", key=f"del_loc_{loc['id']}"):
                    supabase.table("inspectores_localidad").delete().eq("id", loc['id']).execute()
                    forzar_recarga_cache_actas()
                    st.rerun()
        else:
            st.info("No hay localidades asignadas")

# ==================== TAB 3: CALLES ====================
with tab3:
    st.markdown("### 📍 Calles (Mar del Plata)")
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if not inspectores.data:
        st.warning("Primero cargá inspectores en TAB 1")
    else:
        opts = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        legajo_sel = st.selectbox("Seleccionar inspector", options=list(opts.values()), format_func=lambda x: [k for k, v in opts.items() if v == x][0], key="sel_legajo_calles")
        
        with st.expander("➕ Agregar calles (formato: Calle (P) 2000-2500)"):
            st.caption("Podés agregar varias calles separadas por '/' (ej: BELGRANO / BELGRA / BELG)")
            bloque = st.text_area("Pegá el bloque de calles", height=100, key="bloque_calles")
            
            if st.button("Previsualizar", key="btn_preview"):
                if bloque:
                    calles = []
                    for parte in bloque.split(' / '):
                        parte = parte.strip()
                        m = re.match(r'^(.*?)\s*\(([PpIiEeY\s]+)\)\s*(\d+)-(\d+)$', parte)
                        if m:
                            calle = m.group(1).strip().upper()
                            lr = m.group(2).strip().upper()
                            if 'P' in lr and 'I' in lr:
                                lado = 'AMBOS'
                            elif 'P' in lr:
                                lado = 'PAR'
                            elif 'I' in lr:
                                lado = 'IMPAR'
                            else:
                                lado = 'AMBOS'
                            calles.append({'calle': calle, 'lado': lado, 'desde': int(m.group(3)), 'hasta': int(m.group(4))})
                    if calles:
                        st.dataframe(pd.DataFrame(calles), use_container_width=True)
                        st.session_state.calles_temp = calles
                    else:
                        st.error("No se pudo parsear")
            
            if st.button("Guardar calles", key="btn_guardar_calles"):
                if st.session_state.get('calles_temp'):
                    supabase.table("zonas_inspectores").delete().eq("legajo", legajo_sel).execute()
                    for c in st.session_state.calles_temp:
                        supabase.table("zonas_inspectores").insert({
                            "legajo": legajo_sel,
                            "calle": c['calle'],
                            "lado": c['lado'],
                            "altura_desde": c['desde'],
                            "altura_hasta": c['hasta']
                        }).execute()
                    forzar_recarga_cache_actas()
                    st.success("Calles guardadas")
                    st.session_state.calles_temp = None
                    st.rerun()
                else:
                    st.warning("Primero hacé clic en Previsualizar")
        
        st.markdown("---")
        st.markdown("### 📋 Calles actuales")
        
        zonas = supabase.table("zonas_inspectores").select("*").eq("legajo", legajo_sel).order("calle").execute()
        if zonas.data:
            df = pd.DataFrame(zonas.data)[['calle', 'lado', 'altura_desde', 'altura_hasta']]
            df.columns = ['Calle', 'Lado', 'Desde', 'Hasta']
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("#### Eliminar calles")
            for zona in zonas.data:
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                col1.write(zona['calle'])
                col2.write(zona['lado'])
                col3.write(f"{zona['altura_desde']}-{zona['altura_hasta']}")
                if col4.button("✏️", key=f"edit_calle_{zona['id']}"):
                    st.session_state.editando_calle = zona
                if col5.button("🗑️", key=f"del_calle_{zona['id']}"):
                    supabase.table("zonas_inspectores").delete().eq("id", zona['id']).execute()
                    forzar_recarga_cache_actas()
                    st.rerun()
            
            if st.session_state.get('editando_calle'):
                st.markdown("### ✏️ Agregar variantes a esta calle")
                editando = st.session_state.editando_calle
                st.write(f"Calle original: **{editando['calle']}** (Lado: {editando['lado']}, Altura: {editando['altura_desde']}-{editando['altura_hasta']})")
                
                nuevas_variantes = st.text_input("Nuevas variantes (separadas por /)", placeholder="Ej: BELGRA / BELG")
                if st.button("Agregar variantes"):
                    if nuevas_variantes:
                        for var in nuevas_variantes.split('/'):
                            var = var.strip().upper()
                            if var:
                                supabase.table("zonas_inspectores").insert({
                                    "legajo": editando['legajo'],
                                    "calle": var,
                                    "lado": editando['lado'],
                                    "altura_desde": editando['altura_desde'],
                                    "altura_hasta": editando['altura_hasta']
                                }).execute()
                        forzar_recarga_cache_actas()
                        st.success("Variantes agregadas")
                        del st.session_state.editando_calle
                        st.rerun()
                
                if st.button("Cancelar edición"):
                    del st.session_state.editando_calle
                    st.rerun()
        else:
            st.info("No hay calles cargadas")
