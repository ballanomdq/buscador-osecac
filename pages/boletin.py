import streamlit as st
import os
import requests
from supabase import create_client
import pandas as pd
from datetime import datetime, date, timedelta
import re
import base64
from bs4 import BeautifulSoup

st.set_page_config(page_title="Boletín Oficial - OSECAC", layout="wide")

st.markdown("""
<style>
.stButton > button {
    padding: 0.2rem 0.6rem;
    font-size: 0.8rem;
    border-radius: 20px;
    margin: 0 0.2rem;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Fiscalización OSECAC - Boletín Oficial (VERSIÓN SIMPLE PARA DIAGNÓSTICO)")

# ── Supabase ──────────────────────────────────────────────────────────────────
def get_credentials():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return url, key
    except Exception:
        pass
    return os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")

SUPABASE_URL, SUPABASE_KEY = get_credentials()
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Faltan credenciales de Supabase. Revisá los secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Botones superiores ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Forzar descarga", use_container_width=True):
        st.info("Función de descarga desactivada en versión de diagnóstico")

with col2:
    if st.button("🔄 Recargar datos", use_container_width=True):
        st.rerun()

with col3:
    st.write("")

# ── Filtros en sidebar ─────────────────────────────────────────────────────
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
    seccion_filtro   = st.radio("Sección", ["Todas", "JUDICIAL", "OFICIAL"], index=0)
    solo_quiebras    = st.checkbox("🚨 Solo quiebras/concursos")

# ── Consulta Supabase ─────────────────────────────────────────────────────────
st.subheader("🔍 Datos en la base de datos")

# Traemos todos los edictos ordenados por fecha descendente
query = supabase.table("edictos").select("*").order("fecha", desc=True)

if "Todas" not in localidad_filtro and localidad_filtro:
    query = query.in_("localidad", localidad_filtro)
if seccion_filtro != "Todas":
    query = query.eq("seccion", seccion_filtro)
response = query.execute()
datos = response.data

if not datos:
    st.warning("No hay edictos en la base de datos.")
    st.stop()

df = pd.DataFrame(datos)
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

if solo_quiebras:
    df = df[df["texto_completo"].str.lower().str.contains("quiebra|concurso", na=False)]

# Mostrar información básica
st.write(f"**Total de edictos encontrados:** {len(df)}")
st.write("**Últimos 10 edictos (vista previa):**")
st.dataframe(df[["fecha", "boletin_numero", "seccion", "localidad"]].head(10))

# Mostrar agrupación por fecha
st.subheader("Edictos agrupados por fecha")
for fecha, grupo in df.groupby("fecha"):
    st.write(f"📅 **{fecha}** - {len(grupo)} edictos")
