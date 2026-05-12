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
    st.info("No hay edictos cargados.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
if solo_quiebras:
    df = df[df["texto_completo"].str.lower().str.contains("quiebra|concurso", na=False)]

# ── FUNCIONES CORREGIDAS ──────────────────────────────────────────────────────
def generar_html_impresion(row, boletin_numero, fecha_boletin, pagina):
    texto = row["texto_completo"]
    nombre = row.get("sujetos") or "Sin nombre"
    cuit = row.get("cuit_detectados") or ""
    localidad = row["localidad"]
    tipo = row.get("tipo_edicto") or "EDICTO"
    
    for p in ["quiebra", "concurso", localidad.lower(), nombre.lower()]:
        if p:
            texto = re.sub(rf'\b{re.escape(p)}\b', f'<span class="resaltado">\\0</span>', texto, flags=re.IGNORECASE)
    if cuit and isinstance(cuit, str):
        texto = re.sub(rf'\b{re.escape(cuit)}\b', f'<span class="resaltado">\\0</span>', texto, flags=re.IGNORECASE)
    
    html = f"""
    <html><head><meta charset="UTF-8"><title>Boletín N° {boletin_numero} - Pág. {pagina}</title>
    <style>body{{font-family:Arial;margin:40px}}.info{{background:#f5f5f5;padding:10px;border-left:6px solid #1e88e5}}.edicto{{white-space:pre-wrap}}.resaltado{{background:#ffff99}}</style>
    </head><body>
        <div class="info">Boletín N° {boletin_numero} - {fecha_boletin}<br>Sección: {row["seccion"]} | Página: {pagina}<br>{nombre} - {cuit} ({localidad})</div>
        <div class="edicto">{texto}</div>
    </body></html>
    """
    return html

def resaltar_texto(texto, palabras_clave):
    resultado = texto
    for palabra in palabras_clave:
        if palabra and isinstance(palabra, str) and len(palabra) > 2:
            try:
                resultado = re.sub(rf'\b{re.escape(palabra)}\b', f'<span class="resaltado">\\0</span>', resultado, flags=re.IGNORECASE)
            except:
                pass
    return resultado

# ── RENDERIZADO CON CLAVES ÚNICAS ─────────────────────────────────────────────
def renderizar_seccion(df_seccion, seccion_nombre):
    icono_libro = "📘" if seccion_nombre == "JUDICIAL" else "📕"
    if df_seccion.empty:
        st.info(f"No hay edictos en {seccion_nombre}.")
        return
    
    grupos_boletin = df_seccion.groupby(["fecha", "boletin_numero"])
    
    for (fecha, numero), df_bol in sorted(grupos_boletin, key=lambda x: x[0], reverse=True):
        titulo_bol = f"{icono_libro} Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')}"
        
        col_a, col_b = st.columns([6, 1])
        with col_a:
            with st.expander(titulo_bol, expanded=False):
                
                paginas_en_boletin = df_bol.groupby("pagina")
                
                for num_pagina, df_pag in paginas_en_boletin:
                    ids_de_esta_pagina = df_pag["id"].tolist()
                    detalles_sujetos = []
                    todas_palabras_resaltar = set(["quiebra", "concurso", "subasta", "transferencia"])
                    todas_localidades = set()
                    es_quiebra_pagina = False
                    texto_completo = df_pag.iloc[0]["texto_completo"]
                    
                    for _, row in df_pag.iterrows():
                        nombre = row.get("sujetos")
                        cuit = row.get("cuit_detectados")
                        tipo = row.get("tipo_edicto") or "EDICTO"
                        loc = row["localidad"]
                        
                        todas_localidades.add(loc)
                        todas_palabras_resaltar.add(loc)
                        
                        if nombre and nombre not in ["Sin nombre", "None", "", None]:
                            todas_palabras_resaltar.add(nombre)
                            info_sujeto = f"{nombre}"
                            if cuit and isinstance(cuit, str) and cuit not in ["Sin datos", "None", "nan"]:
                                info_sujeto += f" - {cuit}"
                            info_sujeto += f" ({loc})"
                            if info_sujeto not in detalles_sujetos:
                                detalles_sujetos.append(info_sujeto)
                        
                        if cuit and isinstance(cuit, str) and cuit not in ["Sin datos", "None", "nan"]:
                            todas_palabras_resaltar.add(cuit)
                        
                        if "QUIEBRA" in tipo.upper() or "CONCURSO" in tipo.upper():
                            es_quiebra_pagina = True
                    
                    if not detalles_sujetos:
                        detalles_sujetos = ["Sin nombre identificado"]
                    
                    icono = "🚨" if es_quiebra_pagina else "⚪"
                    titulo_fila = f"{icono} Pág. {num_pagina} | {' | '.join(detalles_sujetos)}"
                    
                    # CLAVE ÚNICA: usar timestamp + seccion + numero + pagina
                    unique_key = f"{seccion_nombre}_{numero}_{num_pagina}_{fecha}"
                    
                    with st.expander(titulo_fila):
                        texto_resaltado = resaltar_texto(texto_completo, list(todas_palabras_resaltar))
                        st.markdown(texto_resaltado, unsafe_allow_html=True)
                        
                        c1, c2, c3 = st.columns(3)
                        if c1.button("✅ Revisado", key=f"rev_{unique_key}"):
                            st.success("OK")
                        if c2.button("🗑️ Eliminar Página", key=f"del_{unique_key}"):
                            for id_db in ids_de_esta_pagina:
                                supabase.table("edictos").delete().eq("id", id_db).execute()
                            st.rerun()
                        if c3.button("🖨️ Imprimir", key=f"print_{unique_key}"):
                            row_impresion = df_pag.iloc[0]
                            html = generar_html_impresion(row_impresion, numero, fecha.strftime('%d/%m/%Y'), num_pagina)
                            b64 = base64.b64encode(html.encode()).decode()
                            st.markdown(f'<a href="data:text/html;base64,{b64}" target="_blank">🖨️ Abrir</a>', unsafe_allow_html=True)
        
        with col_b:
            if st.button("🗑️", key=f"del_bol_{seccion_nombre}_{numero}_{fecha}"):
                if st.session_state.get(f"confirm_bol_{seccion_nombre}_{numero}_{fecha}", False):
                    eliminar_boletin_de_db(fecha, numero)
                else:
                    st.session_state[f"confirm_bol_{seccion_nombre}_{numero}_{fecha}"] = True
                    st.warning("⚠️ Confirmar para borrar TODO el boletín.")
        st.markdown("---")

# ── PESTAÑAS ──────────────────────────────────────────────────────────────────
tab_judicial, tab_oficial = st.tabs(["📘 JUDICIAL", "📕 OFICIAL"])
with tab_judicial:
    renderizar_seccion(df[df["seccion"] == "JUDICIAL"], "JUDICIAL")
with tab_oficial:
    renderizar_seccion(df[df["seccion"] == "OFICIAL"], "OFICIAL")
