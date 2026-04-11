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

# ── Funciones de scraping ─────────────────────────────────────────────────────
def obtener_secciones_de_panel(panel) -> dict:
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
                urls = obtener_secciones_de_panel(panel)
                if urls:
                    return urls
        return {}
    except Exception as e:
        st.error(f"Error al obtener URLs del boletín {numero}: {e}")
        return {}

# ── Función de diagnóstico ────────────────────────────────────────────────────
def diagnosticar_base():
    """Consulta la base SIN filtros para ver qué hay realmente."""
    try:
        # Total de registros
        total_resp = supabase.table("edictos").select("id", count="exact").limit(0).execute()
        total = total_resp.count if total_resp.count else 0

        # Últimos 5 registros (sin filtro de fecha)
        ultimos_resp = supabase.table("edictos").select("id, fecha, boletin_numero, seccion, localidad")\
            .order("fecha", desc=True).limit(5).execute()
        ultimos = ultimos_resp.data if ultimos_resp.data else []

        # Fechas distintas
        fechas_resp = supabase.table("edictos").select("fecha").execute()
        fechas_set = set()
        for r in (fechas_resp.data or []):
            fechas_set.add(r.get("fecha", "sin fecha"))

        return total, ultimos, sorted(fechas_set, reverse=True)
    except Exception as e:
        return None, None, str(e)

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
    if st.button("🔍 Diagnóstico", use_container_width=True, help="Ver qué hay en la base de datos"):
        st.session_state.show_diagnostico = not st.session_state.get("show_diagnostico", False)
        st.rerun()

with col4:
    if st.button("🔄 Recargar", use_container_width=True, help="Refrescar datos"):
        st.rerun()

# ── Panel de diagnóstico ──────────────────────────────────────────────────────
if st.session_state.get("show_diagnostico", False):
    with st.expander("🔧 DIAGNÓSTICO DE BASE DE DATOS", expanded=True):
        with st.spinner("Consultando Supabase..."):
            total, ultimos, fechas = diagnosticar_base()

        if total is None:
            st.error(f"❌ ERROR DE CONEXIÓN: {fechas}")
            st.markdown("**Posibles causas:**")
            st.code("""
1. SUPABASE_URL incorrecta (verificá que no tenga /rest al final)
2. SUPABASE_KEY incorrecta (usá la ANON key, no la service_role)
3. RLS (Row Level Security) bloqueando lecturas
4. La tabla 'edictos' no existe

SOLUCIÓN RÁPIDA en Supabase SQL Editor:
  ALTER TABLE edictos DISABLE ROW LEVEL SECURITY;
            """)
        elif total == 0:
            st.warning("⚠️ La tabla existe pero está VACÍA (0 registros)")
            st.markdown("**El scraper nunca guardó nada. Verificá:**")
            st.code("""
1. Andá a GitHub Actions y mirá los logs del workflow scrape_edictos
2. Buscá líneas con "❌ ERROR INSERTANDO"
3. Verificá que las credenciales en GitHub Secrets sean correctas
            """)
        else:
            st.success(f"✅ Hay {total} registros en la base")
            st.markdown("**Fechas encontradas:**")
            for f in fechas[:10]:
                st.write(f"  📅 {f}")
            if len(fechas) > 10:
                st.write(f"  ... y {len(fechas) - 10} fechas más")

            st.markdown("**Últimos 5 registros:**")
            if ultimos:
                for r in ultimos:
                    st.write(f"  📄 {r.get('fecha')} | N°{r.get('boletin_numero')} | {r.get('seccion')} | {r.get('localidad')} | ID:{r.get('id')}")
            else:
                st.write("  (no se pudieron leer)")

            # Test de fecha
            st.markdown("---")
            hoy = date.today()
            st.markdown(f"**Fecha de hoy (servidor Streamlit):** `{hoy}`")
            if fechas and isinstance(fechas[0], str):
                st.markdown(f"**Última fecha en base:** `{fechas[0]}`")
                try:
                    ultima = date.fromisoformat(fechas[0])
                    diff = (hoy - ultima).days
                    if diff < 0:
                        st.error(f"⚠️ La última fecha es {abs(diff)} días EN EL FUTURO. Problema de timezone.")
                    elif diff > 60:
                        st.error(f"⚠️ La última fecha es de hace {diff} días. El filtro de {60} días la oculta.")
                    else:
                        st.success(f"✅ La última fecha está dentro del rango del filtro ({diff} días atrás).")
                except Exception:
                    pass

        if st.button("Cerrar diagnóstico"):
            st.session_state.show_diagnostico = False
            st.rerun()
    st.divider()

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
                    st.error(f"No se encontraron secciones para el boletín N° {num_sel}.")
                    st.session_state.pop("hist_urls", None)

            if st.session_state.get("hist_urls") and st.session_state.get("hist_numero") == num_sel:
                urls = st.session_state["hist_urls"]
                st.write("URLs disponibles:")
                for sec, url_pdf in urls.items():
                    st.markdown(f"- **{sec}**: `{url_pdf}`")
                st.info("Para procesar este boletín histórico, usá 'Forzar descarga' (el scraper tomará el más reciente).")
        else:
            st
