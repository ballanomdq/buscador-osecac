"""
scraper_edictos.py - Versión mejorada
- Aumenta el contexto de búsqueda a 5000 caracteres.
- Mejora la extracción de texto del PDF.
- Guarda el texto completo (sin recortar).
- Mantiene la fecha y número del boletín desde la página oficial.
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
    log.error("Faltan SUPABASE_URL o SUPABASE_KEY en variables de entorno")
    sys.exit(0)

log.info(f"Conectando a Supabase: {SUPABASE_URL[:50]}...")
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
# Aumentamos el contexto a 5000 caracteres (antes 1500)
CONTEXTO_CHARS  = 5000

# ── Regex para extraer números y fechas (solo diagnóstico) ────────────────────
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

# ── Scraping de ediciones anteriores (sin cambios) ─────────────────────────
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
        resp.raise_for_status()
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
                    log.info(f"Boletín encontrado: N° {numero} - {fecha_str} | Secciones: {list(urls.keys())}")
                    return numero, fecha_str, urls
                else:
                    log.warning(f"Boletín N° {numero} encontrado pero sin secciones válidas.")
                    return numero, fecha_str, None
        log.error(f"No se encontró el boletín N° {numero}")
        return None, None, None
    except Exception as e:
        log.error(f"Error buscando boletín N° {numero}: {e}")
        return None, None, None

def obtener_ultimo_boletin():
    url_ediciones = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url_ediciones, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        panel = soup.find("div", class_="panel-default")
        if not panel:
            log.error("No se encontró ningún panel")
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
        if urls:
            log.info(f"Último boletín: N° {numero} - {fecha_str} | Secciones: {list(urls.keys())}")
            return numero, fecha_str, urls
        else:
            log.warning(f"Último boletín N° {numero} sin secciones válidas")
            return numero, fecha_str, None
    except Exception as e:
        log.error(f"Error obteniendo último boletín: {e}")
        return None, None, None

# ── Descarga y procesamiento de PDF mejorados ──────────────────────────────
def descargar_pdf(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        log.info(f"PDF descargado: {len(resp.content)} bytes")
        return resp.content
    except Exception as e:
        log.warning(f"Error descargando {url}: {e}")
        return None

def extraer_texto_pdf(contenido: bytes) -> str:
    """Extrae texto del PDF manejando posibles errores por página."""
    try:
        with pdfplumber.open(BytesIO(contenido)) as pdf:
            paginas = len(pdf.pages)
            textos = []
            for i, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()
                    if text:
                        textos.append(text)
                    else:
                        log.warning(f"Página {i+1} sin texto extraíble")
                except Exception as e:
                    log.warning(f"Error en página {i+1}: {e}")
            texto_completo = "\n".join(textos)
            log.info(f"PDF procesado: {paginas} páginas, {len(texto_completo)} caracteres extraídos")
            return texto_completo
    except Exception as e:
        log.warning(f"Error leyendo PDF: {e}")
        return ""

# ── Búsqueda de localidades con contexto ampliado ──────────────────────────
def buscar_localidades(texto: str) -> list:
    resultados  = []
    # Eliminar correos para evitar falsos positivos
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
    log.info(f"Total menciones encontradas: {len(resultados)}")
    return resultados

# ── Extracción de metadatos mejorada ──────────────────────────────────────
def extraer_cuits_dnis(texto: str) -> list:
    encontrados = set()
    # CUIT con guiones
    for m in re.findall(r'\b\d{2}-\d{8}-\d\b', texto):
        encontrados.add(m)
    # DNI con palabra clave
    for m in re.findall(r'\b(?:DNI|CUIT|CUIL)[\s:]*(\d{6,8})\b', texto, re.IGNORECASE):
        encontrados.add(m)
    # Números de 7 u 8 dígitos que no sean años
    for m in re.findall(r'\b(\d{7,8})\b', texto):
        if not (1900 <= int(m) <= 2030):
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

def guardar_edicto(localidad, texto, seccion, fecha, boletin_numero, url_pdf) -> bool:
    cuits   = extraer_cuits_dnis(texto)
    sujetos = extraer_mayusculas(texto)

    # Verificar si ya existe (por fecha, número, sección y localidad)
    try:
        existente = supabase.table("edictos").select("id")\
            .eq("fecha", fecha.isoformat())\
            .eq("boletin_numero", str(boletin_numero))\
            .eq("seccion", seccion)\
            .eq("localidad", localidad)\
            .execute()
        if existente.data:
            log.info(f"Ya existe: {fecha} | N°{boletin_numero} | {seccion} | {localidad}")
            return False
    except Exception as e:
        log.warning(f"Error en consulta dedup: {e}")

    # Guardar el texto completo (sin recortar) para no perder información
    data = {
        "fecha":           fecha.isoformat(),
        "boletin_numero":  str(boletin_numero),
        "seccion":         seccion,
        "localidad":       localidad,
        "cuit_detectados": ", ".join(cuits) if cuits else None,
        "sujetos":         ", ".join(sujetos) if sujetos else None,
        "texto_completo":  texto,   # Texto completo, sin límite
        "url_pdf":         url_pdf,
    }

    try:
        resultado = supabase.table("edictos").insert(data).execute()
        if resultado.data:
            log.info(f"✅ GUARDADO: {localidad} | {seccion} | {fecha}")
            return True
        else:
            log.warning(f"Insert sin respuesta: {resultado}")
            return False
    except Exception as e:
        error_str = str(e)
        if "duplicate" in error_str.lower() or "unique" in error_str.lower():
            log.info(f"Duplicado detectado por constraint: {localidad}")
            return False
        log.error(f"❌ ERROR INSERTANDO: {e}")
        return False

def eliminar_viejos(dias: int = 60):
    ahora   = datetime.now(BUENOS_AIRES)
    limite  = (ahora - timedelta(days=dias)).date()
    try:
        resultado = supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()
        cant = len(resultado.data) if resultado.data else 0
        log.info(f"Registros anteriores a {limite} eliminados: {cant}")
    except Exception as e:
        log.warning(f"No se pudieron eliminar registros viejos: {e}")

def procesar_boletin(numero: str, fecha_str: str, urls_secciones: dict) -> int:
    if not urls_secciones:
        log.warning(f"No hay URLs de secciones para el boletín {numero}")
        return 0

    # Fecha del boletín (la correcta, desde la página de ediciones anteriores)
    try:
        fecha_boletin = datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except Exception:
        fecha_boletin = datetime.now(BUENOS_AIRES).date()

    total = 0
    for seccion_nombre, url in urls_secciones.items():
        log.info(f"── Procesando {seccion_nombre}: {url}")
        pdf_bytes = descargar_pdf(url)
        if not pdf_bytes:
            log.warning(f"Sin PDF para {seccion_nombre}")
            continue
        texto = extraer_texto_pdf(pdf_bytes)
        if not texto.strip():
            log.warning(f"PDF de {seccion_nombre} sin texto extraíble.")
            continue

        # Solo diagnóstico
        fecha_pdf = extraer_fecha_del_pdf(texto)
        if fecha_pdf and fecha_pdf != fecha_boletin:
            log.warning(f"Fecha en el PDF: {fecha_pdf} | Fecha del boletín: {fecha_boletin} (se mantiene la del boletín)")

        menciones = buscar_localidades(texto)
        log.info(f"{len(menciones)} menciones de localidades encontradas en {seccion_nombre}")

        guardados = 0
        for localidad, fragmento in menciones:
            # Guardamos el texto completo, no solo el fragmento
            if guardar_edicto(localidad, fragmento, seccion_nombre, fecha_boletin, numero, url):
                guardados += 1
        log.info(f"{seccion_nombre}: {guardados} edictos nuevos guardados.")
        total += guardados

    return total

def main():
    log.info("═══════════════════════════════════════")
    log.info("═══ INICIO DEL SCRAPER (VERSIÓN MEJORADA) ═══")
    log.info("═══════════════════════════════════════")

    boletin_numero = None
    if len(sys.argv) > 1:
        boletin_numero = sys.argv[1]
        log.info(f"Argumento recibido: N° {boletin_numero}")
    else:
        boletin_numero = os.environ.get("BOLETIN_NUMERO")
        if boletin_numero:
            log.info(f"Variable de entorno BOLETIN_NUMERO: N° {boletin_numero}")

    if boletin_numero:
        numero, fecha_str, urls = obtener_boletin_por_numero(boletin_numero)
        if not numero:
            log.error(f"No se encontró el boletín N° {boletin_numero}")
            sys.exit(0)
    else:
        numero, fecha_str, urls = obtener_ultimo_boletin()
        if not numero:
            log.error("No se pudo obtener el último boletín")
            sys.exit(0)

    log.info(f"Procesando boletín N° {numero} - {fecha_str}")
    total = procesar_boletin(numero, fecha_str, urls)
    eliminar_viejos(60)
    log.info(f"═══ FIN | Nuevos guardados: {total} ═══")
    sys.exit(0)

if __name__ == "__main__":
    main()
