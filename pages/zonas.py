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
.main-header { background-color: #1e293b; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #3b82f6; }
.main-header h2 { color: #ffffff; margin: 0; font-size: 1.2rem; }
.main-header p { color: #94a3b8; margin: 0; font-size: 0.75rem; }
div[data-testid="stButton"] button { background-color: #3b82f6; color: white; border: none; padding: 0.2rem 0.5rem; font-size: 0.75rem; border-radius: 4px; }
div[data-testid="stButton"] button:hover { background-color: #2563eb; }
div[data-testid="stButton"] button[kind="secondary"] { background-color: #dc2626; }
div[data-testid="stButton"] button[kind="secondary"]:hover { background-color: #b91c1c; }
.stDataFrame { font-size: 0.75rem; }
hr { margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>🗺️ Zonas de Inspectores - Gestión Completa</h2>
    <p>Administración de inspectores, localidades y calles (Mar del Plata)</p>
</div>
""", unsafe_allow_html=True)

col_back, col_reset = st.columns([1, 5])
with col_back:
    if st.button("← Volver", key="btn_volver_zonas"):
        st.switch_page("main.py")
with col_reset:
    if st.button("🚀 BACKUP DE SEGURIDAD", key="btn_reset_oficial", type="primary"):
        st.session_state.confirmar_reset = True

if st.session_state.get('confirmar_reset'):
    st.warning("⚠️ Esta acción BORRARÁ TODAS las zonas actuales y las REEMPLAZARÁ con los datos oficiales de respaldo.")
    
    col_si, col_no = st.columns(2)
    with col_si:
        clave_ingresada = st.text_input("Ingrese la clave de seguridad:", type="password", key="clave_seguridad")
        if st.button("✅ SÍ, RESTAURAR BACKUP"):
            if clave_ingresada == "shaolin1976":
                with st.spinner("Restaurando backup de seguridad..."):
                    cargar_backup_oficial()
                    st.session_state.confirmar_reset = False
                    st.rerun()
            else:
                st.error("❌ Clave de seguridad incorrecta")
    with col_no:
        if st.button("❌ Cancelar"):
            st.session_state.confirmar_reset = False
            st.rerun()

st.markdown("---")

def cargar_backup_oficial():
    """Carga los 5 inspectores con TODAS las calles (BACKUP COMPLETO)"""
    
    inspectores = [
        {"legajo": 7713, "nombre": "RODRIGUEZ, Maximiliano"},
        {"legajo": 9513, "nombre": "POLINESSI, Juan José"},
        {"legajo": 9983, "nombre": "LOPEZ, Martín"},
        {"legajo": 9220, "nombre": "CARBAYO, Víctor Hugo"},
        {"legajo": 7952, "nombre": "GARCIA, Juan Paulo"},
    ]
    
    # BACKUP COMPLETO DE CALLES
    zonas = [
        # INSPECTOR 1: RODRIGUEZ (7713) - Perimetrales
        (7713, "CATAMARCA", "IMPAR", 2201, 3800),
        (7713, "AV COLON", "IMPAR", 3001, 5400),
        (7713, "AV JARA", "PAR", 2202, 3800),
        (7713, "AV TEJEDOR CARLOS", "PAR", 1, 2400),
        (7713, "AV PATRICIO PERALTA RAMOS", "AMBOS", 1, 900),
        (7713, "AV FELIX U CAMET", "AMBOS", 1, 1500),
        # Internas 2201-3800
        (7713, "LA RIOJA", "AMBOS", 2201, 3800),
        (7713, "HNO INDALECIO", "AMBOS", 2201, 3800),
        (7713, "HIPOLITO YRIGOYEN", "AMBOS", 2201, 3800),
        (7713, "MITRE", "AMBOS", 2201, 3800),
        (7713, "SAN LUIS", "AMBOS", 2201, 3800),
        (7713, "CORDOBA", "AMBOS", 2201, 3800),
        (7713, "SANTIAGO DEL ESTERO", "AMBOS", 2201, 3800),
        (7713, "SANTA FE", "AMBOS", 2201, 3800),
        (7713, "CORRIENTES", "AMBOS", 2201, 3800),
        (7713, "ENTRE RIOS", "AMBOS", 2201, 3800),
        (7713, "BUENOS AIRES", "AMBOS", 2201, 3800),
        (7713, "TUCUMAN", "AMBOS", 2201, 3800),
        (7713, "ARENALES", "AMBOS", 2201, 3800),
        (7713, "LAMADRID", "AMBOS", 2201, 3800),
        (7713, "LAS HERAS", "AMBOS", 2201, 3800),
        (7713, "SARMIENTO", "AMBOS", 2201, 3800),
        (7713, "ALSINA", "AMBOS", 2201, 3800),
        (7713, "OLAZABAL", "AMBOS", 2201, 3800),
        (7713, "DEAN FUNES", "AMBOS", 2201, 3800),
        (7713, "GUIDO", "AMBOS", 2201, 3800),
        (7713, "FUNES", "AMBOS", 2201, 3800),
        (7713, "MARIANO MORENO", "AMBOS", 2201, 3800),
        (7713, "MARCONI", "AMBOS", 2201, 3800),
        (7713, "MISIONES", "AMBOS", 2201, 3800),
        (7713, "ITALIA", "AMBOS", 2201, 3800),
        (7713, "DON BOSCO", "AMBOS", 2201, 3800),
        (7713, "NEUQUEN", "AMBOS", 2201, 3800),
        (7713, "AV INDEPENDENCIA", "AMBOS", 2201, 3800),
        (7713, "SALTA", "AMBOS", 2201, 3800),
        (7713, "JUJUY", "AMBOS", 2201, 3800),
        (7713, "ESPAÑA", "AMBOS", 2201, 3800),
        (7713, "20 DE SEPTIEMBRE", "AMBOS", 2201, 3800),
        (7713, "14 DE JULIO", "AMBOS", 2201, 3800),
        (7713, "DORREGO", "AMBOS", 2201, 3800),
        # Internas 3001-5400
        (7713, "HERNANDARIAS", "AMBOS", 3001, 5400),
        (7713, "DON ORIONE", "AMBOS", 3001, 5400),
        (7713, "LUIS AGOTE", "AMBOS", 3001, 5400),
        (7713, "MAGANANES", "AMBOS", 3001, 5400),
        (7713, "AYOLAS", "AMBOS", 3001, 5400),
        (7713, "IRALA", "AMBOS", 3001, 5400),
        (7713, "ORTIZ DE ZARATE", "AMBOS", 3001, 5400),
        (7713, "AV JUAN B JUSTO", "AMBOS", 3001, 5400),
        (7713, "BERMEJO", "AMBOS", 3001, 5400),
        (7713, "ELCANO", "AMBOS", 3001, 5400),
        (7713, "12 DE OCTUBRE", "AMBOS", 3001, 5400),
        (7713, "PAMPA", "AMBOS", 3001, 5400),
        (7713, "CHACO", "AMBOS", 3001, 5400),
        (7713, "LA PAMPA", "AMBOS", 3001, 5400),
        (7713, "SAN JUAN", "AMBOS", 3001, 5400),
        
        # INSPECTOR 2: POLINESSI (9513)
        (9513, "AV COLON", "IMPAR", 2401, 3000),
        (9513, "CATAMARCA", "PAR", 1500, 2200),
        (9513, "HIPOLITO YRIGOYEN", "IMPAR", 1501, 2200),
        (9513, "AV PATRICIO PERALTA RAMOS", "AMBOS", 901, 1800),
        (9513, "AV COLON", "IMPAR", 5401, 9999),
        (9513, "AV JARA", "IMPAR", 3801, 9999),
        (9513, "AV TEJEDOR CARLOS", "IMPAR", 2401, 9999),
        (9513, "AV JOSE COELHO DE MEYRELLES", "AMBOS", 1, 4000),
        (9513, "AV FELIX U CAMET", "AMBOS", 1501, 9999),
        (9513, "RUTA 11 NORTE", "AMBOS", 490, 510),
        (9513, "AV CONSTITUCION", "AMBOS", 1, 9999),
        (9513, "AV PEDRO LURO", "AMBOS", 1, 9999),
        (9513, "AV LIBERTAD", "AMBOS", 1, 9999),
        (9513, "AV FRAY LUIS BELTRAN", "AMBOS", 1, 9999),
        (9513, "AV JOSE MANUEL ESTRADA", "AMBOS", 1, 9999),
        (9513, "AV DELLA PAOLERA", "AMBOS", 1, 9999),
        (9513, "AV ALBERT SCHWEITZER", "AMBOS", 1, 9999),
        (9513, "AV FERMIN ERREA", "AMBOS", 1, 9999),
        (9513, "REPUBLICA NICARAGUA", "AMBOS", 1, 9999),
        (9513, "RUTA 226", "AMBOS", 1, 9999),
        (9513, "SCAGLIA C", "AMBOS", 1, 9999),
        (9513, "C LOS DURAZNOS", "AMBOS", 1, 9999),
        (9513, "MAHATMA GHANDI", "AMBOS", 1, 9999),
        (9513, "SALVADOR VIVA", "IMPAR", 1, 2500),
        (9513, "LA RIOJA", "AMBOS", 1501, 2200),
        (9513, "MITRE", "AMBOS", 1501, 2200),
        (9513, "MORENO", "AMBOS", 2401, 3000),
        (9513, "BELGRANO", "AMBOS", 2401, 3000),
        (9513, "RIVADAVIA", "AMBOS", 2401, 3000),
        (9513, "SAN MARTIN", "AMBOS", 2401, 3000),
        (9513, "AV LURO", "AMBOS", 2401, 3000),
        (9513, "25 DE MAYO", "AMBOS", 2401, 3000),
        (9513, "9 DE JULIO", "AMBOS", 2401, 3000),
        (9513, "3 DE FEBRERO", "AMBOS", 2401, 3000),
        (9513, "11 DE SEPTIEMBRE", "AMBOS", 2401, 3000),
        (9513, "BALCARCE", "AMBOS", 2401, 3000),
        
        # INSPECTOR 3: LOPEZ (9983)
        (9983, "AV COLON", "IMPAR", 1401, 1900),
        (9983, "SAN LUIS", "PAR", 1500, 2200),
        (9983, "SANTA FE", "IMPAR", 1501, 2200),
        (9983, "AV PATRICIO PERALTA RAMOS", "AMBOS", 1801, 2300),
        (9983, "AV COLON", "PAR", 3902, 9999),
        (9983, "SAN JUAN", "IMPAR", 2201, 4400),
        (9983, "PEHUAJO", "IMPAR", 4401, 6000),
        (9983, "AV MARIO BRAVO", "IMPAR", 3901, 9999),
        (9983, "AV VICTORIO TETAMANTI", "AMBOS", 1, 9999),
        (9983, "GUERNICA", "AMBOS", 1, 9999),
        (9983, "CANESA", "AMBOS", 1, 9999),
        (9983, "C GENOVA", "AMBOS", 1, 9999),
        (9983, "JUAN DE DIOS FILIBERTO", "AMBOS", 1, 9999),
        (9983, "AV PRESIDENTE PERON", "AMBOS", 1, 9999),
        (9983, "C 238", "AMBOS", 1, 9999),
        (9983, "ARANA Y GOIRI", "AMBOS", 1, 9999),
        (9983, "SAN FRANCISCO JAVIER", "AMBOS", 1, 9999),
        (9983, "AV JUAN B JUSTO", "AMBOS", 3001, 9999),
        (9983, "SALVADOR VIVA", "AMBOS", 2501, 6000),
        (9983, "MITRE", "AMBOS", 1401, 1900),
        (9983, "SANTIAGO DEL ESTERO", "AMBOS", 1401, 1900),
        (9983, "CORDOBA", "AMBOS", 1401, 1900),
        (9983, "MORENO", "AMBOS", 1401, 1900),
        (9983, "BELGRANO", "AMBOS", 1401, 1900),
        (9983, "RIVADAVIA", "AMBOS", 1401, 1900),
        (9983, "SAN MARTIN", "AMBOS", 1401, 1900),
        (9983, "AV LURO", "AMBOS", 1401, 1900),
        (9983, "25 DE MAYO", "AMBOS", 1401, 1900),
        (9983, "9 DE JULIO", "AMBOS", 1401, 1900),
        (9983, "3 DE FEBRERO", "AMBOS", 1401, 1900),
        (9983, "11 DE SEPTIEMBRE", "AMBOS", 1401, 1900),
        (9983, "BALCARCE", "AMBOS", 1401, 1900),
        (9983, "MALVINAS", "AMBOS", 2201, 4400),
        (9983, "FUNES", "AMBOS", 2201, 4400),
        (9983, "OLAZABAL", "AMBOS", 2201, 4400),
        (9983, "DEAN FUNES", "AMBOS", 2201, 4400),
        
        # INSPECTOR 4: CARBAYO (9220)
        (9220, "AV COLON", "PAR", 1002, 3000),
        (9220, "SAN JUAN", "PAR", 3902, 4400),
        (9220, "PEHUAJO", "PAR", 4402, 6000),
        (9220, "AV MARIO BRAVO", "PAR", 3902, 6000),
        (9220, "CERRITO", "IMPAR", 1501, 6000),
        (9220, "OLAVARRIA", "IMPAR", 1501, 6000),
        (9220, "AV PATRICIO PERALTA RAMOS", "AMBOS", 2801, 3500),
        (9220, "SANTA FE", "PAR", 1500, 2200),
        (9220, "SARMIENTO", "AMBOS", 1501, 2200),
        (9220, "LAS HERAS", "AMBOS", 1501, 2200),
        (9220, "LAMADRID", "AMBOS", 1501, 2200),
        (9220, "ARENALES", "AMBOS", 1501, 2200),
        (9220, "TUCUMAN", "AMBOS", 1501, 2200),
        (9220, "BUENOS AIRES", "AMBOS", 1501, 2200),
        (9220, "ENTRE RIOS", "AMBOS", 1501, 2200),
        (9220, "CORRIENTES", "AMBOS", 1501, 2200),
        (9220, "ALVEAR", "AMBOS", 1501, 2200),
        (9220, "VIAMONTE", "AMBOS", 1501, 2200),
        (9220, "MENDOZA", "AMBOS", 1501, 2200),
        (9220, "PAUNERO", "AMBOS", 1501, 2200),
        (9220, "LAVALLE", "AMBOS", 1501, 2200),
        (9220, "ALSINA", "AMBOS", 1501, 2200),
        (9220, "GUEMES", "AMBOS", 1501, 2200),
        (9220, "GARAY", "AMBOS", 1002, 3000),
        (9220, "CASTELLI", "AMBOS", 1002, 3000),
        (9220, "ALBERTI", "AMBOS", 1002, 3000),
        (9220, "GASCON", "AMBOS", 1002, 3000),
        (9220, "FALUCHO", "AMBOS", 1002, 3000),
        (9220, "BROWN", "AMBOS", 1002, 3000),
        (9220, "AV PASO", "AMBOS", 1002, 3000),
        (9220, "LARREA", "AMBOS", 1002, 3000),
        (9220, "VIEYTES", "AMBOS", 1002, 3000),
        (9220, "MATHEU", "AMBOS", 1002, 3000),
        
        # INSPECTOR 5: GARCIA (7952)
        (7952, "AV COLON", "IMPAR", 1901, 2400),
        (7952, "HIPOLITO YRIGOYEN", "PAR", 1500, 2200),
        (7952, "SAN LUIS", "IMPAR", 1501, 2200),
        (7952, "AV PATRICIO PERALTA RAMOS", "AMBOS", 2301, 2800),
        (7952, "AV COLON", "PAR", 3002, 3900),
        (7952, "SAN JUAN", "PAR", 2202, 3900),
        (7952, "PEHUAJO", "PAR", 2202, 3900),
        (7952, "AV INDEPENDENCIA", "IMPAR", 2201, 4400),
        (7952, "AV JACINTO PERALTA RAMOS", "IMPAR", 4401, 6000),
        (7952, "AV MARIO BRAVO", "AMBOS", 1001, 3900),
        (7952, "ACHA", "PAR", 1, 6000),
        (7952, "AV JUAN B JUSTO", "AMBOS", 1, 3000),
        (7952, "AV DE LOS TRABAJADORES", "AMBOS", 1, 6000),
        (7952, "RUTA 11 SUR", "AMBOS", 1, 6000),
        (7952, "CALLE 515", "AMBOS", 1, 4000),
        (7952, "AV JORGE NEWBERY", "AMBOS", 1, 6000),
        (7952, "CERRITO", "PAR", 1502, 6000),
        (7952, "OLAVARRIA", "PAR", 1502, 6000),
        (7952, "AV PATRICIO PERALTA RAMOS", "AMBOS", 3501, 4500),
        (7952, "CORDOBA", "AMBOS", 1901, 2400),
        (7952, "SANTIAGO DEL ESTERO", "AMBOS", 1901, 2400),
        (7952, "SANTA FE", "AMBOS", 1901, 2400),
        (7952, "MORENO", "AMBOS", 1901, 2400),
        (7952, "BELGRANO", "AMBOS", 1901, 2400),
        (7952, "RIVADAVIA", "AMBOS", 1901, 2400),
        (7952, "SAN MARTIN", "AMBOS", 1901, 2400),
        (7952, "AV LURO", "AMBOS", 1901, 2400),
        (7952, "25 DE MAYO", "AMBOS", 1901, 2400),
        (7952, "9 DE JULIO", "AMBOS", 1901, 2400),
        (7952, "3 DE FEBRERO", "AMBOS", 1901, 2400),
        (7952, "11 DE SEPTIEMBRE", "AMBOS", 1901, 2400),
        (7952, "BALCARCE", "AMBOS", 1901, 2400),
        (7952, "EDISON", "AMBOS", 1, 6000),
        (7952, "POSADAS", "AMBOS", 1, 6000),
        (7952, "RONDEAU", "AMBOS", 1, 6000),
        (7952, "MAGALLANES", "AMBOS", 1, 3000),
        (7952, "12 DE OCTUBRE", "AMBOS", 1, 3000),
        (7952, "ELCANO", "AMBOS", 1, 3000),
        (7952, "PADRE DUTTO", "AMBOS", 1, 6000),
    ]
    
    # Guardar inspectores
    for ins in inspectores:
        existing = supabase.table("inspectores").select("*").eq("legajo", ins["legajo"]).execute()
        if not existing.data:
            supabase.table("inspectores").insert(ins).execute()
        else:
            supabase.table("inspectores").update({"nombre": ins["nombre"]}).eq("legajo", ins["legajo"]).execute()
    
    # Borrar TODAS las zonas existentes
    supabase.table("zonas_inspectores").delete().neq("id", 0).execute()
    
    # Insertar todas las zonas
    for legajo, calle, lado, desde, hasta in zonas:
        supabase.table("zonas_inspectores").insert({
            "legajo": legajo, "calle": calle, "lado": lado,
            "altura_desde": desde, "altura_hasta": hasta
        }).execute()
    
    st.success(f"✅ BACKUP RESTAURADO: {len(zonas)} calles asignadas a 5 inspectores")
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

# Inicializar datos si no están cargados
if 'datos_cargados' not in st.session_state:
    with st.spinner("Cargando datos..."):
        # Verificar si hay datos, si no hay, cargar backup automáticamente
        zonas_existentes = supabase.table("zonas_inspectores").select("id", count="exact").execute()
        if zonas_existentes.count == 0:
            cargar_backup_oficial()
        st.session_state.datos_cargados = True
        st.rerun()

# ==================== TABS ====================
tab1, tab2, tab3, tab4 = st.tabs(["👥 Inspectores", "📍 Localidades", "📍 Calles (MDQ) - Editor", "🔄 Sinónimos"])

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
                zonas_asig = supabase.table("zonas_inspectores").select("*").eq("legajo", ins['legajo']).execute()
                if zonas_asig.data:
                    st.warning(f"Elimine primero las {len(zonas_asig.data)} calles asignadas")
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

# TAB 3: CALLES - EDITOR COMPLETO CON TACHO DE BASURA
with tab3:
    st.markdown("### 📍 Calles de Mar del Plata - Editor Completo")
    st.caption("📝 Podés editar cualquier campo directamente en la tabla. Usá el 🗑️ para eliminar una calle.")
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if not inspectores.data:
        st.warning("Primero cargá inspectores")
    else:
        opts = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        
        # Filtro por inspector
        filtro_legajo = st.selectbox(
            "Filtrar por inspector", 
            options=["TODOS"] + list(opts.values()), 
            format_func=lambda x: "TODOS" if x == "TODOS" else [k for k, v in opts.items() if v == x][0], 
            key="filtro_legajo_calles"
        )
        
        # Obtener zonas
        query = supabase.table("zonas_inspectores").select("*")
        if filtro_legajo != "TODOS":
            query = query.eq("legajo", filtro_legajo)
        zonas = query.order("calle").execute()
        
        if zonas.data:
            # Preparar DataFrame para edición
            df = pd.DataFrame(zonas.data)[['id', 'legajo', 'calle', 'lado', 'altura_desde', 'altura_hasta']]
            df.columns = ['ID', 'Legajo', 'Calle', 'Lado', 'Desde', 'Hasta']
            
            # Agregar columna para el inspector
            inspector_dict = {ins['legajo']: ins['nombre'].split(',')[0] for ins in inspectores.data}
            df['Inspector'] = df['Legajo'].map(inspector_dict)
            
            # Mostrar editor
            st.info("💡 Hacé doble clic en cualquier celda para editar. Los cambios se guardan automáticamente al salir de la celda.")
            
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
                    "Inspector": st.column_config.TextColumn("Inspector", disabled=True),
                },
                key="editor_calles_completo"
            )
            
            # Guardar cambios automáticamente
            for idx, row in edited_df.iterrows():
                original = df.iloc[idx]
                if (row['Legajo'] != original['Legajo'] or
                    row['Calle'] != original['Calle'] or
                    row['Lado'] != original['Lado'] or
                    row['Desde'] != original['Desde'] or
                    row['Hasta'] != original['Hasta']):
                    
                    supabase.table("zonas_inspectores").update({
                        "legajo": int(row['Legajo']),
                        "calle": row['Calle'].upper().strip(),
                        "lado": row['Lado'],
                        "altura_desde": int(row['Desde']),
                        "altura_hasta": int(row['Hasta'])
                    }).eq("id", int(row['ID'])).execute()
                    forzar_recarga_cache()
                    st.toast(f"✅ Actualizado: {row['Calle']}", icon="✅")
                    st.rerun()
            
            st.markdown("---")
            st.markdown("#### 🗑️ Eliminar calle")
            
            # Selector para eliminar con confirmación
            calle_a_eliminar = st.selectbox("Seleccionar calle para eliminar", options=df['Calle'].tolist())
            if calle_a_eliminar:
                fila = df[df['Calle'] == calle_a_eliminar].iloc[0]
                st.warning(f"⚠️ **Eliminar:** {fila['Calle']} - {fila['Lado']} ({fila['Desde']}-{fila['Hasta']}) - Inspector: {fila['Inspector']}")
                
                col_confirm, col_cancel = st.columns(2)
                with col_confirm:
                    if st.button("🗑️ SÍ, ELIMINAR", type="secondary"):
                        supabase.table("zonas_inspectores").delete().eq("id", int(fila['ID'])).execute()
                        forzar_recarga_cache()
                        st.success(f"✅ Eliminada: {fila['Calle']}")
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancelar"):
                        st.rerun()
            
            st.markdown("---")
            st.markdown("#### ➕ Agregar nueva calle")
            
            with st.form("form_nueva_calle", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    nueva_calle = st.text_input("Nombre de la calle", placeholder="Ej: BELGRANO")
                with col2:
                    nuevo_legajo = st.selectbox(
                        "Inspector", 
                        options=list(opts.values()), 
                        format_func=lambda x: [k for k, v in opts.items() if v == x][0]
                    )
                with col3:
                    nuevo_lado = st.selectbox("Lado", ["PAR", "IMPAR", "AMBOS"])
                
                col4, col5 = st.columns(2)
                with col4:
                    nueva_desde = st.number_input("Altura desde", min_value=1, value=1, step=1)
                with col5:
                    nueva_hasta = st.number_input("Altura hasta", min_value=1, value=9999, step=1)
                
                if st.form_submit_button("➕ AGREGAR CALLE"):
                    if nueva_calle:
                        supabase.table("zonas_inspectores").insert({
                            "legajo": int(nuevo_legajo),
                            "calle": nueva_calle.upper().strip(),
                            "lado": nuevo_lado,
                            "altura_desde": int(nueva_desde),
                            "altura_hasta": int(nueva_hasta)
                        }).execute()
                        forzar_recarga_cache()
                        st.success(f"✅ Calle {nueva_calle.upper()} agregada")
                        st.rerun()
                    else:
                        st.error("El nombre de la calle es obligatorio")
        else:
            st.info("No hay calles cargadas")

# TAB 4: SINÓNIMOS
with tab4:
    st.markdown("### 🔄 Sinónimos de Calles")
    st.caption("Acá podés agregar sinónimos para que el sistema reconozca formas alternativas de escribir las calles")
    
    # Verificar tabla
    try:
        supabase.table("sinonimos_calles").select("id").limit(1).execute()
    except:
        st.error("La tabla 'sinonimos_calles' no existe. Ejecutá este SQL en Supabase:")
        st.code("""
CREATE TABLE sinonimos_calles (
  id SERIAL PRIMARY KEY,
  calle_oficial TEXT NOT NULL,
  sinonimo TEXT NOT NULL UNIQUE,
  creado_por TEXT DEFAULT 'usuario',
  fecha_creacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_sinonimos_sinonimo ON sinonimos_calles(sinonimo);
        """)
    
    # Obtener calles oficiales
    calles_oficiales = supabase.table("zonas_inspectores").select("calle").execute()
    calles_unicas = sorted(list(set([c['calle'] for c in calles_oficiales.data]))) if calles_oficiales.data else []
    
    if calles_unicas:
        with st.expander("➕ Agregar nuevo sinónimo"):
            with st.form("form_sinonimo"):
                col1, col2 = st.columns(2)
                with col1:
                    calle_oficial = st.selectbox("Calle oficial", options=calles_unicas)
                with col2:
                    nuevo_sinonimo = st.text_input("Sinónimo (forma alternativa)", placeholder="Ej: H YRIGOREN, YRIGOYEN")
                if st.form_submit_button("Guardar sinónimo"):
                    if nuevo_sinonimo:
                        try:
                            supabase.table("sinonimos_calles").insert({
                                "calle_oficial": calle_oficial,
                                "sinonimo": nuevo_sinonimo.upper().strip(),
                                "creado_por": "usuario"
                            }).execute()
                            forzar_recarga_cache()
                            st.success("Sinónimo agregado")
                            st.rerun()
                        except Exception as e:
                            if "duplicate" in str(e).lower():
                                st.error("Este sinónimo ya existe")
                            else:
                                st.error(f"Error: {e}")
        
        sinonimos = supabase.table("sinonimos_calles").select("*").order("calle_oficial").execute()
        if sinonimos.data:
            st.markdown("#### Lista de sinónimos actuales")
            for sin in sinonimos.data:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 0.5])
                col1.write(f"**{sin['calle_oficial']}**")
                col2.write(sin['sinonimo'])
                col3.write(sin.get('creado_por', 'sistema'))
                if col4.button("🗑️", key=f"del_sin_{sin['id']}"):
                    supabase.table("sinonimos_calles").delete().eq("id", sin['id']).execute()
                    forzar_recarga_cache()
                    st.rerun()
        else:
            st.info("No hay sinónimos cargados aún")
    else:
        st.info("Primero cargá calles oficiales")
