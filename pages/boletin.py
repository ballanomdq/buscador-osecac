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
.stButton > button { padding: 0.2rem 0.6rem; font-size: 0.8rem; border-radius: 20px; margin: 0 0.2rem; }
.resaltado { background-color: #ffff99; font-weight: bold; padding: 2px 4px; border-radius: 4px; }
@media print { body * { visibility: hidden; } .print-area, .print-area * { visibility: visible; } .print-area { position: absolute; left: 0; top: 0; width: 100%; } .stButton, .stTabs, .stExpander, .stCheckbox, .stRadio, .stMultiselect { display: none !important; } }
</style>
""", unsafe_allow_html=True)

st.title("📚 Fiscalización - BOLETINES")
st.caption("📍 *Solo para estas localidades:* Mar del Plata, Alvarado, Miramar, Mechongue, Otamendi, Vivorata, Vidal, Piran, Las Armas, Maipu, Labarden, Guido, Dolores, Castelli, Tordillo, Conesa, Lavalle, San Clemente, Las Toninas, Santa Teresita, Mar del Tuyu, San Bernardo, La Lucila del Mar, Mar de Ajo, Costa del Este, Pinamar, Madariaga, Villa Gesell, Mar Chiquita")
st.info("🗑️ **Los boletines con más de 60 días se eliminarán automáticamente**")

# ── Supabase ──────────────────────────────────────────────────────────────────
def get_credentials():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return url, key
    except:
        pass
    return os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")

SUPABASE_URL, SUPABASE_KEY = get_credentials()
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Faltan credenciales de Supabase.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def obtener_boletines_disponibles():
    url = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
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
        st.error(f"Error: {e}")
        return []

def obtener_urls_secciones(numero: str) -> dict:
    url = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
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
        st.error("Falta GH_TOKEN")
        return False
    repo = "ballanomdq/buscador-osecac"
    url_api = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"ref": "main", "inputs": {"boletin_numero": numero}}
    try:
        response = requests.post(url_api, json=payload, headers=headers, timeout=15)
        if response.status_code == 204:
            st.success(f"Descarga iniciada para N° {numero}.")
            return True
        else:
            st.error(f"Error {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def eliminar_boletin_de_db(fecha, numero):
    supabase.table("edictos").delete().eq("fecha", fecha.isoformat()).eq("boletin_numero", str(numero)).execute()
    st.success(f"Boletín N° {numero} del {fecha.strftime('%d/%m/%Y')} eliminado.")
    st.rerun()

def eliminar_boletines_viejos(dias=60):
    fecha_limite = date.today() - timedelta(days=dias)
    supabase.table("edictos").delete().lt("fecha", fecha_limite.isoformat()).execute()

def obtener_boletines_guardados():
    response = supabase.table("edictos").select("fecha, boletin_numero").execute()
    if not response.data:
        return pd.DataFrame()
    df = pd.DataFrame(response.data)
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    return df.drop_duplicates().sort_values("fecha", ascending=False)

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    if st.button("📥 Buscar y bajar nuevos boletines", use_container_width=True):
        disponibles = obtener_boletines_disponibles()
        if disponibles:
            st.session_state["disponibles"] = disponibles
            st.session_state["mostrar_disponibles"] = True
        else:
            st.warning("No se encontraron boletines.")
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

eliminar_boletines_viejos(60)

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

def generar_html_impresion(row, boletin_numero, fecha_boletin, pagina):
    texto = row["texto_completo"]
    nombre = row.get("sujetos") or "Sin nombre"
    cuit = row.get("cuit_detectados") or ""
    localidad = row["localidad"]
    tipo = row.get("tipo_edicto") or "EDICTO"
    html = f"""
    <html><head><meta charset="UTF-8"><title>Impresión - Boletín N° {boletin_numero}</title>
    <style>body{{font-family:Arial;margin:40px}}.info{{margin-bottom:20px;padding:10px;background:#f5f5f5;border-left:6px solid #1e88e5}}.edicto{{white-space:pre-wrap}}.resaltado{{background-color:#ffff99}}</style>
    </head><body>
        <div class="info"><strong>Boletín Oficial de la Provincia de Buenos Aires</strong><br>
        Número: {boletin_numero} | Fecha: {fecha_boletin}<br>
        Sección: {row["seccion"]} | Localidad: {localidad}<br>
        Tipo: {tipo} | Sujeto: {nombre} | CUIT/DNI: {cuit}<br>Página original: {pagina}</div>
        <div class="edicto">"""
    for p in ["quiebra", "concurso", localidad.lower(), nombre.lower()]:
        if p:
            texto = re.sub(rf'\b{re.escape(p)}\b', f'<span class="resaltado">\\0</span>', texto, flags=re.IGNORECASE)
    html += texto + "</div></body></html>"
    return html

# FUNCION CORREGIDA
def resaltar_texto(texto, localidad, nombre, cuit):
    palabras = ["quiebra", "concurso", "subasta", "transferencia", localidad.lower()]
    if nombre and nombre not in ["Sin nombre", "Sin datos", "None", ""]:
        palabras.append(nombre.lower())
    # CORREGIDO: solo si cuit es string y no está vacío
    if cuit and isinstance(cuit, str) and cuit.strip() and cuit.lower() not in ["nan", "none"]:
        palabras.append(cuit.lower())
    resultado = texto
    for p in palabras:
        if p:
            try:
                resultado = re.sub(rf'\b{re.escape(p)}\b', f'<span class="resaltado">\\0</span>', resultado, flags=re.IGNORECASE)
            except:
                pass
    return resultado

def renderizar_seccion(df_seccion, seccion_nombre):
    icono_libro = "📘" if seccion_nombre == "JUDICIAL" else "📕"
    if df_seccion.empty:
        st.info(f"No hay edictos en {seccion_nombre}.")
        return
    grupos = df_seccion.groupby(["fecha", "boletin_numero"])
    for (fecha, numero), grupo in sorted(grupos, key=lambda x: x[0], reverse=True):
        grupo = grupo.copy()
        grupo["_p"] = grupo["tipo_edicto"].apply(lambda x: 0 if x and ("quiebra" in x.lower() or "concurso" in x.lower()) else 1)
        grupo = grupo.sort_values("_p")
        titulo = f"{icono_libro} Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')} ({len(grupo)} edictos)"
        col_a, col_b = st.columns([6, 1])
        with col_a:
            with st.expander(titulo, expanded=False):
                for _, row in grupo.iterrows():
                    nombre = row.get("sujetos") or ""
                    cuit = row.get("cuit_detectados") or ""
                    tipo = row.get("tipo_edicto") or "EDICTO"
                    localidad = row["localidad"]
                    pagina = row.get("pagina", "?")
                    icono = "🚨" if "QUIEBRA" in tipo or "CONCURSO" in tipo else ("⚠️" if cuit else "⚪")
                    titulo_edicto = f"{icono} {tipo} | {localidad} | {nombre or 'Sin datos'} - {cuit or 'Sin CUIT'} (pág. {pagina})"
                    with st.expander(titulo_edicto):
                        st.markdown(resaltar_texto(row["texto_completo"], localidad, nombre, cuit), unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        if col1.button("✅ Revisado", key=f"rev_{row['id']}"):
                            st.success("Marcado como revisado")
                        if col2.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                            supabase.table("edictos").delete().eq("id", row["id"]).execute()
                            st.rerun()
                        if col3.button("🖨️ Imprimir", key=f"print_{row['id']}"):
                            html = generar_html_impresion(row, numero, fecha.strftime('%d/%m/%Y'), pagina)
                            b64 = base64.b64encode(html.encode()).decode()
                            st.markdown(f'<a href="data:text/html;base64,{b64}" target="_blank">🖨️ Abrir para imprimir</a>', unsafe_allow_html=True)
        with col_b:
            if st.button("🗑️", key=f"del_bol_{seccion_nombre}_{numero}_{fecha}"):
                if st.session_state.get(f"confirm_bol_{seccion_nombre}_{numero}_{fecha}", False):
                    eliminar_boletin_de_db(fecha, numero)
                else:
                    st.session_state[f"confirm_bol_{seccion_nombre}_{numero}_{fecha}"] = True
                    st.warning("⚠️ Hacé clic otra vez para confirmar eliminación de TODO el boletín.")
        st.markdown("---")

tab_judicial, tab_oficial = st.tabs(["📘 JUDICIAL", "📕 OFICIAL"])
with tab_judicial:
    renderizar_seccion(df[df["seccion"] == "JUDICIAL"], "JUDICIAL")
with tab_oficial:
    renderizar_seccion(df[df["seccion"] == "OFICIAL"], "OFICIAL")
