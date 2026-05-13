import streamlit as st
import pandas as pd
from supabase import create_client
import re

# Configuración de página
st.set_page_config(
    page_title="Zonas de Inspectores - OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión a Supabase
SUPABASE_URL_ACTAS = st.secrets["SUPABASE_URL_ACTAS"]
SUPABASE_KEY_ACTAS = st.secrets["SUPABASE_KEY_ACTAS"]
supabase = create_client(SUPABASE_URL_ACTAS, SUPABASE_KEY_ACTAS)

# Estilo
st.markdown("""
<style>
    .main-header { background-color: #1e293b; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #3b82f6; }
    .success-box { background-color: #064e3b; padding: 1rem; border-radius: 6px; border-left: 4px solid #10b981; margin: 1rem 0; color: #ffffff; }
    .info-box { background-color: #1e293b; padding: 1rem; border-radius: 6px; border-left: 4px solid #3b82f6; margin: 1rem 0; color: #ffffff; }
    div[data-testid="stButton"] button { background-color: #3b82f6; color: white; font-weight: 500; border: none; padding: 0.4rem 1.2rem; }
    div[data-testid="stButton"] button:hover { background-color: #2563eb; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h2 style="color: #ffffff; margin: 0; font-weight: 500;">🗺️ Zonas de Inspectores</h2>
    <p style="color: #94a3b8; margin: 0.3rem 0 0 0; font-size: 0.85rem;">Gestión de inspectores y asignación automática de legajos</p>
</div>
""", unsafe_allow_html=True)

# Botón volver
col_back, _ = st.columns([1, 5])
with col_back:
    if st.button("← Volver al inicio"):
        st.switch_page("main.py")

st.markdown("---")

# ==================== PARSING DE CALLES ====================
def parsear_calles(bloque):
    resultados = []
    partes = bloque.split(' / ')
    
    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue
        
        # Formato: "Calle (P) 2000-2500"
        match = re.match(r'^(.*?)\s*\(([PpIiEeY\s]+)\)\s*(\d+)-(\d+)$', parte)
        
        if match:
            calle = match.group(1).strip().upper()
            lado_raw = match.group(2).strip().upper()
            desde = int(match.group(3))
            hasta = int(match.group(4))
            
            if 'P' in lado_raw and 'I' in lado_raw:
                lado = 'AMBOS'
            elif 'P' in lado_raw:
                lado = 'PAR'
            elif 'I' in lado_raw:
                lado = 'IMPAR'
            else:
                lado = 'AMBOS'
            
            resultados.append({'calle': calle, 'lado': lado, 'desde': desde, 'hasta': hasta})
    
    return resultados

# ==================== PESTAÑAS ====================
tab1, tab2, tab3 = st.tabs(["👥 Inspectores", "📍 Zonas", "🔄 Asignar Legajos"])

# ==================== TAB 1: INSPECTORES ====================
with tab1:
    st.markdown("### 👥 Administrar Inspectores")
    
    with st.expander("➕ Agregar inspector"):
        with st.form("form_inspector"):
            nombre = st.text_input("Nombre")
            legajo = st.text_input("Legajo")
            if st.form_submit_button("Guardar"):
                if nombre and legajo:
                    supabase.table("inspectores").insert({"nombre": nombre, "legajo": legajo}).execute()
                    st.success("Agregado")
                    st.rerun()
    
    # Listado
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if inspectores.data:
        for ins in inspectores.data:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{ins['nombre']}**")
            col2.write(f"Legajo: {ins['legajo']}")
            if col3.button("🗑️", key=f"del_{ins['id']}"):
                supabase.table("inspectores").delete().eq("id", ins['id']).execute()
                st.rerun()
    else:
        st.info("No hay inspectores")

# ==================== TAB 2: ZONAS ====================
with tab2:
    st.markdown("### 📍 Cargar calles por inspector")
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    
    if not inspectores.data:
        st.warning("Primero cargá inspectores")
    else:
        # Selector de inspector
        opciones = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        inspector_legajo = st.selectbox("Seleccionar inspector", options=list(opciones.values()), format_func=lambda x: [k for k,v in opciones.items() if v==x][0])
        
        # Bloque de texto para pegar calles
        st.markdown("**Pegá acá las calles (formato: Calle (P) 2000-2500 / Calle2 (I) 1000-2000)**")
        bloque = st.text_area("Bloque de calles", height=150)
        
        if st.button("📋 Previsualizar"):
            if bloque:
                calles = parsear_calles(bloque)
                if calles:
                    df = pd.DataFrame(calles)
                    st.dataframe(df, use_container_width=True)
                    st.session_state.calles_temp = calles
                else:
                    st.error("No se pudo parsear. Verificá el formato.")
        
        if st.button("💾 Guardar todas las calles", type="primary"):
            if st.session_state.get('calles_temp'):
                # Eliminar las existentes y guardar nuevas
                supabase.table("zonas_inspectores").delete().eq("legajo", inspector_legajo).execute()
                for calle in st.session_state.calles_temp:
                    supabase.table("zonas_inspectores").insert({
                        "legajo": inspector_legajo,
                        "calle": calle['calle'],
                        "lado": calle['lado'],
                        "altura_desde": calle['desde'],
                        "altura_hasta": calle['hasta']
                    }).execute()
                st.success("Calles guardadas")
                st.session_state.calles_temp = None
                st.rerun()
            else:
                st.warning("Primero hacé clic en Previsualizar")
        
        # Mostrar calles actuales
        st.markdown("---")
        st.markdown("### 📋 Calles actuales")
        zonas = supabase.table("zonas_inspectores").select("*").eq("legajo", inspector_legajo).order("calle").execute()
        
        if zonas.data:
            df_z = pd.DataFrame(zonas.data)[['calle', 'lado', 'altura_desde', 'altura_hasta']]
            df_z.columns = ['Calle', 'Lado', 'Desde', 'Hasta']
            st.dataframe(df_z, use_container_width=True, hide_index=True)
        else:
            st.info("No hay calles cargadas")

# ==================== TAB 3: ASIGNAR LEGAJOS ====================
with tab3:
    st.markdown("### 🔄 Asignar Legajos Automáticamente")
    
    # Verificar que hay datos
    inspectores = supabase.table("inspectores").select("legajo").execute()
    zonas = supabase.table("zonas_inspectores").select("id").limit(1).execute()
    
    if not inspectores.data:
        st.warning("No hay inspectores cargados")
    elif not zonas.data:
        st.warning("No hay zonas cargadas")
    else:
        sin_legajo = supabase.table("padron_deuda_presunta").select("id", count="exact").is_("leg", "null").execute()
        total = sin_legajo.count
        st.metric("Registros sin legajo", total)
        
        if total == 0:
            st.success("Todos los registros ya tienen legajo")
        else:
            if st.button("🚀 Asignar Legajos", type="primary"):
                with st.spinner("Procesando..."):
                    # Traer todas las zonas
                    todas_zonas = supabase.table("zonas_inspectores").select("*").execute()
                    df_zonas = pd.DataFrame(todas_zonas.data)
                    
                    # Traer registros sin legajo
                    registros = supabase.table("padron_deuda_presunta").select("*").is_("leg", "null").execute()
                    
                    asignados = 0
                    for reg in registros.data:
                        calle = reg.get('calle', '')
                        numero = reg.get('numero', '')
                        
                        if not calle or not numero:
                            continue
                        
                        try:
                            num = int(re.sub(r'\D', '', str(numero)))
                            lado = "PAR" if num % 2 == 0 else "IMPAR"
                            
                            for _, zona in df_zonas.iterrows():
                                if zona['calle'].upper() == calle.upper():
                                    if zona['lado'] == "AMBOS" or zona['lado'] == lado:
                                        if zona['altura_desde'] <= num <= zona['altura_hasta']:
                                            supabase.table("padron_deuda_presunta").update({"leg": zona['legajo']}).eq("id", reg['id']).execute()
                                            asignados += 1
                                            break
                        except:
                            pass
                    
                    st.success(f"✅ {asignados} legajos asignados")
                    st.rerun()
