"""
scraper_edictos.py - VERSIÓN TOLERANTE Y "BRUTA"
- Guarda la página COMPLETA cada vez que aparece una localidad (sin depender de palabras clave).
- Extrae tipo de edicto y nombre de forma flexible (más tolerante).
- Para la sección OFICIAL, sigue filtrando solo TRANSFERENCIAS.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

BUENOS_AIRES = ZoneInfo("America/Argentina/Buenos_Aires")

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    log.error("Faltan SUPABASE_URL o SUPABASE_KEY")
    sys.exit(0)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OSECAC-Scraper/1.0)"}

# ── Localidades objetivo (todas en minúsculas para comparar) ─────────────────
LOCALIDADES = {
    "mar del plata", "alvarado", "miramar", "mechongue", "otamendi", "vivorata",
    "vidal", "piran", "las armas", "maipu", "labarden", "guido", "dolores",
    "castelli", "tordillo", "conesa", "lavalle", "san clemente", "las toninas",
    "santa teresita", "mar del tuyu", "san bernardo", "la lucila del mar",
    "mar de ajo", "costa del este", "pinamar", "madariaga", "villa gesell",
    "mar chiquita", "general guido",
}

# Abreviaturas comunes
ABREVIATURAS = {
    "mdp"            : "mar del plata",
    "m.d.p."         : "mar del plata",
    "depto. jud. de mdp" : "mar del plata",
    "gral. guido"    : "general guido",
    "gral. madariaga": "madariaga",
    "pdo. de dolores": "dolores",
    "mar chiq."      : "mar chiquita",
}
ALIAS_LOCALIDAD = {"general guido": "Guido", "gdor. arias": "Dolores"}

PALABRAS_TRANSFERENCIAS = ["transferencia", "transferencias", "cesión", "cesiones"]

# Expresiones regulares tolerantes
RE_INICIO_TRANSFERENCIAS = re.compile(r'\bTRANSFERENCIAS?\b', re.IGNORECASE)
RE_QUIEBRA = re.compile(r'\b(?:quiebra|concurso)\b', re.IGNORECASE)

# Extracción de nombre: busca después de "quiebra de", "concurso de", o toma secuencia de mayúsculas
RE_NOMBRE_QUIEBRA = re.compile(
    r'(?:quiebra|concurso)\s+de\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,\.]+?)(?:\s*(?:\(?DNI|CUIT|\(|\n)|$)',
    re.IGNORECASE
)

def extraer_tipo_edicto(texto: str) -> str:
    """Devuelve 'QUIEBRA', 'CONCURSO', 'EDICTO' según lo que encuentre."""
    if re.search(r'\bquiebra\b', texto, re.IGNORECASE):
        return "QUIEBRA"
    if re.search(r'\bconcurso\b', texto, re.IGNORECASE):
        return "CONCURSO"
    return "EDICTO"

def extraer_nombre_tolerante(texto: str) -> str:
    """Extrae nombre de forma tolerante."""
    # Primero: "quiebra de NOMBRE"
    m = RE_NOMBRE_QUIEBRA.search(texto)
    if m:
        nombre = m.group(1).strip().strip(',').strip()
        if len(nombre) > 3:
            return nombre.upper()
    # Segundo: buscar una secuencia de mayúsculas de al menos dos palabras
    mayus = re.findall(r'\b([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+)\b', texto)
    if mayus:
        return mayus[0].strip()
    return ""

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

# ── Web scraping (ediciones anteriores) ───────────────────────────────────────
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
    url_ediciones = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url_ediciones, headers=HEADERS, timeout=30)
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
                if urls:
                    return numero, fecha_str, urls
        return None, None, None
    except Exception as e:
        log.error(f"Error: {e}")
        return None, None, None

def obtener_ultimo_boletin():
    url_ediciones = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url_ediciones, headers=HEADERS, timeout=30)
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

# ── Descarga y extracción de páginas ─────────────────────────────────────────
def descargar_pdf(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        log.warning(f"Error descargando {url}: {e}")
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
        log.warning(f"Error leyendo PDF: {e}")
        return []

# ── Guardado en Supabase ──────────────────────────────────────────────────────
def guardar_pagina(
    localidad: str,
    texto: str,
    seccion: str,
    fecha,
    boletin_numero: str,
    url_pdf: str,
    pagina: int,
) -> bool:
    tipo = extraer_tipo_edicto(texto)
    nombre_sujeto = extraer_nombre_tolerante(texto)
    cuits = extraer_cuits_dnis(texto)

    # Evitar duplicados exactos de página + localidad
    existente = supabase.table("edictos").select("id") \
        .eq("fecha", fecha.isoformat()) \
        .eq("boletin_numero", str(boletin_numero)) \
        .eq("seccion", seccion) \
        .eq("localidad", localidad) \
        .eq("pagina", pagina) \
        .execute()
    if existente.data:
        return False

    data = {
        "fecha": fecha.isoformat(),
        "boletin_numero": str(boletin_numero),
        "seccion": seccion,
        "localidad": localidad,
        "tipo_edicto": tipo,
        "cuit_detectados": ", ".join(cuits) if cuits else None,
        "sujetos": nombre_sujeto or None,
        "texto_completo": texto,
        "url_pdf": url_pdf,
        "pagina": pagina,
    }
    try:
        supabase.table("edictos").insert(data).execute()
        log.info(f"✅ GUARDADO: pág {pagina} | {tipo} | {localidad} | {nombre_sujeto or '(sin nombre)'}")
        return True
    except Exception as e:
        log.error(f"❌ Error: {e}")
        return False

def eliminar_viejos(dias=60):
    limite = (datetime.now(BUENOS_AIRES) - timedelta(days=dias)).date()
    supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()

# ── Procesamiento principal ───────────────────────────────────────────────────
def procesar_boletin(numero: str, fecha_str: str, urls_secciones: dict) -> int:
    if not urls_secciones:
        return 0
    try:
        fecha_boletin = datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except:
        fecha_boletin = datetime.now(BUENOS_AIRES).date()

    total = 0
    for seccion_nombre, url in urls_secciones.items():
        log.info(f"── Procesando {seccion_nombre}: {url}")
        pdf_bytes = descargar_pdf(url)
        if not pdf_bytes:
            continue

        paginas = extraer_paginas(pdf_bytes)
        if not paginas:
            continue

        # Para OFICIAL, encontrar primera página de TRANSFERENCIAS
        inicio_transferencias = None
        if seccion_nombre == "OFICIAL":
            for pag, txt in paginas:
                if RE_INICIO_TRANSFERENCIAS.search(txt):
                    inicio_transferencias = pag
                    break
            if inicio_transferencias is None:
                log.warning("No se encontró TRANSFERENCIAS. Se omite OFICIAL.")
                continue

        for pagina, texto_pagina in paginas:
            if seccion_nombre == "OFICIAL" and inicio_transferencias and pagina < inicio_transferencias:
                continue
            localidades = localidades_en_texto(texto_pagina)
            if not localidades:
                continue
            for loc in localidades:
                if guardar_pagina(loc, texto_pagina, seccion_nombre, fecha_boletin, numero, url, pagina):
                    total += 1

    return total

def main():
    log.info("═══ SCRAPER TOLERANTE (PÁGINA COMPLETA) ═══")
    boletin_numero = None
    if len(sys.argv) > 1:
        boletin_numero = sys.argv[1]
    else:
        boletin_numero = os.environ.get("BOLETIN_NUMERO")
    if boletin_numero:
        numero, fecha_str, urls = obtener_boletin_por_numero(boletin_numero)
    else:
        numero, fecha_str, urls = obtener_ultimo_boletin()
    if not numero:
        log.error("No se encontró el boletín")
        sys.exit(0)
    log.info(f"Procesando boletín N° {numero} - {fecha_str}")
    total = procesar_boletin(numero, fecha_str, urls)
    eliminar_viejos(60)
    log.info(f"═══ FIN | Nuevos guardados: {total} ═══")
    sys.exit(0)

if __name__ == "__main__":
    main()
