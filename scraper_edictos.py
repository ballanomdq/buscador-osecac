import requests
import re
from datetime import date
from supabase import create_client, Client
import os
from bs4 import BeautifulSoup

# --- Configuración ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

SECCIONES = {
    "OFICIAL": "https://boletinoficial.gba.gob.ar/secciones/14078/ver",
    "JUDICIAL": "https://boletinoficial.gba.gob.ar/secciones/14079/ver"
}

# --- Funciones auxiliares ---
def obtener_html(url):
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Error al obtener {url}: {e}")
        return None

def extraer_edictos(html, seccion):
    """Extrae bloques de texto que parecen edictos."""
    soup = BeautifulSoup(html, 'html.parser')
    texto = soup.get_text(separator="\n")
    # Dividir por títulos comunes en edictos
    # Patrón: "SUBASTAS ELECTRÓNICAS", "POR X DÍAS", "EDICTOS", "CONCURSOS", "QUIEBRAS"
    # El boletín suele tener cada edicto separado por estos encabezados
    # Usamos una regex para capturar desde un título hasta el siguiente título o fin
    patron = r"(SUBASTAS ELECTRÓNICAS|POR \d+ DÍAS|EDICTOS|CONCURSOS|QUIEBRAS).*?(?=SUBASTAS ELECTRÓNICAS|POR \d+ DÍAS|EDICTOS|CONCURSOS|QUIEBRAS|$)"
    matches = re.findall(patron, texto, re.DOTALL | re.IGNORECASE)
    return matches

def extraer_nombres_cuit(texto):
    """Extrae nombres y CUIT/DNI del texto."""
    nombres = []
    cuits = []
    # Patrón para CUIT/CUIL/DNI
    patron_cuit = r"\b(?:CUIT|CUIL|DNI)[\s:]*([0-9\-]+)\b"
    cuits = re.findall(patron_cuit, texto, re.IGNORECASE)
    # Patrón para nombres en mayúsculas (aproximado)
    # Buscamos líneas con mayúsculas y al menos 3 palabras
    lineas = texto.split('\n')
    for linea in lineas:
        if re.search(patron_cuit, linea, re.IGNORECASE):
            # Buscar texto anterior que pueda ser nombre
            # Simple: tomar todo lo que esté antes del primer DNI/CUIT en la línea
            partes = re.split(patron_cuit, linea, flags=re.IGNORECASE)
            if len(partes) > 1:
                posible = partes[0].strip()
                if len(posible) > 3 and any(c.isalpha() for c in posible):
                    nombres.append(posible)
    return list(set(nombres)), list(set(cuits))

def guardar_edicto(edicto, seccion, fecha, boletin_numero):
    # Buscar localidades
    localidades_encontradas = [loc for loc in LOCALIDADES if loc.lower() in edicto.lower()]
    if not localidades_encontradas:
        return
    nombres, cuits = extraer_nombres_cuit(edicto)
    # Tomamos la primera localidad como principal
    localidad_principal = localidades_encontradas[0]
    # Insertar en Supabase
    data = {
        "fecha": fecha.isoformat(),
        "boletin_numero": boletin_numero,
        "seccion": seccion,
        "localidad": localidad_principal,
        "nombres": ", ".join(nombres) if nombres else None,
        "cuit": ", ".join(cuits) if cuits else None,
        "texto_completo": edicto[:5000],  # limitar a 5000 caracteres
        "url_pdf": None  # podemos agregar enlace al PDF si se encuentra
    }
    # Evitar duplicados (simple: comparar texto)
    existing = supabase.table("edictos").select("id").eq("fecha", fecha.isoformat()).eq("texto_completo", edicto[:500]).execute()
    if not existing.data:
        supabase.table("edictos").insert(data).execute()
        print(f"Guardado edicto de {localidad_principal} en sección {seccion}")

def main():
    hoy = date.today()
    # Opcional: podríamos obtener el número de boletín del HTML
    boletin_numero = "desconocido"
    for seccion, url in SECCIONES.items():
        html = obtener_html(url)
        if html:
            # Intentar extraer número de boletín (ej: "Nº 30210")
            match = re.search(r"N[º°]?\s*(\d+)", html)
            if match:
                boletin_numero = match.group(1)
            edictos = extraer_edictos(html, seccion)
            for edicto in edictos:
                guardar_edicto(edicto, seccion, hoy, boletin_numero)

if __name__ == "__main__":
    main()
