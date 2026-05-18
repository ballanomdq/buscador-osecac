import streamlit as st
import folium
from streamlit_folium import st_folium
from supabase import create_client
import pandas as pd
import random

st.set_page_config(page_title="Mapa de Empresas - OSECAC", layout="wide")

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
}
div[data-testid="stButton"] button:hover { background: #2563eb !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>🗺️ Mapa de Empresas por Inspector</h2>
    <p>Visualización geográfica de las empresas asignadas a cada inspector</p>
</div>
""", unsafe_allow_html=True)

# ── Conexión a Supabase ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

# ── Botón volver ─────────────────────────────────────────────────────────────
col_back, _ = st.columns([1, 11])
with col_back:
    if st.button("← Volver a Fiscalización"):
        st.switch_page("pages/actas.py")

st.markdown("---")

# ── Obtener datos de la base ─────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_empresas():
    """Carga todas las empresas con sus coordenadas"""
    datos = supabase.table("padron_deuda_presunta").select("*").execute()
    return pd.DataFrame(datos.data) if datos.data else pd.DataFrame()

@st.cache_data(ttl=300)
def cargar_inspectores():
    datos = supabase.table("inspectores").select("*").order("legajo").execute()
    return datos.data if datos.data else []

# ── Funciones de geolocalización (aproximada) ────────────────────────────────
# Nota: Para coordenadas exactas necesitarías una API de geocoding.
# Por ahora usamos coordenadas aproximadas basadas en la calle y altura.

def obtener_coordenadas_aproximadas(calle, numero):
    """Devuelve coordenadas aproximadas para una calle de Mar del Plata"""
    
    # Coordenadas de referencia por calle principal
    coordenadas_calles = {
        "AV COLON": [-38.0000, -57.5600],
        "CATAMARCA": [-37.9980, -57.5550],
        "AV JARA": [-37.9950, -57.5480],
        "AV TEJEDOR": [-38.0020, -57.5700],
        "HIPOLITO YRIGOYEN": [-38.0030, -57.5400],
        "SAN LUIS": [-38.0050, -57.5450],
        "SANTA FE": [-38.0020, -57.5500],
        "AV PATRICIO PERALTA RAMOS": [-38.0100, -57.5600],
        "AV MARIO BRAVO": [-38.0200, -57.5800],
        "ACHA": [-37.9900, -57.5300],
        "AV JUAN B JUSTO": [-37.9850, -57.5350],
        "AV DE LOS TRABAJADORES": [-38.0150, -57.5900],
        "BELGRANO": [-38.0050, -57.5500],
        "RIVADAVIA": [-38.0050, -57.5520],
        "SAN MARTIN": [-38.0050, -57.5540],
        "MITRE": [-38.0050, -57.5560],
        "MORENO": [-38.0050, -57.5580],
        "CORDOBA": [-38.0030, -57.5420],
        "SANTIAGO DEL ESTERO": [-38.0030, -57.5440],
        "CORRIENTES": [-38.0030, -57.5460],
        "ENTRE RIOS": [-38.0030, -57.5480],
        "BUENOS AIRES": [-38.0030, -57.5500],
        "TUCUMAN": [-38.0030, -57.5520],
        "SALTA": [-38.0030, -57.5540],
        "JUJUY": [-38.0030, -57.5560],
        "ESPAÑA": [-38.0030, -57.5580],
        "LA RIOJA": [-38.0010, -57.5400],
        "SAN JUAN": [-38.0010, -57.5420],
    }
    
    # Buscar coordenadas base de la calle
    calle_limpia = calle.upper().strip()
    for calle_ref, coords in coordenadas_calles.items():
        if calle_ref in calle_limpia or calle_limpia in calle_ref:
            # Desplazar ligeramente según el número
            try:
                num = int(numero) if numero else 0
                offset = (num / 10000) * 0.01  # Desplazamiento pequeño
                return [coords[0] + offset * 0.01, coords[1] + offset * 0.01]
            except:
                return coords
    
    # Si no se encuentra, coordenada aleatoria dentro de Mar del Plata
    centro_mdp = [-38.0055, -57.5426]
    return [centro_mdp[0] + random.uniform(-0.03, 0.03), centro_mdp[1] + random.uniform(-0.03, 0.03)]

# ── Obtener datos ────────────────────────────────────────────────────────────
with st.spinner("Cargando datos..."):
    df_empresas = cargar_empresas()
    inspectores = cargar_inspectores()

if df_empresas.empty:
    st.warning("No hay empresas cargadas en la base de datos.")
    st.stop()

# ── Asignar colores a inspectores ────────────────────────────────────────────
colores_inspectores = {
    "CON LEGAJO": {}  # Se llenará dinámicamente
}

paleta_colores = [
    "#FF6B6B",  # Rojo claro (GARCIA)
    "#4ECDC4",  # Turquesa (POLINESSI)
    "#45B7D1",  # Celeste (RODRIGUEZ)
    "#96CEB4",  # Verde claro (LOPEZ)
    "#FFEAA7",  # Amarillo (CARBAYO)
    "#DDA0DD",  # Lila
    "#F0B27A",  # Naranja
    "#85C1E9",  # Azul claro
]

# Mapear inspectores a colores
color_por_legajo = {}
for idx, ins in enumerate(inspectores):
    color_por_legajo[ins['legajo']] = paleta_colores[idx % len(paleta_colores)]

# ── Filtros ──────────────────────────────────────────────────────────────────
st.markdown("### 🔍 Filtrar por Inspector")

# Opciones de filtro
opciones_inspectores = ["TODOS"] + [f"{ins['nombre']} (Legajo {ins['legajo']})" for ins in inspectores] + ["SIN LEGAJO"]

inspector_seleccionado = st.selectbox("Seleccionar inspector", opciones_inspectores)

# Preparar datos para el mapa
datos_mapa = []

for _, row in df_empresas.iterrows():
    legajo = row.get('leg')
    razon_social = row.get('razon_social', 'Sin nombre')
    calle = row.get('calle', '')
    numero = row.get('numero', '')
    localidad = row.get('localidad', '')
    cuit = row.get('cuit', '')
    
    # Determinar color según filtro
    if pd.isna(legajo) or legajo is None:
        color = "#FF0000"  # ROJO para sin legajo
        grupo = "SIN LEGAJO"
        nombre_inspector = "Sin asignar"
    else:
        # Buscar inspector por legajo
        inspector = next((ins for ins in inspectores if ins['legajo'] == legajo), None)
        if inspector:
            nombre_inspector = inspector['nombre'].split(',')[0]
            color = color_por_legajo.get(legajo, "#888888")
            grupo = f"{nombre_inspector} (Legajo {legajo})"
        else:
            color = "#888888"
            nombre_inspector = "Desconocido"
            grupo = "Sin inspector"
    
    # Aplicar filtro
    if inspector_seleccionado == "TODOS":
        pasar = True
    elif inspector_seleccionado == "SIN LEGAJO":
        pasar = (grupo == "SIN LEGAJO")
    else:
        pasar = (grupo == inspector_seleccionado)
    
    if pasar:
        # Obtener coordenadas
        coords = obtener_coordenadas_aproximadas(calle, numero)
        
        # Popup con información
        popup_text = f"""
        <div style="min-width: 200px;">
            <b>{razon_social}</b><br>
            <b>CUIT:</b> {cuit}<br>
            <b>Dirección:</b> {calle} {numero}<br>
            <b>Localidad:</b> {localidad}<br>
            <b>Inspector:</b> {nombre_inspector}<br>
            <b>Legajo:</b> {legajo if not pd.isna(legajo) else 'Sin asignar'}
        </div>
        """
        
        datos_mapa.append({
            "coords": coords,
            "popup": popup_text,
            "color": color,
            "razon_social": razon_social,
            "grupo": grupo
        })

# ── Crear el mapa ────────────────────────────────────────────────────────────
if not datos_mapa:
    st.info(f"No hay empresas para mostrar con el filtro '{inspector_seleccionado}'")
    st.stop()

# Centro de Mar del Plata
centro_mdp = [-38.0055, -57.5426]

# Crear mapa base
m = folium.Map(location=centro_mdp, zoom_start=12, tiles="cartodbpositron")

# Agregar marcadores por grupo (para poder ocultar/mostrar)
grupos = {}
for dato in datos_mapa:
    grupo = dato["grupo"]
    if grupo not in grupos:
        grupos[grupo] = folium.FeatureGroup(name=grupo)
    
    # Agregar marcador
    folium.CircleMarker(
        location=dato["coords"],
        radius=6,
        popup=folium.Popup(dato["popup"], max_width=300),
        color=dato["color"],
        fill=True,
        fill_color=dato["color"],
        fill_opacity=0.7,
        tooltip=dato["razon_social"][:30]
    ).add_to(grupos[grupo])

# Agregar cada grupo al mapa
for grupo, feature_group in grupos.items():
    feature_group.add_to(m)

# Agregar control de capas
folium.LayerControl(collapsed=False).add_to(m)

# Agregar marcador central
folium.Marker(
    location=centro_mdp,
    popup="<b>Mar del Plata</b><br>Centro",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)

# ── Mostrar estadísticas y mapa ──────────────────────────────────────────────
st.markdown("---")

# Estadísticas
col_stats1, col_stats2, col_stats3 = st.columns(3)
with col_stats1:
    total_mostrados = len(datos_mapa)
    st.metric("📍 Empresas en mapa", total_mostrados)
with col_stats2:
    con_legajo = sum(1 for d in datos_mapa if d["grupo"] != "SIN LEGAJO")
    st.metric("✅ Con legajo", con_legajo)
with col_stats3:
    sin_legajo = sum(1 for d in datos_mapa if d["grupo"] == "SIN LEGAJO")
    st.metric("❌ Sin legajo", sin_legajo, delta_color="inverse")

st.markdown("---")
st.markdown("### 🗺️ Mapa interactivo")
st.markdown("💡 **Instrucciones:**")
st.markdown("- Haga clic en los puntos para ver los detalles de cada empresa")
st.markdown("- Use el control ☰ en la esquina superior derecha para ocultar/mostrar inspectores")
st.markdown("- Los puntos **ROJOS** son empresas sin legajo asignado")
st.markdown("- Los puntos de colores corresponden a cada inspector")

# Mostrar el mapa
st_folium(m, width=1000, height=600, returned_objects=[])

# ── Leyenda de colores ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎨 Leyenda de colores")

# Crear leyenda con los inspectores que tienen puntos en el mapa
colores_usados = {}
for dato in datos_mapa:
    if dato["grupo"] != "SIN LEGAJO":
        colores_usados[dato["grupo"]] = dato["color"]

# Mostrar leyenda
cols_leyenda = st.columns(min(len(colores_usados) + 2, 4))
idx = 0
for grupo, color in colores_usados.items():
    with cols_leyenda[idx % 4]:
        st.markdown(f'<span style="display:inline-block; width:20px; height:20px; background:{color}; border-radius:50%; margin-right:8px;"></span> {grupo}', unsafe_allow_html=True)
    idx += 1

with cols_leyenda[idx % 4]:
    st.markdown('<span style="display:inline-block; width:20px; height:20px; background:#FF0000; border-radius:50%; margin-right:8px;"></span> ❌ Sin legajo', unsafe_allow_html=True)

st.caption(f"📊 Total de empresas en la base de datos: {len(df_empresas)} | Mostradas en el mapa: {len(datos_mapa)}")
