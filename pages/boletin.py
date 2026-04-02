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

# Estilos CSS para los libros (colores de acento)
st.markdown("""
<style>
/* Libro Judicial (azul) */
div[data-testid="stExpander"] details summary p:has(> .judicial) {
    background-color: #e6f2ff;
    border-left: 6px solid #1e88e5;
    padding: 0.5rem 1rem;
    border-radius: 8px;
}
/* Libro Oficial (gris) */
div[data-testid="stExpander"] details summary p:has(> .oficial) {
    background-color: #f0f0f0;
    border-left: 6px solid #5f6368;
    padding: 0.5rem 1rem;
    border-radius: 8px;
}
/* Edicto alerta roja */
.alerta-roja {
    background-color: #ffebee;
    border-left: 6px solid #d32f2f;
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

# --- Botón de forzar descarga (barra de progreso) ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Forzar descarga de Boletines del día", use_container_width=True):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta el token de GitHub (GH_TOKEN) en secrets.")
        else:
            repo = "ballanomdq/buscador-osecac"  # Ajustar si es necesario
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

# Agrupar por boletín (fecha + número) y sección
df["boletin_clave"] = df["boletin_numero"] + "_" + df["fecha"].dt.strftime("%Y%m%d")
boletines = df.groupby(["boletin_clave", "fecha", "boletin_numero"])

# Ordenar boletines por fecha descendente
boletines_list = []
for (clave, fecha, numero), grupo in boletines:
    boletines_list.append({
        "clave": clave,
        "fecha": fecha,
        "numero": numero,
        "grupo": grupo
    })
boletines_list.sort(key=lambda x: x["fecha"], reverse=True)

# --- Función para determinar el motivo y nivel de alerta de un edicto ---
def analizar_edicto(texto, cuits, sujetos):
    texto_lower = texto.lower()
    if "quiebra" in texto_lower or "concurso" in texto_lower:
        return "🚨", "QUIEBRA/CONCURSO", "roja"
    elif cuits:
        return "⚠️", "PRECAUCIÓN", "amarilla"
    else:
        return "⚪", "INFORMATIVO", "gris"

# --- Función para extraer nombre representativo (prioridad: sujetos en mayúsculas, luego CUIT) ---
def obtener_nombre_cuit(cuits, sujetos):
    if sujetos:
        # Tomar el primer sujeto (suele ser el más relevante)
        return sujetos.split(",")[0].strip()
    elif cuits:
        return cuits.split(",")[0].strip()
    else:
        return "Sin datos identificatorios"

# --- Mostrar libros por cada boletín ---
for boletin in boletines_list:
    fecha = boletin["fecha"]
    numero = boletin["numero"]
    grupo = boletin["grupo"]
    
    # Dividir el grupo por sección
    grupo_judicial = grupo[grupo["seccion"] == "JUDICIAL"]
    grupo_oficial = grupo[grupo["seccion"] == "OFICIAL"]
    
    # Mostrar Libro Judicial si tiene edictos
    if not grupo_judicial.empty:
        with st.expander(f"⚖️ LIBRO JUDICIAL | N° {numero} | {fecha.strftime('%d/%m/%Y')}"):
            # Iterar sobre cada edicto dentro de esta sección
            for _, row in grupo_judicial.iterrows():
                texto = row["texto_completo"]
                cuits = row.get("cuit_detectados")
                sujetos = row.get("sujetos")
                
                # Determinar alerta y título
                icono, motivo, nivel = analizar_edicto(texto, cuits, sujetos)
                localidad = row["localidad"]
                nombre_cuit = obtener_nombre_cuit(cuits, sujetos)
                
                # Título del edicto (expander interno)
                titulo = f"{icono} {motivo} | {localidad} | ({nombre_cuit})"
                
                # Clave única para session_state (revisado/eliminado)
                edicto_id = row["id"]
                revisado_key = f"revisado_{edicto_id}"
                if revisado_key not in st.session_state:
                    st.session_state[revisado_key] = False
                
                # Si está revisado, cambiar el icono en el título
                if st.session_state[revisado_key]:
                    titulo = "🟢 " + titulo
                
                with st.expander(titulo):
                    # Resaltar nombres (suponemos que los sujetos están en mayúsculas)
                    texto_resaltado = texto
                    if sujetos:
                        for s in sujetos.split(","):
                            s_limpio = s.strip()
                            if s_limpio:
                                texto_resaltado = re.sub(rf'\b{re.escape(s_limpio)}\b', f'**{s_limpio}**', texto_resaltado, flags=re.IGNORECASE)
                    st.markdown(texto_resaltado)
                    
                    # Botones de gestión
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("✅ Revisado", key=f"btn_rev_{edicto_id}"):
                            st.session_state[revisado_key] = True
                            st.rerun()
                    with col_b2:
                        if st.button("🗑️ Eliminar", key=f"btn_del_{edicto_id}"):
                            # Confirmación en dos pasos
                            confirm_key = f"confirm_{edicto_id}"
                            if st.session_state.get(confirm_key, False):
                                supabase.table("edictos").delete().eq("id", edicto_id).execute()
                                st.success("Eliminado")
                                st.rerun()
                            else:
                                st.session_state[confirm_key] = True
                                st.warning("Hacé clic otra vez para confirmar eliminación.")
    
    # Mostrar Libro Oficial si tiene edictos
    if not grupo_oficial.empty:
        with st.expander(f"📜 LIBRO OFICIAL | N° {numero} | {fecha.strftime('%d/%m/%Y')}"):
            for _, row in grupo_oficial.iterrows():
                texto = row["texto_completo"]
                cuits = row.get("cuit_detectados")
                sujetos = row.get("sujetos")
                
                icono, motivo, nivel = analizar_edicto(texto, cuits, sujetos)
                localidad = row["localidad"]
                nombre_cuit = obtener_nombre_cuit(cuits, sujetos)
                titulo = f"{icono} {motivo} | {localidad} | ({nombre_cuit})"
                
                edicto_id = row["id"]
                revisado_key = f"revisado_{edicto_id}"
                if revisado_key not in st.session_state:
                    st.session_state[revisado_key] = False
                if st.session_state[revisado_key]:
                    titulo = "🟢 " + titulo
                
                with st.expander(titulo):
                    # Resaltar nombres
                    texto_resaltado = texto
                    if sujetos:
                        for s in sujetos.split(","):
                            s_limpio = s.strip()
                            if s_limpio:
                                texto_resaltado = re.sub(rf'\b{re.escape(s_limpio)}\b', f'**{s_limpio}**', texto_resaltado, flags=re.IGNORECASE)
                    st.markdown(texto_resaltado)
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("✅ Revisado", key=f"btn_rev_{edicto_id}"):
                            st.session_state[revisado_key] = True
                            st.rerun()
                    with col_b2:
                        if st.button("🗑️ Eliminar", key=f"btn_del_{edicto_id}"):
                            confirm_key = f"confirm_{edicto_id}"
                            if st.session_state.get(confirm_key, False):
                                supabase.table("edictos").delete().eq("id", edicto_id).execute()
                                st.success("Eliminado")
                                st.rerun()
                            else:
                                st.session_state[confirm_key] = True
                                st.warning("Hacé clic otra vez para confirmar eliminación.")

# Botón de recarga manual
if st.button("🔄 Recargar datos", key="recargar"):
    st.rerun()
