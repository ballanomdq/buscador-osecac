import streamlit as st
import os
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Boletín Oficial - Fiscalización", layout="wide")
st.title("⚖️ Fiscalización OSECAC - Edictos por Boletín")

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

# --- Lista de localidades ---
LOCALIDADES = [
    "Mar del Plata", "Alvarado", "Miramar", "Mechongue", "Otamendi", "Vivorata",
    "Vidal", "Piran", "Las Armas", "Maipu", "Labarden", "Guido", "Dolores",
    "Castelli", "Tordillo", "Conesa", "Lavalle", "San Clemente", "Las Toninas",
    "Santa Teresita", "Mar del Tuyu", "San Bernardo", "La Lucila del Mar",
    "Mar de Ajo", "Costa del Este", "Pinamar", "Madariaga", "Villa Gesell",
    "Mar Chiquita"
]

# --- Sidebar con acciones y filtros ---
with st.sidebar:
    st.header("Acciones")
    if st.button("🔄 Forzar búsqueda ahora"):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta el token de GitHub (GH_TOKEN) en secrets.")
        else:
            repo = "ballanomdq/buscador-osecac"  # Ajustar si es necesario
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
    # Filtro por sección
    seccion_filtro = st.multiselect("Sección", ["Todas", "JUDICIAL", "OFICIAL"], default=["Todas"])

# --- Consultar datos ---
query = supabase.table("edictos").select("*").order("fecha", desc=True)
if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
if "Todas" not in seccion_filtro and seccion_filtro:
    query = query.in_("seccion", seccion_filtro)
response = query.execute()
datos = response.data

if not datos:
    st.info("No hay edictos guardados todavía. Usá 'Forzar búsqueda ahora' para iniciar el scraping.")
    st.stop()

df = pd.DataFrame(datos)
# Convertir fecha a datetime con zona horaria Argentina para mostrar
df["fecha"] = pd.to_datetime(df["fecha"])
# Si la fecha está en UTC, convertir a Argentina (si no está tz, asumir UTC)
if df["fecha"].dt.tz is None:
    # Asumir que viene UTC
    df["fecha"] = df["fecha"].dt.tz_localize('UTC').dt.tz_convert('America/Argentina/Buenos_Aires')
else:
    df["fecha"] = df["fecha"].dt.tz_convert('America/Argentina/Buenos_Aires')

# Agrupar por fecha (sin boletin_numero para evitar duplicados de misma fecha)
grupos = df.groupby(["fecha"])

st.subheader("📖 Boletines disponibles")

# Ordenar grupos por fecha descendente
for fecha, grupo in grupos.sort_index(ascending=False):
    # Tomar un boletin_numero representativo (puede haber varios, tomamos el primero)
    boletin_numero = grupo.iloc[0]["boletin_numero"]
    with st.container():
        st.markdown(f"### 📘 Boletín del {fecha.strftime('%d/%m/%Y')} - N° {boletin_numero}")
        st.caption(f"Total edictos en esta fecha: {len(grupo)}")
        # Mostrar cada edicto como tarjeta expandible
        for _, row in grupo.iterrows():
            # Icono según sección
            icono = "⚖️" if row["seccion"] == "JUDICIAL" else "📜"
            # Construir título de la tarjeta
            titulo = f"{icono} {row['localidad']}"
            cuits = row.get("cuit_detectados")
            if cuits:
                titulo += f" | CUITs: {cuits}"
            else:
                titulo += " | Sin CUITs"
            with st.expander(titulo):
                st.markdown(f"**Sección:** {row['seccion']}")
                st.markdown(f"**Localidad:** {row['localidad']}")
                if row.get("nombres"):
                    st.markdown(f"**Sujetos destacados:** {row['nombres']}")
                if cuits:
                    st.markdown("**CUITs / DNIs detectados:**")
                    # Mostrar cada CUIT con un botón para copiar
                    for cuit in cuits.split(", "):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(cuit)
                        with col2:
                            if st.button(f"📋 Copiar", key=f"copy_{row['id']}_{cuit}"):
                                st.write(f"Copiado: {cuit}")
                                # Usar JavaScript para copiar al portapapeles
                                st.components.v1.html(
                                    f"""
                                    <script>
                                    navigator.clipboard.writeText("{cuit}");
                                    </script>
                                    """,
                                    height=0,
                                )
                st.markdown("**Texto completo:**")
                st.markdown(row['texto_completo'])
                # Botón eliminar
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
