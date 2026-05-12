"""
scraper_edictos.py - VERSIÓN FINAL
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
    log.error("Faltan credenciales")
    sys.exit(0)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_URL = "https://boletinoficial.gba.gob.ar"
HEADERS = {"User-Agent": "Mozilla/5.0"}

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

RE_INICIO_TRANSFERENCIAS = re.compile(r'\bTRANSFERENCIAS?\b', re.IGNORECASE)

# Nombres basura a ignorar
NOMBRES_BASURA = ["FECHA INICIO", "BOLETÍN OFICIAL", "BOLETIN OFICIAL", "LA PLATA", "BUENOS AIRES"]

def limpiar_nombre(nombre: str) -> str:
    if not nombre:
        return ""
    nombre = nombre.strip()
    nombre_upper = nombre.upper()
    for basura in NOMBRES_BASURA:
        if basura in nombre_upper:
            return ""
    # Limpiar "SEÑORA" del principio
    nombre = re.sub(r'^(SEÑORA|SEÑOR|DOÑA|DON)\s+', '', nombre, flags=re.IGNORECASE)
    return nombre

def extraer_edictos_de_texto(texto: str) -> list:
    """Extrae TODOS los edictos de una página usando 'POR X DÍAS' como separador"""
    if not texto:
        return []
    
    # Limpiar caracteres raros
    texto = texto.replace('�', ' ')
    texto = re.sub(r'\s+', ' ', texto)
    
    # Separar por "POR X DÍAS"
    partes = re.split(r'POR\s+\d+\s+DÍAS\s*[-–]?\s*', texto)
    
    resultados = []
    for parte in partes:
        parte = parte.strip()
        if not parte or len(parte) < 50:
            continue
        
        # Detectar tipo de edicto
        es_quiebra = re.search(r'\bquiebra\b', parte, re.IGNORECASE) is not None
        es_concurso = re.search(r'\bconcurso\b', parte, re.IGNORECASE) is not None
        
        if es_quiebra or es_concurso:
            tipo = "QUIEBRA" if es_quiebra else "CONCURSO"
        else:
            tipo = "EDICTO"
        
        # Extraer nombre
        nombre = ""
        patron_nombre = re.compile(
            r'(?:quiebra|concurso)\s+de\s+(?:la\s+)?(?:señora\s+)?(?:señor\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,\.]+?)(?:\s*(?:\(?DNI|CUIT|CUIL|\(|\n|$))',
            re.IGNORECASE
        )
        m = patron_nombre.search(parte)
        if m:
            nombre = m.group(1).strip().strip(',').strip()
            nombre = re.sub(r'\s+', ' ', nombre)
        else:
            # Buscar nombre en mayúsculas (al menos 2 palabras)
            mayus = re.findall(r'\b([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+)?)\b', parte)
            if mayus:
                nombre = mayus[0]
        
        nombre = limpiar_nombre(nombre)
        if not nombre and tipo == "EDICTO":
            # Para edictos sin quiebra, buscar nombres comunes
            nombres_comunes = re.findall(r'\b([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+)\b', parte)
            if nombres_comunes:
                nombre = limpiar_nombre(nombres_comunes[0])
        
        # Extraer localidades dentro de ESTE edicto
        localidades_edicto = []
        texto_lower = parte.lower()
        for loc in LOCALIDADES:
            if loc in texto_lower:
                localidades_edicto.append(ALIAS_LOCALIDAD.get(loc, loc.title()))
        
        # Extraer CUITs/DNIs
        cuits = set()
        for m in re.findall(r'\b\d{2}-\d{8}-\d\b', parte):
            cuits.add(m)
        for m in re.findall(r'\b(?:DNI|CUIT|CUIL)[\s:Nº°]*(\d{6,11})\b', parte, re.IGNORECASE):
            cuits.add(m)
        for m in re.findall(r'\b(\d{7,8})\b', parte):
            if not (1900 <= int(m) <= 2030):
                cuits.add(m)
        
        if localidades_edicto:
            resultados.append({
                'tipo': tipo,
                'nombre': nombre.upper() if nombre else "(sin nombre)",
                'cuits': ", ".join(sorted(cuits)) if cuits else None,
                'localidades': list(set(localidades_edicto))
            })
    
    return resultados

def guardar_edicto(localidad, edicto, seccion, fecha, boletin_numero, url_pdf, pagina, texto_completo) -> bool:
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
        "tipo_edicto": edicto['tipo'],
        "cuit_detectados": edicto['cuits'],
        "sujetos": edicto['nombre'] if edicto['nombre'] != "(sin nombre)" else None,
        "texto_completo": texto_completo,
        "url_pdf": url_pdf,
        "pagina": pagina,
    }
    supabase.table("edictos").insert(data).execute()
    log.info(f"✅ Guardado: pág {pagina} | {edicto['tipo']} | {localidad} | {edicto['nombre']}")
    return True

def eliminar_viejos(dias=60):
    limite = (datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")) - timedelta(days=dias)).date()
    supabase.table("edictos").delete().lt("fecha", limite.isoformat()).execute()

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
    url = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
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
                return numero, fecha_str, urls if urls else None
        return None, None, None
    except Exception as e:
        log.error(f"Error: {e}")
        return None, None, None

def obtener_ultimo_boletin():
    url = f"{BASE_URL}/ediciones-anteriores"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
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
        log.warning(f"Error: {e}")
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
        log.warning(f"Error: {e}")
        return []

def procesar_boletin(numero: str, fecha_str: str, urls_secciones: dict) -> int:
    if not urls_secciones:
        return 0
    try:
        fecha_boletin = datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except:
        fecha_boletin = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date()

    total = 0
    for seccion, url in urls_secciones.items():
        log.info(f"── {seccion}: {url}")
        pdf_bytes = descargar_pdf(url)
        if not pdf_bytes:
            continue
        paginas = extraer_paginas(pdf_bytes)
        if not paginas:
            continue
        
        inicio_transferencias = None
        if seccion == "OFICIAL":
            for pag, txt in paginas:
                if RE_INICIO_TRANSFERENCIAS.search(txt):
                    inicio_transferencias = pag
                    break
            if inicio_transferencias is None:
                log.warning("No se encontró TRANSFERENCIAS")
                continue
        
        for pagina, texto in paginas:
            if seccion == "OFICIAL" and inicio_transferencias and pagina < inicio_transferencias:
                continue
            
            # Extraer TODOS los edictos de esta página
            edictos = extraer_edictos_de_texto(texto)
            if not edictos:
                continue
            
            # Guardar cada combinación de edicto + localidad
            for edicto in edictos:
                for loc in edicto['localidades']:
                    if guardar_edicto(loc, edicto, seccion, fecha_boletin, numero, url, pagina, texto):
                        total += 1
    
    return total

def main():
    log.info("═══ SCRAPER FINAL (MÚLTIPLES EDICTOS) ═══")
    num = None
    if len(sys.argv) > 1:
        num = sys.argv[1]
    else:
        num = os.environ.get("BOLETIN_NUMERO")
    if num:
        n, f, u = obtener_boletin_por_numero(num)
    else:
        n, f, u = obtener_ultimo_boletin()
    if not n:
        log.error("No se encontró el boletín")
        sys.exit(0)
    log.info(f"Procesando boletín N° {n} - {f}")
    total = procesar_boletin(n, f, u)
    eliminar_viejos(60)
    log.info(f"═══ FIN | Nuevos guardados: {total} ═══")
    sys.exit(0)

if __name__ == "__main__":
    main()
