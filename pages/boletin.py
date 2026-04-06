import streamlit as st
import os
import requests
import re
import pandas as pd
from datetime import datetime
import pytz
import time
from bs4 import BeautifulSoup
from supabase import create_client

# Importamos las funciones del scraper (que ya están en el mismo entorno)
# Necesitamos que el archivo scraper_edictos.py esté en el mismo directorio raíz
# y sea accesible. Lo importamos así:
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scraper_edictos import procesar_boletin_completo, extraer_fecha_boletin, extraer_numero_boletin, extraer_texto_pdf, descargar_pdf, buscar_localidades, guardar_edicto
except ImportError:
    # Si no puede importar, definimos funciones vacías (no debería pasar en producción)
    st.error("No se pudo importar scraper_edictos. Verificá que el archivo esté en la raíz.")
    st.stop()

st.set_page_config(page_title="Boletín Oficial - OSECAC", layout="wide")

# Estilos CSS (mismos que antes)
st.markdown("""
<style>
div[data-testid="stExpander"] details summary {
    background-color: #f0f2f6;
    border-left: 6px solid #1e88e5;
    border-radius: 8px;
    padding: 0.5rem 1rem;
}
div[data-testid="stExpander"] details[open] summary {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
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

# --- Funciones auxiliares para la interfaz (ya las tenías) ---
LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

def obtener_info_edicto(row):
    texto = row["texto_completo"]
    sujetos_db = row.get("sujetos")
    cuits_db = row.get("cuit_detectados")
    # Usamos las mismas funciones de extracción del scraper (redefinidas o importadas)
    # Para no complicar, reutilizamos la lógica interna de extraer_nombre_cuit_quiebra (copiada aquí)
    def extraer_nombre_cuit_quiebra(texto):
        patron = r"(?:quiebra|concurso)\s+(?:de\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)(?:\s+\(?(?:CUIT|DNI)[\s:]*(\d{2}-\d{8}-\d|\d{7,8})?|\.|$)"
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            nombre = match.group(1).strip()
            cuit = match.group(2) if match.group(2) else None
            return nombre, cuit
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

    nombre_quiebra, cuit_quiebra = extraer_nombre_cuit_quiebra(texto)
    if nombre_quiebra:
        nombre = nombre_quiebra
        cuit = cuit_quiebra
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
    nombre_mostrar = nombre if nombre else (cuit if cuit else "Sin datos identificatorios")
    return {
        "nivel": nivel,
        "icono": icono,
        "motivo": motivo,
        "nombre_mostrar": nombre_mostrar,
        "cuit": cuit,
        "es_quiebra": es_quiebra
    }

# --- Obtener lista de boletines históricos desde la página oficial ---
def obtener_lista_historicos():
    """
    Scrapea https://boletinoficial.gba.gob.ar/ediciones-anteriores
    y devuelve una lista de diccionarios con 'numero', 'fecha', 'url_judicial', 'url_oficial'.
    También maneja la paginación (por ahora solo la primera página, pero se puede extender).
    """
    base_url = "https://boletinoficial.gba.gob.ar"
    url_ediciones = f"{base_url}/ediciones-anteriores"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url_ediciones, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        st.error(f"Error al obtener ediciones anteriores: {e}")
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    boletines = []
    # Buscar los paneles de cada boletín
    # En el HTML, cada boletín está dentro de <div class="panel panel-default">
    for panel in soup.find_all("div", class_="panel panel-default"):
        heading = panel.find("div", class_="panel-heading")
        if not heading:
            continue
        # Extraer título: "BOLETÍN N° 30211 - 06/04/2026"
        titulo = heading.get_text(strip=True)
        match = re.search(r"BOLETÍN N° (\d+)\s*-\s*(\d{2}/\d{2}/\d{4})", titulo)
        if not match:
            continue
        numero = match.group(1)
        fecha_str = match.group(2)
        fecha = datetime.strptime(fecha_str, "%d/%m/%Y").date()
        # Dentro del panel-body, buscar los enlaces a las secciones
        body = panel.find("div", class_="panel-body")
        if not body:
            continue
        seccion_judicial = None
        seccion_oficial = None
        # Cada sección tiene <h5 class="body-title">JUDICIAL</h5> y luego un enlace
        for section in body.find_all("div", class_="section"):
            h5 = section.find("h5", class_="body-title")
            if not h5:
                continue
            nombre_seccion = h5.get_text(strip=True).upper()
            # Buscar el enlace con ícono de ojo (ver PDF)
            a_tag = section.find("a", title="Ver PDF")
            if a_tag and a_tag.get("href"):
                url_seccion = a_tag["href"]
                if not url_seccion.startswith("http"):
                    url_seccion = base_url + url_seccion
                if nombre_seccion == "JUDICIAL":
                    seccion_judicial = url_seccion
                elif nombre_seccion == "OFICIAL":
                    seccion_oficial = url_seccion
        if seccion_judicial and seccion_oficial:
            boletines.append({
                "numero": numero,
                "fecha": fecha,
                "fecha_str": fecha_str,
                "url_judicial": seccion_judicial,
                "url_oficial": seccion_oficial
            })
    # Ordenar por fecha descendente (más reciente primero)
    boletines.sort(key=lambda x: x["fecha"], reverse=True)
    return boletines

# --- Botón de forzar descarga del día (igual que antes) ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Forzar descarga de Boletines del día", use_container_width=True):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta el token de GitHub (GH_TOKEN) en secrets.")
        else:
            repo = "ballanomdq/buscador-osecac"
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

# --- Selector de boletines históricos (nueva funcionalidad) ---
with st.expander("📜 Descargar boletín histórico", expanded=False):
    st.markdown("Seleccioná un boletín de la lista (se obtiene de la página oficial de Ediciones Anteriores).")
    if st.button("🔄 Actualizar lista de boletines disponibles"):
        st.session_state['lista_historicos'] = obtener_lista_historicos()
        st.rerun()
    if 'lista_historicos' not in st.session_state:
        st.session_state['lista_historicos'] = obtener_lista_historicos()
    if not st.session_state['lista_historicos']:
        st.info("No se pudo obtener la lista de boletines. Verificá tu conexión a internet o que la página oficial esté accesible.")
    else:
        opciones = [f"{b['numero']} - {b['fecha_str']}" for b in st.session_state['lista_historicos']]
        seleccion = st.selectbox("Elegí un boletín:", opciones)
        if st.button("📥 Descargar este boletín"):
            idx = opciones.index(seleccion)
            boletin = st.session_state['lista_historicos'][idx]
            with st.spinner(f"Descargando y procesando boletín N° {boletin['numero']} del {boletin['fecha_str']}..."):
                try:
                    judicial, oficial = procesar_boletin_completo(
                        boletin['fecha'],
                        boletin['numero'],
                        boletin['url_judicial'],
                        boletin['url_oficial']
                    )
                    st.success(f"✅ Procesado: Judicial: {judicial} edictos, Oficial: {oficial} edictos guardados.")
                except Exception as e:
                    st.error(f"Error al procesar: {e}")
        st.caption("Nota: Este proceso descarga y guarda los edictos de ese boletín exactamente igual que el scraping diario.")

st.divider()

# --- Filtro de localidad (sidebar) ---
with st.sidebar:
    st.header("Filtros")
    localidad_filtro = st.multiselect("Localidad", ["Todas"] + sorted(LOCALIDADES), default=["Todas"])

# --- Consultar datos desde Supabase y mostrarlos (igual que antes) ---
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
            <p>Presione el botón superior para iniciar la fiscalización del día o use el selector de boletines históricos.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

# --- Agrupar por fecha y mostrar (igual que antes) ---
df["fecha_str"] = df["fecha"].astype(str)
grupos_fecha = df.groupby("fecha")
fechas_ordenadas = sorted(grupos_fecha.groups.keys(), reverse=True)

tab_judicial, tab_oficial = st.tabs(["⚖️ JUDICIAL", "📜 OFICIAL"])

def ordenar_edictos(grupo_df):
    prioridades = []
    for _, row in grupo_df.iterrows():
        info = obtener_info_edicto(row)
        prioridades.append(info["nivel"])
    grupo_df = grupo_df.copy()
    grupo_df["_prioridad"] = prioridades
    grupo_df = grupo_df.sort_values("_prioridad")
    return grupo_df.drop(columns=["_prioridad"])

def eliminar_boletin(fecha, numero):
    try:
        supabase.table("edictos").delete().eq("fecha", fecha.isoformat()).eq("boletin_numero", str(numero)).execute()
        st.success(f"✅ Boletín N° {numero} del {fecha.strftime('%d/%m/%Y')} eliminado.")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

for tab, seccion_val in [(tab_judicial, "JUDICIAL"), (tab_oficial, "OFICIAL")]:
    with tab:
        df_seccion = df[df["seccion"] == seccion_val]
        if df_seccion.empty:
            st.info(f"No hay edictos en {seccion_val}.")
            continue
        grupos = df_seccion.groupby(["fecha", "boletin_numero"])
        for (fecha, numero), grupo in grupos:
            grupo = ordenar_edictos(grupo)
            titulo = f"📘 Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')}"
            check_key = f"check_{seccion_val}_{fecha}_{numero}"
            if check_key not in st.session_state:
                st.session_state[check_key] = False
            if st.session_state[check_key]:
                titulo = "✅ " + titulo
            with st.expander(titulo, expanded=False):
                col1, col2 = st.columns([1, 10])
                with col1:
                    nuevo = st.checkbox("Marcar revisado", value=st.session_state[check_key],
                                        key=f"chk_{seccion_val}_{fecha}_{numero}")
                    if nuevo != st.session_state[check_key]:
                        st.session_state[check_key] = nuevo
                        st.rerun()
                with col2:
                    if st.button("🗑️ Eliminar este boletín", key=f"del_bol_{seccion_val}_{fecha}_{numero}"):
                        confirm_key = f"conf_del_{seccion_val}_{fecha}_{numero}"
                        if st.session_state.get(confirm_key, False):
                            eliminar_boletin(fecha, numero)
                        else:
                            st.session_state[confirm_key] = True
                            st.warning("⚠️ Hacé clic otra vez para confirmar eliminación de TODOS los edictos de este boletín.")
                st.markdown("---")
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
                        if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos identificatorios":
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
