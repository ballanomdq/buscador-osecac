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
    <h2 style="color: #ffffff; margin: 0; font-size: 1.2rem;">🗺️ Zonas de Inspectores - Gestión Completa</h2>
</div>
""", unsafe_allow_html=True)

col_back, col_reset = st.columns([1, 5])
with col_back:
    if st.button("← Volver", key="btn_volver_zonas"):
        st.switch_page("main.py")
with col_reset:
    if st.button("⚠️ REEMPLAZAR CON DATOS OFICIALES", key="btn_reset_oficial"):
        st.session_state.confirmar_reset = True

if st.session_state.get('confirmar_reset'):
    st.warning("⚠️ Esto BORRARÁ TODAS las zonas actuales y las REEMPLAZARÁ con los 5 inspectores oficiales.")
    col_si, col_no = st.columns(2)
    with col_si:
        if st.button("SÍ, REEMPLAZAR TODO"):
            cargar_datos_oficiales()
            st.session_state.confirmar_reset = False
            st.rerun()
    with col_no:
        if st.button("Cancelar"):
            st.session_state.confirmar_reset = False
            st.rerun()

st.markdown("---")

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

def cargar_datos_oficiales():
    """Carga los 5 inspectores con sus zonas exactas"""
    
    # Datos oficiales
    inspectores = [
        {"legajo": 7713, "nombre": "RODRIGUEZ, Maximiliano"},
        {"legajo": 9513, "nombre": "POLINESSI, Juan José"},
        {"legajo": 9983, "nombre": "LOPEZ, Martín"},
        {"legajo": 9220, "nombre": "CARBAYO, Víctor Hugo"},
        {"legajo": 7952, "nombre": "GARCIA, Juan Paulo"},
    ]
    
    # Zonas por legajo (calle, lado, desde, hasta)
    zonas = [
        # Legajo 7713 - RODRIGUEZ
        (7713, "CATAMARCA", "IMPAR", 2201, 3800),
        (7713, "AV COLON", "IMPAR", 3001, 5400),
        (7713, "AV JARA", "PAR", 2202, 3800),
        (7713, "AV TEJEDOR", "PAR", 1, 2400),
        (7713, "AV PATRICIO PERALTA RAMOS", "AMBOS", 1, 900),
        (7713, "AV FELIX U CAMET", "AMBOS", 1, 1500),
        
        # Legajo 9513 - POLINESSI
        (9513, "AV COLON", "IMPAR", 2401, 3000),
        (9513, "CATAMARCA", "PAR", 1500, 2200),
        (9513, "HIPOLITO YRIGOYEN", "IMPAR", 1501, 2200),
        (9513, "AV PATRICIO PERALTA RAMOS", "AMBOS", 901, 1800),
        (9513, "AV COLON", "IMPAR", 5401, 9999),
        (9513, "AV JARA", "IMPAR", 3801, 9999),
        (9513, "AV TEJEDOR", "IMPAR", 2401, 9999),
        (9513, "AV JOSE COELHO DE MEYRELLES", "AMBOS", 1, 4000),
        (9513, "AV FELIX U CAMET", "AMBOS", 1501, 9999),
        (9513, "RUTA 11 NORTE", "AMBOS", 490, 510),
        
        # Legajo 9983 - LOPEZ
        (9983, "AV COLON", "IMPAR", 1401, 1900),
        (9983, "SAN LUIS", "PAR", 1500, 2200),
        (9983, "SANTA FE", "IMPAR", 1501, 2200),
        (9983, "AV PATRICIO PERALTA RAMOS", "AMBOS", 1801, 2300),
        (9983, "AV COLON", "PAR", 3902, 9999),
        (9983, "SAN JUAN", "IMPAR", 2201, 4400),
        (9983, "PEHUAJO", "IMPAR", 4401, 6000),
        (9983, "AV MARIO BRAVO", "AMBOS", 3901, 9999),
        
        # Legajo 9220 - CARBAYO
        (9220, "AV COLON", "PAR", 1002, 3000),
        (9220, "SAN JUAN", "PAR", 2202, 4400),
        (9220, "PEHUAJO", "PAR", 4402, 6000),
        (9220, "SANTA FE", "PAR", 1500, 2200),
        (9220, "CERRITO", "IMPAR", 1501, 6000),
        (9220, "OLAVARRIA", "IMPAR", 1501, 6000),
        (9220, "AV MARIO BRAVO", "AMBOS", 1, 1000),
        
        # Legajo 7952 - GARCIA
        (7952, "AV COLON", "IMPAR", 1901, 2400),
        (7952, "HIPOLITO YRIGOYEN", "PAR", 1500, 2200),
        (7952, "SAN LUIS", "IMPAR", 1501, 2200),
        (7952, "AV PATRICIO PERALTA RAMOS", "AMBOS", 2301, 2800),
        (7952, "AV COLON", "PAR", 3002, 3900),
        (7952, "SAN JUAN", "PAR", 2202, 6000),
        (7952, "PEHUAJO", "PAR", 2202, 6000),
        (7952, "AV INDEPENDENCIA", "IMPAR", 2201, 4400),
        (7952, "AV JACINTO PERALTA RAMOS", "IMPAR", 4401, 6000),
        (7952, "AV MARIO BRAVO", "AMBOS", 1001, 3900),
        (7952, "ACHA", "PAR", 1, 6000),
        (7952, "AV JUAN B JUSTO", "AMBOS", 1, 3000),
        (7952, "AV DE LOS TRABAJADORES", "AMBOS", 1, 6000),
        (7952, "CALLE 515", "AMBOS", 1, 4000),
        (7952, "AV JORGE NEWBERY", "AMBOS", 1, 6000),
    ]
    
    # Primero, asegurar que los inspectores existan en la tabla 'inspectores'
    for ins in inspectores:
        existing = supabase.table("inspectores").select("*").eq("legajo", ins["legajo"]).execute()
        if not existing.data:
            supabase.table("inspectores").insert(ins).execute()
        else:
            # Actualizar nombre por si cambió
            supabase.table("inspectores").update({"nombre": ins["nombre"]}).eq("legajo", ins["legajo"]).execute()
    
    # Borrar TODAS las zonas existentes
    supabase.table("zonas_inspectores").delete().neq("id", 0).execute()
    
    # Insertar las nuevas zonas
    for legajo, calle, lado, desde, hasta in zonas:
        supabase.table("zonas_inspectores").insert({
            "legajo": legajo,
            "calle": calle,
            "lado": lado,
            "altura_desde": desde,
            "altura_hasta": hasta
        }).execute()
    
    st.success("✅ Datos oficiales cargados correctamente")

def forzar_recarga_cache():
    try:
        import sys
        if 'actas' in sys.modules:
            import actas
            if hasattr(actas, 'cargar_inspectores_localidad'):
                actas.cargar_inspectores_localidad.clear()
            if hasattr(actas, 'cargar_zonas_inspectores'):
                actas.cargar_zonas_inspectores.clear()
    except Exception:
        pass

# ==================== INTERFAZ PRINCIPAL ====================

tab1, tab2, tab3 = st.tabs(["👥 Inspectores", "📍 Localidades", "📍 Calles (MDQ)"])

# TAB 1: INSPECTORES
with tab1:
    st.markdown("### 👥 Inspectores")
    
    with st.expander("➕ Agregar inspector"):
        with st.form("form_inspector"):
            nombre = st.text_input("Nombre")
            legajo = st.text_input("Legajo")
            if st.form_submit_button("Guardar"):
                if nombre and legajo:
                    supabase.table("inspectores").insert({"nombre": nombre, "legajo": legajo}).execute()
                    forzar_recarga_cache()
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
                forzar_recarga_cache()
                st.rerun()
    else:
        st.info("No hay inspectores")

# TAB 2: LOCALIDADES
with tab2:
    st.markdown("### 📍 Localidades fuera de Mar del Plata")
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if not inspectores.data:
        st.warning("Primero cargá inspectores")
    else:
        opts = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        legajo_sel = st.selectbox("Seleccionar inspector", options=list(opts.values()), format_func=lambda x: [k for k, v in opts.items() if v == x][0], key="sel_legajo_localidad")
        
        with st.expander("➕ Agregar localidad"):
            with st.form("form_localidad"):
                localidad = st.text_input("Nombre de la localidad")
                if st.form_submit_button("Guardar"):
                    if localidad:
                        supabase.table("inspectores_localidad").insert({
                            "legajo": legajo_sel,
                            "localidad": localidad.upper().strip()
                        }).execute()
                        forzar_recarga_cache()
                        st.success("Agregada")
                        st.rerun()
        
        localidades = supabase.table("inspectores_localidad").select("*").eq("legajo", legajo_sel).order("localidad").execute()
        if localidades.data:
            for loc in localidades.data:
                col1, col2 = st.columns([4, 1])
                col1.write(loc['localidad'])
                if col2.button("🗑️", key=f"del_loc_{loc['id']}"):
                    supabase.table("inspectores_localidad").delete().eq("id", loc['id']).execute()
                    forzar_recarga_cache()
                    st.rerun()
        else:
            st.info("No hay localidades asignadas")

# TAB 3: CALLES - EDITOR COMPLETO
with tab3:
    st.markdown("### 📍 Calles (Mar del Plata) - Editor Completo")
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if not inspectores.data:
        st.warning("Primero cargá inspectores")
    else:
        opts = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        legajo_sel = st.selectbox("Filtrar por inspector", options=["TODOS"] + list(opts.values()), format_func=lambda x: "TODOS" if x == "TODOS" else [k for k, v in opts.items() if v == x][0], key="sel_legajo_edicion")
        
        # Obtener zonas
        query = supabase.table("zonas_inspectores").select("*")
        if legajo_sel != "TODOS":
            query = query.eq("legajo", legajo_sel)
        zonas = query.order("calle").execute()
        
        if zonas.data:
            # Mostrar tabla editable
            df = pd.DataFrame(zonas.data)[['id', 'legajo', 'calle', 'lado', 'altura_desde', 'altura_hasta']]
            df.columns = ['ID', 'Legajo', 'Calle', 'Lado', 'Desde', 'Hasta']
            
            # Editor en línea
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", disabled=True),
                    "Legajo": st.column_config.NumberColumn("Legajo", required=True),
                    "Calle": st.column_config.TextColumn("Calle", required=True),
                    "Lado": st.column_config.SelectColumn("Lado", options=["PAR", "IMPAR", "AMBOS"], required=True),
                    "Desde": st.column_config.NumberColumn("Desde", required=True),
                    "Hasta": st.column_config.NumberColumn("Hasta", required=True),
                },
                key="editor_calles"
            )
            
            col_save, col_del = st.columns(2)
            with col_save:
                if st.button("💾 GUARDAR CAMBIOS", type="primary"):
                    for idx, row in edited_df.iterrows():
                        original = df.iloc[idx]
                        if (row['Legajo'] != original['Legajo'] or
                            row['Calle'] != original['Calle'] or
                            row['Lado'] != original['Lado'] or
                            row['Desde'] != original['Desde'] or
                            row['Hasta'] != original['Hasta']):
                            
                            supabase.table("zonas_inspectores").update({
                                "legajo": row['Legajo'],
                                "calle": row['Calle'].upper().strip(),
                                "lado": row['Lado'],
                                "altura_desde": row['Desde'],
                                "altura_hasta": row['Hasta']
                            }).eq("id", row['ID']).execute()
                    forzar_recarga_cache()
                    st.success("Cambios guardados")
                    st.rerun()
            
            with col_del:
                eliminar_ids = st.multiselect("Seleccionar IDs para eliminar", df['ID'].tolist())
                if eliminar_ids and st.button("🗑️ ELIMINAR seleccionadas"):
                    for pid in eliminar_ids:
                        supabase.table("zonas_inspectores").delete().eq("id", pid).execute()
                    forzar_recarga_cache()
                    st.success(f"Eliminadas {len(eliminar_ids)} calles")
                    st.rerun()
        else:
            st.info("No hay calles cargadas")
        
        st.markdown("---")
        st.markdown("### ➕ Agregar nueva calle manualmente")
        
        with st.form("form_nueva_calle"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                nueva_calle = st.text_input("Calle")
            with col2:
                nuevo_legajo = st.selectbox("Legajo", options=list(opts.values()), format_func=lambda x: [k for k, v in opts.items() if v == x][0])
            with col3:
                nuevo_lado = st.selectbox("Lado", ["PAR", "IMPAR", "AMBOS"])
            with col4:
                nueva_desde = st.number_input("Desde", min_value=0, value=1)
                nueva_hasta = st.number_input("Hasta", min_value=0, value=9999)
            
            if st.form_submit_button("Agregar calle"):
                if nueva_calle:
                    supabase.table("zonas_inspectores").insert({
                        "legajo": nuevo_legajo,
                        "calle": nueva_calle.upper().strip(),
                        "lado": nuevo_lado,
                        "altura_desde": nueva_desde,
                        "altura_hasta": nueva_hasta
                    }).execute()
                    forzar_recarga_cache()
                    st.success("Calle agregada")
                    st.rerun()
