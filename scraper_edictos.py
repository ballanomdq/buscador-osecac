"""
scraper_edictos.py
Descarga los PDFs de las secciones del Boletín Oficial PBA usando URLs fijas
(nunca cambian, siempre apuntan al último boletín disponible).
- No depende de la estructura HTML de la página de ediciones anteriores.
- Extrae fecha y número del boletín directamente desde el texto del PDF.
- Siempre termina con sys.exit(0) para no marcar error en GitHub Actions.
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

# ── URLs FIJAS de las secciones (siempre el último boletín) ───────────────────
# Estas URLs nunca cambian aunque el sitio rediseñe su página principal.
SECCIONES = {
    "OFICIAL":   "https://boletinoficial.gba.gob.ar/secciones/14078/ver",
    "JUDICIAL":  "https://boletinoficial.gba.gob.ar/secciones/14079/ver",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OSECAC-Scraper/1.0)"}

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
CONTEXTO_CHARS = 1500

# ── Regex para extraer fecha y número desde el texto del PDF ─────────────────
RE_FECHA = re.compile(
    r"La Plata,\s*(?:lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)?\s*"
    r"(\d{1,2})\s+de\s+"
    r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    r"\s+de\s+(\d{4})",
    re.IGNORECASE
)
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

def extraer_fecha_del_pdf(texto: str):
    """Extrae la fecha de publicación desde el texto del PDF."""
    m = RE_FECHA.search(texto)
    if m:
        try:
            return datetime(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1))).date()
        except Exception:
            pass
    return None

def extraer_numero_del_pdf(texto: str) -> str:
    """Extrae el número de boletín desde el texto del PDF."""
    m = re.search(r"N[º°]?\s*(\d{4,6})", texto)
    return m.group(1) if m else "desconocido"

# ── Descarga del PDF desde la URL de sección ─────────────────────────────────
def obtener_pdf_de_seccion(url_seccion: str):
    """
    La URL de sección devuelve una página HTML con un enlace al PDF.
    Lo parseamos para encontrar el href del PDF, o intentamos descarga directa.
    """
    from bs4 import BeautifulSoup

    try:
        resp = requests.get(url_seccion, headers=HEADERS, timeout=30)
        resp.raise_for_status()

        # Si la respuesta ya es un PDF, lo devolvemos directamente
        content_type = resp.headers.get("Content-Type", "")
        if "pdf" in content_type.lower():
            log.info(f"PDF descargado directamente desde {url_seccion}")
            return resp.content, url_seccion

        # Si es HTML, buscamos el enlace al PDF
        soup = BeautifulSoup(resp.text, "html.parser")
        pdf_url = None

        # Buscar enlace a PDF en la página
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf"):
                pdf_url = href if href.startswith("http") else "https://boletinoficial.gba.gob.ar" + href
                break

        # Si no hay enlace .pdf, buscar iframe o embed
        if not pdf_url:
            for tag in soup.find_all(["iframe", "embed", "object"]):
                src = tag.get("src") or tag.get("data") or ""
                if ".pdf" in src.lower():
                    pdf_url = src if src.startswith("http") else "https://boletinoficial.gba.gob.ar" + src
                    break

        if not pdf_url:
            log.warning(f"No se encontró enlace a PDF en {url_seccion}")
            return None, url_seccion

        log.info(f"Descargando PDF desde {pdf_url}")
        resp_pdf = requests.get(pdf_url, headers=HEADERS, timeout=60)
        resp_pdf.raise_for_status()
        return resp_pdf.content, pdf_url

    except Exception as e:
        log.error(f"Error al obtener PDF de {url_seccion}: {e}")
        return None, url_seccion

# ── Extracción de texto del PDF ───────────────────────────────────────────────
def extraer_texto_pdf(contenido: bytes) -> str:
    try:
        with pdfplumber.open(BytesIO(contenido)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception as e:
        log.warning(f"Error leyendo PDF: {e}")
        return ""

# ── Búsqueda de localidades en el texto ──────────────────────────────────────
def buscar_localidades(texto: str) -> list:
    """Devuelve lista de (localidad_title, fragmento_contexto)."""
    resultados = []
    # Eliminar correos para evitar falsos positivos
    texto_limpio = re.sub(r'\S+@\S+', ' ', texto)
    texto_lower  = texto_limpio.lower()

    for loc in LOCALIDADES:
        pos = 0
        while True:
            idx = texto_lower.find(loc, pos)
            if idx == -1:
                break
            inicio = max(0, idx - CONTEXTO_CHARS)
            fin    = min(len(texto_limpio), idx + CONTEXTO_CHARS)
            nombre_canon = ALIAS_LOCALIDAD.get(loc, loc.title())
            resultados.append((nombre_canon, texto_limpio[inicio:fin].strip()))
            pos = idx + len(loc)

    return resultados

# ── Extracción de CUITs/DNIs ──────────────────────────────────────────────────
def extraer_cuits_dnis(texto: str) -> list:
    encontrados = set()
    for m in re.findall(r'\b\d{2}-\d{8}-\d\b', texto):
        encontrados.add(m)
    for m in re.findall(r'\b(?:DNI|CUIT|CUIL)[\s:]*(\d{6,8})\b', texto, re.IGNORECASE):
        encontrados.add(m)
    return sorted(encontrados)

# ── Extracción de nombres en MAYÚSCULAS ──────────────────────────────────────
def extraer_mayusculas(texto: str) -> list:
    EXCLUIR = {
        "JUZGADO", "PRIMERA", "INSTANCIA", "CIVIL", "COMERCIAL", "SECRETARIA",
        "PROVINCIA", "BUENOS", "AIRES", "REPUBLICA", "ARGENTINA", "PODER",
        "JUDICIAL", "OFICIAL", "BOLETIN", "NUMERO", "ARTICULO", "INCISO",
        "DECRETO", "RESOLUCION", "MINISTERIO", "CDOR", "SINDICO", "QUIEBRA",
        "CONCURSO", "PREVENTIVO", "EDICTO", "DOMICILIO", "CIUDAD", "PARTIDO",
        "REGISTRO", "EXPEDIENTE", "PRESENTE", "MEDIANTE", "CONTRA",
    }
    matches = re.findall(r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+\b', texto)
    resultado = []
    vistos = set()
    for m in matches:
        m_clean = m.strip()
        palabras = m_clean.split()
        if len(m_clean) < 3 or any(p in EXCLUIR for p in palabras):
            continue
        if m_clean not in vistos:
            vistos.add(m_clean)
            resultado.append(m_clean)
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

# ── Limpieza de registros viejos ──────────────────────────────────────────────
def eliminar_viejos(dias: int = 60):
    limite = (datetime.now() - timedelta(days=dias)).date()
    try:
        supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()
        log.info(f"Registros anteriores a {limite} eliminados.")
    except Exception as e:
        log.warning(f"No se pudieron eliminar registros viejos: {e}")

# ── Proceso principal ─────────────────────────────────────────────────────────
def main():
    fecha_fallback = (datetime.utcnow() - timedelta(hours=3)).date()
    total_global   = 0

    for nombre_seccion, url_seccion in SECCIONES.items():
        log.info(f"═══ Procesando sección {nombre_seccion} ═══")

        pdf_bytes, url_pdf_real = obtener_pdf_de_seccion(url_seccion)
        if not pdf_bytes:
            log.warning(f"Sin PDF para {nombre_seccion}. ¿Feriado o cambio de URL?")
            continue

        texto = extraer_texto_pdf(pdf_bytes)
        if not texto.strip():
            log.warning(f"PDF de {nombre_seccion} sin texto extraíble.")
            continue

        # Fecha y número extraídos directamente del PDF (no de HTML)
        fecha          = extraer_fecha_del_pdf(texto) or fecha_fallback
        numero_boletin = extraer_numero_del_pdf(texto)

        log.info(f"Boletín N° {numero_boletin} | Fecha: {fecha} | {len(texto)} caracteres")

        menciones = buscar_localidades(texto)
        log.info(f"{len(menciones)} menciones de localidades encontradas en {nombre_seccion}")

        guardados = 0
        for localidad, fragmento in menciones:
            if guardar_edicto(localidad, fragmento, nombre_seccion, fecha, numero_boletin, url_pdf_real):
                guardados += 1

        log.info(f"{nombre_seccion}: {guardados} edictos nuevos guardados.")
        total_global += guardados

    eliminar_viejos(60)
    log.info(f"═══ FIN | Total guardados: {total_global} ═══")
    sys.exit(0)


if __name__ == "__main__":
    main()
