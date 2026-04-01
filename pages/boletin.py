import streamlit as st
import os
import requests
from supabase import create_client, Client
import pandas as pd

st.set_page_config(page_title="Boletín Oficial", layout="wide")

st.title("📰 Boletín Oficial - Fiscalización")

# --- Lista de localidades (copiala de tu lista) ---
LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

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
    st.error("❌ Faltan las credenciales de Supabase. Revisá los secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Botón para forzar scraping ---
st.subheader("🔍 Acciones")
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Forzar búsqueda ahora", use_container_width=True):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("❌ Falta el token de GitHub (GH_TOKEN) en secrets.")
        else:
            repo = "ballanomdq/buscador-osecac"   # CAMBIÁ SI TU REPO ES OTRO
            url = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {"ref": "main"}
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 204:
                st.success("✅ Scraping iniciado. Los nuevos resultados aparecerán en unos minutos.")
            else:
                st.error(f"❌ Error al iniciar: {response.status_code} - {response.text}")

with col2:
    if st.button("🔄 Recargar datos", use_container_width=True):
        st.rerun()

# --- Mostrar edictos guardados ---
st.subheader("📋 Edictos encontrados")

# Filtros
localidades_seleccionadas = st.multiselect("Filtrar por localidad", ["Todas"] + sorted(LOCALIDADES))
buscar_texto = st.text_input("Buscar por nombre, CUIT o texto")

# Construir consulta
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidades_seleccionadas and localidades_seleccionadas:
    query = query.in_("localidad", localidades_seleccionadas)
if buscar_texto:
    query = query.or_(f"nombres.ilike.%{buscar_texto}%,cuit.ilike.%{buscar_texto}%,texto_completo.ilike.%{buscar_texto}%")

response = query.execute()
datos = response.data

if datos:
    df = pd.DataFrame(datos)
    # Mostrar tabla resumida
    st.dataframe(
        df[["fecha", "boletin_numero", "seccion", "localidad", "nombres", "cuit"]],
        use_container_width=True,
        column_config={
            "fecha": "Fecha",
            "boletin_numero": "Boletín",
            "seccion": "Sección",
            "localidad": "Localidad",
            "nombres": "Nombres",
            "cuit": "CUIT"
        }
    )
    # Detalle expandible
    st.subheader("Detalle completo")
    for _, row in df.iterrows():
        with st.expander(f"{row['fecha']} - {row['localidad']} - {row['nombres'] or 'Sin nombre'}"):
            st.markdown(f"**Sección:** {row['seccion']}")
            st.markdown(f"**Boletín:** {row['boletin_numero']}")
            st.markdown(f"**Localidad:** {row['localidad']}")
            st.markdown(f"**Nombres:** {row['nombres']}")
            st.markdown(f"**CUIT:** {row['cuit']}")
            st.markdown("**Texto completo:**")
            st.markdown(row['texto_completo'])
else:
    st.info("No hay edictos guardados todavía. El scraper se ejecutará automáticamente o podés usar 'Forzar búsqueda ahora'.")
