import streamlit as st
import os
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import pytz
import time
import re

st.set_page_config(page_title="Boletín Oficial - OSECAC", layout="wide")

# Estilos CSS para los libros
st.markdown("""
<style>
div[data-testid="stExpander"] details summary {
    background-color: #f8f9fa;
    border-radius: 8px;
    border-left: 6px solid #1e88e5;
    margin-bottom: 8px;
}
.judicial-libro {
    border-left: 6px solid #1e88e5 !important;
}
.oficial-libro {
    border-left: 6px solid #5f6368 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Fiscalización OSECAC - Boletín Oficial")

# --- Conexión a Supabase ---
def get_credentials():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return url, key
    except:
        pass
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        return url, key
    return None, None

SUPABASE_URL, SUPABASE_KEY = get_credentials()
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Faltan credenciales de Supabase. Revisá los secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Botón de forzar descarga ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Forzar descarga de Boletines del día", use_container_width=True):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta el token de GitHub (GH_TOKEN) en secrets.")
        else:
            repo = "ballanomdq/buscador-osecac"  # Ajustar
            url = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
            data = {"ref": "main"}
            with st.spinner("⏳ Procesando boletines... puede tardar unos segundos."):
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 204:
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    progress_bar.empty()
                    st.success("✅ Scraping iniciado. Los resultados aparecerán en unos minutos.")
                else:
                    st.error(f"Error al iniciar: {response.status_code}")

st.divider()

# --- Filtro de localidad (sidebar) ---
LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

with st.sidebar:
    st.header("Filtros")
    localidad_filtro = st.multiselect("Localidad", ["Todas"] + sorted(LOCALIDADES), default=["Todas"])

# --- Consultar datos ---
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
response = query.execute()
datos = response.data

if not datos:
    st.markdown(
        """
        <div style="text-align: center; margin-top: 50px;">
            <h3>📭 Bienvenido</h3>
            <p>Presione el botón superior para iniciar la fiscalización del día.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"])
if df["fecha"].dt.tz is None:
    df["fecha"] = df["fecha"].dt.tz_localize('UTC').dt.tz_convert('America/Argentina/Buenos_Aires')
else:
    df["fecha"] = df["fecha"].dt.tz_convert('America/Argentina/Buenos_Aires')

# --- Funciones mejoradas ---
def extraer_nombre_cuit_quiebra(texto):
    """
    Busca específicamente el patrón "quiebra de NOMBRE" o "decretado la quiebra de NOMBRE"
    y extrae el nombre y CUIT/DNI asociados. Si no, devuelve (None, None).
    """
    # Patrón para capturar nombre en mayúsculas después de "quiebra de"
    patron_quiebra = r"quiebra de\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)(?=,|\.|con domicilio|DNI|CUIT)"
    match = re.search(patron_quiebra, texto, re.IGNORECASE)
    if match:
        nombre = match.group(1).strip()
        # Buscar CUIT/DNI en los alrededores
        cuit_match = re.search(r'\b\d{2}-\d{8}-\d\b', texto)
        dni_match = re.search(r'\b(DNI|CUIT|CUIL)[\s:]*(\d{7,8})\b', texto, re.IGNORECASE)
        cuit = cuit_match.group(0) if cuit_match else (dni_match.group(2) if dni_match else None)
        return nombre, cuit
    return None, None

def extraer_nombre_general(texto):
    """
    Busca palabras en mayúsculas (posibles nombres) sin contexto de quiebra.
    """
    mayusculas = re.findall(r'\b[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ]+\b', texto)
    if not mayusculas:
        mayusculas = re.findall(r'\b[A-ZÁÉÍÓÚÑ]{5,}\b', texto)
    return mayusculas[0] if mayusculas else None

def obtener_info_edicto(row):
    texto = row["texto_completo"]
    # Datos de BD
    sujetos_db = row.get("sujetos")
    cuits_db = row.get("cuit_detectados")
    
    # Detectar si es quiebra (y validar cercanía)
    es_quiebra = False
    nombre_quiebra = None
    cuit_quiebra = None
    if "quiebra" in texto.lower() or "concurso" in texto.lower():
        nombre_quiebra, cuit_quiebra = extraer_nombre_cuit_quiebra(texto)
        if nombre_quiebra:
            es_quiebra = True  # Solo si el nombre está cerca de la palabra
    
    # Si no es quiebra o no se encontró nombre, usar métodos generales
    if not es_quiebra:
        # Usar sujetos de BD si existe
        if sujetos_db and len(sujetos_db.strip()) > 0:
            nombre = sujetos_db.split(",")[0].strip()
        else:
            nombre = extraer_nombre_general(texto)
        if cuits_db and len(cuits_db.strip()) > 0:
            cuit = cuits_db.split(",")[0].strip()
        else:
            cuit_match = re.search(r'\b\d{2}-\d{8}-\d\b', texto)
            cuit = cuit_match.group(0) if cuit_match else None
    else:
        nombre = nombre_quiebra
        cuit = cuit_quiebra
    
    # Determinar nivel e ícono
    if es_quiebra:
        nivel = "roja"
        icono = "🚨"
        motivo = "QUIEBRA/CONCURSO"
    elif cuit:
        nivel = "amarilla"
        icono = "⚠️"
        motivo = "PRECAUCIÓN"
    else:
        nivel = "gris"
        icono = "⚪"
        motivo = "INFORMATIVO"
    
    nombre_mostrar = nombre if nombre else (cuit if cuit else "Sin datos identificatorios")
    return {
        "quiebra": es_quiebra,
        "nivel": nivel,
        "icono": icono,
        "motivo": motivo,
        "nombre_mostrar": nombre_mostrar,
        "cuit": cuit
    }

# --- Agrupar por boletín y sección ---
df["boletin_clave"] = df["boletin_numero"] + "_" + df["fecha"].dt.strftime("%Y%m%d")
boletines = df.groupby(["boletin_clave", "fecha", "boletin_numero"])

boletines_list = []
for (clave, fecha, numero), grupo in boletines:
    # Dividir por sección
    grupo_judicial = grupo[grupo["seccion"] == "JUDICIAL"]
    grupo_oficial = grupo[grupo["seccion"] == "OFICIAL"]
    # Ordenar cada grupo por prioridad: quiebra > con cuit > resto
    def prioridad(row):
        texto = row["texto_completo"]
        if "quiebra" in texto.lower() or "concurso" in texto.lower():
            return 0
        elif row.get("cuit_detectados"):
            return 1
        else:
            return 2
    if not grupo_judicial.empty:
        grupo_judicial = grupo_judicial.sort_values(by="texto_completo", key=lambda x: x.apply(prioridad))
    if not grupo_oficial.empty:
        grupo_oficial = grupo_oficial.sort_values(by="texto_completo", key=lambda x: x.apply(prioridad))
    boletines_list.append({
        "fecha": fecha,
        "numero": numero,
        "judicial": grupo_judicial,
        "oficial": grupo_oficial
    })
# Ordenar boletines por fecha descendente
boletines_list.sort(key=lambda x: x["fecha"], reverse=True)

# --- Mostrar dos columnas: Judicial y Oficial ---
col_judicial, col_oficial = st.columns(2)

with col_judicial:
    st.markdown("## ⚖️ LIBROS JUDICIALES")
    for boletin in boletines_list:
        if not boletin["judicial"].empty:
            fecha = boletin["fecha"]
            numero = boletin["numero"]
            with st.expander(f"📘 Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')}"):
                # Mostrar edictos ordenados por prioridad (ya lo están)
                for _, row in boletin["judicial"].iterrows():
                    info = obtener_info_edicto(row)
                    titulo = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
                    if info['cuit']:
                        titulo += f" - {info['cuit']}"
                    revisado_key = f"revisado_{row['id']}"
                    if revisado_key in st.session_state and st.session_state[revisado_key]:
                        titulo = "🟢 " + titulo
                    with st.expander(titulo):
                        # Resaltar nombre en el texto
                        texto_resaltado = row["texto_completo"]
                        if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos identificatorios":
                            texto_resaltado = re.sub(rf'\b{re.escape(info['nombre_mostrar'])}\b', f'**{info['nombre_mostrar']}**', texto_resaltado, flags=re.IGNORECASE)
                        st.markdown(texto_resaltado)
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("✅ Revisado", key=f"rev_{row['id']}"):
                                st.session_state[revisado_key] = True
                                st.rerun()
                        with col_b2:
                            if st.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                                confirm_key = f"confirm_{row['id']}"
                                if st.session_state.get(confirm_key, False):
                                    supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                    st.success("Eliminado")
                                    st.rerun()
                                else:
                                    st.session_state[confirm_key] = True
                                    st.warning("Hacé clic otra vez para confirmar eliminación.")

with col_oficial:
    st.markdown("## 📜 LIBROS OFICIALES")
    for boletin in boletines_list:
        if not boletin["oficial"].empty:
            fecha = boletin["fecha"]
            numero = boletin["numero"]
            with st.expander(f"📘 Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')}"):
                for _, row in boletin["oficial"].iterrows():
                    info = obtener_info_edicto(row)
                    titulo = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
                    if info['cuit']:
                        titulo += f" - {info['cuit']}"
                    revisado_key = f"revisado_{row['id']}"
                    if revisado_key in st.session_state and st.session_state[revisado_key]:
                        titulo = "🟢 " + titulo
                    with st.expander(titulo):
                        texto_resaltado = row["texto_completo"]
                        if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos identificatorios":
                            texto_resaltado = re.sub(rf'\b{re.escape(info['nombre_mostrar'])}\b', f'**{info['nombre_mostrar']}**', texto_resaltado, flags=re.IGNORECASE)
                        st.markdown(texto_resaltado)
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("✅ Revisado", key=f"rev_{row['id']}"):
                                st.session_state[revisado_key] = True
                                st.rerun()
                        with col_b2:
                            if st.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                                confirm_key = f"confirm_{row['id']}"
                                if st.session_state.get(confirm_key, False):
                                    supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                    st.success("Eliminado")
                                    st.rerun()
                                else:
                                    st.session_state[confirm_key] = True
                                    st.warning("Hacé clic otra vez para confirmar eliminación.")

if st.button("🔄 Recargar datos", key="recargar"):
    st.rerun()
