import streamlit as st
import os
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import pytz
import time
import re

st.set_page_config(page_title="Boletín Oficial - OSECAC", layout="wide")

# Estilos CSS para los libros (colores de acento)
st.markdown("""
<style>
/* Libro Judicial (azul) */
div[data-testid="stExpander"] details summary {
    background-color: #e6f2ff;
    border-left: 6px solid #1e88e5;
    border-radius: 8px;
}
/* Libro Oficial (gris) */
div[data-testid="stExpander"] details summary {
    background-color: #f0f0f0;
    border-left: 6px solid #5f6368;
}
/* Ajuste para que el contenido del expander no quede apretado */
div[data-testid="stExpander"] details {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Fiscalización OSECAC - Boletín Oficial")

# --- Conexión a Supabase ---
def get_credentials():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return url, key
    except:
        pass
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return url, key
    return None, None

SUPABASE_URL, SUPABASE_KEY = get_credentials()
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Faltan credenciales de Supabase. Revisá los secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Botón de forzar descarga ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Forzar descarga de Boletines del día", use_container_width=True):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta el token de GitHub (GH_TOKEN) en secrets.")
        else:
            repo = "ballanomdq/buscador-osecac"  # Ajustar si es necesario
            url = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
            data = {"ref": "main"}
            with st.spinner("⏳ Procesando boletines... puede tardar unos segundos."):
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 204:
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    progress_bar.empty()
                    st.success("✅ Scraping iniciado. Los resultados aparecerán en unos minutos.")
                else:
                    st.error(f"Error al iniciar: {response.status_code}")

st.divider()

# --- Filtro de localidad (sidebar) ---
LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

with st.sidebar:
    st.header("Filtros")
    localidad_filtro = st.multiselect("Localidad", ["Todas"] + sorted(LOCALIDADES), default=["Todas"])

# --- Consultar datos desde Supabase ---
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
response = query.execute()
datos = response.data

if not datos:
    st.markdown(
        """
        <div style="text-align: center; margin-top: 50px;">
            <h3>📭 Bienvenido</h3>
            <p>Presione el botón superior para iniciar la fiscalización del día.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"])
if df["fecha"].dt.tz is None:
    df["fecha"] = df["fecha"].dt.tz_localize('UTC').dt.tz_convert('America/Argentina/Buenos_Aires')
else:
    df["fecha"] = df["fecha"].dt.tz_convert('America/Argentina/Buenos_Aires')

# --- Funciones mejoradas para análisis dinámico ---
def extraer_nombre_cuit_quiebra(texto):
    """Busca patrones específicos de quiebra: 'quiebra de NOMBRE' o 'decretado la quiebra de NOMBRE'"""
    patron_quiebra = r"(?:quiebra|concurso)\s+(?:de\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)(?:\s+\(?(?:CUIT|DNI)[\s:]*(\d{2}-\d{8}-\d|\d{7,8})?|\.|$)"
    match = re.search(patron_quiebra, texto, re.IGNORECASE)
    if match:
        nombre = match.group(1).strip()
        cuit = match.group(2) if match.group(2) else None
        return nombre, cuit
    return None, None

def extraer_nombre_del_texto(texto):
    """Busca nombres en mayúsculas y CUIT/DNI"""
    cuit_match = re.search(r'\b\d{2}-\d{8}-\d\b', texto)
    cuit = cuit_match.group(0) if cuit_match else None
    dni_match = re.search(r'\b(\d{7,8})\b', texto)
    dni = dni_match.group(1) if dni_match else None
    mayusculas = re.findall(r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ]+\b', texto)
    if not mayusculas:
        mayusculas = re.findall(r'\b[A-ZÁÉÍÓÚÑ]{5,}\b', texto)
    nombre = mayusculas[0] if mayusculas else None
    if not nombre and dni:
        nombre = f"DNI {dni}"
    return nombre, cuit

def obtener_info_edicto(row):
    texto = row["texto_completo"]
    sujetos_db = row.get("sujetos")
    cuits_db = row.get("cuit_detectados")
    
    nombre_quiebra, cuit_quiebra = extraer_nombre_cuit_quiebra(texto)
    if nombre_quiebra:
        nombre = nombre_quiebra
        cuit = cuit_quiebra
        es_quiebra = True
    else:
        es_quiebra = "quiebra" in texto.lower() or "concurso" in texto.lower()
        if sujetos_db and len(sujetos_db.strip()) > 0:
            nombre = sujetos_db.split(",")[0].strip()
        else:
            nombre, _ = extraer_nombre_del_texto(texto)
        if cuits_db and len(cuits_db.strip()) > 0:
            cuit = cuits_db.split(",")[0].strip()
        else:
            _, cuit = extraer_nombre_del_texto(texto)
    
    if es_quiebra:
        nivel = 0
        icono = "🚨"
        motivo = "QUIEBRA/CONCURSO"
    elif cuit:
        nivel = 1
        icono = "⚠️"
        motivo = "PRECAUCIÓN"
    else:
        nivel = 2
        icono = "⚪"
        motivo = "INFORMATIVO"
    
    nombre_mostrar = nombre if nombre else (cuit if cuit else "Sin datos identificatorios")
    return {
        "nivel": nivel,
        "icono": icono,
        "motivo": motivo,
        "nombre_mostrar": nombre_mostrar,
        "cuit": cuit,
        "es_quiebra": es_quiebra
    }

# --- Agrupar por boletín ---
df["boletin_clave"] = df["boletin_numero"] + "_" + df["fecha"].dt.strftime("%Y%m%d")
boletines = df.groupby(["boletin_clave", "fecha", "boletin_numero"])

boletines_list = []
for (clave, fecha, numero), grupo in boletines:
    boletines_list.append({
        "clave": clave,
        "fecha": fecha,
        "numero": numero,
        "grupo": grupo
    })
boletines_list.sort(key=lambda x: x["fecha"], reverse=True)

# --- Función para ordenar edictos dentro de un grupo por prioridad ---
def ordenar_edictos(grupo_df):
    prioridades = []
    for _, row in grupo_df.iterrows():
        info = obtener_info_edicto(row)
        prioridades.append(info["nivel"])
    grupo_df = grupo_df.copy()
    grupo_df["_prioridad"] = prioridades
    grupo_df = grupo_df.sort_values("_prioridad")
    return grupo_df.drop(columns=["_prioridad"])

# --- Mostrar libros en dos columnas ---
col_judicial, col_oficial = st.columns(2)

# Columnas izquierda (Judicial)
with col_judicial:
    st.subheader("⚖️ LIBRO JUDICIAL")
    for boletin in boletines_list:
        grupo = boletin["grupo"]
        grupo_judicial = grupo[grupo["seccion"] == "JUDICIAL"]
        if grupo_judicial.empty:
            continue
        grupo_judicial = ordenar_edictos(grupo_judicial)
        
        # Clave única para el estado del checkbox
        check_key = f"check_boletin_{boletin['clave']}_judicial"
        if check_key not in st.session_state:
            st.session_state[check_key] = False  # por defecto no chequeado
        
        # Usar dos columnas: una para el expander, otra para el checkbox
        col_exp, col_check = st.columns([0.9, 0.1])
        with col_exp:
            # Título del expander (sin el checkbox)
            titulo_expander = f"📘 Boletín N° {boletin['numero']} - {boletin['fecha'].strftime('%d/%m/%Y')}"
            if st.session_state[check_key]:
                titulo_expander = "✅ " + titulo_expander
            with st.expander(titulo_expander, expanded=False):
                # Mostrar edictos ordenados
                for _, row in grupo_judicial.iterrows():
                    info = obtener_info_edicto(row)
                    titulo_edicto = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
                    if info['cuit']:
                        titulo_edicto += f" - {info['cuit']}"
                    revisado_key = f"revisado_{row['id']}"
                    if revisado_key in st.session_state and st.session_state[revisado_key]:
                        titulo_edicto = "🟢 " + titulo_edicto
                    with st.expander(titulo_edicto):
                        # Resaltar el nombre en el texto
                        texto_resaltado = row["texto_completo"]
                        if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos identificatorios":
                            texto_resaltado = re.sub(rf'\b{re.escape(info['nombre_mostrar'])}\b', f'**{info['nombre_mostrar']}**', texto_resaltado, flags=re.IGNORECASE)
                        st.markdown(texto_resaltado)
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("✅ Revisado", key=f"rev_jud_{row['id']}"):
                                st.session_state[revisado_key] = True
                                st.rerun()
                        with col_b2:
                            if st.button("🗑️ Eliminar", key=f"del_jud_{row['id']}"):
                                confirm_key = f"confirm_jud_{row['id']}"
                                if st.session_state.get(confirm_key, False):
                                    supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                    st.success("Eliminado")
                                    st.rerun()
                                else:
                                    st.session_state[confirm_key] = True
                                    st.warning("Hacé clic otra vez para confirmar eliminación.")
        with col_check:
            # Checkbox para marcar boletín como chequeado
            checked = st.checkbox("", value=st.session_state[check_key], key=f"chk_{boletin['clave']}_judicial")
            if checked != st.session_state[check_key]:
                st.session_state[check_key] = checked
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)  # separación entre boletines

# Columna derecha (Oficial)
with col_oficial:
    st.subheader("📜 LIBRO OFICIAL")
    for boletin in boletines_list:
        grupo = boletin["grupo"]
        grupo_oficial = grupo[grupo["seccion"] == "OFICIAL"]
        if grupo_oficial.empty:
            continue
        grupo_oficial = ordenar_edictos(grupo_oficial)
        
        check_key = f"check_boletin_{boletin['clave']}_oficial"
        if check_key not in st.session_state:
            st.session_state[check_key] = False
        
        col_exp, col_check = st.columns([0.9, 0.1])
        with col_exp:
            titulo_expander = f"📘 Boletín N° {boletin['numero']} - {boletin['fecha'].strftime('%d/%m/%Y')}"
            if st.session_state[check_key]:
                titulo_expander = "✅ " + titulo_expander
            with st.expander(titulo_expander, expanded=False):
                for _, row in grupo_oficial.iterrows():
                    info = obtener_info_edicto(row)
                    titulo_edicto = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
                    if info['cuit']:
                        titulo_edicto += f" - {info['cuit']}"
                    revisado_key = f"revisado_{row['id']}"
                    if revisado_key in st.session_state and st.session_state[revisado_key]:
                        titulo_edicto = "🟢 " + titulo_edicto
                    with st.expander(titulo_edicto):
                        texto_resaltado = row["texto_completo"]
                        if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos identificatorios":
                            texto_resaltado = re.sub(rf'\b{re.escape(info['nombre_mostrar'])}\b', f'**{info['nombre_mostrar']}**', texto_resaltado, flags=re.IGNORECASE)
                        st.markdown(texto_resaltado)
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("✅ Revisado", key=f"rev_ofi_{row['id']}"):
                                st.session_state[revisado_key] = True
                                st.rerun()
                        with col_b2:
                            if st.button("🗑️ Eliminar", key=f"del_ofi_{row['id']}"):
                                confirm_key = f"confirm_ofi_{row['id']}"
                                if st.session_state.get(confirm_key, False):
                                    supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                    st.success("Eliminado")
                                    st.rerun()
                                else:
                                    st.session_state[confirm_key] = True
                                    st.warning("Hacé clic otra vez para confirmar eliminación.")
        with col_check:
            checked = st.checkbox("", value=st.session_state[check_key], key=f"chk_{boletin['clave']}_oficial")
            if checked != st.session_state[check_key]:
                st.session_state[check_key] = checked
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

# Botón de recarga manual
if st.button("🔄 Recargar datos", key="recargar"):
    st.rerun()
