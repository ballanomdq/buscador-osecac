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
import io
import base64   # <--- ESTO ES LO QUE FALTABA

st.set_page_config(page_title="Boletín Oficial - OSECAC", layout="wide")

# CSS para botones pequeños
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

# --- Funciones auxiliares para boletines históricos ---
def obtener_lista_boletines():
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
                boletines.append((match.group(1), match.group(2)))
        return boletines
    except Exception as e:
        st.error(f"Error al obtener lista de boletines: {e}")
        return []

def obtener_urls_secciones(numero):
    url_base = "https://boletinoficial.gba.gob.ar"
    try:
        resp = requests.get(f"{url_base}/ediciones-anteriores", timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        for panel in soup.find_all("div", class_="panel panel-default"):
            titulo = panel.find("h5", class_="panel-title")
            if titulo and f"N° {numero}" in titulo.get_text():
                urls = {}
                for a in panel.find_all("a", href=True):
                    texto_a = a.get_text(strip=True).upper()
                    href = a["href"]
                    if "OFICIAL" in texto_a and "ver" in href:
                        urls["OFICIAL"] = href if href.startswith("http") else url_base + href
                    elif "JUDICIAL" in texto_a and "ver" in href:
                        urls["JUDICIAL"] = href if href.startswith("http") else url_base + href
                return urls if len(urls) == 2 else None
    except Exception as e:
        st.error(f"Error al obtener URLs del boletín {numero}: {e}")
    return None

# --- Botones superiores ---
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    if st.button("🔄 Forzar descarga", use_container_width=True, help="Descarga el último boletín disponible"):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta GH_TOKEN")
        else:
            repo = "ballanomdq/buscador-osecac"
            url_api = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
            data = {"ref": "main"}
            with st.spinner("Lanzando scraping..."):
                response = requests.post(url_api, json=data, headers=headers)
                if response.status_code == 204:
                    st.success("Scraping iniciado. Resultados en minutos.")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

with col2:
    if st.button("📜 Históricos", use_container_width=True, help="Seleccionar boletín anterior"):
        st.session_state.show_historicos = not st.session_state.get("show_historicos", False)
        st.rerun()

with col3:
    if st.button("🔄 Recargar", use_container_width=True, help="Refrescar datos"):
        st.rerun()

with col4:
    st.write("")

# --- Selector de históricos ---
if st.session_state.get("show_historicos", False):
    with st.expander("📖 Seleccionar boletín histórico", expanded=True):
        boletines = obtener_lista_boletines()
        if boletines:
            opciones = [f"N° {n} - {f}" for n, f in boletines]
            seleccion = st.selectbox("Elegí un boletín", opciones, key="hist_select")
            if st.button("Descargar este boletín"):
                num = seleccion.split(" - ")[0].replace("N° ", "")
                urls = obtener_urls_secciones(num)
                if urls:
                    st.info("Boletín seleccionado. El automático descarga el último cada día.")
                else:
                    st.error("No se encontraron las secciones de ese boletín.")
        else:
            st.warning("No se pudieron cargar los boletines.")
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

# --- Consulta Supabase ---
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

# --- Funciones de análisis ---
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
        nivel = 0; icono = "🚨"; motivo = "QUIEBRA/CONCURSO"
    elif cuit:
        nivel = 1; icono = "⚠️"; motivo = "PRECAUCIÓN"
    else:
        nivel = 2; icono = "⚪"; motivo = "INFORMATIVO"
    nombre_mostrar = nombre if nombre else (cuit if cuit else "Sin datos")
    return {"nivel": nivel, "icono": icono, "motivo": motivo,
            "nombre_mostrar": nombre_mostrar, "cuit": cuit}

def eliminar_boletin(fecha, numero):
    try:
        supabase.table("edictos").delete()\
            .eq("fecha", fecha.isoformat())\
            .eq("boletin_numero", str(numero)).execute()
        st.success(f"Boletín N° {numero} del {fecha.strftime('%d/%m/%Y')} eliminado.")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

# --- Función para generar el contenido descargable de un boletín ---
def generar_descarga_boletin(grupo, seccion_nombre, fecha, numero):
    """Genera un string HTML con todo el contenido del boletín tal como se ve en la página."""
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Boletín {seccion_nombre} N° {numero} - {fecha.strftime('%d/%m/%Y')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .edicto {{ margin-bottom: 20px; border-left: 4px solid #ccc; padding-left: 10px; }}
            .quiebra {{ color: red; font-weight: bold; }}
            .precaucion {{ color: orange; }}
            .informativo {{ color: gray; }}
            .localidad {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Boletín {seccion_nombre} N° {numero} - {fecha.strftime('%d/%m/%Y')}</h1>
        <p>Total de edictos: {len(grupo)}</p>
        <hr>
    """
    for _, row in grupo.iterrows():
        info = obtener_info_edicto(row)
        # Clase CSS según motivo
        if info['motivo'] == "QUIEBRA/CONCURSO":
            clase = "quiebra"
        elif info['motivo'] == "PRECAUCIÓN":
            clase = "precaucion"
        else:
            clase = "informativo"
        html += f"""
        <div class="edicto">
            <p class="localidad">📍 {row['localidad']}</p>
            <p class="{clase}">{info['icono']} {info['motivo']}</p>
            <p><strong>Identificador:</strong> {info['nombre_mostrar']}</p>
            {f"<p><strong>CUIT/DNI:</strong> {info['cuit']}</p>" if info['cuit'] else ""}
            <p><strong>Texto completo:</strong></p>
            <pre>{row['texto_completo']}</pre>
        </div>
        <hr>
        """
    html += "</body></html>"
    return html

# --- Función para renderizar una sección (Judicial u Oficial) con checkbox de revisado y botón de descarga ---
def renderizar_seccion(df_seccion, seccion_nombre):
    """
    seccion_nombre: "JUDICIAL" o "OFICIAL"
    """
    icono_libro = "📘" if seccion_nombre == "JUDICIAL" else "📕"

    if df_seccion.empty:
        st.info(f"No hay edictos en {seccion_nombre}.")
        return

    grupos = df_seccion.groupby(["fecha", "boletin_numero"])

    for (fecha, numero), grupo in grupos:
        # Reordenar edictos por prioridad
        grupo = grupo.copy()
        grupo["_prioridad"] = [obtener_info_edicto(row)["nivel"] for _, row in grupo.iterrows()]
        grupo = grupo.sort_values("_prioridad").drop(columns=["_prioridad"])

        check_key = f"check_{seccion_nombre}_{fecha}_{numero}"
        if check_key not in st.session_state:
            st.session_state[check_key] = False

        prefijo_rev = "✅ " if st.session_state[check_key] else ""
        titulo_boletin = f"{prefijo_rev}{icono_libro} Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')}"

        with st.expander(titulo_boletin, expanded=False):
            # Fila de botones: checkbox para marcar boletín completo, botón de eliminar, botón de descargar
            col_a, col_b, col_c, _ = st.columns([1, 1, 1, 7])
            with col_a:
                nuevo = st.checkbox(
                    "Marcar revisado",
                    value=st.session_state[check_key],
                    key=f"chk_{seccion_nombre}_{fecha}_{numero}"
                )
                if nuevo != st.session_state[check_key]:
                    st.session_state[check_key] = nuevo
                    st.rerun()
            with col_b:
                if st.button("🗑️ Eliminar", key=f"del_bol_{seccion_nombre}_{fecha}_{numero}"):
                    confirm_key = f"confirm_del_{seccion_nombre}_{fecha}_{numero}"
                    if st.session_state.get(confirm_key, False):
                        eliminar_boletin(fecha, numero)
                    else:
                        st.session_state[confirm_key] = True
                        st.warning("⚠️ Hacé clic otra vez en 'Eliminar' para confirmar.")
            with col_c:
                # Botón para descargar este boletín completo
                if st.button("💾 Descargar", key=f"download_{seccion_nombre}_{fecha}_{numero}"):
                    html_content = generar_descarga_boletin(grupo, seccion_nombre, fecha, numero)
                    b64 = base64.b64encode(html_content.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="Boletin_{seccion_nombre}_{numero}_{fecha.strftime("%Y%m%d")}.html">Descargar</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("Listo para descargar (clic en el enlace que apareció arriba).")
                    time.sleep(2)
                    st.rerun()
            st.markdown("---")

            # Edictos individuales
            for _, row in grupo.iterrows():
                info = obtener_info_edicto(row)
                titulo_edicto = (
                    f"{info['icono']} {info['motivo']} | "
                    f"{row['localidad']} | ({info['nombre_mostrar']})"
                )
                if info['cuit']:
                    titulo_edicto += f" - {info['cuit']}"

                rev_key = f"revisado_edicto_{row['id']}"
                # Checkbox para marcar/desmarcar edicto individual
                edicto_checked = st.session_state.get(rev_key, False)
                # Usamos un checkbox en lugar del botón anterior
                # Para mantener la compatibilidad, lo ponemos dentro del expander del edicto
                # pero el título no se modifica con el checkbox; la marca visual será el checkbox mismo.
                # Para mayor claridad, agregamos el checkbox en el cuerpo, no en el título.
                # No obstante, para que se vea un tilde en el título, podríamos agregar un ícono, pero lo dejamos simple.
                # El usuario puede marcar/desmarcar el checkbox.
                with st.expander(titulo_edicto):
                    # Checkbox para marcar revisado
                    nuevo_estado = st.checkbox("✓ Marcar como revisado", value=edicto_checked, key=f"chk_edicto_{row['id']}")
                    if nuevo_estado != edicto_checked:
                        st.session_state[rev_key] = nuevo_estado
                        st.rerun()
                    # Mostrar el texto resaltado
                    texto_resaltado = row["texto_completo"]
                    if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos":
                        texto_resaltado = re.sub(
                            rf'\b{re.escape(info["nombre_mostrar"])}\b',
                            f'**{info["nombre_mostrar"]}**',
                            texto_resaltado,
                            flags=re.IGNORECASE
                        )
                    st.markdown(texto_resaltado)
                    # Botón eliminar edicto individual (sin cambios)
                    if st.button("🗑️ Eliminar este edicto", key=f"del_edicto_{row['id']}"):
                        conf_key = f"conf_edicto_{row['id']}"
                        if st.session_state.get(conf_key, False):
                            supabase.table("edictos").delete().eq("id", row["id"]).execute()
                            st.success("Eliminado")
                            st.rerun()
                        else:
                            st.session_state[conf_key] = True
                            st.warning("Hacé clic otra vez para confirmar.")
        st.markdown("---")

# --- Pestañas principales ---
tab_judicial, tab_oficial = st.tabs(["📘 JUDICIAL", "📕 OFICIAL"])

with tab_judicial:
    df_judicial = df[df["seccion"] == "JUDICIAL"]
    renderizar_seccion(df_judicial, "JUDICIAL")

with tab_oficial:
    df_oficial = df[df["seccion"] == "OFICIAL"]
    renderizar_seccion(df_oficial, "OFICIAL")
