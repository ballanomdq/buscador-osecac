import streamlit as st
import os
import requests
from supabase import create_client
import pandas as pd
from datetime import datetime, date
import pytz
import time
import re
from bs4 import BeautifulSoup

st.set_page_config(page_title="Boletín Oficial - OSECAC", layout="wide")

# Estilos CSS para botones pequeños e iconos
st.markdown("""
<style>
/* Botones pequeños con iconos */
.small-btn {
    background-color: #f0f2f6;
    border: none;
    border-radius: 20px;
    padding: 0.2rem 0.6rem;
    font-size: 0.8rem;
    margin: 0 0.2rem;
    cursor: pointer;
}
.small-btn:hover {
    background-color: #e0e2e6;
}
/* Para los expanders de boletines */
div[data-testid="stExpander"] details summary {
    background-color: #f0f2f6;
    border-left: 6px solid #1e88e5;
    border-radius: 8px;
    padding: 0.5rem 1rem;
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

# --- Funciones auxiliares para obtener boletines históricos ---
def obtener_lista_boletines():
    """Scrapea la página de ediciones anteriores y devuelve lista de (numero, fecha_str)"""
    url = "https://boletinoficial.gba.gob.ar/ediciones-anteriores"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        boletines = []
        for panel in soup.find_all("div", class_="panel panel-default"):
            titulo = panel.find("h5", class_="panel-title")
            if not titulo:
                continue
            texto = titulo.get_text(strip=True)
            match = re.search(r"N°\s*(\d+)\s*-\s*(\d{2}/\d{2}/\d{4})", texto)
            if match:
                numero = match.group(1)
                fecha_str = match.group(2)
                boletines.append((numero, fecha_str))
        return boletines
    except Exception as e:
        st.error(f"Error al obtener lista de boletines: {e}")
        return []

def obtener_urls_secciones_boletin(numero):
    """Obtiene las URLs de las secciones Oficial y Judicial para un número de boletín dado"""
    url_base = "https://boletinoficial.gba.gob.ar"
    try:
        # Ir a la página de ediciones anteriores y encontrar el panel correspondiente
        resp = requests.get(f"{url_base}/ediciones-anteriores", timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        for panel in soup.find_all("div", class_="panel panel-default"):
            titulo = panel.find("h5", class_="panel-title")
            if titulo and f"N° {numero}" in titulo.get_text():
                urls = {}
                for a in panel.find_all("a", href=True):
                    texto = a.get_text(strip=True).upper()
                    href = a["href"]
                    if "OFICIAL" in texto and "ver" in href:
                        urls["OFICIAL"] = href if href.startswith("http") else url_base + href
                    elif "JUDICIAL" in texto and "ver" in href:
                        urls["JUDICIAL"] = href if href.startswith("http") else url_base + href
                return urls if len(urls) == 2 else None
    except Exception as e:
        st.error(f"Error al obtener URLs del boletín {numero}: {e}")
    return None

# --- Botones discretos en la parte superior (usando columnas) ---
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    if st.button("🔄 Forzar descarga del día", use_container_width=True, help="Descarga el último boletín disponible"):
        # Llamar a GitHub Actions o directamente al scraper? Por ahora lanzamos workflow
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta GH_TOKEN")
        else:
            repo = "ballanomdq/buscador-osecac"
            url_api = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
            data = {"ref": "main"}
            with st.spinner("Lanzando scraping automático..."):
                response = requests.post(url_api, json=data, headers=headers)
                if response.status_code == 204:
                    st.success("Scraping iniciado. Los resultados aparecerán en unos minutos.")
                else:
                    st.error(f"Error {response.status_code}")

with col2:
    if st.button("📜 Históricos", use_container_width=True, help="Seleccionar y descargar un boletín anterior"):
        st.session_state.show_historicos = not st.session_state.get("show_historicos", False)
        st.rerun()

with col3:
    if st.button("🔄 Recargar datos", use_container_width=True, help="Refresca la vista con los datos actuales"):
        st.rerun()

with col4:
    # Placeholder
    pass

# --- Selector de boletines históricos (si se activó) ---
if st.session_state.get("show_historicos", False):
    with st.expander("📖 Seleccionar boletín histórico", expanded=True):
        boletines = obtener_lista_boletines()
        if boletines:
            opciones = [f"N° {n} - {f}" for n, f in boletines]
            seleccion = st.selectbox("Elegí un boletín", opciones, key="hist_select")
            if st.button("Descargar este boletín"):
                # Extraer número
                num = seleccion.split(" - ")[0].replace("N° ", "")
                urls = obtener_urls_secciones_boletin(num)
                if urls:
                    with st.spinner(f"Descargando boletín N° {num}..."):
                        # Aquí llamarías a una función que procese el boletín (puede ser una API o directamente ejecutar scraper)
                        # Por simplicidad, lanzamos un workflow con un parámetro? O mejor, hacemos un script local?
                        # Como esto es complejo, mostramos un mensaje y sugerimos usar el botón de forzar descarga que ya está actualizado.
                        st.info(f"Boletín N° {num} seleccionado. Usá el botón 'Forzar descarga del día' (ya está actualizado para obtener el último). Para bajar uno específico, necesitaríamos una función extra. Por ahora, el sistema automático ya baja el último cada mañana.")
                else:
                    st.error("No se pudieron obtener las secciones de ese boletín.")
        else:
            st.warning("No se pudieron cargar los boletines históricos.")
        if st.button("Cerrar"):
            st.session_state.show_historicos = False
            st.rerun()
    st.divider()

# --- Filtros en sidebar ---
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
    seccion_filtro = st.radio("Sección", ["Todas", "JUDICIAL", "OFICIAL"], index=0)
    solo_quiebras = st.checkbox("🚨 Solo quiebras/concursos")

# --- Consultar datos desde Supabase ---
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
if seccion_filtro != "Todas":
    query = query.eq("seccion", seccion_filtro)
response = query.execute()
datos = response.data

if not datos:
    st.info("No hay edictos cargados. Usá el botón 'Forzar descarga del día' para iniciar la fiscalización.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

# --- Funciones de análisis de edictos (igual que antes) ---
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
        nombre = nombre_q
        cuit = cuit_q
        es_quiebra = True
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
    nombre_mostrar = nombre if nombre else (cuit if cuit else "Sin datos")
    return {"nivel": nivel, "icono": icono, "motivo": motivo, "nombre_mostrar": nombre_mostrar, "cuit": cuit}

# --- Función para eliminar un boletín completo (con confirmación) ---
def eliminar_boletin(fecha, numero):
    try:
        supabase.table("edictos").delete().eq("fecha", fecha.isoformat()).eq("boletin_numero", str(numero)).execute()
        st.success(f"Boletín N° {numero} del {fecha.strftime('%d/%m/%Y')} eliminado.")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

# --- Agrupar por fecha y número de boletín ---
df["boletin_clave"] = df["boletin_numero"] + "_" + df["fecha"].astype(str)
grupos = df.groupby(["fecha", "boletin_numero"])

# --- Mostrar pestañas Judicial y Oficial ---
tab_judicial, tab_oficial = st.tabs(["⚖️ JUDICIAL", "📜 OFICIAL"])

for tab, seccion_val in [(tab_judicial, "JUDICIAL"), (tab_oficial, "OFICIAL")]:
    with tab:
        df_seccion = df[df["seccion"] == seccion_val]
        if df_seccion.empty:
            st.info(f"No hay edictos en {seccion_val}.")
            continue
        # Agrupar por (fecha, numero_boletin)
        grupos_seccion = df_seccion.groupby(["fecha", "boletin_numero"])
        for (fecha, numero), grupo in grupos_seccion:
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
                # Fila de botones discretos (checkbox y eliminar)
                col_a, col_b, col_c = st.columns([1, 1, 8])
                with col_a:
                    nuevo = st.checkbox("Marcar revisado", value=st.session_state[check_key],
                                        key=f"chk_{seccion_val}_{fecha}_{numero}")
                    if nuevo != st.session_state[check_key]:
                        st.session_state[check_key] = nuevo
                        st.rerun()
                with col_b:
                    # Botón eliminar con confirmación (ventana de diálogo)
                    if st.button("🗑️ Eliminar", key=f"del_bol_{seccion_val}_{fecha}_{numero}"):
                        # Usamos un modal de confirmación simple con session_state
                        confirm_key = f"confirm_del_{seccion_val}_{fecha}_{numero}"
                        if st.session_state.get(confirm_key, False):
                            eliminar_boletin(fecha, numero)
                        else:
                            st.session_state[confirm_key] = True
                            st.warning("⚠️ Hacé clic otra vez en 'Eliminar' para confirmar.")
                # Espacio para que no quede apretado
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
                            texto_resaltado = re.sub(rf'\b{re.escape(info["nombre_mostrar"])}\b', f'**{info["nombre_mostrar"]}**', texto_resaltado, flags=re.IGNORECASE)
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
