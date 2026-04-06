import streamlit as st
import os
import requests
from supabase import create_client
import pandas as pd
from datetime import datetime
import pytz
import time
import re

st.set_page_config(page_title="Boletín Oficial - OSECAC", layout="wide")
st.markdown("""
<style>
div[data-testid="stExpander"] details summary {
    background-color: #f0f2f6;
    border-left: 6px solid #1e88e5;
    border-radius: 8px;
    padding: 0.5rem 1rem;
}
</style>
""", unsafe_allow_html=True)
st.title("📚 Fiscalización OSECAC - Boletín Oficial")

# --- Conexión Supabase ---
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
    st.error("Faltan credenciales de Supabase.")
    st.stop()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Botón forzar descarga ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Forzar descarga de Boletines del día", use_container_width=True):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta GH_TOKEN en secrets.")
        else:
            repo = "ballanomdq/buscador-osecac"
            url = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
            data = {"ref": "main"}
            with st.spinner("⏳ Procesando..."):
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 204:
                    st.success("✅ Scraping iniciado.")
                else:
                    st.error(f"Error {response.status_code}")

st.divider()

# --- Filtros ---
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

# --- Consultar datos ---
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
datos = query.execute().data
if not datos:
    st.info("📭 No hay edictos. Usá el botón superior.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date  # ya es fecha correcta

# --- Funciones de análisis (igual que antes, con manejo de None) ---
def extraer_nombre_cuit_quiebra(texto):
    patron = r"(?:quiebra|concurso)\s+(?:de\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)(?:\s+\(?(?:CUIT|DNI)[\s:]*(\d{2}-\d{8}-\d|\d{7,8})?|\.|$)"
    match = re.search(patron, texto, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2) if match.group(2) else None
    return None, None

def extraer_nombre_del_texto(texto):
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
    nombre_q, cuit_q = extraer_nombre_cuit_quiebra(texto)
    if nombre_q:
        nombre, cuit, es_quiebra = nombre_q, cuit_q, True
    else:
        es_quiebra = "quiebra" in texto.lower() or "concurso" in texto.lower()
        if sujetos_db and isinstance(sujetos_db, str) and sujetos_db.strip():
            nombre = sujetos_db.split(",")[0].strip()
        else:
            nombre, _ = extraer_nombre_del_texto(texto)
        if cuits_db and isinstance(cuits_db, str) and cuits_db.strip():
            cuit = cuits_db.split(",")[0].strip()
        else:
            _, cuit = extraer_nombre_del_texto(texto)
    if es_quiebra:
        icono, motivo, nivel = "🚨", "QUIEBRA/CONCURSO", 0
    elif cuit:
        icono, motivo, nivel = "⚠️", "PRECAUCIÓN", 1
    else:
        icono, motivo, nivel = "⚪", "INFORMATIVO", 2
    nombre_mostrar = nombre if nombre else (cuit if cuit else "Sin datos")
    return {"nivel": nivel, "icono": icono, "motivo": motivo, "nombre_mostrar": nombre_mostrar, "cuit": cuit}

# --- Función para eliminar boletín completo (misma fecha y número) ---
def eliminar_boletin(fecha, numero):
    try:
        supabase.table("edictos").delete().eq("fecha", fecha.isoformat()).eq("boletin_numero", str(numero)).execute()
        st.success(f"✅ Boletín N° {numero} del {fecha.strftime('%d/%m/%Y')} eliminado.")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

# --- Pestañas Judicial y Oficial ---
tab_judicial, tab_oficial = st.tabs(["⚖️ JUDICIAL", "📜 OFICIAL"])

for tab, seccion_val in [(tab_judicial, "JUDICIAL"), (tab_oficial, "OFICIAL")]:
    with tab:
        df_seccion = df[df["seccion"] == seccion_val]
        if df_seccion.empty:
            st.info(f"No hay edictos en {seccion_val}.")
            continue
        # Agrupar por (fecha, numero_boletin)
        grupos = df_seccion.groupby(["fecha", "boletin_numero"])
        for (fecha, numero), grupo in grupos:
            # Ordenar edictos por prioridad
            prioridades = [obtener_info_edicto(row)["nivel"] for _, row in grupo.iterrows()]
            grupo = grupo.copy()
            grupo["_prioridad"] = prioridades
            grupo = grupo.sort_values("_prioridad").drop(columns=["_prioridad"])
            
            # Título del expander
            titulo = f"📘 Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')}"
            check_key = f"check_{seccion_val}_{fecha}_{numero}"
            if check_key not in st.session_state:
                st.session_state[check_key] = False
            if st.session_state[check_key]:
                titulo = "✅ " + titulo
            
            with st.expander(titulo, expanded=False):
                # Checkbox para marcar boletín como revisado
                col1, col2 = st.columns([1, 10])
                with col1:
                    nuevo = st.checkbox("Marcar revisado", value=st.session_state[check_key],
                                        key=f"chk_{seccion_val}_{fecha}_{numero}")
                    if nuevo != st.session_state[check_key]:
                        st.session_state[check_key] = nuevo
                        st.rerun()
                # Botón eliminar todo el boletín
                with col2:
                    if st.button("🗑️ Eliminar este boletín", key=f"del_bol_{seccion_val}_{fecha}_{numero}"):
                        confirm_key = f"conf_del_{seccion_val}_{fecha}_{numero}"
                        if st.session_state.get(confirm_key, False):
                            eliminar_boletin(fecha, numero)
                        else:
                            st.session_state[confirm_key] = True
                            st.warning("⚠️ Hacé clic otra vez para confirmar eliminación de TODOS los edictos de este boletín.")
                st.markdown("---")
                # Mostrar edictos
                for _, row in grupo.iterrows():
                    info = obtener_info_edicto(row)
                    titulo_edicto = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
                    if info['cuit']:
                        titulo_edicto += f" - {info['cuit']}"
                    rev_key = f"revisado_{row['id']}"
                    if rev_key in st.session_state and st.session_state[rev_key]:
                        titulo_edicto = "🟢 " + titulo_edicto
                    with st.expander(titulo_edicto):
                        texto_resaltado = row["texto_completo"]
                        if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos":
                            texto_resaltado = re.sub(rf'\b{re.escape(info['nombre_mostrar'])}\b', f'**{info["nombre_mostrar"]}**', texto_resaltado, flags=re.IGNORECASE)
                        st.markdown(texto_resaltado)
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("✅ Revisado", key=f"rev_{row['id']}"):
                                st.session_state[rev_key] = True
                                st.rerun()
                        with col_b2:
                            if st.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                                conf_key = f"conf_{row['id']}"
                                if st.session_state.get(conf_key, False):
                                    supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                    st.success("Eliminado")
                                    st.rerun()
                                else:
                                    st.session_state[conf_key] = True
                                    st.warning("Confirmar otra vez")
            st.markdown("---")

if st.button("🔄 Recargar datos", key="recargar"):
    st.rerun()
