import requests
import re
from datetime import date
from supabase import create_client, Client
import os
from bs4 import BeautifulSoup
import sys

# --- Configuración ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Faltan las variables de entorno SUPABASE_URL y/o SUPABASE_KEY")
    sys.exit(1)

print(f"✅ Conectando a Supabase: {SUPABASE_URL[:30]}...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Supabase conectado")

LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

# URL base del Boletín Oficial de la Provincia de Buenos Aires
BASE_URL = "https://boletinoficial.gba.gob.ar"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def obtener_html(url, timeout=30):
    try:
        print(f"  → GET {url}")
        resp = requests.get(url, timeout=timeout, headers=HEADERS)
        print(f"  ← Status: {resp.status_code}")
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ HTTP error {e.response.status_code} para {url}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ Error de conexión para {url}: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout para {url}")
        return None
    except Exception as e:
        print(f"  ❌ Error inesperado para {url}: {e}")
        return None

def obtener_url_boletin_hoy():
    """Intenta obtener la URL del boletín de hoy desde la página principal."""
    urls_a_probar = [
        f"{BASE_URL}/",
        f"{BASE_URL}/boletin/ver",
        f"{BASE_URL}/home",
    ]
    for url in urls_a_probar:
        html = obtener_html(url)
        if html:
            return html, url
    return None, None

def extraer_secciones_del_boletin(html_principal, url_base):
    """Busca enlaces a las secciones del boletín del día."""
    soup = BeautifulSoup(html_principal, 'html.parser')
    secciones = {}

    # Buscar enlaces que contengan "secciones" o términos clave
    for a in soup.find_all('a', href=True):
        href = a['href']
        texto = a.get_text(strip=True).upper()
        if 'seccion' in href.lower() or any(k in texto for k in ['OFICIAL', 'JUDICIAL', 'EDICTO']):
            url_completa = href if href.startswith('http') else BASE_URL + href
            secciones[texto[:30]] = url_completa

    print(f"  Secciones encontradas: {list(secciones.keys())}")
    return secciones

def extraer_bloques_edictos(html):
    """Extrae bloques de texto individuales que representan edictos."""
    soup = BeautifulSoup(html, 'html.parser')

    # Estrategia 1: buscar divs o párrafos con contenido de edicto
    bloques = []

    # Buscar contenedores típicos de edictos
    for selector in ['div.aviso', 'div.edicto', 'article', 'div.publicacion', 'div.item']:
        elementos = soup.select(selector)
        if elementos:
            print(f"  Encontrados {len(elementos)} bloques con selector '{selector}'")
            for el in elementos:
                texto = el.get_text(separator="\n", strip=True)
                if len(texto) > 50:
                    bloques.append(texto)
            if bloques:
                return bloques

    # Estrategia 2: usar el texto completo y dividir por patrones comunes
    texto_completo = soup.get_text(separator="\n")
    print(f"  Texto total extraído: {len(texto_completo)} caracteres")

    # Dividir por separadores típicos de edictos bonaerenses
    patron_separador = r"\n(?=(?:POR \d+ D[ÍI]AS?|EDICTO|SUCESORIO|TRANSFERENCIA|CONCURSO|QUIEBRA|SUBASTA))"
    partes = re.split(patron_separador, texto_completo, flags=re.IGNORECASE)

    for parte in partes:
        parte = parte.strip()
        if len(parte) > 100:  # descartar bloques muy cortos
            bloques.append(parte)

    print(f"  Bloques extraídos por regex: {len(bloques)}")
    return bloques

def extraer_nombres_cuit(texto):
    """Extrae nombres y CUIT/DNI del texto."""
    # Buscar CUIT/CUIL/DNI
    patron_cuit = r"(?:CUIT|CUIL|DNI)[\s:\-]*(\d[\d\-]{6,})"
    cuits = re.findall(patron_cuit, texto, re.IGNORECASE)
    cuits = list(set(c.strip('-').strip() for c in cuits if len(c) >= 7))

    # Buscar nombres (texto en mayúsculas antes de CUIT/DNI)
    nombres = []
    lineas = texto.split('\n')
    for i, linea in enumerate(lineas):
        if re.search(patron_cuit, linea, re.IGNORECASE):
            # Tomar la línea y la anterior como posibles nombres
            partes = re.split(r'(?:CUIT|CUIL|DNI)', linea, flags=re.IGNORECASE)
            if partes[0].strip() and len(partes[0].strip()) > 3:
                nombres.append(partes[0].strip())
            if i > 0 and lineas[i-1].strip() and len(lineas[i-1].strip()) > 3:
                nombres.append(lineas[i-1].strip())

    nombres = list(set(n for n in nombres if any(c.isalpha() for c in n)))[:5]
    return nombres, cuits

def guardar_edicto(texto, seccion, fecha, boletin_numero, url_fuente):
    """Guarda un edicto en Supabase si contiene localidades de interés."""
    # Verificar si contiene alguna localidad de interés
    localidades_encontradas = [
        loc for loc in LOCALIDADES
        if loc.lower() in texto.lower()
    ]
    if not localidades_encontradas:
        return False

    nombres, cuits = extraer_nombres_cuit(texto)
    localidad_principal = localidades_encontradas[0]

    # Verificar duplicado por fecha + primeros 500 chars
    clave_texto = texto[:500]
    try:
        existing = supabase.table("edictos").select("id").eq("fecha", fecha.isoformat()).eq("texto_completo", clave_texto).execute()
        if existing.data:
            print(f"  ⚠️ Edicto duplicado, omitiendo ({localidad_principal})")
            return False
    except Exception as e:
        print(f"  ⚠️ Error al verificar duplicado: {e}")

    data = {
        "fecha": fecha.isoformat(),
        "boletin_numero": str(boletin_numero),
        "seccion": seccion,
        "localidad": localidad_principal,
        "nombres": ", ".join(nombres) if nombres else None,
        "cuit": ", ".join(cuits) if cuits else None,
        "texto_completo": texto[:5000],
        "url_pdf": url_fuente
    }

    try:
        supabase.table("edictos").insert(data).execute()
        print(f"  ✅ Guardado: {localidad_principal} | {nombres[:1]} | sección {seccion}")
        return True
    except Exception as e:
        print(f"  ❌ Error al guardar en Supabase: {e}")
        return False

def main():
    hoy = date.today()
    print(f"\n{'='*50}")
    print(f"🗞️  Scraping Boletín Oficial - {hoy.strftime('%d/%m/%Y')}")
    print(f"{'='*50}\n")

    total_guardados = 0

    # URLs de las secciones a scrapear
    secciones_urls = {
        "JUDICIAL": [
            f"{BASE_URL}/secciones/14079/ver",
            f"{BASE_URL}/seccion/judicial",
        ],
        "OFICIAL": [
            f"{BASE_URL}/secciones/14078/ver",
            f"{BASE_URL}/seccion/oficial",
        ]
    }

    for nombre_seccion, urls in secciones_urls.items():
        print(f"\n📂 Procesando sección: {nombre_seccion}")
        html = None
        url_usada = None

        for url in urls:
            html = obtener_html(url)
            if html and len(html) > 500:
                url_usada = url
                print(f"  ✅ HTML obtenido de: {url} ({len(html)} chars)")
                break
            else:
                print(f"  ⚠️ Sin contenido útil en: {url}")

        if not html:
            print(f"  ❌ No se pudo obtener contenido para sección {nombre_seccion}")
            continue

        # Extraer número de boletín del HTML
        boletin_numero = "desconocido"
        match = re.search(r"[Nn][º°ú]?\s*(\d{4,6})", html)
        if match:
            boletin_numero = match.group(1)
            print(f"  📋 Número de boletín detectado: {boletin_numero}")

        # Extraer y procesar edictos
        bloques = extraer_bloques_edictos(html)
        print(f"  📄 Total de bloques a analizar: {len(bloques)}")

        guardados_seccion = 0
        for i, bloque in enumerate(bloques):
            guardado = guardar_edicto(bloque, nombre_seccion, hoy, boletin_numero, url_usada)
            if guardado:
                guardados_seccion += 1

        print(f"  💾 Edictos guardados en {nombre_seccion}: {guardados_seccion}")
        total_guardados += guardados_seccion

    print(f"\n{'='*50}")
    print(f"✅ Scraping completado. Total guardados: {total_guardados}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
