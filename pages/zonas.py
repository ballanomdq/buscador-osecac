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
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2 style="color: #ffffff; margin: 0; font-size: 1.2rem;">🗺️ Zonas de Inspectores - Gestión Completa</h2>
    <p style="color: #94a3b8; margin: 0; font-size: 0.75rem;">Administración de inspectores, localidades y calles (Mar del Plata)</p>
</div>
""", unsafe_allow_html=True)

col_back, _ = st.columns([1, 5])
with col_back:
    if st.button("← Volver", key="btn_volver_zonas"):
        st.switch_page("main.py")

st.markdown("---")

# ==================== FUNCIONES ====================

def limpiar_y_cargar_datos_oficiales():
    """Elimina datos viejos y carga los 5 inspectores oficiales con todas sus calles"""
    
    # 1. Eliminar inspectora Morea si existe (legajo 1234 como ejemplo, o cualquier otra)
    morea = supabase.table("inspectores").select("*").ilike("nombre", "%MOREA%").execute()
    if morea.data:
        for m in morea.data:
            supabase.table("inspectores").delete().eq("id", m['id']).execute()
    
    # 2. Datos oficiales
    inspectores = [
        {"legajo": 7713, "nombre": "RODRIGUEZ, Maximiliano"},
        {"legajo": 9513, "nombre": "POLINESSI, Juan José"},
        {"legajo": 9983, "nombre": "LOPEZ, Martín"},
        {"legajo": 9220, "nombre": "CARBAYO, Víctor Hugo"},
        {"legajo": 7952, "nombre": "GARCIA, Juan Paulo"},
    ]
    
    zonas = [
        # RODRIGUEZ (7713)
        (7713, "CATAMARCA", "IMPAR", 2201, 3800),
        (7713, "AV COLON", "IMPAR", 3001, 5400),
        (7713, "AV JARA", "PAR", 2202, 3800),
        (7713, "AV TEJEDOR", "PAR", 1, 2400),
        (7713, "AV PATRICIO PERALTA RAMOS", "AMBOS", 1, 900),
        (7713, "AV FELIX U CAMET", "AMBOS", 1, 1500),
        
        # POLINESSI (9513)
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
        
        # LOPEZ (9983)
        (9983, "AV COLON", "IMPAR", 1401, 1900),
        (9983, "SAN LUIS", "PAR", 1500, 2200),
        (9983, "SANTA FE", "IMPAR", 1501, 2200),
        (9983, "AV PATRICIO PERALTA RAMOS", "AMBOS", 1801, 2300),
        (9983, "AV COLON", "PAR", 3902, 9999),
        (9983, "SAN JUAN", "IMPAR", 2201, 4400),
        (9983, "PEHUAJO", "IMPAR", 4401, 6000),
        (9983, "AV MARIO BRAVO", "AMBOS", 3901, 9999),
        
        # CARBAYO (9220)
        (9220, "AV COLON", "PAR", 1002, 3000),
        (9220, "SAN JUAN", "PAR", 2202, 4400),
        (9220, "PEHUAJO", "PAR", 4402, 6000),
        (9220, "SANTA FE", "PAR", 1500, 2200),
        (9220, "CERRITO", "IMPAR", 1501, 6000),
        (9220, "OLAVARRIA", "IMPAR", 1501, 6000),
        (9220, "AV MARIO BRAVO", "AMBOS", 1, 1000),
        
        # GARCIA (7952)
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
    
    # 3. Guardar inspectores
    for ins in inspectores:
        existing = supabase.table("inspectores").select("*").eq("legajo", ins["legajo"]).execute()
        if not existing.data:
            supabase.table("inspectores").insert(ins).execute()
        else:
            supabase.table("inspectores").update({"nombre": ins["nombre"]}).eq("legajo", ins["legajo"]).execute()
    
    # 4. Borrar TODAS las zonas viejas
    supabase.table("zonas_inspectores").delete().neq("id", 0).execute()
    
    # 5. Insertar nuevas zonas
    for legajo, calle, lado, desde, hasta in zonas:
        supabase.table("zonas_inspectores").insert({
            "legajo": legajo,
            "calle": calle,
            "lado": lado,
            "altura_desde": desde,
            "altura_hasta": hasta
        }).execute()
    
    st.success("✅ DATOS CARGADOS: 5 inspectores y todas sus calles")
    st.balloons()

def forzar_recarga_cache():
    try:
        import sys
        if 'actas' in sys.modules:
            import actas
            if hasattr(actas, 'cargar_inspectores_localidad'):
                actas.cargar_inspectores_localidad.clear()
            if hasattr(actas, 'cargar_zonas_inspectores'):
                actas.cargar_zonas_inspectores.clear()
    except:
        pass

# ==================== INICIALIZAR DATOS AL ARRANCAR ====================
# Esto corre UNA SOLA VEZ cuando se abre la página
if 'datos_cargados' not in st.session_state:
    with st.spinner("Cargando datos oficiales..."):
        limpiar_y_cargar_datos_oficiales()
        st.session_state.datos_cargados = True
        st.rerun()

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs(["👥 Inspectores", "📍 Localidades", "📍 Calles (MDQ) - Editor"])

# TAB 1: INSPECTORES
with tab1:
    st.markdown("### 👥 Inspectores")
    
    with st.expander("➕ Agregar inspector"):
        with st.form("form_inspector"):
            nombre = st.text_input("Nombre completo")
            legajo = st.text_input("Número de legajo")
            if st.form_submit_button("Guardar"):
                if nombre and legajo:
                    supabase.table("inspectores").insert({"nombre": nombre.upper(), "legajo": int(legajo)}).execute()
                    forzar_recarga_cache()
                    st.rerun()
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if inspectores.data:
        for ins in inspectores.data:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{ins['nombre']}**")
            col2.write(f"Legajo: {ins['legajo']}")
            if col3.button("🗑️", key=f"del_insp_{ins['id']}"):
                # Verificar si tiene zonas
                zonas_asig = supabase.table("zonas_inspectores").select("*").eq("legajo", ins['legajo']).execute()
                if zonas_asig.data:
                    st.warning(f"Este inspector tiene {len(zonas_asig.data)} calles asignadas. Eliminalas primero.")
                else:
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
        legajo_sel = st.selectbox("Seleccionar inspector", options=list(opts.values()), format_func=lambda x: [k for k, v in opts.items() if v == x][0], key="sel_localidad")
        
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

# TAB 3: CALLES - EDITOR FACIL
with tab3:
    st.markdown("### 📍 Calles de Mar del Plata - Editor")
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if not inspectores.data:
        st.warning("Cargando inspectores...")
    else:
        opts = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        
        # Filtro
        filtro = st.selectbox("Filtrar por inspector", options=["TODOS"] + list(opts.values()), 
                              format_func=lambda x: "TODOS" if x == "TODOS" else [k for k, v in opts.items() if v == x][0])
        
        query = supabase.table("zonas_inspectores").select("*")
        if filtro != "TODOS":
            query = query.eq("legajo", filtro)
        zonas = query.order("calle").execute()
        
        if zonas.data:
            st.markdown("#### 🗑️ Eliminar calles (clic en el tacho)")
            
            # Mostrar cada calle con su tacho de basura
            for zona in zonas.data:
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 0.8, 0.8, 1.5, 0.3])
                
                # Nombre inspector
                inspector = next((i for i in inspectores.data if i['legajo'] == zona['legajo']), None)
                nombre_corto = inspector['nombre'].split(',')[0] if inspector else str(zona['legajo'])
                
                col1.write(f"**{zona['calle']}**")
                col2.write(zona['lado'])
                col3.write(str(zona['altura_desde']))
                col4.write(str(zona['altura_hasta']))
                col5.write(nombre_corto)
                
                # Botón eliminar
                if col6.button("🗑️", key=f"del_{zona['id']}"):
                    supabase.table("zonas_inspectores").delete().eq("id", zona['id']).execute()
                    forzar_recarga_cache()
                    st.rerun()
            
            st.markdown("---")
            st.markdown("#### ✏️ EDITAR calle existente")
            
            # Selector para elegir qué calle editar
            calles_lista = [f"{z['calle']} - {z['lado']} ({z['altura_desde']}-{z['altura_hasta']})" for z in zonas.data]
            calle_a_editar = st.selectbox("Seleccionar calle para editar", options=calles_lista)
            
            if calle_a_editar:
                # Encontrar la zona seleccionada
                idx = calles_lista.index(calle_a_editar)
                zona_edit = zonas.data[idx]
                
                with st.form("editar_calle"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        nueva_calle = st.text_input("Calle", value=zona_edit['calle'])
                    with col2:
                        nuevo_lado = st.selectbox("Lado", ["PAR", "IMPAR", "AMBOS"], index=["PAR", "IMPAR", "AMBOS"].index(zona_edit['lado']))
                    with col3:
                        nuevo_desde = st.number_input("Altura desde", value=int(zona_edit['altura_desde']))
                    with col4:
                        nuevo_hasta = st.number_input("Altura hasta", value=int(zona_edit['altura_hasta']))
                    
                    nuevo_legajo = st.selectbox("Inspector", options=list(opts.values()), 
                                                format_func=lambda x: [k for k, v in opts.items() if v == x][0],
                                                index=list(opts.values()).index(zona_edit['legajo']))
                    
                    if st.form_submit_button("💾 GUARDAR CAMBIOS"):
                        supabase.table("zonas_inspectores").update({
                            "calle": nueva_calle.upper().strip(),
                            "lado": nuevo_lado,
                            "altura_desde": int(nuevo_desde),
                            "altura_hasta": int(nuevo_hasta),
                            "legajo": nuevo_legajo
                        }).eq("id", zona_edit['id']).execute()
                        forzar_recarga_cache()
                        st.success("Calle actualizada")
                        st.rerun()
            
            st.markdown("---")
            st.markdown("#### ➕ AGREGAR nueva calle")
            
            with st.form("nueva_calle"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    nueva_calle = st.text_input("Nombre de la calle")
                with col2:
                    nuevo_legajo = st.selectbox("Inspector", options=list(opts.values()), 
                                                format_func=lambda x: [k for k, v in opts.items() if v == x][0],
                                                key="nuevo_legajo")
                with col3:
                    nuevo_lado = st.selectbox("Lado", ["PAR", "IMPAR", "AMBOS"], key="nuevo_lado")
                col4, col5 = st.columns(2)
                with col4:
                    desde = st.number_input("Altura desde", min_value=1, value=1)
                with col5:
                    hasta = st.number_input("Altura hasta", min_value=1, value=9999)
                
                if st.form_submit_button("➕ AGREGAR CALLE"):
                    if nueva_calle:
                        supabase.table("zonas_inspectores").insert({
                            "legajo": nuevo_legajo,
                            "calle": nueva_calle.upper().strip(),
                            "lado": nuevo_lado,
                            "altura_desde": int(desde),
                            "altura_hasta": int(hasta)
                        }).execute()
                        forzar_recarga_cache()
                        st.success("Calle agregada")
                        st.rerun()
        else:
            st.info("No hay calles cargadas")
