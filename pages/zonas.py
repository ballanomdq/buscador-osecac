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
.stSelectbox, .stTextInput { font-size: 0.75rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2 style="color: #ffffff; margin: 0; font-size: 1.2rem;">🗺️ Zonas de Inspectores</h2>
</div>
""", unsafe_allow_html=True)

col_back, _ = st.columns([1, 5])
with col_back:
    if st.button("← Volver"):
        st.switch_page("main.py")

st.markdown("---")

def normalizar_localidad(loc):
    if not loc:
        return ""
    loc = loc.upper().strip()
    reemplazos = {"BLNRIO": "BALNEARIO", "GRAL": "GENERAL", "CNEL": "CORONEL", "CTE": "COMANDANTE", "BS. AS.": "", "BS AS": ""}
    for a, b in reemplazos.items():
        loc = loc.replace(a, b)
    loc = re.sub(r'\s+', ' ', loc).replace('(', '').replace(')', '')
    return loc.strip()

def normalizar_calle(calle):
    if not calle:
        return ""
    calle = calle.upper().strip()
    par = re.search(r'\(([^)]+)\)', calle)
    if par:
        calle = par.group(1)
    for p in ['AV ', 'AV.', 'AVENIDA ', 'CALLE ', 'C/']:
        if calle.startswith(p):
            calle = calle[len(p):]
    calle = re.sub(r'^\d+\s+', '', calle)
    calle = calle.replace("SETIEMBRE", "SEPTIEMBRE")
    return calle.strip()

tab1, tab2, tab3 = st.tabs(["👥 Inspectores", "📍 Localidades", "📍 Calles (MDQ)"])

# ==================== TAB 1: INSPECTORES ====================
with tab1:
    st.markdown("### 👥 Inspectores")
    
    with st.expander("➕ Agregar"):
        with st.form("form_insp"):
            c1, c2 = st.columns(2)
            with c1:
                nombre = st.text_input("Nombre", key="nombre_insp")
            with c2:
                legajo = st.text_input("Legajo", key="legajo_insp")
            if st.form_submit_button("Guardar"):
                if nombre and legajo:
                    supabase.table("inspectores").insert({"nombre": nombre, "legajo": legajo}).execute()
                    st.rerun()
    
    ins = supabase.table("inspectores").select("*").order("legajo").execute()
    if ins.data:
        df = pd.DataFrame(ins.data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        for i, row in df.iterrows():
            c1, c2 = st.columns([4, 1])
            c1.write(f"{row['nombre']} (Legajo {row['legajo']})")
            if c2.button("🗑️", key=f"del_{row['id']}"):
                supabase.table("inspectores").delete().eq("id", row['id']).execute()
                st.rerun()
    else:
        st.info("No hay inspectores")

# ==================== TAB 2: LOCALIDADES ====================
with tab2:
    st.markdown("### 📍 Localidades (fuera de MDQ)")
    
    ins = supabase.table("inspectores").select("*").order("legajo").execute()
    if not ins.data:
        st.warning("Primero cargá inspectores")
    else:
        opts = {f"{i['nombre']} (Legajo {i['legajo']})": i['legajo'] for i in ins.data}
        leg = st.selectbox("Inspector", options=list(opts.values()), format_func=lambda x: [k for k, v in opts.items() if v == x][0])
        
        with st.expander("➕ Agregar localidad"):
            with st.form("form_loc"):
                loc = st.text_input("Localidad")
                if st.form_submit_button("Guardar"):
                    if loc:
                        supabase.table("inspectores_localidad").insert({"legajo": leg, "localidad": normalizar_localidad(loc)}).execute()
                        st.rerun()
        
        locs = supabase.table("inspectores_localidad").select("*").eq("legajo", leg).order("localidad").execute()
        if locs.data:
            for l in locs.data:
                c1, c2 = st.columns([4, 1])
                c1.write(l['localidad'])
                if c2.button("🗑️", key=f"del_loc_{l['id']}"):
                    supabase.table("inspectores_localidad").delete().eq("id", l['id']).execute()
                    st.rerun()
        else:
            st.info("Sin localidades")

# ==================== TAB 3: CALLES (MDQ) ====================
with tab3:
    st.markdown("### 📍 Calles (Mar del Plata)")
    
    ins = supabase.table("inspectores").select("*").order("legajo").execute()
    if not ins.data:
        st.warning("Primero cargá inspectores")
    else:
        opts = {f"{i['nombre']} (Legajo {i['legajo']})": i['legajo'] for i in ins.data}
        leg = st.selectbox("Inspector", options=list(opts.values()), format_func=lambda x: [k for k, v in opts.items() if v == x][0])
        
        with st.expander("➕ Agregar calles (formato: Calle (P) 2000-2500)"):
            bloque = st.text_area("Bloque", height=100, key="bloque_calles")
            if st.button("Previsualizar"):
                calles = []
                for parte in bloque.split(' / '):
                    m = re.match(r'^(.*?)\s*\(([PpIiEeY\s]+)\)\s*(\d+)-(\d+)$', parte.strip())
                    if m:
                        calle = m.group(1).strip().upper()
                        lr = m.group(2).strip().upper()
                        lado = 'AMBOS' if ('P' in lr and 'I' in lr) else ('PAR' if 'P' in lr else ('IMPAR' if 'I' in lr else 'AMBOS'))
                        calles.append({'calle': calle, 'lado': lado, 'desde': int(m.group(3)), 'hasta': int(m.group(4))})
                if calles:
                    st.dataframe(pd.DataFrame(calles), use_container_width=True)
                    st.session_state.calles_temp = calles
            if st.button("Guardar calles"):
                if st.session_state.get('calles_temp'):
                    supabase.table("zonas_inspectores").delete().eq("legajo", leg).execute()
                    for c in st.session_state.calles_temp:
                        supabase.table("zonas_inspectores").insert({
                            "legajo": leg, "calle": c['calle'], "lado": c['lado'],
                            "altura_desde": c['desde'], "altura_hasta": c['hasta']
                        }).execute()
                    st.success("Guardado")
                    st.session_state.calles_temp = None
                    st.rerun()
        
        zonas = supabase.table("zonas_inspectores").select("*").eq("legajo", leg).order("calle").execute()
        if zonas.data:
            df = pd.DataFrame(zonas.data)[['calle', 'lado', 'altura_desde', 'altura_hasta']]
            df.columns = ['Calle', 'Lado', 'Desde', 'Hasta']
            st.dataframe(df, use_container_width=True, hide_index=True)
            for z in zonas.data:
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(z['calle'])
                c2.write(z['lado'])
                c3.write(f"{z['altura_desde']}-{z['altura_hasta']}")
                if c4.button("🗑️", key=f"del_{z['id']}"):
                    supabase.table("zonas_inspectores").delete().eq("id", z['id']).execute()
                    st.rerun()
        else:
            st.info("Sin calles")
