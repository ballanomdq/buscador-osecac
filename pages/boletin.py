import streamlit as st
import os
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Boletín Oficial - Fiscalización", layout="wide")
st.title("⚖️ Fiscalización - Edictos por Boletín")

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

# --- Lista de localidades (para filtro) ---
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

# --- Consultar datos ---
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
response = query.execute()
datos = response.data

if not datos:
    st.info("No hay edictos guardados todavía. Usá 'Forzar búsqueda ahora' para iniciar el scraping.")
    st.stop()

df = pd.DataFrame(datos)

# Asegurar que la fecha sea datetime (ya debería ser string ISO)
df["fecha"] = pd.to_datetime(df["fecha"])

# Agrupar por fecha (y opcionalmente por boletín, pero para evitar duplicados agrupamos solo por fecha)
grupos = df.groupby("fecha")

st.subheader("📖 Edictos agrupados por fecha")

for fecha, grupo in grupos:
    # Extraer datos destacados para el resumen del día
    resumen_cuits = set()
    for _, row in grupo.iterrows():
        if row.get("cuit_detectados"):
            resumen_cuits.update(row["cuit_detectados"].split(", "))

    with st.container():
        st.markdown(f"### 📅 {fecha.strftime('%d/%m/%Y')} · {len(grupo)} edictos")
        if resumen_cuits:
            st.caption(f"**CUITs encontrados:** {', '.join(list(resumen_cuits)[:8])}")

        # Mostrar cada edicto como una tarjeta expandible
        for idx, row in grupo.iterrows():
            # Determinar icono según sección
            icono = "⚖️" if row["seccion"] == "JUDICIAL" else "📜"
            # Título de la tarjeta: localidad + CUITs
            cuit_str = row.get("cuit_detectados") or "Sin CUITs"
            titulo = f"{icono} **{row['localidad']}** | CUITs: {cuit_str}"
            with st.expander(titulo):
                # Mostrar sujetos en mayúsculas (si existen)
                if row.get("sujetos"):
                    st.markdown(f"**👤 Sujetos detectados:** {row['sujetos']}")
                # Mostrar el texto completo
                st.markdown("**Texto completo del edicto:**")
                st.markdown(row["texto_completo"])
                # Botones para copiar cada CUIT individualmente
                if row.get("cuit_detectados"):
                    cuits_list = row["cuit_detectados"].split(", ")
                    st.markdown("**Acciones:**")
                    cols = st.columns(len(cuits_list))
                    for i, cuit in enumerate(cuits_list):
                        with cols[i]:
                            if st.button(f"📋 Copiar {cuit}", key=f"copy_{row['id']}_{i}"):
                                st.write(f"Copiado: {cuit}")
                                # Simulación de copia al portapapeles (requiere JS)
                                st.markdown(
                                    f"<script>navigator.clipboard.writeText('{cuit}');</script>",
                                    unsafe_allow_html=True
                                )
                # Botón eliminar edicto
                if st.button("🗑️ Eliminar este edicto", key=f"elim_{row['id']}"):
                    if st.session_state.get(f"confirm_{row['id']}", False):
                        supabase.table("edictos").delete().eq("id", row["id"]).execute()
                        st.success("Eliminado")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_{row['id']}"] = True
                        st.warning("Hacé clic otra vez para confirmar eliminación.")
        st.markdown("---")

if st.button("🔄 Recargar datos"):
    st.rerun()
