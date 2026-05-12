"""
scraper_edictos.py - Versión con:
- Segmentación por bloques de edictos.
- Filtro en OFICIAL: solo capítulo "TRANSFERENCIAS".
- Guarda el número de página y el texto completo de la página.
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

# Abreviaturas y variantes textuales
ABREVIATURAS = {
    "mdp"                        : "mar del plata",
    "m.d.p."                     : "mar del plata",
    "m.d.p"                      : "mar del plata",
    "depto. jud. de mdp"         : "departamento judicial mar del plata",
    "depto. jud. mdp"            : "departamento judicial mar del plata",
    "dto. jud. de mdp"           : "departamento judicial mar del plata",
    "dto. jud. mdp"              : "departamento judicial mar del plata",
    "dpto. jud. mdp"             : "departamento judicial mar del plata",
    "dpto. jud. de mdp"          : "departamento judicial mar del plata",
    "depto. judicial mar del plata": "departamento judicial mar del plata",
    "gral. guido"                : "general guido",
    "gral guido"                 : "general guido",
    "gral. madariaga"            : "madariaga",
    "gral madariaga"             : "madariaga",
    "pdo. de dolores"            : "dolores",
    "partido de dolores"         : "dolores",
    "mar chiq."                  : "mar chiquita",
}

ALIAS_LOCALIDAD = {
    "general guido" : "Guido",
    "gdor. arias"   : "Dolores",
}

# ── Tipos de edictos que nos interesan (para cualquier sección) ──────────────
TIPOS_EDICTO = [
    "quiebra", "concurso preventivo", "concurso", "subasta",
    "sucesion", "citacion", "inhibicion", "embargo", "remate",
]

# ── En OFICIAL solo nos interesa TRANSFERENCIAS ───────────────────────────────
PALABRAS_TRANSFERENCIAS = ["transferencia", "transferencias", "cesión", "cesiones"]

# ── Regex ─────────────────────────────────────────────────────────────────────
RE_SEPARADOR = re.compile(
    r'(?:^|\n)\s*POR\s+\w+\s+D[IÍ]AS?\b',
    re.IGNORECASE | re.MULTILINE
)

RE_INICIO_TRANSFERENCIAS = re.compile(r'\bTRANSFERENCIAS?\b', re.IGNORECASE)

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


# ── Segmentación en bloques ───────────────────────────────────────────────────
def segmentar_en_edictos(texto: str) -> list[str]:
    matches = list(RE_SEPARADOR.finditer(texto))
    if not matches:
        log.warning("No se encontraron separadores 'POR X DÍAS' — se procesa como bloque único")
        return [texto.strip()] if texto.strip() else []
    bloques = []
    for i, m in enumerate(matches):
        inicio = m.start()
        fin    = matches[i + 1].start() if i + 1 < len(matches) else len(texto)
        bloque = texto[inicio:fin].strip()
        if len(bloque) > 50:
            bloques.append(bloque)
    log.info(f"Texto segmentado en {len(bloques)} bloques")
    return bloques


# ── Detección de localidad ────────────────────────────────────────────────────
def normalizar_abreviaturas(texto: str) -> str:
    for abrev, expansion in ABREVIATURAS.items():
        texto = re.sub(
            r'(?<![a-záéíóúñ])' + re.escape(abrev) + r'(?![a-záéíóúñ])',
            expansion,
            texto
        )
    return texto

def localidades_en_bloque(bloque: str) -> list[str]:
    bloque_lower = bloque.lower()
    bloque_lower = re.sub(r'\S+@\S+', ' ', bloque_lower)
    bloque_lower = normalizar_abreviaturas(bloque_lower)
    encontradas = []
    vistas = set()
    for loc in LOCALIDADES:
        if loc in bloque_lower and loc not in vistas:
            vistas.add(loc)
            nombre = ALIAS_LOCALIDAD.get(loc, loc.title())
            encontradas.append(nombre)
    return encontradas


# ── Filtro para OFICIAL: solo TRANSFERENCIAS ──────────────────────────────────
def es_capitulo_transferencias(bloque: str) -> bool:
    cabecera = bloque[:500].lower()
    return any(p in cabecera for p in PALABRAS_TRANSFERENCIAS)


# ── Extracción de tipo y nombre ───────────────────────────────────────────────
def extraer_tipo_edicto(bloque: str) -> str:
    bloque_lower = bloque.lower()
    for tipo in TIPOS_EDICTO:
        if tipo in bloque_lower:
            return tipo.upper()
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

def extraer_nombre_sujeto(bloque: str) -> str:
    m = re.search(
        r'(?:quiebra|concurso\s+preventivo|concurso)\s+de\s+'
        r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑA-Za-záéíóúñ,\s\.]+?)(?:\s*[-–,]|\s+con\s+domicilio|\s+CUIT|\s+DNI|\n)',
        bloque, re.IGNORECASE
    )
    if m:
        nombre = m.group(1).strip().rstrip(',').strip()
        if len(nombre) > 3:
            return nombre.upper()
    m = re.search(
        r'\b([A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,})*),\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)\b',
        bloque
    )
    if m:
        return f"{m.group(1)}, {m.group(2)}"
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


# ── Guardado en Supabase (con página) ─────────────────────────────────────────
def guardar_edicto(
    localidad: str,
    texto: str,
    seccion: str,
    fecha,
    boletin_numero: str,
    url_pdf: str,
    tipo_edicto: str,
    nombre_sujeto: str,
    pagina: int,
) -> bool:
    cuits = extraer_cuits_dnis(texto)
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
        "pagina":          pagina,
    }
    try:
        resultado = supabase.table("edictos").insert(data).execute()
        if resultado.data:
            log.info(f"✅ GUARDADO: {tipo_edicto} | {localidad} | {nombre_sujeto or '(sin nombre)'} | pág {pagina}")
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


# ── Limpieza de viejos ────────────────────────────────────────────────────────
def eliminar_viejos(dias: int = 60):
    ahora  = datetime.now(BUENOS_AIRES)
    limite = (ahora - timedelta(days=dias)).date()
    try:
        resultado = supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()
        cant = len(resultado.data) if resultado.data else 0
        log.info(f"Registros anteriores a {limite} eliminados: {cant}")
    except Exception as e:
        log.warning(f"No se pudieron eliminar registros viejos: {e}")


# ── Scraping web (ediciones anteriores) ───────────────────────────────────────
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


# ── Descarga y extracción con páginas ─────────────────────────────────────────
def descargar_pdf(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        log.info(f"PDF descargado: {len(resp.content)} bytes")
        return resp.content
    except Exception as e:
        log.warning(f"Error descargando {url}: {e}")
        return None

def extraer_texto_con_paginas(contenido: bytes):
    try:
        with pdfplumber.open(BytesIO(contenido)) as pdf:
            paginas_texto = []
            for i, page in enumerate(pdf.pages, start=1):
                try:
                    text = page.extract_text()
                    if text:
                        paginas_texto.append((i, text))
                    else:
                        log.warning(f"Página {i} sin texto extraíble")
                except Exception as e:
                    log.warning(f"Error en página {i}: {e}")
            log.info(f"PDF procesado: {len(paginas_texto)} páginas con texto")
            return paginas_texto
    except Exception as e:
        log.warning(f"Error leyendo PDF: {e}")
        return []


# ── Procesamiento principal ───────────────────────────────────────────────────
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
        paginas_texto = extraer_texto_con_paginas(pdf_bytes)
        if not paginas_texto:
            log.warning(f"PDF de {seccion_nombre} sin texto extraíble.")
            continue
        inicio_transferencias = None
        if seccion_nombre == "OFICIAL":
            for pagina, texto in paginas_texto:
                if RE_INICIO_TRANSFERENCIAS.search(texto):
                    inicio_transferencias = pagina
                    log.info(f"Capítulo TRANSFERENCIAS detectado en página {pagina}")
                    break
            if inicio_transferencias is None:
                log.warning("No se encontró TRANSFERENCIAS en OFICIAL. Se omite toda la sección.")
                continue
        for pagina, texto_pagina in paginas_texto:
            if seccion_nombre == "OFICIAL" and inicio_transferencias and pagina < inicio_transferencias:
                continue
            bloques = segmentar_en_edictos(texto_pagina)
            log.info(f"Página {pagina}: {len(bloques)} bloques")
            for bloque in bloques:
                if len(bloque) < 50:
                    continue
                if seccion_nombre == "OFICIAL" and not es_capitulo_transferencias(bloque):
                    continue
                localidades = localidades_en_bloque(bloque)
                if not localidades:
                    continue
                tipo_edicto   = extraer_tipo_edicto(bloque)
                nombre_sujeto = extraer_nombre_sujeto(bloque)
                for localidad in localidades:
                    if guardar_edicto(
                        localidad     = localidad,
                        texto         = texto_pagina,   # Toda la página
                        seccion       = seccion_nombre,
                        fecha         = fecha_boletin,
                        boletin_numero= numero,
                        url_pdf       = url,
                        tipo_edicto   = tipo_edicto,
                        nombre_sujeto = nombre_sujeto,
                        pagina        = pagina,
                    ):
                        total += 1
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
