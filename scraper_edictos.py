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

# ── Configuración de logging ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Supabase ────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    log.error("Faltan SUPABASE_URL o SUPABASE_KEY")
    sys.exit(0)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Localidades objetivo ─────────────────────────────────────────────────
LOCALIDADES = {
    "mar del plata", "alvarado", "miramar", "mechongue", "otamendi", "vivorata",
    "vidal", "piran", "las armas", "maipu", "labarden", "guido", "dolores",
    "castelli", "tordillo", "conesa", "lavalle", "san clemente", "las toninas",
    "santa teresita", "mar del tuyu", "san bernardo", "la lucila del mar",
    "mar de ajo", "costa del este", "pinamar", "madariaga", "villa gesell",
    "mar chiquita", "general guido",
}
ALIAS_LOCALIDAD = {"general guido": "Guido", "gdor. arias": "Dolores"}

SECCIONES = {
    "JUDICIAL": "https://boletinoficial.gba.gob.ar/secciones/14079/ver",
    "OFICIAL":  "https://boletinoficial.gba.gob.ar/secciones/14078/ver",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OSECAC-Scraper/1.0)"}
CONTEXTO_CHARS = 1500

# ── Extracción de fecha real del boletín (desde el texto del PDF) ────────
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
    m = re.search(r"N[º°]?\s*(\d{4,6})", texto)
    return m.group(1) if m else "desconocido"

# ── Descarga y extracción de PDF ────────────────────────────────────────
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

# ── Búsqueda de localidades y extracción de datos ────────────────────────
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
            fragmento = texto[inicio:fin].strip()
            resultados.append((loc.title(), fragmento))
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

def guardar_edicto(localidad, texto, seccion, fecha, boletin_numero, url):
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
        "url_pdf": url,
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
    log.info(f"Eliminados registros anteriores a {limite}")

# ── Procesar un boletín completo (dos secciones) ─────────────────────────
def procesar_boletin_completo(fecha, numero, seccion_judicial_url, seccion_oficial_url):
    """
    Procesa las dos secciones de un boletín (Judicial y Oficial) y guarda los edictos.
    Retorna (guardados_judicial, guardados_oficial).
    """
    guardados_judicial = 0
    guardados_oficial = 0

    # Sección Judicial
    pdf_bytes = descargar_pdf(seccion_judicial_url)
    if pdf_bytes:
        texto = extraer_texto_pdf(pdf_bytes)
        if texto:
            # La fecha real debería ser la misma, pero si no, usamos la que nos dieron
            menciones = buscar_localidades(texto)
            for loc, frag in menciones:
                if guardar_edicto(loc, frag, "JUDICIAL", fecha, numero, seccion_judicial_url):
                    guardados_judicial += 1
    else:
        log.warning(f"No se pudo descargar Judicial para boletín {numero}")

    # Sección Oficial
    pdf_bytes = descargar_pdf(seccion_oficial_url)
    if pdf_bytes:
        texto = extraer_texto_pdf(pdf_bytes)
        if texto:
            menciones = buscar_localidades(texto)
            for loc, frag in menciones:
                if guardar_edicto(loc, frag, "OFICIAL", fecha, numero, seccion_oficial_url):
                    guardados_oficial += 1
    else:
        log.warning(f"No se pudo descargar Oficial para boletín {numero}")

    return guardados_judicial, guardados_oficial

# ── Scraping diario automático (usa las URLs fijas) ──────────────────────
def main_diario():
    total = 0
    for nombre_seccion, url in SECCIONES.items():
        pdf_bytes = descargar_pdf(url)
        if not pdf_bytes:
            continue
        texto = extraer_texto_pdf(pdf_bytes)
        if not texto:
            continue
        fecha_boletin = extraer_fecha_boletin(texto)
        if not fecha_boletin:
            # Fallback: fecha actual Argentina
            fecha_boletin = (datetime.utcnow() - timedelta(hours=3)).date()
        boletin_numero = extraer_numero_boletin(texto)
        menciones = buscar_localidades(texto)
        for loc, frag in menciones:
            if guardar_edicto(loc, frag, nombre_seccion, fecha_boletin, boletin_numero, url):
                total += 1
        log.info(f"{nombre_seccion}: {len(menciones)} menciones, guardados parciales...")
    eliminar_viejos(60)
    log.info(f"Total guardados en ejecución diaria: {total}")

if __name__ == "__main__":
    # Si se pasa el argumento "historico", se espera que se llamen a funciones externas.
    # Para el uso normal (workflow diario), simplemente ejecutamos main_diario.
    if len(sys.argv) > 1 and sys.argv[1] == "historico":
        # No hacer nada aquí, la interfaz de Streamlit llamará directamente a procesar_boletin_completo
        pass
    else:
        main_diario()
