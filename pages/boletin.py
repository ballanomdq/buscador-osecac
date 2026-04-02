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

# Estilos CSS (igual que antes)
st.markdown("""
<style>
div[data-testid="stExpander"] details summary p:has(> .judicial) {
    background-color: #e6f2ff;
    border-left: 6px solid #1e88e5;
    padding: 0.5rem 1rem;
    border-radius: 8px;
}
div[data-testid="stExpander"] details summary p:has(> .oficial) {
    background-color: #f0f0f0;
    border-left: 6px solid #5f6368;
    padding: 0.5rem 1rem;
    border-radius: 8px;
}
.alerta-roja {
    background-color: #ffebee;
    border-left: 6px solid #d32f2f;
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
def extraer_nombre_del_texto(texto):
    """
    Busca patrones de nombres en mayúsculas (al menos dos palabras o una palabra larga)
    y también DNI/CUIT. Devuelve (nombre, cuit).
    """
    # Buscar CUIT primero
    cuit_match = re.search(r'\b\d{2}-\d{8}-\d\b', texto)
    cuit = cuit_match.group(0) if cuit_match else None
    # Buscar DNI (7-8 dígitos)
    dni_match = re.search(r'\b(\d{7,8})\b', texto)
    dni = dni_match.group(1) if dni_match else None
    
    # Buscar palabras en mayúsculas (que no sean números ni letras sueltas)
    # Patrón: al menos dos palabras mayúsculas separadas por espacio, o una palabra larga (>5 letras)
    mayusculas = re.findall(r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ]+\b', texto)
    if not mayusculas:
        mayusculas = re.findall(r'\b[A-ZÁÉÍÓÚÑ]{5,}\b', texto)
    nombre = mayusculas[0] if mayusculas else None
    # Si no hay nombre, intentar con DNI
    if not nombre and dni:
        nombre = f"DNI {dni}"
    return nombre, cuit

def es_quiebra(texto):
    return "quiebra" in texto.lower() or "concurso" in texto.lower()

def obtener_info_edicto(row):
    texto = row["texto_completo"]
    sujetos_db = row.get("sujetos")
    cuits_db = row.get("cuit_detectados")
    
    # Detectar quiebra
    quiebra = es_quiebra(texto)
    
    # Extraer nombre y cuit dinámicamente si los campos están vacíos
    if sujetos_db and len(sujetos_db.strip()) > 0:
        nombre = sujetos_db.split(",")[0].strip()
    else:
        nombre, _ = extraer_nombre_del_texto(texto)
    if cuits_db and len(cuits_db.strip()) > 0:
        cuit = cuits_db.split(",")[0].strip()
    else:
        _, cuit = extraer_nombre_del_texto(texto)
    
    # Determinar nivel de alerta
    if quiebra:
        nivel = "roja"
        icono = "🚨"
        motivo = "QUIEBRA/CONCURSO"
    elif cuit:
        nivel = "amarilla"
        icono = "⚠️"
        motivo = "PRECAUCIÓN"
    else:
        nivel = "gris"
        icono = "⚪"
        motivo = "INFORMATIVO"
    
    # Nombre a mostrar en título
    nombre_mostrar = nombre if nombre else (cuit if cuit else "Sin datos identificatorios")
    return {
        "quiebra": quiebra,
        "nivel": nivel,
        "icono": icono,
        "motivo": motivo,
        "nombre_mostrar": nombre_mostrar,
        "cuit": cuit
    }

# --- Separar alertas de quiebra (prioridad 1) ---
alertas = df[df["texto_completo"].str.lower().str.contains("quiebra|concurso", na=False)]
otros = df[~df.index.isin(alertas.index)]

# --- Mostrar sección de alertas (si existe) ---
if not alertas.empty:
    st.subheader("🚨 ALERTAS DE QUIEBRAS Y CONCURSOS")
    st.caption("Estos edictos contienen palabras clave 'quiebra' o 'concurso'. No dependen del filtro de localidad.")
    for _, row in alertas.iterrows():
        info = obtener_info_edicto(row)
        titulo = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
        if info['cuit']:
            titulo += f" - {info['cuit']}"
        with st.expander(titulo):
            # Mostrar texto con resaltado de nombres (usando el mismo método)
            texto_resaltado = row["texto_completo"]
            if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos identificatorios":
                texto_resaltado = re.sub(rf'\b{re.escape(info['nombre_mostrar'])}\b', f'**{info['nombre_mostrar']}**', texto_resaltado, flags=re.IGNORECASE)
            st.markdown(texto_resaltado)
            # Botones de gestión
            edicto_id = row["id"]
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("✅ Revisado", key=f"rev_alert_{edicto_id}"):
                    # Marcar como revisado (en session_state)
                    st.session_state[f"revisado_{edicto_id}"] = True
                    st.rerun()
            with col_b2:
                if st.button("🗑️ Eliminar", key=f"del_alert_{edicto_id}"):
                    confirm_key = f"confirm_alert_{edicto_id}"
                    if st.session_state.get(confirm_key, False):
                        supabase.table("edictos").delete().eq("id", edicto_id).execute()
                        st.success("Eliminado")
                        st.rerun()
                    else:
                        st.session_state[confirm_key] = True
                        st.warning("Hacé clic otra vez para confirmar eliminación.")
    st.divider()

# --- Si no hay otros edictos (después de filtrar alertas), terminar ---
if otros.empty:
    st.info("No hay más edictos para mostrar.")
    st.stop()

# --- Agrupar los edictos restantes por boletín (libros) ---
df_resto = otros
df_resto["boletin_clave"] = df_resto["boletin_numero"] + "_" + df_resto["fecha"].dt.strftime("%Y%m%d")
boletines = df_resto.groupby(["boletin_clave", "fecha", "boletin_numero"])

boletines_list = []
for (clave, fecha, numero), grupo in boletines:
    boletines_list.append({
        "clave": clave,
        "fecha": fecha,
        "numero": numero,
        "grupo": grupo
    })
boletines_list.sort(key=lambda x: x["fecha"], reverse=True)

# --- Mostrar libros (Judicial y Oficial) ---
for boletin in boletines_list:
    fecha = boletin["fecha"]
    numero = boletin["numero"]
    grupo = boletin["grupo"]
    
    grupo_judicial = grupo[grupo["seccion"] == "JUDICIAL"]
    grupo_oficial = grupo[grupo["seccion"] == "OFICIAL"]
    
    if not grupo_judicial.empty:
        with st.expander(f"⚖️ LIBRO JUDICIAL | N° {numero} | {fecha.strftime('%d/%m/%Y')}"):
            for _, row in grupo_judicial.iterrows():
                info = obtener_info_edicto(row)
                titulo = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
                if info['cuit']:
                    titulo += f" - {info['cuit']}"
                # Si está revisado, cambiar ícono
                revisado_key = f"revisado_{row['id']}"
                if revisado_key in st.session_state and st.session_state[revisado_key]:
                    titulo = "🟢 " + titulo
                with st.expander(titulo):
                    texto_resaltado = row["texto_completo"]
                    if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos identificatorios":
                        texto_resaltado = re.sub(rf'\b{re.escape(info['nombre_mostrar'])}\b', f'**{info['nombre_mostrar']}**', texto_resaltado, flags=re.IGNORECASE)
                    st.markdown(texto_resaltado)
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("✅ Revisado", key=f"rev_{row['id']}"):
                            st.session_state[revisado_key] = True
                            st.rerun()
                    with col_b2:
                        if st.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                            confirm_key = f"confirm_{row['id']}"
                            if st.session_state.get(confirm_key, False):
                                supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                st.success("Eliminado")
                                st.rerun()
                            else:
                                st.session_state[confirm_key] = True
                                st.warning("Hacé clic otra vez para confirmar eliminación.")
    
    if not grupo_oficial.empty:
        with st.expander(f"📜 LIBRO OFICIAL | N° {numero} | {fecha.strftime('%d/%m/%Y')}"):
            for _, row in grupo_oficial.iterrows():
                info = obtener_info_edicto(row)
                titulo = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
                if info['cuit']:
                    titulo += f" - {info['cuit']}"
                revisado_key = f"revisado_{row['id']}"
                if revisado_key in st.session_state and st.session_state[revisado_key]:
                    titulo = "🟢 " + titulo
                with st.expander(titulo):
                    texto_resaltado = row["texto_completo"]
                    if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos identificatorios":
                        texto_resaltado = re.sub(rf'\b{re.escape(info['nombre_mostrar'])}\b', f'**{info['nombre_mostrar']}**', texto_resaltado, flags=re.IGNORECASE)
                    st.markdown(texto_resaltado)
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("✅ Revisado", key=f"rev_{row['id']}"):
                            st.session_state[revisado_key] = True
                            st.rerun()
                    with col_b2:
                        if st.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                            confirm_key = f"confirm_{row['id']}"
                            if st.session_state.get(confirm_key, False):
                                supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                st.success("Eliminado")
                                st.rerun()
                            else:
                                st.session_state[confirm_key] = True
                                st.warning("Hacé clic otra vez para confirmar eliminación.")

if st.button("🔄 Recargar datos", key="recargar"):
    st.rerun()
