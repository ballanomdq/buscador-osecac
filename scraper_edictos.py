"""
scraper_edictos.py - Versión con segmentación por bloques de edictos
─────────────────────────────────────────────────────────────────────
CAMBIO PRINCIPAL:
  En lugar de tomar un fragmento de N caracteres alrededor de la localidad,
  ahora se divide el PDF en bloques lógicos (edictos individuales) usando
  el marcador "POR X DÍAS" como separador. Cada bloque es un edicto completo.
  Se busca la localidad DENTRO del bloque completo, y si está presente,
  se guarda el bloque íntegro. Esto garantiza que palabras como "quiebra",
  "concurso", el nombre del fallido y el CUIT siempre estén en el texto
  guardado, sin importar su posición relativa respecto a la localidad.
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

# ── Tipos de edictos que nos interesan ───────────────────────────────────────
TIPOS_EDICTO = [
    "quiebra", "concurso preventivo", "concurso", "subasta",
    "sucesion", "citacion", "inhibicion", "embargo", "remate",
]

# ── Regex de segmentación y extracción ───────────────────────────────────────

# Separador de edictos: "POR N DÍAS" al final de cada edicto
RE_SEPARADOR = re.compile(
    r'\bPOR\s+\w+\s+D[IÍ]AS?\b',
    re.IGNORECASE
)

# Regex para fecha del boletín en el texto del PDF
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


# ── Segmentación del texto en bloques/edictos ─────────────────────────────────

def segmentar_en_edictos(texto: str) -> list[str]:
    """
    Divide el texto completo del PDF en bloques individuales de edictos.

    Estrategia:
      Busca todas las posiciones donde aparece "POR N DÍAS" (el cierre de
      cada edicto). Cada bloque va desde el final del cierre anterior
      hasta el final del cierre actual (inclusive).

    Si no encuentra ningún separador (texto sin estructura esperada),
    devuelve el texto completo como un único bloque.
    """
    separadores = list(RE_SEPARADOR.finditer(texto))

    if not separadores:
        log.warning("No se encontraron separadores 'POR X DÍAS' — se procesa como bloque único")
        return [texto.strip()] if texto.strip() else []

    bloques = []
    inicio  = 0

    for sep in separadores:
        fin    = sep.end()
        bloque = texto[inicio:fin].strip()
        if bloque:
            bloques.append(bloque)
        inicio = fin  # el siguiente bloque empieza justo después

    # Texto residual al final (sin cierre "POR X DÍAS")
    residual = texto[inicio:].strip()
    if residual:
        bloques.append(residual)

    log.info(f"Texto segmentado en {len(bloques)} bloques de edictos")
    return bloques


# ── Detección de localidad en un bloque ──────────────────────────────────────

def localidades_en_bloque(bloque: str) -> list[str]:
    """
    Devuelve la lista de localidades (normalizadas) que aparecen
    en el bloque de texto, eliminando duplicados.
    """
    bloque_lower = bloque.lower()
    # Eliminar correos para evitar falsos positivos
    bloque_lower = re.sub(r'\S+@\S+', ' ', bloque_lower)

    encontradas = []
    vistas = set()
    for loc in LOCALIDADES:
        if loc in bloque_lower and loc not in vistas:
            vistas.add(loc)
            nombre = ALIAS_LOCALIDAD.get(loc, loc.title())
            encontradas.append(nombre)
    return encontradas


# ── Extracción de tipo de edicto ──────────────────────────────────────────────

def extraer_tipo_edicto(bloque: str) -> str:
    """
    Detecta el tipo de edicto (QUIEBRA, CONCURSO, SUBASTA, etc.)
    buscando palabras clave en el texto del bloque.
    Devuelve la primera coincidencia en mayúsculas, o 'EDICTO' por defecto.
    """
    bloque_lower = bloque.lower()
    for tipo in TIPOS_EDICTO:
        if tipo in bloque_lower:
            return tipo.upper()
    return "EDICTO"


# ── Extracción de CUITs y DNIs ────────────────────────────────────────────────

def extraer_cuits_dnis(texto: str) -> list:
    encontrados = set()
    # CUIT/CUIL con guiones: XX-XXXXXXXX-X
    for m in re.findall(r'\b\d{2}-\d{8}-\d\b', texto):
        encontrados.add(m)
    # CUIT/CUIL/DNI seguido de número
    for m in re.findall(r'\b(?:DNI|CUIT|CUIL)[\s:Nº°]*(\d{6,11})\b', texto, re.IGNORECASE):
        encontrados.add(m)
    # Números de 7 u 8 dígitos que no sean años (posibles DNIs sin prefijo)
    for m in re.findall(r'\b(\d{7,8})\b', texto):
        if not (1900 <= int(m) <= 2030):
            encontrados.add(m)
    return sorted(encontrados)


# ── Extracción de nombre del sujeto (fallido, concursado, etc.) ───────────────

def extraer_nombre_sujeto(bloque: str) -> str:
    """
    Intenta extraer el nombre del sujeto del edicto.

    Estrategias (en orden de confiabilidad):
    1. Patrón "quiebra/concurso de NOMBRE, NOMBRE"
    2. Patrón "APELLIDO, NOMBRE" en mayúsculas
    3. Secuencia de palabras en MAYÚSCULAS contiguas (hasta 6 palabras)
    """
    # Estrategia 1: después de "quiebra de" o "concurso de"
    m = re.search(
        r'(?:quiebra|concurso\s+preventivo|concurso)\s+de\s+'
        r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑA-Za-záéíóúñ,\s\.]+?)(?:\s*[-–,]|\s+con\s+domicilio|\s+CUIT|\s+DNI|\n)',
        bloque, re.IGNORECASE
    )
    if m:
        nombre = m.group(1).strip().rstrip(',').strip()
        if len(nombre) > 3:
            return nombre.upper()

    # Estrategia 2: "APELLIDO, Nombre" con coma
    m = re.search(
        r'\b([A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,})*),\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)\b',
        bloque
    )
    if m:
        return f"{m.group(1)}, {m.group(2)}"

    # Estrategia 3: secuencia de palabras en MAYÚSCULAS
    palabras_excluir = {
        "JUZGADO","PRIMERA","INSTANCIA","CIVIL","COMERCIAL","SECRETARIA",
        "PROVINCIA","BUENOS","AIRES","REPUBLICA","ARGENTINA","PODER",
        "JUDICIAL","OFICIAL","BOLETIN","NUMERO","ARTICULO","DECRETO",
        "RESOLUCION","MINISTERIO","SINDICO","QUIEBRA","CONCURSO","POR",
        "PREVENTIVO","EDICTO","DOMICILIO","CIUDAD","PARTIDO","REGISTRO",
        "EXPEDIENTE","PRESENTE","MEDIANTE","CONTRA","DIAS","HACE","SABER",
        "MAR","DEL","PLATA","LA","LAS","LOS","SAN","SANTA","GENERAL",
    }
    secuencias = re.findall(r'\b([A-ZÁÉÍÓÚÑ]{3,}(?:\s+[A-ZÁÉÍÓÚÑ]{3,}){1,5})\b', bloque)
    for seq in secuencias:
        palabras = seq.split()
        if not any(p in palabras_excluir for p in palabras):
            return seq

    return ""


# ── Guardar edicto en Supabase ────────────────────────────────────────────────

def guardar_edicto(
    localidad: str,
    texto: str,
    seccion: str,
    fecha,
    boletin_numero: str,
    url_pdf: str,
    tipo_edicto: str,
    nombre_sujeto: str,
) -> bool:
    cuits = extraer_cuits_dnis(texto)

    # Deduplicación: mismo boletín + sección + localidad + tipo + nombre
    try:
        existente = supabase.table("edictos").select("id") \
            .eq("fecha", fecha.isoformat()) \
            .eq("boletin_numero", str(boletin_numero)) \
            .eq("seccion", seccion) \
            .eq("localidad", localidad) \
            .eq("tipo_edicto", tipo_edicto) \
            .eq("sujetos", nombre_sujeto) \
            .execute()
        if existente.data:
            log.info(f"Ya existe: {fecha} | N°{boletin_numero} | {seccion} | {localidad} | {nombre_sujeto}")
            return False
    except Exception as e:
        log.warning(f"Error en consulta dedup: {e}")

    data = {
        "fecha":           fecha.isoformat(),
        "boletin_numero":  str(boletin_numero),
        "seccion":         seccion,
        "localidad":       localidad,
        "tipo_edicto":     tipo_edicto,
        "cuit_detectados": ", ".join(cuits) if cuits else None,
        "sujetos":         nombre_sujeto or None,
        "texto_completo":  texto,
        "url_pdf":         url_pdf,
    }

    try:
        resultado = supabase.table("edictos").insert(data).execute()
        if resultado.data:
            log.info(f"✅ GUARDADO: {tipo_edicto} | {localidad} | {nombre_sujeto or '(sin nombre)'} | {fecha}")
            return True
        else:
            log.warning(f"Insert sin respuesta: {resultado}")
            return False
    except Exception as e:
        error_str = str(e)
        if "duplicate" in error_str.lower() or "unique" in error_str.lower():
            log.info(f"Duplicado por constraint: {localidad} | {nombre_sujeto}")
            return False
        log.error(f"❌ ERROR INSERTANDO: {e}")
        return False


# ── Limpieza de registros viejos ──────────────────────────────────────────────

def eliminar_viejos(dias: int = 60):
    ahora  = datetime.now(BUENOS_AIRES)
    limite = (ahora - timedelta(days=dias)).date()
    try:
        resultado = supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()
        cant = len(resultado.data) if resultado.data else 0
        log.info(f"Registros anteriores a {limite} eliminados: {cant}")
    except Exception as e:
        log.warning(f"No se pudieron eliminar registros viejos: {e}")


# ── Scraping de la web del boletín (sin cambios respecto a versión anterior) ──

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
        m_num   = re.search(r"N[°º]?\s*(\d+)", texto, re.IGNORECASE)
        m_fecha = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
        if not m_num or not m_fecha:
            return None, None, None
        numero    = m_num.group(1)
        fecha_str = m_fecha.group(1)
        urls      = obtener_secciones_de_panel(panel)
        if urls:
            log.info(f"Último boletín: N° {numero} - {fecha_str} | Secciones: {list(urls.keys())}")
            return numero, fecha_str, urls
        else:
            log.warning(f"Último boletín N° {numero} sin secciones válidas")
            return numero, fecha_str, None
    except Exception as e:
        log.error(f"Error obteniendo último boletín: {e}")
        return None, None, None


# ── Descarga y extracción de texto del PDF ────────────────────────────────────

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
    """Extrae el texto completo del PDF página por página."""
    try:
        with pdfplumber.open(BytesIO(contenido)) as pdf:
            paginas = len(pdf.pages)
            textos  = []
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
            log.info(f"PDF procesado: {paginas} páginas, {len(texto_completo)} chars")
            return texto_completo
    except Exception as e:
        log.warning(f"Error leyendo PDF: {e}")
        return ""


# ── Procesamiento principal de un boletín ────────────────────────────────────

def procesar_boletin(numero: str, fecha_str: str, urls_secciones: dict) -> int:
    if not urls_secciones:
        log.warning(f"No hay URLs de secciones para el boletín {numero}")
        return 0

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

        texto_completo = extraer_texto_pdf(pdf_bytes)
        if not texto_completo.strip():
            log.warning(f"PDF de {seccion_nombre} sin texto extraíble.")
            continue

        # Diagnóstico de fecha
        fecha_pdf = extraer_fecha_del_pdf(texto_completo)
        if fecha_pdf and fecha_pdf != fecha_boletin:
            log.warning(
                f"Fecha en el PDF: {fecha_pdf} | "
                f"Fecha del boletín: {fecha_boletin} (se mantiene la del boletín)"
            )

        # ── NUEVA LÓGICA: segmentar en bloques de edictos ──────────────────
        bloques = segmentar_en_edictos(texto_completo)
        log.info(f"{seccion_nombre}: {len(bloques)} bloques encontrados")

        guardados = 0

        for bloque in bloques:
            if len(bloque) < 50:          # bloques vacíos o residuos de cabecera
                continue

            localidades = localidades_en_bloque(bloque)
            if not localidades:
                continue                  # edicto sin localidad de interés

            tipo_edicto   = extraer_tipo_edicto(bloque)
            nombre_sujeto = extraer_nombre_sujeto(bloque)

            for localidad in localidades:
                if guardar_edicto(
                    localidad     = localidad,
                    texto         = bloque,
                    seccion       = seccion_nombre,
                    fecha         = fecha_boletin,
                    boletin_numero= numero,
                    url_pdf       = url,
                    tipo_edicto   = tipo_edicto,
                    nombre_sujeto = nombre_sujeto,
                ):
                    guardados += 1

        log.info(f"{seccion_nombre}: {guardados} edictos nuevos guardados.")
        total += guardados

    return total


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    log.info("═══════════════════════════════════════════════════")
    log.info("═══ SCRAPER CON SEGMENTACIÓN POR BLOQUES ══════════")
    log.info("═══════════════════════════════════════════════════")

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
