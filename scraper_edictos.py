"""
scraper_edictos.py - VERSIÓN DEFINITIVA
- Extrae MÚLTIPLES edictos por página
- Limpia caracteres � (reemplaza por espacio)
- Vincula páginas consecutivas
- Niveles de confianza: ALTA, MEDIA, BAJA
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
    log.error("Faltan SUPABASE_URL o SUPABASE_KEY")
    sys.exit(0)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OSECAC-Scraper/1.0)"}

LOCALIDADES = {
    "mar del plata", "alvarado", "miramar", "mechongue", "otamendi", "vivorata",
    "vidal", "piran", "las armas", "maipu", "labarden", "guido", "dolores",
    "castelli", "tordillo", "conesa", "lavalle", "san clemente", "las toninas",
    "santa teresita", "mar del tuyu", "san bernardo", "la lucila del mar",
    "mar de ajo", "costa del este", "pinamar", "madariaga", "villa gesell",
    "mar chiquita", "general guido",
}

ABREVIATURAS = {
    "mdp": "mar del plata",
    "m.d.p.": "mar del plata",
    "depto. jud. de mdp": "mar del plata",
    "gral. guido": "general guido",
    "gral. madariaga": "madariaga",
    "pdo. de dolores": "dolores",
    "mar chiq.": "mar chiquita",
}

ALIAS_LOCALIDAD = {"general guido": "Guido", "gdor. arias": "Dolores"}

RE_INICIO_TRANSFERENCIAS = re.compile(r'\bTRANSFERENCIAS?\b', re.IGNORECASE)

# Palabras a ignorar al extraer nombres
PALABRAS_IGNORAR = re.compile(
    r'^(la|el|los|las|señora|señor|señora?|doña|don|de|del|de la|de los|de las)\s+',
    re.IGNORECASE
)

def limpiar_texto(texto: str) -> str:
    """Reemplaza caracteres � por espacios y normaliza"""
    if not texto:
        return ""
    # Reemplazar � por espacio
    texto = texto.replace('�', ' ')
    # Eliminar múltiples espacios
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def extraer_nombre_mejorado(texto: str) -> str:
    """Extrae el nombre real ignorando artículos y títulos"""
    if not texto:
        return ""
    
    # Limpiar primero
    texto_limpio = limpiar_texto(texto)
    
    # Buscar patrón "quiebra de ..." o "concurso de ..."
    patron_principal = re.compile(
        r'(?:quiebra|concurso)\s+de\s+(.+?)(?:\s*(?:\(?DNI|CUIT|CUIL|\(|\n|$))',
        re.IGNORECASE
    )
    
    m = patron_principal.search(texto_limpio)
    if not m:
        # Buscar secuencias de mayúsculas (apellido y nombre)
        mayus = re.findall(r'\b([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+)?)\b', texto_limpio)
        if mayus:
            nombres_validos = [n for n in mayus if len(n.split()) >= 2]
            if nombres_validos:
                return nombres_validos[0].strip()
        return ""
    
    raw_nombre = m.group(1).strip()
    # Limpiar: eliminar artículos y títulos
    limpio = PALABRAS_IGNORAR.sub('', raw_nombre).strip()
    
    if not limpio:
        limpio = raw_nombre
    
    # Eliminar textos residuales
    if "BOLETÍN" in limpio.upper() or "OFICIAL" in limpio.upper():
        partes = limpio.split()
        candidatos = []
        for parte in partes:
            if re.match(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]*$', parte) and len(parte) > 2:
                if parte.upper() not in ['LA', 'EL', 'LOS', 'LAS', 'DE', 'DEL', 'Y']:
                    candidatos.append(parte)
        if len(candidatos) >= 2:
            return ' '.join(candidatos[:3])
    
    limpio = re.sub(r'[,\n\r]+$', '', limpio)
    return limpio.upper() if len(limpio) > 3 else ""

def extraer_todos_edictos_de_pagina(texto: str) -> list:
    """
    Extrae TODOS los edictos de una página usando "POR X DÍAS" como separador
    Retorna lista de dicts: {'tipo': str, 'nombre': str, 'cuits': list}
    """
    if not texto:
        return []
    
    texto_limpio = limpiar_texto(texto)
    
    # Separar por "POR X DÍAS" (cada nuevo edicto empieza ahí)
    partes = re.split(r'POR\s+\d+\s+DÍAS\s*[-–]?\s*', texto_limpio)
    
    edictos = []
    for parte in partes:
        parte = parte.strip()
        if not parte or len(parte) < 50:
            continue
        
        # Buscar si tiene quiebra o concurso
        tiene_quiebra = re.search(r'\bquiebra\b', parte, re.IGNORECASE) is not None
        tiene_concurso = re.search(r'\bconcurso\b', parte, re.IGNORECASE) is not None
        
        if not (tiene_quiebra or tiene_concurso):
            continue
        
        tipo = "QUIEBRA" if tiene_quiebra else ("CONCURSO" if tiene_concurso else "EDICTO")
        
        # Extraer nombre
        nombre = extraer_nombre_mejorado(parte)
        
        # Extraer CUITs/DNIs
        cuits = set()
        for m in re.findall(r'\b\d{2}-\d{8}-\d\b', parte):
            cuits.add(m)
        for m in re.findall(r'\b(?:DNI|CUIT|CUIL)[\s:Nº°]*(\d{6,11})\b', parte, re.IGNORECASE):
            cuits.add(m)
        for m in re.findall(r'\b(\d{7,8})\b', parte):
            if not (1900 <= int(m) <= 2030):
                cuits.add(m)
        
        edictos.append({
            'tipo': tipo,
            'nombre': nombre,
            'cuits': ", ".join(sorted(cuits)) if cuits else None,
            'texto': parte[:500]  # Guardamos parte del texto para referencia
        })
    
    return edictos

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

# ── Vincular páginas consecutivas ──────────────────────────────────────────
def vincular_paginas_consecutivas(paginas_con_localidades, todas_paginas):
    resultado = {}
    
    for pag, locs in paginas_con_localidades.items():
        texto_pagina = todas_paginas[pag]
        
        # Extraer TODOS los edictos de esta página
        edictos_pagina = extraer_todos_edictos_de_pagina(texto_pagina)
        
        # También revisar página anterior y siguiente
        paginas_a_revisar = [pag]
        if pag - 1 in todas_paginas:
            paginas_a_revisar.append(pag - 1)
        if pag + 1 in todas_paginas:
            paginas_a_revisar.append(pag + 1)
        
        todos_edictos = list(edictos_pagina)
        for otra_pag in paginas_a_revisar:
            if otra_pag != pag:
                otros_edictos = extraer_todos_edictos_de_pagina(todas_paginas[otra_pag])
                todos_edictos.extend(otros_edictos)
        
        # Si no encontró edictos, usar método anterior como fallback
        if not todos_edictos:
            tipo_actual = extraer_tipo_edicto_fallback(texto_pagina)
            nombre_actual = extraer_nombre_mejorado(texto_pagina)
            todos_edictos = [{'tipo': tipo_actual, 'nombre': nombre_actual, 'cuits': None}]
        
        # Para cada localidad, usar el PRIMER edicto de la página (o el que tenga nombre)
        # Pero si hay múltiples, intentar asignar correctamente
        mejor_edicto = None
        for e in todos_edictos:
            if e['nombre'] and len(e['nombre']) > 5 and "BOLETÍN" not in e['nombre'].upper():
                mejor_edicto = e
                break
        if not mejor_edicto and todos_edictos:
            mejor_edicto = todos_edictos[0]
        
        if mejor_edicto:
            tipo_maximo = mejor_edicto['tipo']
            nombre_principal = mejor_edicto['nombre']
            cuits = mejor_edicto['cuits']
        else:
            tipo_maximo = "EDICTO"
            nombre_principal = ""
            cuits = None
        
        if tipo_maximo in ["QUIEBRA", "CONCURSO"]:
            if nombre_principal and len(nombre_principal) > 3:
                nivel_confianza = "ALTA"
            else:
                nivel_confianza = "MEDIA"
        else:
            nivel_confianza = "BAJA"
        
        resultado[pag] = {
            'localidades': locs,
            'tipo_edicto': tipo_maximo,
            'sujetos': nombre_principal if nombre_principal else None,
            'nivel_confianza': nivel_confianza,
            'cuits': cuits,
            'paginas_relacionadas': list(set(paginas_a_revisar))
        }
    
    return resultado

def extraer_tipo_edicto_fallback(texto: str) -> str:
    texto_limpio = limpiar_texto(texto)
    if re.search(r'\bquiebra\b', texto_limpio, re.IGNORECASE):
        return "QUIEBRA"
    if re.search(r'\bconcurso\b', texto_limpio, re.IGNORECASE):
        return "CONCURSO"
    return "EDICTO"

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

        inicio_transferencias = None
        if seccion_nombre == "OFICIAL":
            for pag, txt in paginas:
                if RE_INICIO_TRANSFERENCIAS.search(txt):
                    inicio_transferencias = pag
                    break
            if inicio_transferencias is None:
                log.warning("No se encontró TRANSFERENCIAS. Se omite OFICIAL.")
                continue

        todas_paginas = {pag: txt for pag, txt in paginas}
        paginas_con_localidades = {}
        
        for pagina, texto_pagina in paginas:
            if seccion_nombre == "OFICIAL" and inicio_transferencias and pagina < inicio_transferencias:
                continue
            localidades = localidades_en_texto(texto_pagina)
            if localidades:
                paginas_con_localidades[pagina] = localidades
        
        if not paginas_con_localidades:
            continue
        
        paginas_procesadas = vincular_paginas_consecutivas(paginas_con_localidades, todas_paginas)
        
        for pagina, datos in paginas_procesadas.items():
            texto_pagina = todas_paginas[pagina]
            
            for loc in datos['localidades']:
                existente = supabase.table("edictos").select("id") \
                    .eq("fecha", fecha_boletin.isoformat()) \
                    .eq("boletin_numero", str(numero)) \
                    .eq("seccion", seccion_nombre) \
                    .eq("localidad", loc) \
                    .eq("pagina", pagina) \
                    .execute()
                if existente.data:
                    continue
                
                data = {
                    "fecha": fecha_boletin.isoformat(),
                    "boletin_numero": str(numero),
                    "seccion": seccion_nombre,
                    "localidad": loc,
                    "tipo_edicto": datos['tipo_edicto'],
                    "cuit_detectados": datos['cuits'],
                    "sujetos": datos['sujetos'],
                    "texto_completo": texto_pagina,
                    "url_pdf": url,
                    "pagina": pagina,
                    "nivel_confianza": datos['nivel_confianza'],
                    "paginas_relacionadas": datos['paginas_relacionadas']
                }
                try:
                    supabase.table("edictos").insert(data).execute()
                    log.info(f"✅ pág {pagina} | {datos['tipo_edicto']} | {datos['nivel_confianza']} | {loc} | {datos['sujetos'] or '(sin nombre)'}")
                    total += 1
                except Exception as e:
                    log.error(f"❌ Error: {e}")
    
    return total

def main():
    log.info("═══ SCRAPER DEFINITIVO (MÚLTIPLES EDICTOS POR PÁGINA) ═══")
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
