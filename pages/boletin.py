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
/* Niveles de confianza en los expanders de edictos */
.conf-alta   { border-left: 5px solid #dc2626 !important; background: #fff1f2 !important; }
.conf-media  { border-left: 5px solid #d97706 !important; background: #fffbeb !important; }
.conf-baja   { border-left: 5px solid #9ca3af !important; background: #f9fafb !important; }
/* Badge de confianza inline */
.badge-alta  { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5;
               border-radius:4px; padding:1px 6px; font-size:0.72rem; font-weight:600; }
.badge-media { background:#fef3c7; color:#92400e; border:1px solid #fcd34d;
               border-radius:4px; padding:1px 6px; font-size:0.72rem; font-weight:600; }
.badge-baja  { background:#f3f4f6; color:#374151; border:1px solid #d1d5db;
               border-radius:4px; padding:1px 6px; font-size:0.72rem; font-weight:600; }
.resaltado   { background-color:#ffff99; font-weight:bold; padding:1px 3px; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

st.title("📚 Fiscalización - BOLETINES")
st.caption("📍 Mar del Plata · Alvarado · Miramar · Mechongue · Otamendi · Vivorata · Vidal · Piran · Las Armas · Maipu · Labarden · Guido · Dolores · Castelli · Tordillo · Conesa · Lavalle · San Clemente · Las Toninas · Santa Teresita · Mar del Tuyu · San Bernardo · La Lucila del Mar · Mar de Ajo · Costa del Este · Pinamar · Madariaga · Villa Gesell · Mar Chiquita")

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
    st.error("Faltan credenciales de Supabase.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS  = {"User-Agent": "Mozilla/5.0 (compatible; OSECAC-Scraper/1.0)"}

# ── Scraping de ediciones disponibles ────────────────────────────────────────
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
        st.error(f"Error: {e}")
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
                        link = section.find("a", title="Ver PDF") or \
                               section.find("a", href=re.compile(r"/secciones/\d+/ver"))
                        if link and link.get("href"):
                            href = link["href"]
                            url_c = href if href.startswith("http") else BASE_URL + href
                            if "OFICIAL" in nombre:
                                urls["OFICIAL"] = url_c
                            elif "JUDICIAL" in nombre:
                                urls["JUDICIAL"] = url_c
                return urls or None
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def descargar_boletin(numero, fecha_str):
    token = st.secrets.get("GH_TOKEN")
    if not token:
        st.error("Falta GH_TOKEN en los secrets.")
        return False
    repo    = "ballanomdq/buscador-osecac"
    url_api = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.post(url_api, json={"ref": "main"}, headers=headers, timeout=15)
        if r.status_code == 204:
            st.success(f"Descarga iniciada para N° {numero}. Resultados en unos minutos.")
            return True
        st.error(f"Error {r.status_code}: {r.text}")
        return False
    except Exception as e:
        st.error(str(e))
        return False

# ── Gestión BD ────────────────────────────────────────────────────────────────
def eliminar_boletin_db(fecha, numero):
    try:
        supabase.table("edictos").delete() \
            .eq("fecha", fecha.isoformat()) \
            .eq("boletin_numero", str(numero)).execute()
        st.success(f"Boletín N° {numero} del {fecha.strftime('%d/%m/%Y')} eliminado.")
        st.rerun()
    except Exception as e:
        st.error(str(e))

def eliminar_viejos_auto(dias=60):
    limite = date.today() - timedelta(days=dias)
    try:
        old = supabase.table("edictos").select("fecha,boletin_numero") \
              .lt("fecha", limite.isoformat()).execute()
        if old.data:
            supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()
            unicos = {(r["fecha"], r["boletin_numero"]) for r in old.data}
            st.info(f"🧹 Se eliminaron automáticamente {len(unicos)} boletines anteriores a {limite}.")
    except Exception as e:
        st.warning(f"No se pudieron eliminar boletines viejos: {e}")

def obtener_boletines_guardados():
    r = supabase.table("edictos").select("fecha,boletin_numero").execute()
    if not r.data:
        return pd.DataFrame()
    df = pd.DataFrame(r.data)
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    return df.drop_duplicates().sort_values("fecha", ascending=False)

# ── Botones principales ───────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("📥 Buscar y bajar nuevos boletines", use_container_width=True):
        with st.spinner("Consultando..."):
            disp = obtener_boletines_disponibles()
        if disp:
            st.session_state["disponibles"]        = disp
            st.session_state["mostrar_disponibles"] = True
        else:
            st.warning("No se encontraron boletines.")
with c2:
    if st.button("🗑️ Limpiar boletines viejos", use_container_width=True):
        g = obtener_boletines_guardados()
        if g.empty:
            st.info("No hay boletines guardados.")
        else:
            st.session_state["para_eliminar"]   = g
            st.session_state["mostrar_eliminar"] = True
with c3:
    if st.button("🔄 Actualizar vista", use_container_width=True):
        st.rerun()
with c4:
    st.write("")

# Limpieza automática al cargar
eliminar_viejos_auto(60)

# ── Panel descarga ────────────────────────────────────────────────────────────
if st.session_state.get("mostrar_disponibles"):
    with st.expander("📥 Boletines disponibles", expanded=True):
        disp = st.session_state.get("disponibles", [])
        if disp:
            opciones = {f"N° {n} - {f}": n for n, f in disp}
            sel      = st.selectbox("Elegí un boletín:", list(opciones.keys()))
            if st.button("✅ DESCARGAR ESTE BOLETÍN"):
                descargar_boletin(opciones[sel], sel.split(" - ")[1])
        if st.button("Cerrar "):
            st.session_state["mostrar_disponibles"] = False
            st.rerun()
    st.divider()

# ── Panel eliminar ────────────────────────────────────────────────────────────
if st.session_state.get("mostrar_eliminar"):
    with st.expander("🗑️ Eliminar boletín guardado", expanded=True):
        g = st.session_state.get("para_eliminar", pd.DataFrame())
        if not g.empty:
            opciones = {f"{r['fecha']} - N° {r['boletin_numero']}": r for _, r in g.iterrows()}
            sel      = st.selectbox("Elegí un boletín para eliminar:", list(opciones.keys()))
            if st.button("⚠️ CONFIRMAR ELIMINACIÓN"):
                row = opciones[sel]
                eliminar_boletin_db(row["fecha"], row["boletin_numero"])
        if st.button("Cerrar  "):
            st.session_state["mostrar_eliminar"] = False
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

    st.markdown("---")
    st.markdown("**Nivel de confianza**")
    st.caption("🔴 ALTA · 🟡 MEDIA · ⚪ BAJA")
    filtro_confianza = st.multiselect(
        "Mostrar niveles:",
        ["ALTA", "MEDIA", "BAJA"],
        default=["ALTA", "MEDIA", "BAJA"],
        label_visibility="collapsed"
    )

# ── Consulta Supabase ─────────────────────────────────────────────────────────
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
if seccion_filtro != "Todas":
    query = query.eq("seccion", seccion_filtro)
response = query.execute()
datos    = response.data

if not datos:
    st.info("No hay edictos cargados. Usá 'Buscar y bajar nuevos boletines' para comenzar.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

# Aplicar filtros adicionales
if solo_quiebras:
    df = df[df["texto_completo"].str.lower().str.contains("quiebra|concurso", na=False)]

if filtro_confianza and len(filtro_confianza) < 3:
    # Compatibilidad: si nivel_confianza es NULL en registros viejos, los incluimos
    mask = df["nivel_confianza"].isin(filtro_confianza) | df["nivel_confianza"].isna()
    df   = df[mask]

if df.empty:
    st.info("No hay edictos para los filtros seleccionados.")
    st.stop()

# ── Leyenda de colores ────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; gap:12px; margin-bottom:8px; font-size:0.8rem;">
  <span class="badge-alta">🔴 ALTA — quiebra/concurso + nombre identificado</span>
  <span class="badge-media">🟡 MEDIA — quiebra/concurso sin nombre claro</span>
  <span class="badge-baja">⚪ BAJA — solo localidad, sin palabra clave</span>
</div>
""", unsafe_allow_html=True)

# ── Funciones de análisis ─────────────────────────────────────────────────────
def badge_confianza(nivel):
    if nivel == "ALTA":
        return '<span class="badge-alta">🔴 ALTA</span>'
    if nivel == "MEDIA":
        return '<span class="badge-media">🟡 MEDIA</span>'
    return '<span class="badge-baja">⚪ BAJA</span>'

def prioridad_confianza(nivel):
    return {"ALTA": 0, "MEDIA": 1, "BAJA": 2}.get(nivel or "BAJA", 2)

def resaltar_texto(texto, localidad, nombre, cuit):
    palabras = ["quiebra", "concurso", "subasta", "transferencia", localidad.lower()]
    if nombre and nombre not in ["Sin datos", "None", "", "Sin nombre"]:
        palabras.append(nombre.lower())
    if cuit and cuit.strip():
        palabras.append(cuit.lower())
    resultado = texto
    for p in palabras:
        if p:
            resultado = re.sub(
                rf'\b({re.escape(p)})\b',
                r'<span class="resaltado">\1</span>',
                resultado, flags=re.IGNORECASE
            )
    return resultado

def generar_html_impresion(row, numero, fecha_str):
    texto = row["texto_completo"]
    nombre = row.get("sujetos") or "Sin nombre"
    cuit   = row.get("cuit_detectados") or ""
    nivel  = row.get("nivel_confianza") or "BAJA"
    color  = {"ALTA":"#fee2e2","MEDIA":"#fef3c7","BAJA":"#f3f4f6"}.get(nivel, "#f3f4f6")
    texto_r = resaltar_texto(texto, row["localidad"], nombre, cuit)
    return f"""<html><head><meta charset="UTF-8">
    <title>Edicto — Boletín N° {numero}</title>
    <style>body{{font-family:Arial;margin:40px}}
    .info{{padding:10px;background:{color};border-left:6px solid #888;margin-bottom:20px}}
    .edicto{{white-space:pre-wrap;font-family:monospace}}
    .resaltado{{background:#ffff99;font-weight:bold}}</style></head><body>
    <div class="info">
      <strong>Boletín Oficial PBA</strong><br>
      N° {numero} | Fecha: {fecha_str} | Sección: {row['seccion']}<br>
      Localidad: {row['localidad']} | Tipo: {row.get('tipo_edicto','?')} | Página: {row.get('pagina','?')}<br>
      Sujeto: {nombre} | CUIT/DNI: {cuit}<br>
      Nivel de confianza: {nivel}
    </div>
    <div class="edicto">{texto_r}</div>
    </body></html>"""

# ── Renderizado por sección ───────────────────────────────────────────────────
def renderizar_seccion(df_sec, seccion_nombre):
    icono_libro = "📘" if seccion_nombre == "JUDICIAL" else "📕"
    if df_sec.empty:
        st.info(f"No hay edictos en {seccion_nombre}.")
        return

    grupos = sorted(df_sec.groupby(["fecha","boletin_numero"]), key=lambda x: x[0], reverse=True)

    for (fecha, numero), grupo in grupos:
        grupo = grupo.copy()
        # Ordenar: ALTA primero, luego MEDIA, luego BAJA
        grupo["_prio"] = grupo["nivel_confianza"].apply(prioridad_confianza)
        grupo = grupo.sort_values("_prio").drop(columns=["_prio"])

        # Contar por nivel para el título del boletín
        n_alta  = (grupo["nivel_confianza"] == "ALTA").sum()
        n_media = (grupo["nivel_confianza"] == "MEDIA").sum()
        badges  = ""
        if n_alta:  badges += f" 🔴{n_alta}"
        if n_media: badges += f" 🟡{n_media}"

        titulo_bol = f"{icono_libro} Boletín N° {numero} — {fecha.strftime('%d/%m/%Y')} ({len(grupo)} edictos){badges}"

        col_a, col_b = st.columns([6, 1])
        with col_a:
            with st.expander(titulo_bol, expanded=False):
                for _, row in grupo.iterrows():
                    nombre  = row.get("sujetos") or ""
                    cuit    = row.get("cuit_detectados") or ""
                    tipo    = row.get("tipo_edicto") or "EDICTO"
                    nivel   = row.get("nivel_confianza") or "BAJA"
                    localidad = row["localidad"]
                    pagina  = row.get("pagina", "?")

                    icono = "🚨" if nivel == "ALTA" else ("⚠️" if nivel == "MEDIA" else "⚪")
                    nombre_mostrar = nombre if nombre and nombre not in ["Sin nombre","Sin datos","None",""] else "Sin datos"

                    titulo_ed = (
                        f"{icono} {tipo} | {localidad} | {nombre_mostrar}"
                        + (f" — {cuit}" if cuit else "")
                        + f" (p.{pagina})"
                    )

                    rev_key = f"rev_{row['id']}"
                    if st.session_state.get(rev_key):
                        titulo_ed = "🟢 " + titulo_ed

                    with st.expander(titulo_ed):
                        # Badge de confianza
                        st.markdown(
                            f"Nivel de confianza: {badge_confianza(nivel)}",
                            unsafe_allow_html=True
                        )
                        st.markdown("---")

                        texto_r = resaltar_texto(row["texto_completo"], localidad, nombre, cuit)
                        st.markdown(texto_r, unsafe_allow_html=True)

                        cx, cy, cz = st.columns(3)
                        with cx:
                            if st.button("✅ Revisado", key=f"btn_rev_{row['id']}"):
                                st.session_state[rev_key] = True
                                st.rerun()
                        with cy:
                            if st.button("🗑️ Eliminar", key=f"btn_del_{row['id']}"):
                                ck = f"conf_del_{row['id']}"
                                if st.session_state.get(ck):
                                    supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                    st.success("Eliminado.")
                                    st.rerun()
                                else:
                                    st.session_state[ck] = True
                                    st.warning("Clic otra vez para confirmar.")
                        with cz:
                            if st.button("🖨️ Imprimir", key=f"btn_print_{row['id']}"):
                                html_p = generar_html_impresion(row, numero, fecha.strftime('%d/%m/%Y'))
                                b64    = base64.b64encode(html_p.encode()).decode()
                                st.markdown(
                                    f'<a href="data:text/html;base64,{b64}" target="_blank">🖨️ Abrir para imprimir</a>',
                                    unsafe_allow_html=True
                                )

        with col_b:
            if st.button("🗑️", key=f"del_bol_{seccion_nombre}_{numero}_{fecha}"):
                ck = f"conf_bol_{seccion_nombre}_{numero}_{fecha}"
                if st.session_state.get(ck):
                    eliminar_boletin_db(fecha, numero)
                else:
                    st.session_state[ck] = True
                    st.warning("⚠️ Clic otra vez para eliminar TODO el boletín.")

        st.markdown("---")

# ── Pestañas ──────────────────────────────────────────────────────────────────
tab_j, tab_o = st.tabs(["📘 JUDICIAL", "📕 OFICIAL"])
with tab_j:
    renderizar_seccion(df[df["seccion"] == "JUDICIAL"], "JUDICIAL")
with tab_o:
    renderizar_seccion(df[df["seccion"] == "OFICIAL"], "OFICIAL")
