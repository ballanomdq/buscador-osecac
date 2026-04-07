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

# --- Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    log.error("Faltan SUPABASE_URL o SUPABASE_KEY")
    sys.exit(0)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Localidades ---
LOCALIDADES = {
    "mar del plata", "alvarado", "miramar", "mechongue", "otamendi", "vivorata",
    "vidal", "piran", "las armas", "maipu", "labarden", "guido", "dolores",
    "castelli", "tordillo", "conesa", "lavalle", "san clemente", "las toninas",
    "santa teresita", "mar del tuyu", "san bernardo", "la lucila del mar",
    "mar de ajo", "costa del este", "pinamar", "madariaga", "villa gesell",
    "mar chiquita", "general guido",
}
ALIAS_LOCALIDAD = {"general guido": "Guido", "gdor. arias": "Dolores"}
CONTEXTO_CHARS = 1500
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OSECAC-Scraper/1.0)"}

# --- URLs base ---
BASE_URL = "https://boletinoficial.gba.gob.ar"
SECCIONES = {
    "JUDICIAL": "JUDICIAL",
    "OFICIAL": "OFICIAL",
}

# --- Funciones de extracción de fecha y número desde el PDF ---
RE_FECHA = re.compile(
    r"La Plata,\s*(?:martes|miércoles|jueves|viernes|sábado|domingo|lunes)?\s*(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})",
    re.IGNORECASE
)
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

def extraer_fecha_boletin(texto):
    match = RE_FECHA.search(texto)
    if match:
        dia = int(match.group(1))
        mes = MESES[match.group(2).lower()]
        año = int(match.group(3))
        return datetime(año, mes, dia).date()
    return None

def extraer_numero_boletin(texto):
    match = re.search(r"N[º°]?\s*(\d{4,6})", texto)
    return match.group(1) if match else "desconocido"

# --- Obtener el último boletín desde la página de ediciones anteriores ---
def obtener_ultimo_boletin():
    """
    Scrapea la página de ediciones anteriores y devuelve el número y fecha del último boletín,
    así como las URLs de sus secciones (Oficial y Judicial).
    Retorna (numero, fecha_str, urls_secciones) o (None, None, None) si falla.
    """
    url_ediciones = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url_ediciones, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Buscar el primer panel (último boletín)
        panel = soup.find("div", class_="panel panel-default")
        if not panel:
            log.warning("No se encontró el panel del último boletín")
            return None, None, None
        titulo = panel.find("h5", class_="panel-title")
        if not titulo:
            return None, None, None
        # Extraer número y fecha: "BOLETÍN N° 30212 - 07/04/2026"
        texto_titulo = titulo.get_text(strip=True)
        match = re.search(r"N°\s*(\d+)\s*-\s*(\d{2}/\d{2}/\d{4})", texto_titulo)
        if not match:
            return None, None, None
        numero = match.group(1)
        fecha_str = match.group(2)  # dd/mm/aaaa
        # Dentro del mismo panel, buscar los enlaces a las secciones (Oficial y Judicial)
        secciones_urls = {}
        enlaces = panel.find_all("a", href=True)
        for a in enlaces:
            texto = a.get_text(strip=True).upper()
            href = a["href"]
            if "OFICIAL" in texto and "ver" in href:
                secciones_urls["OFICIAL"] = href if href.startswith("http") else BASE_URL + href
            elif "JUDICIAL" in texto and "ver" in href:
                secciones_urls["JUDICIAL"] = href if href.startswith("http") else BASE_URL + href
        if "OFICIAL" not in secciones_urls or "JUDICIAL" not in secciones_urls:
            log.warning(f"No se encontraron ambas secciones para el boletín {numero}")
            return numero, fecha_str, secciones_urls
        return numero, fecha_str, secciones_urls
    except Exception as e:
        log.error(f"Error al obtener el último boletín: {e}")
        return None, None, None

# --- Descarga y procesamiento de PDF ---
def descargar_pdf(url):
    try:
        resp = requests.get(url, timeout=60, headers=HEADERS)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        log.warning(f"Error descargando {url}: {e}")
        return None

def extraer_texto_pdf(contenido):
    try:
        with pdfplumber.open(BytesIO(contenido)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception as e:
        log.warning(f"Error leyendo PDF: {e}")
        return ""

def buscar_localidades(texto):
    resultados = []
    texto_lower = texto.lower()
    for loc in LOCALIDADES:
        pos = 0
        while True:
            idx = texto_lower.find(loc, pos)
            if idx == -1:
                break
            inicio = max(0, idx - CONTEXTO_CHARS)
            fin = min(len(texto), idx + CONTEXTO_CHARS)
            resultados.append((loc.title(), texto[inicio:fin].strip()))
            pos = idx + len(loc)
    return resultados

def extraer_cuits_dnis(texto):
    patron_cuit = r"\b\d{2}-\d{8}-\d\b"
    patron_dni = r"\b(?:DNI|CUIT|CUIL)[\s:]*(\d{6,8})\b"
    patron_solo_numeros = r"\b(\d{7,8})\b"
    encontrados = set()
    for m in re.findall(patron_cuit, texto):
        encontrados.add(m)
    for m in re.findall(patron_dni, texto, re.IGNORECASE):
        encontrados.add(m)
    for m in re.findall(patron_solo_numeros, texto):
        if len(m) >= 7 and not (1900 <= int(m[:4]) <= 2030):
            encontrados.add(m)
    return sorted(encontrados)

def extraer_mayusculas(texto):
    patron_mayus = r"\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+\b"
    matches = re.findall(patron_mayus, texto)
    mayusculas = [m.strip() for m in matches if len(m.strip()) >= 3 and not m.isdigit()]
    return list(set(mayusculas))

def guardar_edicto(localidad, texto, seccion, fecha, boletin_numero, url_pdf):
    cuits = extraer_cuits_dnis(texto)
    sujetos = extraer_mayusculas(texto)
    clave_dedup = texto[:400]
    existente = supabase.table("edictos").select("id")\
        .eq("fecha", fecha.isoformat())\
        .eq("texto_completo", clave_dedup).execute()
    if existente.data:
        return False
    data = {
        "fecha": fecha.isoformat(),
        "boletin_numero": str(boletin_numero),
        "seccion": seccion,
        "localidad": localidad,
        "cuit_detectados": ", ".join(cuits) if cuits else None,
        "sujetos": ", ".join(sujetos[:5]) if sujetos else None,
        "texto_completo": texto[:5000],
        "url_pdf": url_pdf,
    }
    try:
        supabase.table("edictos").insert(data).execute()
        return True
    except Exception as e:
        log.error(f"Error guardando: {e}")
        return False

def eliminar_viejos(dias=60):
    limite = (datetime.now() - timedelta(days=dias)).date()
    supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()

def procesar_boletin(numero, fecha_str, urls_secciones):
    """
    Procesa un boletín específico dado su número y URLs de secciones.
    Retorna cantidad total de edictos guardados.
    """
    try:
        fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except:
        fecha_obj = (datetime.utcnow() - timedelta(hours=3)).date()
    total = 0
    for seccion_nombre, url in urls_secciones.items():
        log.info(f"Procesando sección {seccion_nombre} del boletín {numero}")
        pdf_bytes = descargar_pdf(url)
        if not pdf_bytes:
            log.warning(f"No se pudo descargar PDF de {seccion_nombre}")
            continue
        texto = extraer_texto_pdf(pdf_bytes)
        if not texto:
            continue
        # Si no se pudo extraer fecha del PDF, usar la que viene del listado
        fecha_pdf = extraer_fecha_boletin(texto)
        if fecha_pdf:
            fecha_obj = fecha_pdf
        menciones = buscar_localidades(texto)
        for localidad, fragmento in menciones:
            if guardar_edicto(localidad, fragmento, seccion_nombre, fecha_obj, numero, url):
                total += 1
        log.info(f"{seccion_nombre}: {len(menciones)} menciones, {total} guardados acumulados")
    return total

def main():
    # Obtener el último boletín desde la página de ediciones anteriores
    numero, fecha_str, urls = obtener_ultimo_boletin()
    if not numero:
        log.error("No se pudo obtener el último boletín. Saliendo sin error.")
        sys.exit(0)
    log.info(f"Último boletín detectado: N° {numero} - {fecha_str}")
    total = procesar_boletin(numero, fecha_str, urls)
    eliminar_viejos(60)
    log.info(f"Total guardados en esta ejecución: {total}")
    sys.exit(0)

if __name__ == "__main__":
    main()
