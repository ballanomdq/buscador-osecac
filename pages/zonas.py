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
    .warning-box { background-color: #451a03; padding: 1rem; border-radius: 6px; border-left: 4px solid #f59e0b; margin: 1rem 0; color: #ffffff; }
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

# ==================== DATOS DE INSPECTORES (HARDCODEADOS) ====================

# 1. Inspectores por LOCALIDAD (fuera de Mar del Plata)
INSPECTORES_POR_LOCALIDAD = {
    "RODRIGUEZ MAXIMILIANO": {
        "legajo": "7713",
        "localidades": [
            "MAR DE AJO", "SAN BERNARDO", "COSTA AZUL", "LA LUCILA DEL MAR",
            "NUEVA ATLANTIS", "AGUAS VERDES", "GRAL. MADARIAGA", "SANTA CLARA DEL MAR",
            "MAR DE COBO", "BALNEARIO MAR CHIQUITA"
        ]
    },
    "POLINESSI JUAN JOSE": {
        "legajo": "9513",
        "localidades": [
            "VILLA GESELL", "MAR DE LAS PAMPAS", "MAR AZUL", "MIRAMAR",
            "CMTE. NICANOR OTAMENDI", "MECHONGUE", "SIERRA DE LOS PADRES", "ESTACION CAMET"
        ]
    },
    "LOPEZ MARTIN": {
        "legajo": "9983",
        "localidades": [
            "SANTA TERESITA", "MAR DEL TUYU", "COSTA DEL ESTE", "LAS TONINAS", "BATAN"
        ]
    },
    "CARBAYO VICTOR HUGO": {
        "legajo": "9220",
        "localidades": [
            "VIVORATA", "CNEL. VIDAL", "GRAL. PIRAN", "LAS ARMAS", "MAIPU",
            "LABARDEN", "GRAL. GUIDO", "DOLORES", "CASTELLI", "GRAL. CONESA"
        ]
    },
    "GARCIA JUAN PAULO": {
        "legajo": "7952",
        "localidades": [
            "PINAMAR", "CARILO", "OSTENDE", "VALERIA DEL MAR",
            "SAN CLEMENTE DEL TUYU", "GRAL. LAVALLE", "CHAPADMALAL"
        ]
    }
}

# 2. Datos de calles por inspector para MAR DEL PLATA
INSPECTORES_CALLES_MDQ = {
    "GARCIA JUAN PAULO": {
        "legajo": "7952",
        "calles": [
            ("COLON", "PAR", 2000, 2500), ("SAN JUAN", "PAR", 2100, 5400),
            ("PEHUAJO", "PAR", 2100, 5400), ("INDEPENDENCIA", "IMPAR", 2100, 3500),
            ("J.P. RAMOS", "IMPAR", 3500, 5400), ("MARIO BRAVO", "AMBOS", 2000, 2500),
            ("H. YRIGOYEN", "PAR", 1600, 2100), ("SAN LUIS", "IMPAR", 1600, 2100),
            ("COLON", "IMPAR", 1600, 1800), ("P.P. RAMOS", "AMBOS", 1600, 1800),
            ("ACHA", "PAR", 3500, 5400), ("J.B. JUSTO", "AMBOS", 0, 500),
            ("MARIO BRAVO", "AMBOS", 0, 500), ("TRABAJADORES", "AMBOS", 3500, 5400),
            ("RUTA 11", "AMBOS", 5400, 9000), ("CALLE 515", "AMBOS", 0, 3000),
            ("JORGE NEWBERY", "AMBOS", 5400, 9000), ("SALTA", "AMBOS", 2100, 5300),
            ("JUJUY", "AMBOS", 2100, 5300), ("ESPAÑA", "AMBOS", 2100, 5300),
            ("20 SEPTIEMBRE", "AMBOS", 2100, 5300), ("14 JULIO", "AMBOS", 2100, 5300),
            ("DORREGO", "AMBOS", 2100, 5300), ("GUIDO", "AMBOS", 2100, 5300),
            ("FUNES", "AMBOS", 2100, 5300), ("OLAZABAL", "AMBOS", 2100, 5300),
            ("ALMIRANTE BROWN", "AMBOS", 2100, 5300), ("FALUCHO", "AMBOS", 2100, 5300),
            ("GASCON", "AMBOS", 2100, 5300), ("ALBERTI", "AMBOS", 2100, 5300),
            ("MATHEU", "AMBOS", 2100, 5300), ("QUINTANA", "AMBOS", 2100, 5300),
            ("SAAVEDRA", "AMBOS", 2100, 5300), ("ROCA", "AMBOS", 2100, 5300),
            ("PEÑA", "AMBOS", 2100, 5300), ("PRIMERA JUNTA", "AMBOS", 2100, 5300),
            ("RODRIGUEZ PEÑA", "AMBOS", 2100, 5300), ("LAPRIDA", "AMBOS", 2100, 5300),
            ("AZCUENAGA", "AMBOS", 2100, 5300), ("LARREA", "AMBOS", 2100, 5300),
            ("VIEYTES", "AMBOS", 2100, 5300), ("PASO", "AMBOS", 2100, 5300),
            ("CASTELLI", "AMBOS", 2100, 5300), ("GARAY", "AMBOS", 2100, 5300),
            ("RAWSON", "AMBOS", 2100, 5300), ("MITRE", "AMBOS", 1600, 2000),
            ("SAN MARTIN", "AMBOS", 1600, 2000), ("RIVADAVIA", "AMBOS", 1600, 2000),
            ("BELGRANO", "AMBOS", 1600, 2000), ("MORENO", "AMBOS", 1600, 2000),
            ("BOLIVAR", "AMBOS", 1600, 2000), ("POSADAS", "AMBOS", 3600, 5300),
            ("RONDEAU", "AMBOS", 3600, 5300), ("BERMEJO", "AMBOS", 3600, 5300),
            ("FIGUEROA ALCORTA", "AMBOS", 3600, 5300), ("MARTINEZ DE HOZ", "AMBOS", 3600, 5300),
            ("SOLIS", "AMBOS", 3600, 5300), ("GABOTO", "AMBOS", 3600, 5300),
            ("ELCANO", "AMBOS", 3600, 5300), ("MAGALLANES", "AMBOS", 3600, 5300),
            ("12 DE OCTUBRE", "AMBOS", 3600, 5300), ("AYOLAS", "AMBOS", 3600, 5300),
            ("IRALA", "AMBOS", 3600, 5300), ("VERTIZ", "AMBOS", 3600, 5300),
            ("AZOPARDO", "AMBOS", 3600, 5300), ("BOUCHARD", "AMBOS", 3600, 5300),
            ("PIEDRABUENA", "AMBOS", 3600, 5300), ("RODRIGUEZ", "AMBOS", 3600, 5300),
            ("BESTO", "AMBOS", 3600, 5300), ("TRIPULANTES DEL FOURNIER", "AMBOS", 3600, 5300),
            ("ROSALES", "AMBOS", 3600, 5300), ("FORTUNATO DE LA PLAZA", "AMBOS", 3600, 5300),
            ("LEBENSOHN", "AMBOS", 3600, 5300), ("MALABIA", "AMBOS", 3600, 5300),
            ("ARANA Y GOIRI", "AMBOS", 3600, 5300), ("ORTIZ DE ZARATE", "AMBOS", 3600, 5300),
            ("GUANAHANI", "AMBOS", 3600, 5300), ("DON ARTURO", "AMBOS", 5500, 8900),
            ("MARGARITAS", "AMBOS", 5500, 8900), ("JAZMINES", "AMBOS", 5500, 8900),
            ("LOS ALERCES", "AMBOS", 5500, 8900), ("LOS SAUCES", "AMBOS", 5500, 8900)
        ]
    },
    "CARBAYO VICTOR HUGO": {
        "legajo": "9220",
        "calles": [
            ("COLON", "PAR", 2199, 3199), ("BUENOS AIRES", "IMPAR", 2201, 4499),
            ("SAN LUIS", "IMPAR", 2199, 3199), ("INDEPENDENCIA", "PAR", 2201, 4499),
            ("SALTA", "AMBOS", 2100, 5300), ("JUJUY", "AMBOS", 2100, 5300),
            ("ESPAÑA", "AMBOS", 2100, 5300), ("20 SEPTIEMBRE", "AMBOS", 2100, 5300),
            ("14 JULIO", "AMBOS", 2100, 5300), ("DORREGO", "AMBOS", 2100, 5300),
            ("GUIDO", "AMBOS", 2100, 5300), ("FUNES", "AMBOS", 2100, 5300),
            ("OLAZABAL", "AMBOS", 2100, 5300), ("ALMIRANTE BROWN", "AMBOS", 2100, 5300),
            ("FALUCHO", "AMBOS", 2100, 5300), ("GASCON", "AMBOS", 2100, 5300),
            ("ALBERTI", "AMBOS", 2100, 5300), ("MATHEU", "AMBOS", 2100, 5300),
            ("QUINTANA", "AMBOS", 2100, 5300), ("SAAVEDRA", "AMBOS", 2100, 5300),
            ("ROCA", "AMBOS", 2100, 5300), ("PEÑA", "AMBOS", 2100, 5300),
            ("PRIMERA JUNTA", "AMBOS", 2100, 5300), ("RODRIGUEZ PEÑA", "AMBOS", 2100, 5300),
            ("LAPRIDA", "AMBOS", 2100, 5300), ("AZCUENAGA", "AMBOS", 2100, 5300),
            ("LARREA", "AMBOS", 2100, 5300), ("VIEYTES", "AMBOS", 2100, 5300),
            ("PASO", "AMBOS", 2100, 5300), ("CASTELLI", "AMBOS", 2100, 5300),
            ("GARAY", "AMBOS", 2100, 5300), ("RAWSON", "AMBOS", 2100, 5300)
        ]
    },
    "RODRIGUEZ MAXIMILIANO": {
        "legajo": "7713",
        "calles": [
            ("CATAMARCA", "IMPAR", 500, 2100), ("COLON", "IMPAR", 3500, 3100),
            ("JARA", "PAR", 1, 9999), ("TEJEDOR CARLOS", "PAR", 1, 9999),
            ("PATRICIO PERALTA RAMOS", "AMBOS", 1, 9999), ("FELIX U. CAMET", "AMBOS", 1, 9999),
            ("MITRE", "AMBOS", 1600, 2000), ("SAN MARTIN", "AMBOS", 1600, 2000),
            ("RIVADAVIA", "AMBOS", 1600, 2000), ("BELGRANO", "AMBOS", 1600, 2000),
            ("MORENO", "AMBOS", 1600, 2000), ("BOLIVAR", "AMBOS", 1600, 2000)
        ]
    },
    "POLINESSI JUAN JOSE": {
        "legajo": "9513",
        "calles": [
            ("COLON", "IMPAR", 6301, 9999), ("CHAMPAGNAT", "IMPAR", 2199, 9999),
            ("CATAMARCA", "PAR", 2198, 3098), ("H. YRIGOYEN", "IMPAR", 2199, 9999),
            ("PATRICIO PERALTA RAMOS", "AMBOS", 1, 9999), ("FELIX U. CAMET", "AMBOS", 1, 9999),
            ("DON ARTURO", "AMBOS", 5500, 8900), ("MARGARITAS", "AMBOS", 5500, 8900),
            ("JAZMINES", "AMBOS", 5500, 8900), ("LOS ALERCES", "AMBOS", 5500, 8900),
            ("LOS SAUCES", "AMBOS", 5500, 8900)
        ]
    },
    "LOPEZ MARTIN": {
        "legajo": "9983",
        "calles": [
            ("COLON", "IMPAR", 1, 9999), ("SAN LUIS", "PAR", 1, 9999),
            ("PATRICIO PERALTA RAMOS", "AMBOS", 1, 9999), ("SANTA FE", "IMPAR", 1, 9999),
            ("POSADAS", "AMBOS", 3600, 5300), ("RONDEAU", "AMBOS", 3600, 5300),
            ("BERMEJO", "AMBOS", 3600, 5300), ("FIGUEROA ALCORTA", "AMBOS", 3600, 5300),
            ("MARTINEZ DE HOZ", "AMBOS", 3600, 5300), ("SOLIS", "AMBOS", 3600, 5300),
            ("GABOTO", "AMBOS", 3600, 5300), ("ELCANO", "AMBOS", 3600, 5300),
            ("MAGALLANES", "AMBOS", 3600, 5300), ("12 DE OCTUBRE", "AMBOS", 3600, 5300),
            ("AYOLAS", "AMBOS", 3600, 5300), ("IRALA", "AMBOS", 3600, 5300),
            ("VERTIZ", "AMBOS", 3600, 5300), ("AZOPARDO", "AMBOS", 3600, 5300),
            ("BOUCHARD", "AMBOS", 3600, 5300), ("PIEDRABUENA", "AMBOS", 3600, 5300),
            ("RODRIGUEZ", "AMBOS", 3600, 5300), ("BESTO", "AMBOS", 3600, 5300),
            ("TRIPULANTES DEL FOURNIER", "AMBOS", 3600, 5300), ("ROSALES", "AMBOS", 3600, 5300),
            ("FORTUNATO DE LA PLAZA", "AMBOS", 3600, 5300), ("LEBENSOHN", "AMBOS", 3600, 5300),
            ("MALABIA", "AMBOS", 3600, 5300), ("ARANA Y GOIRI", "AMBOS", 3600, 5300),
            ("ORTIZ DE ZARATE", "AMBOS", 3600, 5300), ("GUANAHANI", "AMBOS", 3600, 5300)
        ]
    }
}

# ==================== FUNCIÓN PARA PARSAR CALLES ====================
def normalizar_calle(calle):
    """Normaliza el nombre de la calle para comparación"""
    calle = calle.upper().strip()
    # Quitar prefijos comunes
    for prefijo in ['AV ', 'AV.', 'AVENIDA ', 'CALLE ', 'C/']:
        if calle.startswith(prefijo):
            calle = calle[len(prefijo):]
    # Quitar sufijos
    for sufijo in [' AV', ' AV.', ' AVENIDA']:
        if calle.endswith(sufijo):
            calle = calle[:-len(sufijo)]
    return calle.strip()

def asignar_legajo_por_direccion(localidad, calle, numero):
    """Devuelve el legajo según localidad, calle y número"""
    
    # 1. Si la localidad NO es MAR DEL PLATA → buscar en INSPECTORES_POR_LOCALIDAD
    if localidad.upper() != "MAR DEL PLATA":
        for inspector, data in INSPECTORES_POR_LOCALIDAD.items():
            for loc in data["localidades"]:
                if loc == localidad.upper():
                    return data["legajo"]
        return None
    
    # 2. Si es MAR DEL PLATA → buscar por calle
    if not calle or not numero:
        return None
    
    try:
        numero_limpio = int(re.sub(r'\D', '', str(numero)))
    except:
        return None
    
    lado = "PAR" if numero_limpio % 2 == 0 else "IMPAR"
    calle_norm = normalizar_calle(calle)
    
    for inspector, data in INSPECTORES_CALLES_MDQ.items():
        for calle_data in data["calles"]:
            calle_zona = normalizar_calle(calle_data[0])
            if calle_zona == calle_norm:
                lado_zona = calle_data[1]
                desde = calle_data[2]
                hasta = calle_data[3]
                
                # Verificar lado
                if lado_zona == "AMBOS" or lado_zona == lado:
                    # Verificar altura
                    if desde <= numero_limpio <= hasta:
                        return data["legajo"]
    return None

# ==================== PESTAÑAS ====================
tab1, tab2, tab3 = st.tabs(["👥 Inspectores", "📍 Calles por Inspector", "🔄 Asignar Legajos"])

# ==================== TAB 1: LISTADO DE INSPECTORES ====================
with tab1:
    st.markdown("### 👥 Listado de Inspectores")
    
    # Mostrar inspectores por localidad
    st.markdown("#### 🌍 Inspectores por Localidad (fuera de Mar del Plata)")
    for inspector, data in INSPECTORES_POR_LOCALIDAD.items():
        with st.expander(f"{inspector} (Legajo {data['legajo']})"):
            st.write("**Localidades que cubre:**")
            for loc in data["localidades"]:
                st.write(f"- {loc}")
    
    # Mostrar inspectores de Mar del Plata
    st.markdown("#### 🏙️ Inspectores de Mar del Plata (por calles)")
    for inspector, data in INSPECTORES_CALLES_MDQ.items():
        with st.expander(f"{inspector} (Legajo {data['legajo']})"):
            st.write(f"**Calles que cubre en Mar del Plata:** {len(data['calles'])} calles")

# ==================== TAB 2: VER CALLES POR INSPECTOR ====================
with tab2:
    st.markdown("### 📍 Ver calles asignadas a cada inspector")
    
    # Selector de inspector
    opciones = list(INSPECTORES_CALLES_MDQ.keys())
    inspector_seleccionado = st.selectbox("Seleccionar inspector", opciones)
    
    if inspector_seleccionado:
        data = INSPECTORES_CALLES_MDQ[inspector_seleccionado]
        st.markdown(f"**Inspector:** {inspector_seleccionado}")
        st.markdown(f"**Legajo:** {data['legajo']}")
        
        df_calles = pd.DataFrame(data['calles'], columns=['Calle', 'Lado', 'Desde', 'Hasta'])
        st.dataframe(df_calles, use_container_width=True, hide_index=True)

# ==================== TAB 3: ASIGNAR LEGAJOS AUTOMÁTICAMENTE ====================
with tab3:
    st.markdown("### 🔄 Asignar Legajos Automáticamente")
    st.markdown("""
    <div class="info-box">
        <strong>📌 ¿Qué hace esta función?</strong><br>
        - Toma todas las empresas que tienen <strong>leg vacío</strong> en el padrón.<br>
        - Si la localidad NO es Mar del Plata, asigna el inspector fijo de esa localidad.<br>
        - Si la localidad ES Mar del Plata, busca por calle + número en las zonas definidas.<br>
        - Asigna automáticamente el número de legajo.
    </div>
    """, unsafe_allow_html=True)
    
    # Contar registros sin legajo
    sin_legajo = supabase.table("padron_deuda_presunta").select("id", count="exact").is_("leg", "null").execute()
    total_sin_legajo = sin_legajo.count
    
    st.metric("📊 Registros sin legajo", total_sin_legajo)
    
    if total_sin_legajo == 0:
        st.success("✅ Todos los registros ya tienen legajo asignado.")
    else:
        st.info(f"📌 Se asignarán legajos a {total_sin_legajo} registros")
        
        if st.button("🚀 Asignar Legajos Automáticamente", type="primary"):
            with st.spinner("Procesando direcciones y asignando legajos..."):
                # Obtener registros sin legajo
                todos_registros = []
                offset = 0
                batch_size = 100
                while True:
                    batch = supabase.table("padron_deuda_presunta").select("*").is_("leg", "null").range(offset, offset + batch_size - 1).execute()
                    if not batch.data:
                        break
                    todos_registros.extend(batch.data)
                    offset += batch_size
                    if len(batch.data) < batch_size:
                        break
                
                asignados = 0
                no_asignados = 0
                asignados_por_localidad = 0
                asignados_por_calle = 0
                
                # Preparar updates masivos
                updates = []
                
                for reg in todos_registros:
                    localidad = reg.get('localidad', '')
                    calle = reg.get('calle', '')
                    numero = reg.get('numero', '')
                    
                    if not localidad:
                        no_asignados += 1
                        continue
                    
                    legajo_asignado = asignar_legajo_por_direccion(localidad, calle, numero)
                    
                    if legajo_asignado:
                        updates.append({"id": reg['id'], "leg": legajo_asignado})
                        asignados += 1
                        if localidad.upper() != "MAR DEL PLATA":
                            asignados_por_localidad += 1
                        else:
                            asignados_por_calle += 1
                    else:
                        no_asignados += 1
                
                # Ejecutar updates masivos
                if updates:
                    for i in range(0, len(updates), 100):
                        lote = updates[i:i+100]
                        for item in lote:
                            supabase.table("padron_deuda_presunta").update({"leg": item['leg']}).eq("id", item['id']).execute()
                
                st.success(f"""
                ✅ Asignación completada:\n
                - Total asignados: {asignados}\n
                - Por localidad (fuera de MDQ): {asignados_por_localidad}\n
                - Por calle (en MDQ): {asignados_por_calle}\n
                - No encontrados: {no_asignados}
                """)
                st.rerun()
