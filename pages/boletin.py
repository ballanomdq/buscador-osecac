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

# ── Funciones de scraping (selectores actualizados) ───────────────────────────
def obtener_secciones_de_panel(panel) -> dict:
    """
    Extrae URLs de sección desde un div.panel-default usando los selectores
    actuales del sitio del Boletín Oficial:
      div.section > h5.body-title   → nombre (OFICIAL / JUDICIAL)
      a[title="Ver PDF"]             → href del PDF
    """
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
    """Devuelve lista de (numero, fecha_str) de los boletines disponibles."""
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
    """
    Dado un número de boletín, devuelve sus URLs de sección.
    Usa los selectores HTML actualizados.
    """
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
            # Buscar el número en el título (flexible ante variaciones de formato)
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
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta GH_TOKEN en los secrets.")
        else:
            repo    = "ballanomdq/buscador-osecac"
            url_api = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
            with st.spinner("Lanzando scraping..."):
                response = requests.post(url_api, json={"ref": "main"}, headers=headers)
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

# ── Selector de históricos ────────────────────────────────────────────────────
if st.session_state.get("show_historicos", False):
    with st.expander("📖 Seleccionar y descargar boletín histórico", expanded=True):
        with st.spinner("Cargando lista de boletines..."):
            boletines = obtener_lista_boletines()

        if boletines:
            opciones  = [f"N° {n} - {f}" for n, f in boletines]
            seleccion = st.selectbox("Elegí un boletín", opciones, key="hist_select")
            num_sel   = seleccion.split(" - ")[0].replace("N° ", "").strip()

            if st.button("🔍 Obtener secciones de este boletín"):
                with st.spinner(f"Buscando secciones del boletín N° {num_sel}..."):
                    urls = obtener_urls_secciones(num_sel)
                if urls:
                    st.success(f"Secciones encontradas: {', '.join(urls.keys())}")
                    st.session_state["hist_urls"]   = urls
                    st.session_state["hist_numero"] = num_sel
                else:
                    st.error(
                        f"No se encontraron secciones para el boletín N° {num_sel}. "
                        "Puede que ese boletín no tenga PDF disponible aún."
                    )
                    st.session_state.pop("hist_urls", None)

            # Si ya tenemos las URLs, mostrar botón de descarga manual
            if st.session_state.get("hist_urls") and st.session_state.get("hist_numero") == num_sel:
                urls = st.session_state["hist_urls"]
                st.write("URLs disponibles:")
                for sec, url_pdf in urls.items():
                    st.markdown(f"- **{sec}**: `{url_pdf}`")
                st.info(
                    "Para procesar este boletín histórico completamente, "
                    "iniciá el scraper desde 'Forzar descarga' — "
                    "el scraper automáticamente tomará el más reciente."
                )
        else:
            st.warning("No se pudo cargar la lista de boletines.")

        if st.button("Cerrar"):
            st.session_state.show_historicos = False
            st.session_state.pop("hist_urls", None)
            st.rerun()
    st.divider()

# ── Sidebar filtros ───────────────────────────────────────────────────────────
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
    dias_a_mostrar   = st.slider("Mostrar últimos N días", min_value=1, max_value=60, value=15)

# ── Consulta Supabase ─────────────────────────────────────────────────────────
fecha_limite = date.today() - timedelta(days=dias_a_mostrar)
query = supabase.table("edictos").select("*").gte("fecha", fecha_limite.isoformat()).order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
if seccion_filtro != "Todas":
    query = query.eq("seccion", seccion_filtro)
response = query.execute()
datos    = response.data

if not datos:
    st.info("No hay edictos en el período seleccionado. Usá 'Forzar descarga' para iniciar.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

# ── Funciones de análisis ─────────────────────────────────────────────────────
def extraer_nombre_cuit_quiebra(texto):
    patron = r"(?:quiebra|concurso)\s+(?:de\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)(?:\s+\(?(?:CUIT|DNI)[\s:]*(\d{2}-\d{8}-\d|\d{7,8})?|\.|$)"
    m = re.search(patron, texto, re.IGNORECASE)
    if m:
        return m.group(1).strip(), m.group(2) if m.group(2) else None
    return None, None

def extraer_nombre_del_texto(texto):
    cuit_m = re.search(r'\b\d{2}-\d{8}-\d\b', texto)
    cuit   = cuit_m.group(0) if cuit_m else None
    dni_m  = re.search(r'\b(\d{7,8})\b', texto)
    dni    = dni_m.group(1) if dni_m else None
    mayus  = re.findall(r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ]+\b', texto)
    if not mayus:
        mayus = re.findall(r'\b[A-ZÁÉÍÓÚÑ]{5,}\b', texto)
    nombre = mayus[0] if mayus else (f"DNI {dni}" if dni else None)
    return nombre, cuit

def obtener_info_edicto(row):
    texto     = row["texto_completo"]
    sujetos_db = row.get("sujetos")
    cuits_db   = row.get("cuit_detectados")
    nombre_q, cuit_q = extraer_nombre_cuit_quiebra(texto)
    if nombre_q:
        nombre, cuit, es_quiebra = nombre_q, cuit_q, True
    else:
        es_quiebra = "quiebra" in texto.lower() or "concurso" in texto.lower()
        nombre = sujetos_db.split(",")[0].strip() if sujetos_db and sujetos_db.strip() else None
        if not nombre:
            nombre, _ = extraer_nombre_del_texto(texto)
        cuit = cuits_db.split(",")[0].strip() if cuits_db and cuits_db.strip() else None
        if not cuit:
            _, cuit = extraer_nombre_del_texto(texto)
    if es_quiebra:
        nivel, icono, motivo = 0, "🚨", "QUIEBRA/CONCURSO"
    elif cuit:
        nivel, icono, motivo = 1, "⚠️", "PRECAUCIÓN"
    else:
        nivel, icono, motivo = 2, "⚪", "INFORMATIVO"
    return {
        "nivel": nivel, "icono": icono, "motivo": motivo,
        "nombre_mostrar": nombre or cuit or "Sin datos",
        "cuit": cuit
    }

def eliminar_boletin(fecha, numero):
    try:
        supabase.table("edictos").delete()\
            .eq("fecha", fecha.isoformat())\
            .eq("boletin_numero", str(numero)).execute()
        st.success(f"Boletín N° {numero} del {fecha.strftime('%d/%m/%Y')} eliminado.")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

def generar_descarga_boletin(grupo, seccion_nombre, fecha, numero):
    html = f"""<html><head><meta charset="UTF-8">
    <title>Boletín {seccion_nombre} N° {numero} - {fecha.strftime('%d/%m/%Y')}</title>
    <style>body{{font-family:Arial,sans-serif;margin:20px}}
    .edicto{{margin-bottom:20px;border-left:4px solid #ccc;padding-left:10px}}
    .quiebra{{color:red;font-weight:bold}}.precaucion{{color:orange}}
    .informativo{{color:gray}}.localidad{{font-weight:bold}}</style>
    </head><body>
    <h1>Boletín {seccion_nombre} N° {numero} - {fecha.strftime('%d/%m/%Y')}</h1>
    <p>Total: {len(grupo)} edictos</p><hr>"""
    for _, row in grupo.iterrows():
        info  = obtener_info_edicto(row)
        clase = {"QUIEBRA/CONCURSO":"quiebra","PRECAUCIÓN":"precaucion"}.get(info['motivo'],"informativo")
        html += f"""<div class="edicto">
        <p class="localidad">📍 {row['localidad']}</p>
        <p class="{clase}">{info['icono']} {info['motivo']}</p>
        <p><strong>Identificador:</strong> {info['nombre_mostrar']}</p>
        {f"<p><strong>CUIT/DNI:</strong> {info['cuit']}</p>" if info['cuit'] else ""}
        <pre>{row['texto_completo']}</pre></div><hr>"""
    html += "</body></html>"
    return html

# ── Renderizado de una sección ────────────────────────────────────────────────
def renderizar_seccion(df_seccion, seccion_nombre):
    icono_libro = "📘" if seccion_nombre == "JUDICIAL" else "📕"
    if df_seccion.empty:
        st.info(f"No hay edictos en {seccion_nombre} para el período seleccionado.")
        return

    grupos = df_seccion.groupby(["fecha", "boletin_numero"])
    for (fecha, numero), grupo in grupos:
        grupo = grupo.copy()
        grupo["_p"] = [obtener_info_edicto(r)["nivel"] for _, r in grupo.iterrows()]
        grupo = grupo.sort_values("_p").drop(columns=["_p"])

        check_key = f"check_{seccion_nombre}_{fecha}_{numero}"
        if check_key not in st.session_state:
            st.session_state[check_key] = False

        prefijo = "✅ " if st.session_state[check_key] else ""
        titulo  = f"{prefijo}{icono_libro} Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')}"

        with st.expander(titulo, expanded=False):
            col_a, col_b, col_c, _ = st.columns([1, 1, 1, 7])
            with col_a:
                nuevo = st.checkbox("Marcar revisado", value=st.session_state[check_key],
                                    key=f"chk_{seccion_nombre}_{fecha}_{numero}")
                if nuevo != st.session_state[check_key]:
                    st.session_state[check_key] = nuevo
                    st.rerun()
            with col_b:
                if st.button("🗑️ Eliminar", key=f"del_bol_{seccion_nombre}_{fecha}_{numero}"):
                    ck = f"confirm_del_{seccion_nombre}_{fecha}_{numero}"
                    if st.session_state.get(ck, False):
                        eliminar_boletin(fecha, numero)
                    else:
                        st.session_state[ck] = True
                        st.warning("⚠️ Hacé clic otra vez para confirmar.")
            with col_c:
                if st.button("💾 Descargar", key=f"dl_{seccion_nombre}_{fecha}_{numero}"):
                    html_c = generar_descarga_boletin(grupo, seccion_nombre, fecha, numero)
                    b64    = base64.b64encode(html_c.encode()).decode()
                    href   = (f'<a href="data:text/html;base64,{b64}" '
                              f'download="Boletin_{seccion_nombre}_{numero}_{fecha.strftime("%Y%m%d")}.html">'
                              f'📥 Descargar HTML</a>')
                    st.markdown(href, unsafe_allow_html=True)

            st.markdown("---")
            for _, row in grupo.iterrows():
                info    = obtener_info_edicto(row)
                tit_ed  = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
                if info['cuit']:
                    tit_ed += f" - {info['cuit']}"
                rev_key = f"revisado_edicto_{row['id']}"
                if st.session_state.get(rev_key, False):
                    tit_ed = "🟢 " + tit_ed
                with st.expander(tit_ed):
                    nuevo_e = st.checkbox("✓ Marcar como revisado", value=st.session_state.get(rev_key, False),
                                          key=f"chk_edicto_{row['id']}")
                    if nuevo_e != st.session_state.get(rev_key, False):
                        st.session_state[rev_key] = nuevo_e
                        st.rerun()
                    texto_r = row["texto_completo"]
                    if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos":
                        texto_r = re.sub(
                            rf'\b{re.escape(info["nombre_mostrar"])}\b',
                            f'**{info["nombre_mostrar"]}**',
                            texto_r, flags=re.IGNORECASE
                        )
                    st.markdown(texto_r)
                    if st.button("🗑️ Eliminar este edicto", key=f"del_edicto_{row['id']}"):
                        ck = f"conf_edicto_{row['id']}"
                        if st.session_state.get(ck, False):
                            supabase.table("edictos").delete().eq("id", row["id"]).execute()
                            st.success("Eliminado")
                            st.rerun()
                        else:
                            st.session_state[ck] = True
                            st.warning("Hacé clic otra vez para confirmar.")
        st.markdown("---")

# ── Pestañas ──────────────────────────────────────────────────────────────────
tab_judicial, tab_oficial = st.tabs(["📘 JUDICIAL", "📕 OFICIAL"])
with tab_judicial:
    renderizar_seccion(df[df["seccion"] == "JUDICIAL"], "JUDICIAL")
with tab_oficial:
    renderizar_seccion(df[df["seccion"] == "OFICIAL"], "OFICIAL")
