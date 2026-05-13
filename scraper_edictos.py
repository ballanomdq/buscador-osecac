"""
scraper_edictos.py - VERSIÓN DEFINITIVA CON EXTRACCIÓN PERFECTA DE NOMBRES
"""

import sys
import re
import os
import logging
import requests
import pdfplumber
from io import BytesIO
from datetime import datetime, timedelta
from supabase import create_client
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    log.error("Faltan credenciales")
    sys.exit(0)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS  = {"User-Agent": "Mozilla/5.0 (compatible; OSECAC-Scraper/1.0)"}

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

RE_FECHA = re.compile(
    r"La Plata,\s*(?:lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)?\s*"
    r"(\d{1,2})\s+de\s+"
    r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    r"\s+de\s+(\d{4})", re.IGNORECASE
)
MESES = {
    "enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
    "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12
}

# ── Utilidades ────────────────────────────────────────────────────────────────
def normalizar_abreviaturas(texto: str) -> str:
    t = texto.lower()
    for abrev, expansion in ABREVIATURAS.items():
        t = re.sub(rf'\b{re.escape(abrev)}\b', expansion, t)
    return t

def localidades_en_texto(texto: str) -> list:
    norm = normalizar_abreviaturas(texto)
    norm = re.sub(r'\S+@\S+', ' ', norm)
    vistas = set()
    result = []
    for loc in LOCALIDADES:
        if loc in norm and loc not in vistas:
            vistas.add(loc)
            result.append(ALIAS_LOCALIDAD.get(loc, loc.title()))
    return result

def extraer_fecha_del_pdf(texto: str):
    m = RE_FECHA.search(texto)
    if m:
        try:
            return datetime(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1))).date()
        except Exception:
            pass
    return None

def extraer_numero_del_pdf(texto: str) -> str:
    m = re.search(r"N[º°]?\s*(\d{4,6})", texto)
    return m.group(1) if m else "desconocido"

def extraer_cuits(texto: str) -> str:
    encontrados = set()
    for m in re.findall(r'\b\d{2}-\d{8}-\d\b', texto):
        encontrados.add(m)
    for m in re.findall(r'\b(?:DNI|CUIT|CUIL)[\s:]*(\d{6,8})\b', texto, re.IGNORECASE):
        encontrados.add(m)
    for m in re.findall(r'\b(\d{7,8})\b', texto):
        if not (1900 <= int(m) <= 2030):
            encontrados.add(m)
    return ", ".join(sorted(encontrados)) if encontrados else None

# ── FUNCIÓN CORREGIDA POR CLAUDE ──────────────────────────────────────────────
def extraer_sujeto(texto: str) -> str | None:
    # Palabras que NO son parte del nombre — si el match empieza con alguna, descartamos
    EXCLUIR_INICIO = re.compile(
        r'^(la\s+provincia|el\s+estado|los\s+acreedores|las\s+partes'
        r'|señora|señor|doña|don|la|el|los|las|sr\.|sra\.)\s+',
        re.IGNORECASE
    )
    # Palabras que indican que el nombre terminó
    RE_CORTE = re.compile(
        r'\b(dni|cuit|cuil|domicili|sindico|síndico|con\s+domicilio'
        r'|quien|cuya|siendo|present|por\s+el\s+término|edicto|juzgado'
        r'|secretar|actuaciones|expediente|inciso|artículo)\b',
        re.IGNORECASE
    )

    # Buscar el patrón "quiebra/concurso de [opcionales] NOMBRE"
    m = re.search(
        r'(?:quiebra|concurso(?:\s+preventivo)?)\s+de\s+'
        r'(?:(?:la\s+señora|el\s+señor|la\s+firma|señora|señor|doña|don|la|el)\s+)?'
        r'([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑA-Za-záéíóúüñ\s,\.]{2,80})',
        texto, re.IGNORECASE
    )
    if not m:
        return None

    nombre = m.group(1).strip()

    # Cortar en cuanto aparezca una palabra que no es parte del nombre
    corte = RE_CORTE.search(nombre)
    if corte:
        nombre = nombre[:corte.start()].strip()

    # Cortar también en salto de línea o paréntesis
    nombre = re.split(r'[\n\r\(]', nombre)[0].strip()

    # Limpiar puntuación final
    nombre = nombre.rstrip('.,;: ')

    # Si después de limpiar empieza con artículo/tratamiento, quitarlo
    nombre = EXCLUIR_INICIO.sub('', nombre).strip()

    # Validar: debe tener al menos 5 caracteres y no ser una frase genérica
    FRASES_INVALIDAS = {
        "LA PROVINCIA", "EL ESTADO", "LOS ACREEDORES", "LAS PARTES",
        "LA CONCURSADA", "EL CONCURSADO", "LA FALLIDA", "EL FALLIDO",
    }
    if len(nombre) < 5 or nombre.upper() in FRASES_INVALIDAS:
        return None

    return nombre.upper()

# ── Nivel de confianza ────────────────────────────────────────────────────────
def calcular_confianza(texto: str) -> str:
    tiene_quiebra   = bool(re.search(r'\bquiebra\b',   texto, re.IGNORECASE))
    tiene_concurso  = bool(re.search(r'\bconcurso\b',  texto, re.IGNORECASE))
    if not (tiene_quiebra or tiene_concurso):
        return "BAJA"
    nombre = extraer_sujeto(texto)
    if nombre and len(nombre) > 4:
        return "ALTA"
    return "MEDIA"

# ── Scraping ──────────────────────────────────────────────────────────────────
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
        clave = "OFICIAL" if "OFICIAL" in nombre else ("JUDICIAL" if "JUDICIAL" in nombre else None)
        if not clave:
            continue
        link = section.find("a", title="Ver PDF") or section.find("a", href=re.compile(r"/secciones/\d+/ver"))
        if link and link.get("href"):
            href = link["href"]
            urls[clave] = href if href.startswith("http") else BASE_URL + href
    return urls

def obtener_ultimo_boletin():
    try:
        resp = requests.get(f"{BASE_URL}/ediciones-anteriores", headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for panel in soup.find_all("div", class_="panel-default"):
            titulo_tag = panel.find("h5", class_="panel-title")
            if not titulo_tag:
                continue
            texto = titulo_tag.get_text(strip=True)
            m = re.search(r"N[°º]?\s*(\d+)\s*[-–]\s*(\d{2}/\d{2}/\d{4})", texto, re.IGNORECASE)
            if not m:
                continue
            numero, fecha_str = m.group(1), m.group(2)
            urls = obtener_secciones_de_panel(panel)
            if urls:
                log.info(f"Último boletín: N° {numero} - {fecha_str}")
                return numero, fecha_str, urls
        log.error("No se encontró boletín")
        return None, None, None
    except Exception as e:
        log.error(f"Error: {e}")
        return None, None, None

def descargar_pdf(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        return r.content
    except Exception as e:
        log.warning(f"Error descargando: {e}")
        return None

def extraer_paginas(contenido: bytes) -> list:
    paginas = []
    try:
        with pdfplumber.open(BytesIO(contenido)) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                texto = page.extract_text() or ""
                if texto.strip():
                    paginas.append((i, texto))
    except Exception as e:
        log.warning(f"Error extrayendo: {e}")
    return paginas

def texto_desde_transferencias(texto: str) -> str:
    m = re.search(r'\bTRANSFERENCIAS?\b', texto, re.IGNORECASE)
    if m:
        return texto[m.start():]
    return texto

def guardar_pagina(localidad, texto, seccion, fecha, numero, url_pdf, pagina) -> bool:
    fecha_iso = fecha.isoformat()
    existente = supabase.table("edictos").select("id") \
        .eq("fecha", fecha_iso) \
        .eq("boletin_numero", str(numero)) \
        .eq("seccion", seccion) \
        .eq("localidad", localidad) \
        .eq("pagina", pagina) \
        .execute()
    if existente.data:
        return False

    confianza = calcular_confianza(texto)
    sujeto = extraer_sujeto(texto)
    cuits = extraer_cuits(texto)

    if re.search(r'\bquiebra\b', texto, re.IGNORECASE):
        tipo = "QUIEBRA"
    elif re.search(r'\bconcurso\b', texto, re.IGNORECASE):
        tipo = "CONCURSO"
    elif re.search(r'\bsubasta\b', texto, re.IGNORECASE):
        tipo = "SUBASTA"
    elif re.search(r'\btransferencia\b', texto, re.IGNORECASE):
        tipo = "TRANSFERENCIA"
    else:
        tipo = "EDICTO"

    try:
        supabase.table("edictos").insert({
            "fecha": fecha_iso,
            "boletin_numero": str(numero),
            "seccion": seccion,
            "localidad": localidad,
            "tipo_edicto": tipo,
            "sujetos": sujeto,
            "cuit_detectados": cuits,
            "texto_completo": texto[:5000],
            "url_pdf": url_pdf,
            "pagina": pagina,
            "nivel_confianza": confianza,
        }).execute()
        log.info(f"✅ Guardado: pág {pagina} | {confianza} | {localidad} | {sujeto or 'sin nombre'}")
        return True
    except Exception as e:
        log.error(f"Error guardando: {e}")
        return False

def eliminar_viejos(dias=60):
    limite = (datetime.now() - timedelta(days=dias)).date()
    try:
        supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()
        log.info(f"Registros anteriores a {limite} eliminados")
    except Exception as e:
        log.warning(f"No se pudieron eliminar viejos: {e}")

def procesar_boletin(numero, fecha_str, urls_secciones) -> int:
    try:
        fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except Exception:
        fecha_obj = (datetime.utcnow() - timedelta(hours=3)).date()

    total = 0
    for seccion, url in urls_secciones.items():
        log.info(f"── {seccion}: {url}")
        pdf_bytes = descargar_pdf(url)
        if not pdf_bytes:
            continue

        paginas = extraer_paginas(pdf_bytes)
        if not paginas:
            continue

        texto_total = " ".join(t for _, t in paginas[:3])
        fecha_pdf = extraer_fecha_del_pdf(texto_total)
        if fecha_pdf:
            fecha_obj = fecha_pdf
        num_pdf = extraer_numero_del_pdf(texto_total)
        if num_pdf != "desconocido":
            numero = num_pdf

        log.info(f"N° {numero} | Fecha: {fecha_obj} | {len(paginas)} páginas")

        for num_pag, texto_pag in paginas:
            if seccion == "OFICIAL":
                texto_pag = texto_desde_transferencias(texto_pag)
            locs = localidades_en_texto(texto_pag)
            if not locs:
                continue
            for loc in locs:
                if guardar_pagina(loc, texto_pag, seccion, fecha_obj, numero, url, num_pag):
                    total += 1
        log.info(f"{seccion}: {total} registros nuevos")
    return total

def main():
    log.info("═══ SCRAPER DEFINITIVO (CLAUDE) ═══")
    numero, fecha_str, urls = obtener_ultimo_boletin()
    if not numero:
        log.error("No se obtuvo boletín")
        sys.exit(0)
    log.info(f"Procesando N° {numero} - {fecha_str}")
    total = procesar_boletin(numero, fecha_str, urls)
    eliminar_viejos(60)
    log.info(f"═══ FIN | Guardados: {total} ═══")
    sys.exit(0)

if __name__ == "__main__":
    main()
