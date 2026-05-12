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
    body * { visibility: hidden; }
    .print-area, .print-area * { visibility: visible; }
    .print-area { position: absolute; left: 0; top: 0; width: 100%; }
    .stButton, .stTabs, .stExpander, .stCheckbox, .stRadio, .stMultiselect { display: none !important; }
}
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

# ── Funciones ─────────────────────────────────────────────────────────────────
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
    st.success(f"Boletín N° {numero} eliminado.")
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

# ── Botones ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("📥 Buscar y bajar nuevos boletines"):
        disponibles = obtener_boletines_disponibles()
        if disponibles:
            st.session_state["disponibles"] = disponibles
            st.session_state["mostrar_disponibles"] = True
with col2:
    if st.button("🗑️ Limpiar boletines viejos manual"):
        guardados = obtener_boletines_guardados()
        if not guardados.empty:
            st.session_state["para_eliminar"] = guardados
            st.session_state["mostrar_eliminar"] = True
with col3:
    if st.button("🔄 Actualizar vista"):
        st.rerun()

eliminar_boletines_viejos(60)

# ── Paneles ───────────────────────────────────────────────────────────────────
if st.session_state.get("mostrar_disponibles", False):
    with st.expander("📥 Boletines disponibles", expanded=True):
        disponibles = st.session_state.get("disponibles", [])
        if disponibles:
            opciones = {f"N° {n} - {f}": n for n, f in disponibles}
            seleccion = st.selectbox("Elegí un boletín:", list(opciones.keys()))
            if st.button("✅ DESCARGAR"):
                num = opciones[seleccion]
                fecha_str = seleccion.split(" - ")[1]
                descargar_y_procesar_boletin(num, fecha_str)
        if st.button("Cerrar"):
            st.session_state["mostrar_disponibles"] = False
            st.rerun()
    st.divider()

if st.session_state.get("mostrar_eliminar", False):
    with st.expander("🗑️ Eliminar boletín", expanded=True):
        guardados = st.session_state.get("para_eliminar", pd.DataFrame())
        if not guardados.empty:
            opciones = {f"{row['fecha']} - N° {row['boletin_numero']}": row for _, row in guardados.iterrows()}
            seleccion = st.selectbox("Elegí:", list(opciones.keys()))
            if st.button("⚠️ CONFIRMAR ELIMINACIÓN"):
                row = opciones[seleccion]
                eliminar_boletin_de_db(row["fecha"], row["boletin_numero"])
        if st.button("Cerrar"):
            st.session_state["mostrar_eliminar"] = False
            st.rerun()
    st.divider()

# ── Filtros ───────────────────────────────────────────────────────────────────
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

# ── Consulta ──────────────────────────────────────────────────────────────────
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
if seccion_filtro != "Todas":
    query = query.eq("seccion", seccion_filtro)

response = query.execute()
datos = response.data

if not datos:
    st.info("No hay edictos cargados.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

if solo_quiebras:
    df = df[df["texto_completo"].str.lower().str.contains("quiebra|concurso", na=False)]

# ── Función para resaltar texto ───────────────────────────────────────────────
def resaltar_texto(texto, localidad, nombre, cuit):
    palabras = ["quiebra", "concurso", "subasta", "transferencia", localidad.lower()]
    if nombre and nombre not in ["Sin nombre", "None", ""]:
        palabras.append(nombre.lower())
    if cuit and isinstance(cuit, str):
        palabras.append(cuit.lower())
    resultado = texto
    for palabra in palabras:
        if palabra:
            resultado = re.sub(rf'\b{re.escape(palabra)}\b', f'<span class="resaltado">\\0</span>', resultado, flags=re.IGNORECASE)
    return resultado

# ── Renderizado AGRUPADO POR PÁGINA (pero con títulos completos) ──────────────
def renderizar_seccion(df_seccion, seccion_nombre):
    icono_libro = "📘" if seccion_nombre == "JUDICIAL" else "📕"
    if df_seccion.empty:
        st.info(f"No hay edictos en {seccion_nombre}.")
        return
    
    # Agrupar por página dentro de cada boletín
    if "pagina" not in df_seccion.columns:
        st.warning("Falta la columna 'pagina'. Re-descargá los boletines.")
        return
    
    # Primero ordenar por fecha descendente, luego por página
    df_seccion = df_seccion.sort_values(["fecha", "boletin_numero", "pagina"], ascending=[False, False, True])
    
    # Agrupar por boletín y página
    grupos = df_seccion.groupby(["fecha", "boletin_numero", "pagina"])
    
    for (fecha, numero, pagina), grupo in grupos:
        # Determinar el nivel de prioridad (quiebra primero)
        tipos = grupo["tipo_edicto"].values
        prioridad = 0 if any(t in ["QUIEBRA", "CONCURSO"] for t in tipos) else 1
        
        # Recolectar TODOS los nombres con sus localidades y CUITs
        items = []
        for _, row in grupo.iterrows():
            nombre = row.get("sujetos")
            loc = row["localidad"]
            cuit = row.get("cuit_detectados")
            tipo = row.get("tipo_edicto", "EDICTO")
            
            if nombre and nombre not in ["Sin nombre", "None", "", None]:
                items.append({
                    "nombre": nombre,
                    "localidad": loc,
                    "cuit": cuit,
                    "tipo": tipo
                })
        
        # Si no hay nombres, mostrar mensaje
        if not items:
            items = [{"nombre": "Sin nombre", "localidad": "?", "cuit": "", "tipo": "EDICTO"}]
        
        # Construir título con TODOS los nombres
        nombres_str = []
        for item in items:
            cuit_str = f" - {item['cuit']}" if item['cuit'] else ""
            nombres_str.append(f"{item['nombre']}{cuit_str} ({item['localidad']})")
        
        titulo_nombres = " | ".join(nombres_str)
        
        # Determinar ícono y tipo principal
        tipos_set = set(item['tipo'] for item in items)
        tiene_quiebra = "QUIEBRA" in tipos_set or "CONCURSO" in tipos_set
        icono = "🚨" if tiene_quiebra else "📄"
        
        # Título final
        titulo = f"{icono} {seccion_nombre} | Pág. {pagina} | {titulo_nombres}"
        
        with st.expander(titulo, expanded=False):
            # Mostrar el texto completo (usar el primer elemento del grupo)
            texto_completo = grupo.iloc[0]["texto_completo"]
            
            # Resaltar todas las palabras clave
            texto_resaltado = texto_completo
            for palabra in ["quiebra", "concurso", "subasta", "transferencia"]:
                texto_resaltado = re.sub(rf'\b{re.escape(palabra)}\b', f'<span class="resaltado">\\0</span>', texto_resaltado, flags=re.IGNORECASE)
            for item in items:
                if item['nombre'] and item['nombre'] not in ["Sin nombre", "None", ""]:
                    texto_resaltado = re.sub(rf'\b{re.escape(item['nombre'])}\b', f'<span class="resaltado">\\0</span>', texto_resaltado, flags=re.IGNORECASE)
                if item['localidad']:
                    texto_resaltado = re.sub(rf'\b{re.escape(item['localidad'])}\b', f'<span class="resaltado">\\0</span>', texto_resaltado, flags=re.IGNORECASE)
                if item['cuit']:
                    texto_resaltado = re.sub(rf'\b{re.escape(item['cuit'])}\b', f'<span class="resaltado">\\0</span>', texto_resaltado, flags=re.IGNORECASE)
            
            st.markdown(texto_resaltado, unsafe_allow_html=True)
            
            # Botones
            col_x, col_y, col_z = st.columns(3)
            with col_x:
                if st.button("✅ Revisado", key=f"rev_{seccion_nombre}_{numero}_{pagina}"):
                    st.success("OK")
            with col_y:
                if st.button("🗑️ Eliminar página", key=f"del_{seccion_nombre}_{numero}_{pagina}"):
                    supabase.table("edictos").delete().eq("fecha", fecha.isoformat()).eq("boletin_numero", str(numero)).eq("seccion", seccion_nombre).eq("pagina", pagina).execute()
                    st.rerun()
            with col_z:
                html_impresion = f"""
                <html><head><meta charset="UTF-8"><title>Boletín N° {numero} - Pág. {pagina}</title>
                <style>body{{font-family:Arial;margin:40px}} .info{{background:#f5f5f5;padding:10px;border-left:6px solid #1e88e5}}</style>
                </head><body>
                <div class="info"><strong>Boletín N° {numero}</strong> - {fecha.strftime('%d/%m/%Y')}<br>
                Sección: {seccion_nombre} | Página: {pagina}<br>
                {titulo_nombres}</div>
                <div class="edicto">{texto_resaltado}</div>
                </body></html>
                """
                b64 = base64.b64encode(html_impresion.encode()).decode()
                st.markdown(f'<a href="data:text/html;base64,{b64}" target="_blank">🖨️ Imprimir</a>', unsafe_allow_html=True)

# ── Pestañas ──────────────────────────────────────────────────────────────────
tab_judicial, tab_oficial = st.tabs(["📘 JUDICIAL", "📕 OFICIAL"])
with tab_judicial:
    renderizar_seccion(df[df["seccion"] == "JUDICIAL"], "JUDICIAL")
with tab_oficial:
    renderizar_seccion(df[df["seccion"] == "OFICIAL"], "OFICIAL")
