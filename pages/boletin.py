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

# Estilos CSS para mejorar la apariencia de los libros
st.markdown("""
<style>
/* Fondo de los expanders de libros */
div[data-testid="stExpander"] details summary p {
    font-weight: bold;
    font-size: 1.1rem;
}
.judicial-libro summary {
    background-color: #e6f2ff;
    border-left: 8px solid #1e88e5;
    border-radius: 10px;
    padding: 0.5rem;
}
.oficial-libro summary {
    background-color: #f0f0f0;
    border-left: 8px solid #5f6368;
    border-radius: 10px;
    padding: 0.5rem;
}
.alerta-roja {
    background-color: #ffebee;
    border-left: 4px solid #d32f2f;
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

# --- Consultar datos desde Supabase ---
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

# ================== FUNCIONES MEJORADAS ==================
def extraer_nombre_cuit_quiebra(texto):
    """
    Extrae nombre y CUIT específicos de un edicto de quiebra buscando patrones.
    Prioriza: 'quiebra de NOMBRE', 'decretado la quiebra de NOMBRE', luego DNI/CUIT.
    Devuelve (nombre, cuit, es_quiebra_real)
    """
    texto_lower = texto.lower()
    es_quiebra = "quiebra" in texto_lower or "concurso" in texto_lower
    if not es_quiebra:
        return None, None, False
    
    # Buscar patrones de quiebra con nombre
    patron_quiebra = r"(?:quiebra|concurso)(?:\s+de|\s+del)?\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)(?:\s+\(|,|\.|con DNI|con CUIT|$)"
    match = re.search(patron_quiebra, texto, re.IGNORECASE)
    nombre = match.group(1).strip() if match else None
    
    # Si no se encontró con ese patrón, buscar palabras en mayúsculas largas (posible nombre)
    if not nombre:
        mayus = re.findall(r'\b[A-ZÁÉÍÓÚÑ]{4,}(?:\s+[A-ZÁÉÍÓÚÑ]{4,})+\b', texto)
        if mayus:
            nombre = mayus[0]
    
    # Buscar CUIT o DNI
    cuit_match = re.search(r'\b\d{2}-\d{8}-\d\b', texto)
    cuit = cuit_match.group(0) if cuit_match else None
    if not cuit:
        dni_match = re.search(r'\b(\d{7,8})\b', texto)
        cuit = dni_match.group(1) if dni_match else None
    
    return nombre, cuit, es_quiebra

def extraer_nombre_cuit_general(texto):
    """Extrae nombre y CUIT/DNI de texto genérico (sin quiebra)"""
    # Buscar nombres en mayúsculas (al menos dos palabras o una larga)
    mayus = re.findall(r'\b[A-ZÁÉÍÓÚÑ]{4,}(?:\s+[A-ZÁÉÍÓÚÑ]{4,})+\b', texto)
    nombre = mayus[0] if mayus else None
    cuit_match = re.search(r'\b\d{2}-\d{8}-\d\b', texto)
    cuit = cuit_match.group(0) if cuit_match else None
    if not cuit:
        dni_match = re.search(r'\b(\d{7,8})\b', texto)
        cuit = dni_match.group(1) if dni_match else None
    return nombre, cuit

def obtener_info_edicto(row):
    texto = row["texto_completo"]
    sujetos_db = row.get("sujetos")
    cuits_db = row.get("cuit_detectados")
    
    # Primero verificar si es quiebra real (con nombre cercano)
    nombre_q, cuit_q, es_quiebra = extraer_nombre_cuit_quiebra(texto)
    
    if es_quiebra:
        # Es una alerta roja legítima
        nombre = nombre_q if nombre_q else (sujetos_db.split(",")[0] if sujetos_db else None)
        cuit = cuit_q if cuit_q else (cuits_db.split(",")[0] if cuits_db else None)
        nivel = "roja"
        icono = "🚨"
        motivo = "QUIEBRA/CONCURSO"
        if not nombre:
            # Si no se pudo extraer nombre, intentar con el método general
            nombre, _ = extraer_nombre_cuit_general(texto)
        return {
            "quiebra": True,
            "nivel": nivel,
            "icono": icono,
            "motivo": motivo,
            "nombre_mostrar": nombre if nombre else (cuit if cuit else "Sin datos identificatorios"),
            "cuit": cuit
        }
    else:
        # No es quiebra, usar lógica normal con prioridad a sujetos_db
        if sujetos_db and len(sujetos_db.strip()) > 0:
            nombre = sujetos_db.split(",")[0].strip()
        else:
            nombre, _ = extraer_nombre_cuit_general(texto)
        if cuits_db and len(cuits_db.strip()) > 0:
            cuit = cuits_db.split(",")[0].strip()
        else:
            _, cuit = extraer_nombre_cuit_general(texto)
        if cuit:
            nivel = "amarilla"
            icono = "⚠️"
            motivo = "PRECAUCIÓN"
        else:
            nivel = "gris"
            icono = "⚪"
            motivo = "INFORMATIVO"
        return {
            "quiebra": False,
            "nivel": nivel,
            "icono": icono,
            "motivo": motivo,
            "nombre_mostrar": nombre if nombre else (cuit if cuit else "Sin datos identificatorios"),
            "cuit": cuit
        }

# ================== SEPARAR ALERTAS REALES DE QUIEBRA ==================
# Usamos la función mejorada para detectar quiebras verdaderas
alertas = []
otros = []
for _, row in df.iterrows():
    info = obtener_info_edicto(row)
    if info["quiebra"]:
        alertas.append((row, info))
    else:
        otros.append((row, info))

# --- Mostrar sección de alertas (si existe) ---
if alertas:
    st.subheader("🚨 ALERTAS DE QUIEBRAS Y CONCURSOS")
    st.caption("Estos edictos contienen palabras clave 'quiebra' o 'concurso' y se ha verificado que están asociadas a un nombre.")
    for row, info in alertas:
        titulo = f"{info['icono']} {info['motivo']} | {row['localidad']} | ({info['nombre_mostrar']})"
        if info['cuit']:
            titulo += f" - {info['cuit']}"
        with st.expander(titulo):
            texto_resaltado = row["texto_completo"]
            if info['nombre_mostrar'] and info['nombre_mostrar'] != "Sin datos identificatorios":
                texto_resaltado = re.sub(rf'\b{re.escape(info['nombre_mostrar'])}\b', f'**{info['nombre_mostrar']}**', texto_resaltado, flags=re.IGNORECASE)
            st.markdown(texto_resaltado)
            edicto_id = row["id"]
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("✅ Revisado", key=f"rev_alert_{edicto_id}"):
                    st.session_state[f"revisado_{edicto_id}"] = True
                    st.rerun()
            with col_b2:
                if st.button("🗑️ Eliminar", key=f"del_alert_{edicto_id}"):
                    confirm_key = f"confirm_alert_{edicto_id}"
                    if st.session_state.get(confirm_key, False):
                        supabase.table("edictos").delete().eq("id", edicto_id).execute()
                        st.success("Eliminado")
                        st.rerun()
                    else:
                        st.session_state[confirm_key] = True
                        st.warning("Hacé clic otra vez para confirmar eliminación.")
    st.divider()

# ================== ORGANIZAR POR BOLETINES (LIBROS) ==================
if not otros:
    st.info("No hay más edictos para mostrar.")
    st.stop()

df_resto = pd.DataFrame([row for row, _ in otros])
df_resto["boletin_clave"] = df_resto["boletin_numero"] + "_" + df_resto["fecha"].dt.strftime("%Y%m%d")
# Agrupar por boletín y sección para poder separar en columnas
boletines = df_resto.groupby(["boletin_clave", "fecha", "boletin_numero"])

boletines_list = []
for (clave, fecha, numero), grupo in boletines:
    boletines_list.append({
        "clave": clave,
        "fecha": fecha,
        "numero": numero,
        "grupo": grupo
    })
boletines_list.sort(key=lambda x: x["fecha"], reverse=True)

# --- Dividir en dos columnas: Judicial y Oficial ---
col_judicial, col_oficial = st.columns(2)

with col_judicial:
    st.markdown("## ⚖️ LIBRO JUDICIAL")
    for boletin in boletines_list:
        grupo = boletin["grupo"]
        judicial = grupo[grupo["seccion"] == "JUDICIAL"]
        if judicial.empty:
            continue
        fecha = boletin["fecha"]
        numero = boletin["numero"]
        with st.expander(f"📘 Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')}"):
            for _, row in judicial.iterrows():
                # Obtener info usando la función mejorada (ya que estos no son quiebras)
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

with col_oficial:
    st.markdown("## 📜 LIBRO OFICIAL")
    for boletin in boletines_list:
        grupo = boletin["grupo"]
        oficial = grupo[grupo["seccion"] == "OFICIAL"]
        if oficial.empty:
            continue
        fecha = boletin["fecha"]
        numero = boletin["numero"]
        with st.expander(f"📘 Boletín N° {numero} - {fecha.strftime('%d/%m/%Y')}"):
            for _, row in oficial.iterrows():
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

# Botón de recarga manual al final
if st.button("🔄 Recargar datos", key="recargar"):
    st.rerun()
