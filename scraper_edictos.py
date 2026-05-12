"""
scraper_edictos.py - VERSIÓN ORIGINAL (CORREGIDA SOLO NOMBRES)
"""

import sys
import re
import os
import logging
import requests
import pdfplumber
from io import BytesIO
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from supabase import create_client
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

BUENOS_AIRES = ZoneInfo("America/Argentina/Buenos_Aires")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    log.error("Faltan credenciales")
    sys.exit(0)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS = {"User-Agent": "Mozilla/5.0"}

LOCALIDADES = {
    "mar del plata", "alvarado", "miramar", "mechongue", "otamendi", "vivorata",
    "vidal", "piran", "las armas", "maipu", "labarden", "guido", "dolores",
    "castelli", "tordillo", "conesa", "lavalle", "san clemente", "las toninas",
    "santa teresita", "mar del tuyu", "san bernardo", "la lucila del mar",
    "mar de ajo", "costa del este", "pinamar", "madariaga", "villa gesell",
    "mar chiquita", "general guido",
}

ABREVIATURAS = {
    "mdp": "mar del plata", "m.d.p.": "mar del plata",
    "gral. guido": "general guido", "gral. madariaga": "madariaga",
    "pdo. de dolores": "dolores", "mar chiq.": "mar chiquita",
}

ALIAS_LOCALIDAD = {"general guido": "Guido", "gdor. arias": "Dolores"}

RE_INICIO_TRANSFERENCIAS = re.compile(r'\bTRANSFERENCIAS?\b', re.IGNORECASE)

# CORREGIDO: mejor extracción de nombre
def extraer_nombre_corregido(texto: str) -> str:
    # Busca "quiebra de ..." o "concurso de ..."
    patron = re.compile(
        r'(?:quiebra|concurso)\s+de\s+(?:la\s+)?(?:señora\s+)?(?:señor\s+)?(?:doña\s+)?(?:don\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,\.]+?)(?:\s*(?:\(?DNI|CUIT|CUIL|\(|\n|$))',
        re.IGNORECASE
    )
    m = patron.search(texto)
    if m:
        nombre = m.group(1).strip().strip(',').strip()
        # Limpiar residuos
        nombre = re.sub(r'\s+', ' ', nombre)
        if len(nombre) > 3:
            return nombre.upper()
    
    # Si no, busca secuencia de mayúsculas
    mayus = re.findall(r'\b([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+)?)\b', texto)
    if mayus:
        return mayus[0].strip()
    return ""

def extraer_tipo_edicto(texto: str) -> str:
    if re.search(r'\bquiebra\b', texto, re.IGNORECASE):
        return "QUIEBRA"
    if re.search(r'\bconcurso\b', texto, re.IGNORECASE):
        return "CONCURSO"
    return "EDICTO"

def extraer_cuits_dnis(texto: str) -> list:
    encontrados = set()
    for m in re.findall(r'\b\d{2}-\d{8}-\d\b', texto):
        encontrados.add(m)
    for m in re.findall(r'\b(?:DNI|CUIT|CUIL)[\s:Nº°]*(\d{6,11})\b', texto, re.IGNORECASE):
        encontrados.add(m)
    for m in re.findall(r'\b(\d{7,8})\b', texto):
        if not (1900 <= int(m) <= 2030):
            encontrados.add(m)
    return sorted(encontrados)

def normalizar_abreviaturas(texto: str) -> str:
    texto_lower = texto.lower()
    for abrev, expansion in ABREVIATURAS.items():
        texto_lower = re.sub(rf'\b{re.escape(abrev)}\b', expansion, texto_lower)
    return texto_lower

def localidades_en_texto(texto: str) -> list:
    texto_norm = normalizar_abreviaturas(texto)
    encontradas = []
    vistas = set()
    for loc in LOCALIDADES:
        if loc in texto_norm and loc not in vistas:
            vistas.add(loc)
            encontradas.append(ALIAS_LOCALIDAD.get(loc, loc.title()))
    return encontradas

def guardar_pagina(localidad, texto, seccion, fecha, boletin_numero, url_pdf, pagina) -> bool:
    tipo = extraer_tipo_edicto(texto)
    nombre = extraer_nombre_corregido(texto)
    cuits = extraer_cuits_dnis(texto)
    
    existente = supabase.table("edictos").select("id").eq("fecha", fecha.isoformat()).eq("boletin_numero", str(boletin_numero)).eq("seccion", seccion).eq("localidad", localidad).eq("pagina", pagina).execute()
    if existente.data:
        return False
    
    data = {
        "fecha": fecha.isoformat(),
        "boletin_numero": str(boletin_numero),
        "seccion": seccion,
        "localidad": localidad,
        "tipo_edicto": tipo,
        "cuit_detectados": ", ".join(cuits) if cuits else None,
        "sujetos": nombre if nombre else None,
        "texto_completo": texto,
        "url_pdf": url_pdf,
        "pagina": pagina,
    }
    supabase.table("edictos").insert(data).execute()
    log.info(f"✅ Guardado: pág {pagina} | {tipo} | {localidad} | {nombre or '(sin nombre)'}")
    return True

def eliminar_viejos(dias=60):
    limite = (datetime.now(BUENOS_AIRES) - timedelta(days=dias)).date()
    supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()

# ── Web scraping ──────────────────────────────────────────────────────────────
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
    return urls

def obtener_boletin_por_numero(numero: str):
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
                m_fecha = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
                fecha_str = m_fecha.group(1) if m_fecha else None
                urls = obtener_secciones_de_panel(panel)
                return numero, fecha_str, urls if urls else None
        return None, None, None
    except Exception as e:
        log.error(f"Error: {e}")
        return None, None, None

def obtener_ultimo_boletin():
    url = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        panel = soup.find("div", class_="panel-default")
        if not panel:
            return None, None, None
        titulo_tag = panel.find("h5", class_="panel-title")
        if not titulo_tag:
            return None, None, None
        texto = titulo_tag.get_text(strip=True)
        m_num = re.search(r"N[°º]?\s*(\d+)", texto, re.IGNORECASE)
        m_fecha = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
        if not m_num or not m_fecha:
            return None, None, None
        numero = m_num.group(1)
        fecha_str = m_fecha.group(1)
        urls = obtener_secciones_de_panel(panel)
        return numero, fecha_str, urls if urls else None
    except Exception as e:
        log.error(f"Error: {e}")
        return None, None, None

def descargar_pdf(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        log.warning(f"Error: {e}")
        return None

def extraer_paginas(contenido: bytes):
    try:
        with pdfplumber.open(BytesIO(contenido)) as pdf:
            paginas = []
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    paginas.append((i, text))
            return paginas
    except Exception as e:
        log.warning(f"Error: {e}")
        return []

def procesar_boletin(numero: str, fecha_str: str, urls_secciones: dict) -> int:
    if not urls_secciones:
        return 0
    try:
        fecha_boletin = datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except:
        fecha_boletin = datetime.now(BUENOS_AIRES).date()

    total = 0
    for seccion, url in urls_secciones.items():
        log.info(f"── {seccion}: {url}")
        pdf_bytes = descargar_pdf(url)
        if not pdf_bytes:
            continue
        paginas = extraer_paginas(pdf_bytes)
        if not paginas:
            continue
        
        inicio_transferencias = None
        if seccion == "OFICIAL":
            for pag, txt in paginas:
                if RE_INICIO_TRANSFERENCIAS.search(txt):
                    inicio_transferencias = pag
                    break
            if inicio_transferencias is None:
                log.warning("No se encontró TRANSFERENCIAS")
                continue
        
        for pagina, texto in paginas:
            if seccion == "OFICIAL" and inicio_transferencias and pagina < inicio_transferencias:
                continue
            locs = localidades_en_texto(texto)
            if not locs:
                continue
            for loc in locs:
                if guardar_pagina(loc, texto, seccion, fecha_boletin, numero, url, pagina):
                    total += 1
    return total

def main():
    log.info("═══ SCRAPER ORIGINAL CORREGIDO ═══")
    num = None
    if len(sys.argv) > 1:
        num = sys.argv[1]
    else:
        num = os.environ.get("BOLETIN_NUMERO")
    if num:
        n, f, u = obtener_boletin_por_numero(num)
    else:
        n, f, u = obtener_ultimo_boletin()
    if not n:
        log.error("No se encontró el boletín")
        sys.exit(0)
    log.info(f"Procesando boletín N° {n} - {f}")
    total = procesar_boletin(n, f, u)
    eliminar_viejos(60)
    log.info(f"═══ FIN | Nuevos guardados: {total} ═══")
    sys.exit(0)

if __name__ == "__main__":
    main()
