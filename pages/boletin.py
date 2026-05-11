import streamlit as st
import os
import requests
from supabase import create_client
import pandas as pd
from datetime import datetime, date, timedelta
import re
import time
import base64
from bs4 import BeautifulSoup

st.set_page_config(page_title="Boletín Oficial - OSECAC", layout="wide")

st.markdown("""
<style>
.stButton > button {
    padding: 0.2rem 0.6rem;
    font-size: 0.8rem;
    border-radius: 20px;
    margin: 0 0.2rem;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Fiscalización OSECAC - Boletín Oficial")

# ── Supabase ──────────────────────────────────────────────────────────────────
def get_credentials():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return url, key
    except Exception:
        pass
    return os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")

SUPABASE_URL, SUPABASE_KEY = get_credentials()
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Faltan credenciales de Supabase. Revisá los secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS  = {"User-Agent": "Mozilla/5.0 (compatible; OSECAC-Scraper/1.0)"}

# ── Función para ejecutar scraping de un boletín específico ───────────────────
def ejecutar_scraping_boletin(numero: str):
    """Dispara el workflow de GitHub Actions para un boletín específico"""
    token = st.secrets.get("GH_TOKEN")
    if not token:
        st.error("Falta GH_TOKEN en los secrets.")
        return False
    
    repo = "ballanomdq/buscador-osecac"
    url_api = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    # Pasar el número de boletín como input del workflow
    payload = {
        "ref": "main",
        "inputs": {
            "boletin_numero": numero
        }
    }
    try:
        response = requests.post(url_api, json=payload, headers=headers, timeout=15)
        if response.status_code == 204:
            st.success(f"✅ Scraping iniciado para el boletín N° {numero}. Los resultados aparecerán en unos minutos.")
            return True
        else:
            st.error(f"❌ Error al iniciar scraping: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return False

# ── Funciones de scraping (para selector histórico) ───────────────────────────
def obtener_secciones_de_panel(panel) -> dict:
    urls = {}
    panel_body = panel.find("div", class_="panel-body")
    if not panel_body:
        return urls
    for section in panel_body.find_all("div", class_="section"):
        titulo_tag = section.find("h5", class_="body-title")
        if not titulo_tag:
            continue
        nombre = titulo_tag.get_text(strip=True).upper()
        if "OFICIAL" in nombre:
            clave = "OFICIAL"
        elif "JUDICIAL" in nombre:
            clave = "JUDICIAL"
        else:
            continue
        link = section.find("a", title="Ver PDF")
        if not link:
            link = section.find("a", href=re.compile(r"/secciones/\d+/ver"))
        if link and link.get("href"):
            href = link["href"]
            urls[clave] = href if href.startswith("http") else BASE_URL + href
    return urls

def obtener_lista_boletines() -> list:
    url = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        boletines = []
        for panel in soup.find_all("div", class_="panel-default"):
            titulo_tag = panel.find("h5", class_="panel-title")
            if not titulo_tag:
                continue
            texto = titulo_tag.get_text(strip=True)
            m = re.search(r"N[°º]?\s*(\d+)\s*[-–]\s*(\d{2}/\d{2}/\d{4})", texto, re.IGNORECASE)
            if m:
                boletines.append((m.group(1), m.group(2)))
        return boletines
    except Exception as e:
        st.error(f"Error al obtener lista de boletines: {e}")
        return []

def obtener_urls_secciones(numero: str) -> dict:
    url = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for panel in soup.find_all("div", class_="panel-default"):
            titulo_tag = panel.find("h5", class_="panel-title")
            if not titulo_tag:
                continue
            texto = titulo_tag.get_text(strip=True)
            if re.search(rf"N[°º]?\s*{re.escape(numero)}\b", texto, re.IGNORECASE):
                urls = obtener_secciones_de_panel(panel)
                if urls:
                    return urls
        return {}
    except Exception as e:
        st.error(f"Error al obtener URLs del boletín {numero}: {e}")
        return {}

# ── Botones superiores ────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("🔄 Forzar descarga", use_container_width=True, help="Descarga el último boletín"):
        ejecutar_scraping_boletin("")  # Vacío = último boletín

with col2:
    if st.button("📜 Históricos", use_container_width=True, help="Seleccionar boletín anterior"):
        st.session_state.show_historicos = not st.session_state.get("show_historicos", False)
        st.rerun()

with col3:
    if st.button("🔄 Recargar", use_container_width=True, help="Refrescar datos"):
        st.rerun()

with col4:
    st.write("")

# ── Selector de históricos ────────────────────────────────────────────────────
if st.session_state.get("show_historicos", False):
    with st.expander("📖 Seleccionar y descargar boletín histórico", expanded=True):
        with st.spinner("Cargando lista de boletines..."):
            boletines = obtener_lista_boletines()

        if boletines:
            opciones  = [f"N° {n} - {f}" for n, f in boletines]
            seleccion = st.selectbox("Elegí un boletín", opciones, key="hist_select")
            num_sel   = seleccion.split(" - ")[0].replace("N° ", "").strip()

            if st.button("📥 DESCARGAR ESTE BOLETÍN", key="btn_descargar_historico", type="primary"):
                with st.spinner(f"Iniciando descarga del boletín N° {num_sel}..."):
                    ejecutar_scraping_boletin(num_sel)
        else:
            st.warning("No se pudo cargar la lista de boletines.")

        if st.button("Cerrar"):
            st.session_state.show_historicos = False
            st.rerun()
    st.divider()

# ── Sidebar filtros (SIN FILTRO DE DÍAS) ─────────────────────────────────────
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
    seccion_filtro   = st.radio("Sección", ["Todas", "JUDICIAL", "OFICIAL"], index=0)
    solo_quiebras    = st.checkbox("🚨 Solo quiebras/concursos")

# ── Consulta Supabase ─────────────────────────────────────────────────────────
query = supabase.table("edictos").select("*").order("fecha", desc=True)

if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
if seccion_filtro != "Todas":
    query = query.eq("seccion", seccion_filtro)
response = query.execute()
datos = response.data

if not datos:
    st.info("No hay edictos cargados. Usá 'Forzar descarga' para iniciar.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

if solo_quiebras:
    df = df[df["texto_completo"].str.lower().str.contains("quiebra|concurso", na=False)]
    if df.empty:
        st.info("No hay edictos de quiebras/concursos en los filtros seleccionados.")
        st.stop()

# ── El resto de las funciones (extraer_nombre_cuit_quiebra, etc.) se mantienen IGUAL que en tu código actual ──
# (Copialas desde tu versión funcional, ya que no cambian)

# ... (aquí van las funciones extraer_nombre_cuit_quiebra, extraer_nombre_del_texto, obtener_info_edicto, eliminar_boletin, generar_descarga_boletin, renderizar_seccion, y las pestañas)
