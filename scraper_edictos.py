"""
scraper_edictos.py
Descarga el último boletín del Boletín Oficial PBA usando la página de
ediciones anteriores con los selectores HTML actualizados:
  - div.panel-default > h5.panel-title  (título con N° y fecha)
  - div.section > h5.body-title         (nombre de sección: OFICIAL / JUDICIAL)
  - a[title="Ver PDF"]                   (enlace al PDF)
Siempre termina con sys.exit(0) para no marcar error en GitHub Actions.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    log.error("Faltan SUPABASE_URL o SUPABASE_KEY")
    sys.exit(0)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS  = {"User-Agent": "Mozilla/5.0 (compatible; OSECAC-Scraper/1.0)"}

# ── Localidades objetivo ──────────────────────────────────────────────────────
LOCALIDADES = {
    "mar del plata", "alvarado", "miramar", "mechongue", "otamendi", "vivorata",
    "vidal", "piran", "las armas", "maipu", "labarden", "guido", "dolores",
    "castelli", "tordillo", "conesa", "lavalle", "san clemente", "las toninas",
    "santa teresita", "mar del tuyu", "san bernardo", "la lucila del mar",
    "mar de ajo", "costa del este", "pinamar", "madariaga", "villa gesell",
    "mar chiquita", "general guido",
}
ALIAS_LOCALIDAD = {"general guido": "Guido", "gdor. arias": "Dolores"}
CONTEXTO_CHARS  = 1500

# ── Regex ─────────────────────────────────────────────────────────────────────
RE_FECHA = re.compile(
    r"La Plata,\s*(?:lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)?\s*"
    r"(\d{1,2})\s+de\s+"
    r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    r"\s+de\s+(\d{4})",
    re.IGNORECASE
)
MESES = {
    "enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
    "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12
}

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

# ── Scraping de ediciones anteriores (selectores actualizados) ────────────────
def obtener_secciones_de_panel(panel) -> dict:
    """
    Dado un div.panel-default, extrae las URLs de cada sección usando
    los selectores actuales del sitio:
      div.section > h5.body-title  → nombre de sección
      a[title="Ver PDF"]           → href del PDF
    """
    urls = {}
    panel_body = panel.find("div", class_="panel-body")
    if not panel_body:
        return urls
    for section in panel_body.find_all("div", class_="section"):
        titulo_tag = section.find("h5", class_="body-title")
        if not titulo_tag:
            continue
        nombre = titulo_tag.get_text(strip=True).upper()
        # Normalizar: puede decir "OFICIAL" o "JUDICIAL"
        if "OFICIAL" in nombre:
            clave = "OFICIAL"
        elif "JUDICIAL" in nombre:
            clave = "JUDICIAL"
        else:
            continue
        # Buscar el enlace "Ver PDF"
        link = section.find("a", title="Ver PDF")
        if not link:
            # Fallback: cualquier enlace con "ver" en el href
            link = section.find("a", href=re.compile(r"/secciones/\d+/ver"))
        if link and link.get("href"):
            href = link["href"]
            urls[clave] = href if href.startswith("http") else BASE_URL + href
    return urls

def obtener_ultimo_boletin():
    """
    Scrapea la página de ediciones anteriores y devuelve
    (numero, fecha_str, urls_secciones) del boletín más reciente.
    """
    url_ediciones = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url_ediciones, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for panel in soup.find_all("div", class_="panel-default"):
            titulo_tag = panel.find("h5", class_="panel-title")
            if not titulo_tag:
                continue
            texto_titulo = titulo_tag.get_text(strip=True)
            m = re.search(r"N[°º]?\s*(\d+)\s*[-–]\s*(\d{2}/\d{2}/\d{4})", texto_titulo, re.IGNORECASE)
            if not m:
                continue
            numero    = m.group(1)
            fecha_str = m.group(2)
            urls      = obtener_secciones_de_panel(panel)
            if urls:
                log.info(f"Último boletín: N° {numero} - {fecha_str} | Secciones: {list(urls.keys())}")
                return numero, fecha_str, urls
            else:
                log.warning(f"Panel encontrado para N° {numero} pero sin secciones. Probando el siguiente.")

        log.error("No se encontró ningún boletín con secciones válidas.")
        return None, None, None

    except Exception as e:
        log.error(f"Error al obtener ediciones anteriores: {e}")
        return None, None, None

def obtener_urls_por_numero(numero: str) -> dict:
    """Dado un número de boletín, devuelve sus URLs de sección."""
    url_ediciones = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url_ediciones, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for panel in soup.find_all("div", class_="panel-default"):
            titulo_tag = panel.find("h5", class_="panel-title")
            if not titulo_tag:
                continue
            texto = titulo_tag.get_text(strip=True)
            if f"N° {numero}" in texto or f"N°{numero}" in texto or f"N º {numero}" in texto:
                urls = obtener_secciones_de_panel(panel)
                if urls:
                    return urls
        log.warning(f"No se encontraron secciones para el boletín N° {numero}")
        return {}
    except Exception as e:
        log.error(f"Error buscando boletín N° {numero}: {e}")
        return {}

# ── Descarga y procesamiento de PDF ──────────────────────────────────────────
def descargar_pdf(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        log.warning(f"Error descargando {url}: {e}")
        return None

def extraer_texto_pdf(contenido: bytes) -> str:
    try:
        with pdfplumber.open(BytesIO(contenido)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception as e:
        log.warning(f"Error leyendo PDF: {e}")
        return ""

# ── Búsqueda de localidades ───────────────────────────────────────────────────
def buscar_localidades(texto: str) -> list:
    resultados  = []
    texto_clean = re.sub(r'\S+@\S+', ' ', texto)
    texto_lower = texto_clean.lower()
    for loc in LOCALIDADES:
        pos = 0
        while True:
            idx = texto_lower.find(loc, pos)
            if idx == -1:
                break
            inicio = max(0, idx - CONTEXTO_CHARS)
            fin    = min(len(texto_clean), idx + CONTEXTO_CHARS)
            nombre = ALIAS_LOCALIDAD.get(loc, loc.title())
            resultados.append((nombre, texto_clean[inicio:fin].strip()))
            pos = idx + len(loc)
    return resultados

# ── Extracción de metadatos ───────────────────────────────────────────────────
def extraer_cuits_dnis(texto: str) -> list:
    encontrados = set()
    for m in re.findall(r'\b\d{2}-\d{8}-\d\b', texto):
        encontrados.add(m)
    for m in re.findall(r'\b(?:DNI|CUIT|CUIL)[\s:]*(\d{6,8})\b', texto, re.IGNORECASE):
        encontrados.add(m)
    return sorted(encontrados)

def extraer_mayusculas(texto: str) -> list:
    EXCLUIR = {
        "JUZGADO","PRIMERA","INSTANCIA","CIVIL","COMERCIAL","SECRETARIA",
        "PROVINCIA","BUENOS","AIRES","REPUBLICA","ARGENTINA","PODER",
        "JUDICIAL","OFICIAL","BOLETIN","NUMERO","ARTICULO","DECRETO",
        "RESOLUCION","MINISTERIO","CDOR","SINDICO","QUIEBRA","CONCURSO",
        "PREVENTIVO","EDICTO","DOMICILIO","CIUDAD","PARTIDO","REGISTRO",
        "EXPEDIENTE","PRESENTE","MEDIANTE","CONTRA",
    }
    matches   = re.findall(r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+\b', texto)
    resultado = []
    vistos    = set()
    for m in matches:
        m_c = m.strip()
        if len(m_c) < 3 or any(p in EXCLUIR for p in m_c.split()):
            continue
        if m_c not in vistos:
            vistos.add(m_c)
            resultado.append(m_c)
        if len(resultado) >= 5:
            break
    return resultado

# ── Guardado en Supabase ──────────────────────────────────────────────────────
def guardar_edicto(localidad, texto, seccion, fecha, boletin_numero, url_pdf) -> bool:
    cuits   = extraer_cuits_dnis(texto)
    sujetos = extraer_mayusculas(texto)
    clave   = texto[:400]
    try:
        existente = supabase.table("edictos").select("id")\
            .eq("fecha", fecha.isoformat())\
            .eq("texto_completo", clave).execute()
        if existente.data:
            return False
    except Exception:
        pass
    data = {
        "fecha":           fecha.isoformat(),
        "boletin_numero":  str(boletin_numero),
        "seccion":         seccion,
        "localidad":       localidad,
        "cuit_detectados": ", ".join(cuits)   if cuits   else None,
        "sujetos":         ", ".join(sujetos) if sujetos else None,
        "texto_completo":  texto[:5000],
        "url_pdf":         url_pdf,
    }
    try:
        supabase.table("edictos").insert(data).execute()
        return True
    except Exception as e:
        log.error(f"Error guardando edicto: {e}")
        return False

def eliminar_viejos(dias: int = 60):
    limite = (datetime.now() - timedelta(days=dias)).date()
    try:
        supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()
        log.info(f"Registros anteriores a {limite} eliminados.")
    except Exception as e:
        log.warning(f"No se pudieron eliminar registros viejos: {e}")

# ── Procesar un boletín completo ──────────────────────────────────────────────
def procesar_boletin(numero: str, fecha_str: str, urls_secciones: dict) -> int:
    try:
        fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except Exception:
        fecha_obj = (datetime.utcnow() - timedelta(hours=3)).date()

    total = 0
    for seccion_nombre, url in urls_secciones.items():
        log.info(f"── {seccion_nombre}: {url}")
        pdf_bytes = descargar_pdf(url)
        if not pdf_bytes:
            log.warning(f"Sin PDF para {seccion_nombre}")
            continue
        texto = extraer_texto_pdf(pdf_bytes)
        if not texto.strip():
            log.warning(f"PDF de {seccion_nombre} sin texto.")
            continue

        # Refinar fecha/número con lo que dice el propio PDF
        fecha_pdf = extraer_fecha_del_pdf(texto)
        if fecha_pdf:
            fecha_obj = fecha_pdf
        num_pdf = extraer_numero_del_pdf(texto)
        if num_pdf != "desconocido":
            numero = num_pdf

        menciones = buscar_localidades(texto)
        log.info(f"{len(menciones)} menciones encontradas en {seccion_nombre}")

        guardados = 0
        for localidad, fragmento in menciones:
            if guardar_edicto(localidad, fragmento, seccion_nombre, fecha_obj, numero, url):
                guardados += 1
        log.info(f"{seccion_nombre}: {guardados} edictos nuevos guardados.")
        total += guardados

    return total

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    log.info("═══ Inicio del scraper ═══")
    numero, fecha_str, urls = obtener_ultimo_boletin()
    if not numero:
        log.error("No se pudo obtener el último boletín. Saliendo sin error.")
        sys.exit(0)

    log.info(f"Procesando boletín N° {numero} - {fecha_str}")
    total = procesar_boletin(numero, fecha_str, urls)
    eliminar_viejos(60)
    log.info(f"═══ FIN | Total guardados: {total} ═══")
    sys.exit(0)

if __name__ == "__main__":
    main()
