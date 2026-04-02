import streamlit as st
import os
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import date

st.set_page_config(page_title="Boletín Oficial - Fiscalización", layout="wide")
st.title("📚 Fiscalización - Edictos por Boletín")

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

# --- Lista de localidades (para filtro opcional) ---
LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

# --- Botón para forzar scraping (manual) ---
with st.sidebar:
    st.header("Acciones")
    if st.button("🔄 Forzar búsqueda ahora"):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta el token de GitHub (GH_TOKEN) en secrets.")
        else:
            repo = "ballanomdq/buscador-osecac"  # CAMBIAR SI ES OTRO
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
                st.error(f"Error al iniciar: {response.status_code}")

    st.header("Filtros")
    localidad_filtro = st.multiselect("Localidad", ["Todas"] + sorted(LOCALIDADES), default=["Todas"])

# --- Consultar datos agrupados por fecha ---
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
response = query.execute()
datos = response.data

if not datos:
    st.info("No hay edictos guardados todavía. Usá 'Forzar búsqueda ahora' para iniciar el scraping.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"])

# Agrupar por fecha (boletín)
grupos = df.groupby(["fecha", "boletin_numero"])

st.subheader("📖 Boletines disponibles")

for (fecha, boletin), grupo in grupos:
    # Extraer nombres y CUITs únicos del grupo
    nombres_y_cuits = set()
    for _, row in grupo.iterrows():
        if row["nombres"]:
            nombres_y_cuits.update(row["nombres"].split(", "))
        if row["cuit"]:
            nombres_y_cuits.update(row["cuit"].split(", "))
    resumen = list(nombres_y_cuits)[:10]

    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"### 📘 Boletín N° {boletin}")
            st.caption(f"🗓️ {fecha.strftime('%d/%m/%Y')} · {len(grupo)} edictos")
        with col2:
            # Botón "ojo" para ver resumen
            if st.button("👁️ Ver datos clave", key=f"resumen_{fecha}_{boletin}"):
                with st.expander(f"Resumen de {boletin} ({fecha.strftime('%d/%m/%Y')})", expanded=True):
                    if resumen:
                        st.write("**Nombres / CUITs encontrados:**")
                        for item in resumen:
                            st.write(f"- {item}")
                    else:
                        st.write("No se extrajeron nombres o CUITs.")
        with col3:
            # Botón para ver edictos completos
            if st.button("📄 Ver edictos", key=f"detalle_{fecha}_{boletin}"):
                with st.expander(f"Edictos de {boletin} ({fecha.strftime('%d/%m/%Y')})", expanded=True):
                    for _, row in grupo.iterrows():
                        st.markdown(f"**📍 {row['localidad']}**")
                        if row["nombres"]:
                            st.markdown(f"*Nombres:* {row['nombres']}")
                        if row["cuit"]:
                            st.markdown(f"*CUIT:* {row['cuit']}")
                        st.markdown(f"**Texto:** {row['texto_completo'][:300]}...")
                        # Botón eliminar edicto (con confirmación)
                        if st.button("🗑️ Eliminar este edicto", key=f"elim_{row['id']}"):
                            if st.session_state.get(f"confirm_{row['id']}", False):
                                supabase.table("edictos").delete().eq("id", row["id"]).execute()
                                st.success("Eliminado")
                                st.rerun()
                            else:
                                st.session_state[f"confirm_{row['id']}"] = True
                                st.warning("Hacé clic otra vez para confirmar eliminación.")
                        st.markdown("---")
        st.markdown("---")

# Botón para recargar datos manualmente
if st.button("🔄 Recargar datos"):
    st.rerun()
