import streamlit as st
import os
import requests
from supabase import create_client
import pandas as pd
from datetime import datetime, date, timedelta
import re
import base64
from bs4 import BeautifulSoup

st.set_page_config(page_title="Fiscalización - BOLETINES", layout="wide")

st.markdown("""
<style>
.stButton > button {
    padding: 0.2rem 0.6rem;
    font-size: 0.8rem;
    border-radius: 20px;
    margin: 0 0.2rem;
}
.resaltado {
    background-color: #ffff99;
    font-weight: bold;
    padding: 2px 4px;
    border-radius: 4px;
}
@media print {
    body * {
        visibility: hidden;
    }
    .print-area, .print-area * {
        visibility: visible;
    }
    .print-area {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
    }
    .stButton, .stTabs, .stExpander, .stCheckbox, .stRadio, .stMultiselect {
        display: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Fiscalización - BOLETINES")
st.caption("📍 *Solo para estas localidades:* Mar del Plata, Alvarado, Miramar, Mechongue, Otamendi, Vivorata, Vidal, Piran, Las Armas, Maipu, Labarden, Guido, Dolores, Castelli, Tordillo, Conesa, Lavalle, San Clemente, Las Toninas, Santa Teresita, Mar del Tuyu, San Bernardo, La Lucila del Mar, Mar de Ajo, Costa del Este, Pinamar, Madariaga, Villa Gesell, Mar Chiquita")
st.info("🗑️ **Los boletines con más de 60 días se eliminarán automáticamente** para mantener la página rápida y ordenada.")

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

# ── Funciones para consultar boletines disponibles ────────────────────────────
def obtener_boletines_disponibles():
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
                urls = {}
                panel_body = panel.find("div", class_="panel-body")
                if panel_body:
                    for section in panel_body.find_all("div", class_="section"):
                        titulo_sec = section.find("h5", class_="body-title")
                        if not titulo_sec:
                            continue
                        nombre = titulo_sec.get_text(strip=True).upper()
                        link = section.find("a", title="Ver PDF")
                        if not link:
                            link = section.find("a", href=re.compile(r"/secciones/\d+/ver"))
                        if link and link.get("href"):
                            href = link["href"]
                            url_completa = href if href.startswith("http") else BASE_URL + href
                            if "OFICIAL" in nombre:
                                urls["OFICIAL"] = url_completa
                            elif "JUDICIAL" in nombre:
                                urls["JUDICIAL"] = url_completa
                return urls if urls else None
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def descargar_y_procesar_boletin(numero: str, fecha_str: str):
    token = st.secrets.get("GH_TOKEN")
    if not token:
        st.error("Falta GH_TOKEN en los secrets.")
        return False
    repo = "ballanomdq/buscador-osecac"
    url_api = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"ref": "main", "inputs": {"boletin_numero": numero}}
    try:
        response = requests.post(url_api, json=payload, headers=headers, timeout=15)
        if response.status_code == 204:
            st.success(f"Descarga iniciada para el boletín N° {numero}. Los resultados aparecerán en unos minutos.")
            return True
        else:
            st.error(f"Error {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# ── Funciones de gestión en la base de datos ──────────────────────────────────
def eliminar_boletin_de_db(fecha, numero):
    try:
        supabase.table("edictos").delete()\
            .eq("fecha", fecha.isoformat())\
            .eq("boletin_numero", str(numero)).execute()
        st.success(f"Boletín N° {numero} del {fecha.strftime('%d/%m/%Y')} eliminado.")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

def eliminar_boletines_viejos(dias=60):
    fecha_limite = date.today() - timedelta(days=dias)
    try:
        boletines_a_eliminar = supabase.table("edictos").select("fecha", "boletin_numero").lt("fecha", fecha_limite.isoformat()).execute()
        if boletines_a_eliminar.data:
            supabase.table("edictos").delete().lt("fecha", fecha_limite.isoformat()).execute()
            unicos = set([(b["fecha"], b["boletin_numero"]) for b in boletines_a_eliminar.data])
            if unicos:
                st.info(f"🧹 Se eliminaron automáticamente {len(unicos)} boletines con fecha anterior a {fecha_limite} (más de {dias} días).")
    except Exception as e:
        st.warning(f"No se pudieron eliminar boletines viejos automáticamente: {e}")

def obtener_boletines_guardados():
    response = supabase.table("edictos").select("fecha, boletin_numero").execute()
    if not response.data:
        return pd.DataFrame()
    df = pd.DataFrame(response.data)
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    return df.drop_duplicates().sort_values("fecha", ascending=False)

# ── Botones de acción principales ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("📥 Buscar y bajar nuevos boletines", use_container_width=True):
        with st.spinner("Consultando boletines disponibles..."):
            disponibles = obtener_boletines_disponibles()
        if disponibles:
            st.session_state["disponibles"] = disponibles
            st.session_state["mostrar_disponibles"] = True
        else:
            st.warning("No se encontraron boletines disponibles.")

with col2:
    if st.button("🗑️ Limpiar boletines viejos manual", use_container_width=True):
        guardados = obtener_boletines_guardados()
        if guardados.empty:
            st.info("No hay boletines guardados.")
        else:
            st.session_state["para_eliminar"] = guardados
            st.session_state["mostrar_eliminar"] = True

with col3:
    if st.button("🔄 Actualizar vista", use_container_width=True):
        st.rerun()

with col4:
    st.write("")

# ── Eliminación automática de boletines viejos (al cargar la página) ──────────
eliminar_boletines_viejos(60)

# ── Panel para mostrar boletines disponibles y descargar ──────────────────────
if st.session_state.get("mostrar_disponibles", False):
    with st.expander("📥 Boletines disponibles para descargar", expanded=True):
        disponibles = st.session_state.get("disponibles", [])
        if disponibles:
            opciones = {f"N° {n} - {f}": n for n, f in disponibles}
            seleccion = st.selectbox("Elegí un boletín:", list(opciones.keys()))
            if st.button("✅ DESCARGAR ESTE BOLETÍN"):
                num = opciones[seleccion]
                fecha_str = seleccion.split(" - ")[1]
                descargar_y_procesar_boletin(num, fecha_str)
        else:
            st.info("No hay boletines disponibles para descargar.")
        if st.button("Cerrar"):
            st.session_state["mostrar_disponibles"] = False
            st.rerun()
    st.divider()

# ── Panel para eliminar boletines guardados ───────────────────────────────────
if st.session_state.get("mostrar_eliminar", False):
    with st.expander("🗑️ Seleccionar boletín para eliminar", expanded=True):
        guardados = st.session_state.get("para_eliminar", pd.DataFrame())
        if not guardados.empty:
            opciones = {f"{row['fecha']} - N° {row['boletin_numero']}": row for _, row in guardados.iterrows()}
            seleccion = st.selectbox("Elegí un boletín para eliminar:", list(opciones.keys()))
            if st.button("⚠️ CONFIRMAR ELIMINACIÓN"):
                row = opciones[seleccion]
                eliminar_boletin_de_db(row["fecha"], row["boletin_numero"])
        else:
            st.info("No hay boletines guardados para eliminar.")
        if st.button("Cerrar"):
            st.session_state["mostrar_eliminar"] = False
            st.rerun()
    st.divider()

# ── Filtros en sidebar ────────────────────────────────────────────────────────
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

# ── Consulta a Supabase con filtros ───────────────────────────────────────────
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
if seccion_filtro != "Todas":
    query = query.eq("seccion", seccion_filtro)
response = query.execute()
datos = response.data

if not datos:
    st.info("No hay edictos cargados. Usá 'Buscar y bajar nuevos boletines' para comenzar.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
if solo_quiebras:
    df = df[df["texto_completo"].str.lower().str.contains("quiebra|concurso", na=False)]

# ── Función para generar HTML de impresión ────────────────────────────────────
def generar_html_impresion(row, boletin_numero, fecha_boletin, pagina):
    texto = row["texto_completo"]
    nombre = row.get("sujetos") or "Sin nombre"
    cuit = row.get("cuit_detectados") or ""
    localidad = row["localidad"]
    tipo = row.get("tipo_edicto") or "EDICTO"
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Impresión edicto - Boletín N° {boletin_numero}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            .info {{ margin-bottom: 20px; padding: 10px; background: #f5f5f5; border-left: 6px solid #1e88e5; }}
            .edicto {{ white-space: pre-wrap; font-family: monospace; margin-top: 20px; }}
            .resaltado {{ background-color: #ffff99; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="info">
            <strong>Boletín Oficial de la Provincia de Buenos Aires</strong><br>
            Número: {boletin_numero} | Fecha: {fecha_boletin}<br>
            Sección: {row["seccion"]} | Localidad: {localidad}<br>
            Tipo: {tipo} | Sujeto: {nombre} | CUIT/DNI: {cuit}<br>
            Página original: {pagina}
        </div>
        <div class="edicto">
    """
    # Resaltar palabras clave
    texto_resaltado = texto
    palabras_clave = ["quiebra", "concurso", "subasta", "transferencia", row["localidad"].lower(), nombre.lower()]
    for palabra in palabras_clave:
        if palabra:
            texto_resaltado = re.sub(rf'\b{re.escape(palabra)}\b', f'<span class="resaltado">\\0</span>', texto_resaltado, flags=re.IGNORECASE)
    html += texto_resaltado
    html += """
        </div>
    </body>
    </html>
    """
    return html

# ── Renderizado por sección (modificado para incluir botón imprimir y número de página) ──
def renderizar_seccion(df_seccion, seccion_nombre):
    icono_libro = "📘" if seccion_nombre == "JUDICIAL" else "📕"
    if df_seccion.empty:
        st.info(f"No hay edictos en {seccion_nombre}.")
        return
    grupos = df_seccion.groupby(["fecha", "boletin_numero"])
    grupos_ordenados = sorted(grupos, key=lambda x: x[0], reverse=True)
    for (fecha, numero), grupo in grupos_ordenados:
        grupo = grupo.copy()
        grupo["_p"] = [row.get("tipo_edicto", "").lower() in ("quiebra", "concurso", "concurso preventivo") for _, row in grupo.iterrows()]
        grupo = grupo.sort_values("_p", ascending=False).drop(columns=["_p"])
        titulo = f"{icono_libro} Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')} ({len(grupo)} edictos)"
        col_a, col_b = st.columns([6, 1])
        with col_a:
            with st.expander(titulo, expanded=False):
                for _, row in grupo.iterrows():
                    nombre = row.get("sujetos") or "Sin datos"
                    cuit = row.get("cuit_detectados") or ""
                    tipo = row.get("tipo_edicto") or "EDICTO"
                    localidad = row["localidad"]
                    pagina = row.get("pagina", "?")
                    # Mostrar el número de página en el título
                    titulo_edicto = f"🚨 {tipo} | {localidad} | {nombre} - {cuit} (pág. {pagina})"
                    if "quiebra" in tipo.lower() or "concurso" in tipo.lower():
                        icono = "🚨"
                    elif cuit:
                        icono = "⚠️"
                    else:
                        icono = "⚪"
                    titulo_edicto = f"{icono} {tipo} | {localidad} | {nombre} - {cuit} (pág. {pagina})"
                    with st.expander(titulo_edicto):
                        # Resaltar en pantalla
                        texto_resaltado = row["texto_completo"]
                        palabras_clave = ["quiebra", "concurso", "subasta", "transferencia", localidad.lower(), nombre.lower()]
                        for palabra in palabras_clave:
                            if palabra:
                                texto_resaltado = re.sub(rf'\b{re.escape(palabra)}\b', f'<span class="resaltado">\\0</span>', texto_resaltado, flags=re.IGNORECASE)
                        st.markdown(texto_resaltado, unsafe_allow_html=True)
                        col_x, col_y, col_z = st.columns(3)
                        with col_x:
                            if st.button("✅ Revisado", key=f"rev_{row['id']}"):
                                st.success("Marcado como revisado (solo visual)")
                        with col_y:
                            if st.button("🗑️ Eliminar este edicto", key=f"del_{row['id']}"):
                                supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                st.success("Eliminado")
                                st.rerun()
                        with col_z:
                            # Botón Imprimir
                            if st.button("🖨️ Imprimir", key=f"print_{row['id']}"):
                                html_impresion = generar_html_impresion(row, numero, fecha.strftime('%d/%m/%Y'), pagina)
                                b64 = base64.b64encode(html_impresion.encode()).decode()
                                href = f'<a href="data:text/html;base64,{b64}" target="_blank">🖨️ Abrir para imprimir</a>'
                                st.markdown(href, unsafe_allow_html=True)
        with col_b:
            clave_eliminar = f"del_bol_{seccion_nombre}_{numero}_{fecha}"
            if st.button("🗑️", key=clave_eliminar):
                confirm_key = f"confirm_del_bol_{seccion_nombre}_{numero}_{fecha}"
                if st.session_state.get(confirm_key, False):
                    eliminar_boletin_de_db(fecha, numero)
                else:
                    st.session_state[confirm_key] = True
                    st.warning("⚠️ Hacé clic otra vez para confirmar eliminación de TODO el boletín.")
        st.markdown("---")

# ── Pestañas principales ──────────────────────────────────────────────────────
tab_judicial, tab_oficial = st.tabs(["📘 JUDICIAL", "📕 OFICIAL"])
with tab_judicial:
    renderizar_seccion(df[df["seccion"] == "JUDICIAL"], "JUDICIAL")
with tab_oficial:
    renderizar_seccion(df[df["seccion"] == "OFICIAL"], "OFICIAL")
