import requests
import re
import io
from datetime import datetime, timedelta
import pytz
from supabase import create_client
import os
import sys
import pdfplumber

# --- Configuración ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Faltan SUPABASE_URL y/o SUPABASE_KEY")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Supabase conectado")

# --- Zona horaria Argentina ---
AR_TZ = pytz.timezone('America/Argentina/Buenos_Aires')

# --- Lista de localidades ---
LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

SECCIONES = {
    "JUDICIAL": "https://boletinoficial.gba.gob.ar/secciones/14079/ver",
    "OFICIAL":  "https://boletinoficial.gba.gob.ar/secciones/14078/ver",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

CONTEXTO_CHARS = 1500  # Podés aumentarlo si querés más contexto


def descargar_pdf(url):
    try:
        print(f"  → Descargando: {url}")
        resp = requests.get(url, timeout=60, headers=HEADERS)
        print(f"  ← Status: {resp.status_code} | Content-Type: {resp.headers.get('Content-Type','?')}")
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"  ❌ Error descargando: {e}")
        return None


def extraer_texto_pdf(pdf_bytes):
    texto_total = []
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            print(f"  📄 PDF con {len(pdf.pages)} páginas")
            for page in pdf.pages:
                texto = page.extract_text()
                if texto:
                    texto_total.append(texto)
        texto_completo = "\n".join(texto_total)
        print(f"  📝 Texto extraído: {len(texto_completo):,} caracteres")
        return texto_completo
    except Exception as e:
        print(f"  ❌ Error leyendo PDF: {e}")
        return ""


def buscar_localidades(texto):
    resultados = []
    texto_lower = texto.lower()
    for localidad in LOCALIDADES:
        pos = 0
        while True:
            idx = texto_lower.find(localidad.lower(), pos)
            if idx == -1:
                break
            inicio = max(0, idx - CONTEXTO_CHARS)
            fin = min(len(texto), idx + CONTEXTO_CHARS)
            fragmento = texto[inicio:fin].strip()
            resultados.append((localidad, fragmento))
            pos = idx + len(localidad)
    print(f"  🔍 Menciones encontradas: {len(resultados)}")
    return resultados


def extraer_cuits_dnis(texto):
    """
    Busca CUIT (xx-xxxxxxxx-x) y DNI (hasta 8 dígitos) en el texto.
    Devuelve lista de strings únicos.
    """
    patron_cuit = r"\b\d{2}-\d{8}-\d\b"          # Formato xx-xxxxxxxx-x
    patron_dni = r"\b(?:DNI|CUIT|CUIL)[\s:]*(\d{6,8})\b"  # DNI junto a la palabra
    # También buscar solo números largos que parezcan DNI (7-8 dígitos)
    patron_solo_numeros = r"\b(\d{7,8})\b"

    encontrados = set()
    # Buscar CUIT formales
    for match in re.findall(patron_cuit, texto):
        encontrados.add(match)
    # Buscar DNI con palabra clave
    for match in re.findall(patron_dni, texto, re.IGNORECASE):
        encontrados.add(match)
    # Buscar números aislados de 7 u 8 dígitos (evitar confundir con años)
    for match in re.findall(patron_solo_numeros, texto):
        if len(match) >= 7 and not (1900 <= int(match[:4]) <= 2030):  # evita años
            encontrados.add(match)

    return sorted(encontrados)


def extraer_mayusculas(texto):
    """
    Encuentra palabras o secuencias de 2 o más palabras en mayúsculas
    (razones sociales, apellidos, etc.)
    """
    patron_mayus = r"\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+\b"
    matches = re.findall(patron_mayus, texto)
    # Filtrar palabras muy cortas o repetidas
    mayusculas = []
    for m in matches:
        # Si la palabra tiene al menos 3 letras y no es solo números
        if len(m.strip()) >= 3 and not m.isdigit():
            mayusculas.append(m.strip())
    return list(set(mayusculas))


def guardar_edicto(localidad, texto, seccion, fecha, boletin_numero, url):
    # Extraer CUIT/DNI
    cuits = extraer_cuits_dnis(texto)
    # Extraer palabras en mayúsculas (sujetos)
    sujetos = extraer_mayusculas(texto)

    clave_dedup = texto[:400]

    try:
        existing = supabase.table("edictos").select("id")\
            .eq("fecha", fecha.isoformat())\
            .eq("texto_completo", clave_dedup)\
            .execute()
        if existing.data:
            return False
    except Exception as e:
        print(f"  ⚠️ Error verificando duplicado: {e}")

    data = {
        "fecha": fecha.isoformat(),
        "boletin_numero": str(boletin_numero),
        "seccion": seccion,
        "localidad": localidad,
        "cuit_detectados": ", ".join(cuits) if cuits else None,
        "sujetos": ", ".join(sujetos[:5]) if sujetos else None,   # solo primeros 5 para no saturar
        "texto_completo": texto[:5000],
        "url_pdf": url,
    }

    try:
        supabase.table("edictos").insert(data).execute()
        print(f"  ✅ Guardado: {localidad} | CUITs: {cuits[:2]}")
        return True
    except Exception as e:
        print(f"  ❌ Error insertando: {e}")
        return False


def eliminar_viejos(dias=60):
    fecha_limite = datetime.now(AR_TZ).date() - timedelta(days=dias)
    try:
        result = supabase.table("edictos").delete().lt("fecha", fecha_limite.isoformat()).execute()
        print(f"🗑️ Eliminados {len(result.data)} registros anteriores a {fecha_limite}")
    except Exception as e:
        print(f"⚠️ Error al eliminar registros viejos: {e}")


def main():
    # Fecha actual en Argentina
    hoy = datetime.now(AR_TZ).date()
    print(f"\n{'='*55}")
    print(f"🗞️  Boletín Oficial PBA — {hoy.strftime('%d/%m/%Y')} (hora Argentina)")
    print(f"{'='*55}\n")

    total = 0

    for nombre_seccion, url in SECCIONES.items():
        print(f"\n📂 Sección: {nombre_seccion}")

        pdf_bytes = descargar_pdf(url)
        if not pdf_bytes:
            print(f"  ❌ No se pudo descargar")
            continue

        texto = extraer_texto_pdf(pdf_bytes)
        if not texto:
            print(f"  ❌ No se pudo extraer texto")
            continue

        boletin_numero = "desconocido"
        match = re.search(r"[Nn][º°]?\s*(\d{4,6})", texto)
        if match:
            boletin_numero = match.group(1)
            print(f"  📋 Boletín N°: {boletin_numero}")

        menciones = buscar_localidades(texto)
        guardados = 0
        for localidad, fragmento in menciones:
            ok = guardar_edicto(localidad, fragmento, nombre_seccion, hoy, boletin_numero, url)
            if ok:
                guardados += 1

        print(f"  💾 Guardados en {nombre_seccion}: {guardados}")
        total += guardados

    eliminar_viejos(60)

    print(f"\n{'='*55}")
    print(f"✅ Total guardados hoy: {total}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
