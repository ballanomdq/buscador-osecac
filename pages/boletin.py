import streamlit as st
import os
import time
import requests
import base64
import re
import pandas as pd
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────────────────────────────────────
# Supabase con retry — usando las credenciales que FUNCIONAN (ACTAS)
# ──────────────────────────────────────────────────────────────────────────────
def get_supabase():
    """Crea el cliente Supabase usando las credenciales ACTAS (las que funcionan)."""
    if "supabase_client" not in st.session_state:
        from supabase import create_client
        try:
            # Usar las credenciales ACTAS que ya funcionan en tu página principal
            url = st.secrets.get("SUPABASE_URL_ACTAS") or os.environ.get("SUPABASE_URL_ACTAS")
            key = st.secrets.get("SUPABASE_KEY_ACTAS") or os.environ.get("SUPABASE_KEY_ACTAS")
        except Exception:
            url = os.environ.get("SUPABASE_URL_ACTAS")
            key = os.environ.get("SUPABASE_KEY_ACTAS")
        
        if not url or not key:
            st.error("⚠️ Faltan credenciales de Supabase.")
            st.stop()
        st.session_state["supabase_client"] = create_client(url, key)
    return st.session_state["supabase_client"]


def supabase_execute(query_obj, retries=3, delay=2):
    """Ejecuta una query de Supabase con reintentos automáticos."""
    last_err = None
    for intento in range(1, retries + 1):
        try:
            resp = query_obj.execute()
            return resp.data, None
        except Exception as e:
            last_err = e
            if intento < retries:
                time.sleep(delay * intento)
    return None, str(last_err)


# ──────────────────────────────────────────────────────────────────────────────
# Página
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Fiscalización · Boletines", layout="wide")

st.markdown("""
<style>
/* ── Layout ── */
.block-container { padding-top: 1.2rem; }
.stButton > button {
    padding: 0.2rem 0.7rem; font-size: 0.78rem;
    border-radius: 20px; margin: 0 0.15rem;
}

/* ── Tarjeta de edicto ── */
.edicto-card {
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    font-size: 0.85rem;
    border-left: 5px solid #9ca3af;
    background: #f9fafb;
}
.edicto-card.alta  { border-left-color: #dc2626; background: #fff1f2; }
.edicto-card.media { border-left-color: #d97706; background: #fffbeb; }

/* ── Badges ── */
.badge {
    display: inline-block;
    border-radius: 4px; padding: 1px 7px;
    font-size: 0.71rem; font-weight: 700;
    vertical-align: middle; margin-left: 4px;
}
.badge-alta  { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; }
.badge-media { background:#fef3c7; color:#92400e; border:1px solid #fcd34d; }
.badge-baja  { background:#f3f4f6; color:#374151; border:1px solid #d1d5db; }

/* ── Highlights ── */
.hl   { background:#ffff99; font-weight:700; padding:1px 2px; border-radius:2px; }
.hl-c { background:#bbf7d0; font-weight:700; padding:1px 2px; border-radius:2px; }
.hl-n { background:#bfdbfe; font-weight:700; padding:1px 2px; border-radius:2px; }

/* ── Header info ── */
.hdr-meta {
    font-size:0.78rem; color:#64748b;
    display:flex; flex-wrap:wrap; gap:12px;
    margin-bottom: 4px;
}
.hdr-meta span::before { content:"· "; }
.hdr-meta span:first-child::before { content:""; }
</style>
""", unsafe_allow_html=True)

st.title("📚 Fiscalización · Boletines Oficiales PBA")
st.caption(
    "⚠️ Esta app SOLO LEE datos de la base. No modifica tu página principal."
)

supabase = get_supabase()

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS  = {"User-Agent": "Mozilla/5.0"}

LOCALIDADES = sorted([
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
])

# ──────────────────────────────────────────────────────────────────────────────
# Helpers de scraping
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def obtener_boletines_disponibles():
    try:
        resp = requests.get(f"{BASE_URL}/ediciones-anteriores", headers=HEADERS, timeout=30)
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
        st.error(f"Error al obtener boletines: {e}")
        return []


def descargar_boletin_gh(numero):
    token = st.secrets.get("GH_TOKEN") if hasattr(st, "secrets") else None
    if not token:
        st.error("Falta GH_TOKEN en secrets.")
        return False
    repo    = "ballanomdq/buscador-osecac"
    url_api = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.post(url_api, json={"ref": "main"}, headers=headers, timeout=15)
        if r.status_code == 204:
            st.success(f"✅ Descarga iniciada para boletín N° {numero}.")
            return True
        st.error(f"GitHub respondió {r.status_code}: {r.text[:200]}")
        return False
    except Exception as e:
        st.error(f"Error al llamar GitHub Actions: {e}")
        return False


def eliminar_boletin_db(fecha, numero):
    """Elimina SOLO de la tabla de fiscalización, no toca tu tabla principal."""
    try:
        data, err = supabase_execute(
            supabase.table("edictos_fiscalizacion").delete()
                .eq("fecha", fecha.isoformat())
                .eq("boletin_numero", str(numero))
        )
        if err:
            st.error(f"Error al eliminar: {err}")
        else:
            st.success(f"Boletín N° {numero} del {fecha} eliminado de fiscalización.")
            st.rerun()
    except Exception as e:
        st.error(str(e))


def obtener_boletines_guardados():
    """Lee SOLO de la tabla de fiscalización."""
    data, err = supabase_execute(
        supabase.table("edictos_fiscalizacion").select("fecha,boletin_numero")
    )
    if err or not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    return df.drop_duplicates().sort_values("fecha", ascending=False)


# ──────────────────────────────────────────────────────────────────────────────
# Extracción mejorada de CUIT / nombre desde texto libre
# ──────────────────────────────────────────────────────────────────────────────
_RE_CUIT = re.compile(r'\b(\d{2}[-.\s]?\d{8}[-.\s]?\d{1})\b')
_RE_DNI  = re.compile(r'\b(?:D\.?N\.?I\.?\s*N?[°º]?\s*)(\d{7,8})\b', re.IGNORECASE)
_RE_NOMBRE_CTX = re.compile(
    r'(?:'
    r'quiebra\s+de\s+|'
    r'concurso\s+(?:preventivo\s+)?de\s+|'
    r'fallida?:\s*|'
    r'concursada?:\s*|'
    r'deudora?:\s*|'
    r'(?:señor|señora|sr\.?|sra\.?)\s+'
    r')'
    r'([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñüÁÉÍÓÚÑ,\.\s]{3,60}?)(?=[,;\n]|\s{2,}|$)',
    re.IGNORECASE
)


def extraer_cuits(texto: str) -> list[str]:
    cuits = [re.sub(r'[\s.]', '-', c) for c in _RE_CUIT.findall(texto)]
    dnis  = [f"DNI {d}" for d in _RE_DNI.findall(texto)]
    vistos, resultado = set(), []
    for v in cuits + dnis:
        if v not in vistos:
            vistos.add(v)
            resultado.append(v)
    return resultado


def extraer_nombre(texto: str, nombre_guardado: str | None) -> str:
    invalidos = {"", "sin datos", "sin nombre", "none", "null"}
    if nombre_guardado and nombre_guardado.strip().lower() not in invalidos:
        return nombre_guardado.strip()
    m = _RE_NOMBRE_CTX.search(texto or "")
    if m:
        return m.group(1).strip().rstrip(",")
    return "Sin datos"


def resaltar(texto: str, localidad: str, nombre: str, cuits: list[str]) -> str:
    resultado = texto
    palabras_clave = ["quiebra", "concurso", "subasta", "transferencia",
                      "inhibición", "embargado", "citación"]
    for p in palabras_clave + [localidad.lower()]:
        if p:
            resultado = re.sub(
                rf'(?i)({re.escape(p)})',
                r'<span class="hl">\1</span>',
                resultado
            )
    if nombre and nombre != "Sin datos":
        for parte in nombre.split():
            if len(parte) > 3:
                resultado = re.sub(
                    rf'(?i)({re.escape(parte)})',
                    r'<span class="hl-n">\1</span>',
                    resultado
                )
    for cuit in cuits:
        nro = re.sub(r'\D', '', cuit)
        if nro:
            resultado = re.sub(
                rf'({re.escape(nro[:2])}[-.\s]?{re.escape(nro[2:10])}[-.\s]?{re.escape(nro[10:])})',
                r'<span class="hl-c">\1</span>',
                resultado
            )
    return resultado


def badge(nivel):
    m = {
        "ALTA":  ('<span class="badge badge-alta">🔴 ALTA</span>',  "alta"),
        "MEDIA": ('<span class="badge badge-media">🟡 MEDIA</span>', "media"),
    }
    return m.get(nivel, ('<span class="badge badge-baja">⚪ BAJA</span>', "baja"))


def prio(nivel):
    return {"ALTA": 0, "MEDIA": 1, "BAJA": 2}.get(nivel or "BAJA", 2)


def renderizar_seccion(df_sec: pd.DataFrame, sec_nombre: str):
    icono = "📘" if sec_nombre == "JUDICIAL" else "📕"

    if df_sec.empty:
        st.info(f"No hay edictos en la sección {sec_nombre} con los filtros aplicados.")
        return

    grupos = sorted(
        df_sec.groupby(["fecha", "boletin_numero"]),
        key=lambda x: x[0], reverse=True
    )

    for (fecha, numero), grupo in grupos:
        grupo = grupo.copy()
        grupo["_prio"] = grupo["nivel_confianza"].apply(prio)
        grupo = grupo.sort_values("_prio").drop(columns=["_prio"])

        n_alta  = (grupo["nivel_confianza"] == "ALTA").sum()
        n_media = (grupo["nivel_confianza"] == "MEDIA").sum()
        badges_txt = ("  🔴 " + str(n_alta) if n_alta else "") + \
                     ("  🟡 " + str(n_media) if n_media else "")

        titulo_bol = (
            f"{icono} Boletín N° {numero} — {fecha.strftime('%d/%m/%Y')} "
            f"({len(grupo)} edictos){badges_txt}"
        )

        col_tit, col_del = st.columns([11, 1])
        with col_tit:
            with st.expander(titulo_bol, expanded=False):
                for _, row in grupo.iterrows():
                    texto_completo = row.get("texto_completo") or ""
                    nivel    = row.get("nivel_confianza") or "BAJA"
                    tipo     = row.get("tipo_edicto") or "EDICTO"
                    localidad= row.get("localidad") or "?"
                    pagina   = row.get("pagina", "?")

                    nombre = extraer_nombre(texto_completo, row.get("sujetos"))
                    cuits  = extraer_cuits(texto_completo)
                    cuit_db = row.get("cuit_detectados") or ""
                    for c in re.split(r'[,;\s]+', cuit_db):
                        c = c.strip()
                        if c and c not in cuits:
                            cuits.insert(0, c)

                    badge_html, clase_css = badge(nivel)
                    icono_niv = {"ALTA": "🚨", "MEDIA": "⚠️"}.get(nivel, "⚪")
                    cuit_resumen = cuits[0] if cuits else "—"

                    rev_key = f"rev_{row['id']}"
                    check   = "🟢 " if st.session_state.get(rev_key) else ""
                    titulo_ed = (
                        f"{check}{icono_niv} {tipo} | {localidad} | "
                        f"{nombre}"
                        + (f" — {cuit_resumen}" if cuit_resumen != "—" else "")
                        + f"  (p.{pagina})"
                    )

                    with st.expander(titulo_ed):
                        cuits_str = " · ".join(cuits) if cuits else "No detectado"
                        st.markdown(
                            f'<div class="hdr-meta">'
                            f'<span>Nivel: {badge_html}</span>'
                            f'<span>Tipo: <strong>{tipo}</strong></span>'
                            f'<span>Localidad: <strong>{localidad}</strong></span>'
                            f'<span>CUIT/DNI: <strong>{cuits_str}</strong></span>'
                            f'<span>Sujeto: <strong>{nombre}</strong></span>'
                            f'<span>Página: {pagina}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        st.divider()

                        texto_r = resaltar(texto_completo, localidad, nombre, cuits)
                        st.markdown(
                            f'<div class="edicto-card {clase_css}">{texto_r}</div>',
                            unsafe_allow_html=True
                        )

                        st.caption("🟡 palabras clave · 🟢 CUIT/DNI · 🔵 nombre del sujeto")

                        ca, cb, cc = st.columns(3)
                        with ca:
                            if st.button("✅ Revisado", key=f"rev_btn_{row['id']}"):
                                st.session_state[rev_key] = True
                                st.rerun()
                        with cb:
                            ck = f"conf_del_{row['id']}"
                            lbl = "⚠️ ¿Confirmar?" if st.session_state.get(ck) else "🗑️ Eliminar"
                            if st.button(lbl, key=f"del_btn_{row['id']}"):
                                if st.session_state.get(ck):
                                    data, err = supabase_execute(
                                        supabase.table("edictos_fiscalizacion").delete().eq("id", row["id"])
                                    )
                                    if err:
                                        st.error(f"Error: {err}")
                                    else:
                                        st.rerun()
                                else:
                                    st.session_state[ck] = True
                                    st.rerun()
                        with cc:
                            if st.button("🖨️ Imprimir", key=f"print_{row['id']}"):
                                html_p = generar_html_impresion(row, numero, fecha.strftime('%d/%m/%Y'), nombre, cuits)
                                b64 = base64.b64encode(html_p.encode()).decode()
                                st.markdown(
                                    f'<a href="data:text/html;base64,{b64}" target="_blank">'
                                    f'🖨️ Abrir para imprimir</a>',
                                    unsafe_allow_html=True
                                )

        with col_del:
            ck_bol = f"conf_bol_{sec_nombre}_{numero}_{fecha}"
            lbl_bol = "⚠️" if st.session_state.get(ck_bol) else "🗑️"
            if st.button(lbl_bol, key=f"del_bol_{sec_nombre}_{numero}_{fecha}",
                         help="Eliminar todo este boletín"):
                if st.session_state.get(ck_bol):
                    eliminar_boletin_db(fecha, numero)
                else:
                    st.session_state[ck_bol] = True
                    st.rerun()

        st.markdown("---")


def generar_html_impresion(row, numero, fecha_str, nombre, cuits):
    nivel  = row.get("nivel_confianza") or "BAJA"
    color  = {"ALTA": "#fee2e2", "MEDIA": "#fef3c7"}.get(nivel, "#f3f4f6")
    texto  = resaltar(row["texto_completo"], row["localidad"], nombre, cuits)
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>Boletín N° {numero} — {fecha_str}</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; font-size: 14px; }}
  .info {{ padding: 12px; background: {color}; border-left: 6px solid #888; margin-bottom: 20px; border-radius: 4px; }}
  .info dt {{ font-weight: bold; display: inline; }}
  .texto {{ white-space: pre-wrap; line-height: 1.6; }}
  .hl   {{ background: #ffff99; font-weight: bold; }}
  .hl-c {{ background: #bbf7d0; font-weight: bold; }}
  .hl-n {{ background: #bfdbfe; font-weight: bold; }}
  @media print {{ .info {{ page-break-after: avoid; }} }}
</style></head><body>
<div class="info">
  <strong>Boletín Oficial PBA — N° {numero} | {fecha_str}</strong><br>
  <dt>Localidad:</dt> {row['localidad']} &nbsp;
  <dt>Tipo:</dt> {row.get('tipo_edicto','?')} &nbsp;
  <dt>Página:</dt> {row.get('pagina','?')}<br>
  <dt>Sujeto:</dt> {nombre} &nbsp;
  <dt>CUIT/DNI:</dt> {', '.join(cuits) or '—'} &nbsp;
  <dt>Confianza:</dt> {nivel}
</div>
<div class="texto">{texto}</div>
</body></html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar — filtros
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filtros")
    st.info("📌 Esta app SOLO LEE datos. No modifica tu página principal.")

    localidad_filtro = st.multiselect(
        "Localidad", ["Todas"] + LOCALIDADES, default=["Todas"]
    )
    seccion_filtro = st.radio("Sección", ["Todas", "JUDICIAL", "OFICIAL"], index=0)
    solo_quiebras  = st.checkbox("🚨 Solo quiebras / concursos")
    filtro_conf    = st.multiselect(
        "Nivel de confianza", ["ALTA", "MEDIA", "BAJA"],
        default=["ALTA", "MEDIA", "BAJA"]
    )
    st.markdown("---")
    st.caption(
        "**Leyenda confianza**\n\n"
        "🔴 **ALTA** — quiebra/concurso + nombre identificado\n\n"
        "🟡 **MEDIA** — quiebra/concurso sin nombre claro\n\n"
        "⚪ **BAJA** — solo detectado por localidad"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Barra de acciones
# ──────────────────────────────────────────────────────────────────────────────
ac1, ac2, ac3 = st.columns(3)

with ac1:
    if st.button("📥 Ver boletines disponibles"):
        with st.spinner("Consultando boletinoficial.gba.gob.ar…"):
            disp = obtener_boletines_disponibles()
        if disp:
            st.session_state["disponibles"] = disp
            st.session_state["panel_descarga"] = True
        else:
            st.warning("No se encontraron boletines disponibles.")

with ac2:
    if st.button("🗑️ Eliminar boletín guardado"):
        g = obtener_boletines_guardados()
        if g.empty:
            st.info("No hay boletines guardados.")
        else:
            st.session_state["para_eliminar"] = g
            st.session_state["panel_eliminar"] = True

with ac3:
    if st.button("🔄 Actualizar vista"):
        st.rerun()


# ── Panel: descargar ──────────────────────────────────────────────────────────
if st.session_state.get("panel_descarga"):
    with st.expander("📥 Descargar boletín", expanded=True):
        disp = st.session_state.get("disponibles", [])
        if disp:
            opciones = {f"N° {n}  —  {f}": n for n, f in disp}
            sel = st.selectbox("Seleccioná el boletín:", list(opciones.keys()))
            if st.button("✅ Iniciar descarga"):
                descargar_boletin_gh(opciones[sel])
        if st.button("Cerrar panel descarga"):
            st.session_state["panel_descarga"] = False
            st.rerun()
    st.divider()

# ── Panel: eliminar ───────────────────────────────────────────────────────────
if st.session_state.get("panel_eliminar"):
    with st.expander("🗑️ Eliminar boletín guardado", expanded=True):
        g = st.session_state.get("para_eliminar", pd.DataFrame())
        if not g.empty:
            opciones = {
                f"{r['fecha'].strftime('%d/%m/%Y')}  —  N° {r['boletin_numero']}": r
                for _, r in g.iterrows()
            }
            sel = st.selectbox("Seleccioná:", list(opciones.keys()))
            if st.button("⚠️ CONFIRMAR eliminación"):
                row = opciones[sel]
                eliminar_boletin_db(row["fecha"], row["boletin_numero"])
        if st.button("Cerrar panel eliminación"):
            st.session_state["panel_eliminar"] = False
            st.rerun()
    st.divider()


# ──────────────────────────────────────────────────────────────────────────────
# Consulta principal - USA TABLA SEPARADA "edictos_fiscalizacion"
# ──────────────────────────────────────────────────────────────────────────────
q = supabase.table("edictos_fiscalizacion").select("*").order("fecha", desc=True)

if "Todas" not in localidad_filtro and localidad_filtro:
    q = q.in_("localidad", localidad_filtro)
if seccion_filtro != "Todas":
    q = q.eq("seccion", seccion_filtro)

with st.spinner("Cargando edictos…"):
    datos, err = supabase_execute(q)

if err:
    st.error(
        "❌ No se pudo conectar a la base de datos.\n\n"
        f"**Detalle:** `{err}`\n\n"
        "Intentá nuevamente en unos segundos con el botón **🔄 Actualizar vista**."
    )
    st.stop()

if not datos:
    st.info("No hay edictos cargados aún en la tabla de fiscalización.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

if solo_quiebras:
    df = df[df["tipo_edicto"].isin(["QUIEBRA", "CONCURSO"])]

if filtro_conf and len(filtro_conf) < 3:
    df = df[df["nivel_confianza"].isin(filtro_conf)]

if df.empty:
    st.info("No hay resultados para los filtros seleccionados.")
    st.stop()

# Estadísticas rápidas
total = len(df)
n_a   = (df["nivel_confianza"] == "ALTA").sum()
n_m   = (df["nivel_confianza"] == "MEDIA").sum()
st.markdown(
    f"**{total}** edictos encontrados &nbsp;·&nbsp; "
    f"🔴 **{n_a}** alta &nbsp;·&nbsp; 🟡 **{n_m}** media",
    unsafe_allow_html=True
)

# ──────────────────────────────────────────────────────────────────────────────
# Pestañas por sección
# ──────────────────────────────────────────────────────────────────────────────
tab_j, tab_o = st.tabs(["📘 JUDICIAL", "📕 OFICIAL"])

with tab_j:
    renderizar_seccion(df[df["seccion"] == "JUDICIAL"].copy(), "JUDICIAL")

with tab_o:
    renderizar_seccion(df[df["seccion"] == "OFICIAL"].copy(), "OFICIAL")
