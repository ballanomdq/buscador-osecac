import requests
import re
from datetime import date
from supabase import create_client, Client
import os
import sys
from bs4 import BeautifulSoup

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

BASE_URL = "https://boletinoficial.gba.gob.ar"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Caracteres a capturar antes y después de cada mención de localidad
CONTEXTO_CHARS = 1500

def obtener_html(url, timeout=30):
    try:
        print(f"  → GET {url}")
        resp = requests.get(url, timeout=timeout, headers=HEADERS)
        print(f"  ← Status: {resp.status_code} ({len(resp.text):,} chars)")
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def extraer_texto(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(separator="\n")

def extraer_contexto_por_localidad(texto):
    """
    Busca cada localidad en el texto completo y extrae un bloque
    de contexto alrededor de cada mención. Devuelve lista de (localidad, fragmento).
    """
    resultados = []
    texto_lower = texto.lower()

    for localidad in LOCALIDADES:
        pos = 0
        localidad_lower = localidad.lower()
        while True:
            idx = texto_lower.find(localidad_lower, pos)
            if idx == -1:
                break
            inicio = max(0, idx - CONTEXTO_CHARS)
            fin = min(len(texto), idx + CONTEXTO_CHARS)
            fragmento = texto[inicio:fin].strip()
            resultados.append((localidad, fragmento))
            pos = idx + len(localidad)

    print(f"  🔍 Menciones de localidades encontradas: {len(resultados)}")
    return resultados

def extraer_nombres_cuit(texto):
    patron_cuit = r"(?:CUIT|CUIL|DNI)[\s:\-]*(\d[\d\-]{6,})"
    cuits = list(set(re.findall(patron_cuit, texto, re.IGNORECASE)))

    nombres = []
    lineas = texto.split('\n')
    for i, linea in enumerate(lineas):
        if re.search(patron_cuit, linea, re.IGNORECASE):
            partes = re.split(r'(?:CUIT|CUIL|DNI)', linea, flags=re.IGNORECASE)
            candidato = partes[0].strip()
            if len(candidato) > 3 and any(c.isalpha() for c in candidato):
                nombres.append(candidato)
            if i > 0:
                anterior = lineas[i-1].strip()
                if len(anterior) > 3 and any(c.isalpha() for c in anterior):
                    nombres.append(anterior)

    return list(set(nombres))[:5], cuits

def guardar_edicto(localidad, texto, seccion, fecha, boletin_numero, url_fuente):
    nombres, cuits = extraer_nombres_cuit(texto)
    clave = texto[:300]

    try:
        existing = supabase.table("edictos").select("id").eq("fecha", fecha.isoformat()).eq("texto_completo", clave).execute()
        if existing.data:
            return False  # duplicado
    except Exception as e:
        print(f"  ⚠️ Error verificando duplicado: {e}")

    data = {
        "fecha": fecha.isoformat(),
        "boletin_numero": str(boletin_numero),
        "seccion": seccion,
        "localidad": localidad,
        "nombres": ", ".join(nombres) if nombres else None,
        "cuit": ", ".join(cuits) if cuits else None,
        "texto_completo": texto[:5000],
        "url_pdf": url_fuente
    }

    try:
        supabase.table("edictos").insert(data).execute()
        print(f"  ✅ Guardado: {localidad} | nombres: {nombres[:1]}")
        return True
    except Exception as e:
        print(f"  ❌ Error al guardar: {e}")
        return False

def main():
    hoy = date.today()
    print(f"\n{'='*50}")
    print(f"🗞️  Scraping Boletín Oficial - {hoy.strftime('%d/%m/%Y')}")
    print(f"{'='*50}\n")

    total_guardados = 0

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
        print(f"\n📂 Sección: {nombre_seccion}")
        html = None
        url_usada = None

        for url in urls:
            html = obtener_html(url)
            if html and len(html) > 500:
                url_usada = url
                break
            print(f"  ⚠️ Sin contenido útil en: {url}")

        if not html:
            print(f"  ❌ No se pudo obtener contenido para {nombre_seccion}")
            continue

        texto = extraer_texto(html)
        print(f"  📄 Texto extraído: {len(texto):,} caracteres")

        boletin_numero = "desconocido"
        match = re.search(r"[Nn][º°ú]?\s*(\d{4,6})", html)
        if match:
            boletin_numero = match.group(1)
            print(f"  📋 Boletín N°: {boletin_numero}")

        menciones = extraer_contexto_por_localidad(texto)

        guardados = 0
        for localidad, fragmento in menciones:
            ok = guardar_edicto(localidad, fragmento, nombre_seccion, hoy, boletin_numero, url_usada)
            if ok:
                guardados += 1

        print(f"  💾 Guardados en {nombre_seccion}: {guardados}")
        total_guardados += guardados

    print(f"\n{'='*50}")
    print(f"✅ Total guardados hoy: {total_guardados}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
