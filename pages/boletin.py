import streamlit as st
import os
import requests
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import pytz
import time

st.set_page_config(page_title="Boletín Oficial - Fiscalización", layout="wide")
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

# --- Botón principal con barra de progreso ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Forzar descarga de Boletines del día", use_container_width=True):
        token = st.secrets.get("GH_TOKEN")
        if not token:
            st.error("Falta el token de GitHub (GH_TOKEN) en secrets.")
        else:
            repo = "ballanomdq/buscador-osecac"  # Ajustá si es necesario
            url = f"https://api.github.com/repos/{repo}/actions/workflows/scrape_edictos.yml/dispatches"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {"ref": "main"}
            with st.spinner("⏳ Procesando boletines... esto puede tomar unos segundos."):
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 204:
                    # Simular progreso (ya que el workflow corre en segundo plano)
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    progress_bar.empty()
                    st.success("✅ Scraping iniciado. Los resultados aparecerán en unos minutos.")
                else:
                    st.error(f"Error al iniciar: {response.status_code}")

st.divider()

# --- Consultar datos ---
query = supabase.table("edictos").select("*").order("fecha", desc=True)
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
# Convertir a zona horaria Argentina
if df["fecha"].dt.tz is None:
    df["fecha"] = df["fecha"].dt.tz_localize('UTC').dt.tz_convert('America/Argentina/Buenos_Aires')
else:
    df["fecha"] = df["fecha"].dt.tz_convert('America/Argentina/Buenos_Aires')

# Agrupar por número de boletín y fecha (un boletín puede tener varias secciones)
# Usamos una clave compuesta
df["boletin_clave"] = df["boletin_numero"] + "_" + df["fecha"].dt.strftime("%Y%m%d")
boletines = df.groupby(["boletin_clave", "fecha", "boletin_numero"])

st.subheader("📖 Boletines disponibles")

# Convertir a lista para ordenar por fecha descendente
boletines_list = []
for (clave, fecha, numero), grupo in boletines:
    boletines_list.append({
        "clave": clave,
        "fecha": fecha,
        "numero": numero,
        "grupo": grupo
    })
boletines_list.sort(key=lambda x: x["fecha"], reverse=True)

# Mostrar tarjetas en una cuadrícula (3 columnas)
cols = st.columns(3)
for idx, boletin in enumerate(boletines_list):
    col = cols[idx % 3]
    with col:
        # Determinar íconos según las secciones presentes en el grupo
        secciones = boletin["grupo"]["seccion"].unique()
        icono = "⚖️" if "JUDICIAL" in secciones else "📜"
        if "JUDICIAL" in secciones and "OFICIAL" in secciones:
            icono = "⚖️📜"
        color = "#e6f2ff" if "JUDICIAL" in secciones else "#f0f0f0"  # azul suave o gris suave
        # Crear tarjeta expandible
        with st.expander(f"{icono} Boletín N° {boletin['numero']} - {boletin['fecha'].strftime('%d/%m/%Y')}"):
            # Mostrar las dos secciones por separado
            for seccion in ["JUDICIAL", "OFICIAL"]:
                subgrupo = boletin["grupo"][boletin["grupo"]["seccion"] == seccion]
                if not subgrupo.empty:
                    st.markdown(f"### {seccion}")
                    # Para cada edicto dentro de la sección
                    for _, row in subgrupo.iterrows():
                        # Detectar si tiene alerta de quiebra
                        es_quiebra = "quiebra" in row["texto_completo"].lower()
                        if es_quiebra:
                            st.markdown(f"<span style='background-color:#ffcccc; padding:2px 6px; border-radius:10px;'>⚠️ QUIEBRA</span>", unsafe_allow_html=True)
                        # Título del edicto
                        st.markdown(f"**📍 {row['localidad']}**")
                        cuits = row.get("cuit_detectados")
                        if cuits:
                            st.markdown(f"**CUITs:** {cuits}")
                        if row.get("sujetos"):
                            st.markdown(f"**Sujetos:** {row['sujetos']}")
                        # Botones para copiar CUITs individuales
                        if cuits:
                            for cuit in cuits.split(", "):
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.write(cuit)
                                with col2:
                                    if st.button(f"📋 Copiar", key=f"copy_{row['id']}_{cuit}"):
                                        st.write(f"Copiado: {cuit}")
                                        st.components.v1.html(
                                            f"<script>navigator.clipboard.writeText('{cuit}');</script>",
                                            height=0,
                                        )
                        # Texto completo (corto o expandible)
                        with st.expander("Ver texto completo"):
                            st.markdown(row["texto_completo"])
                        st.markdown("---")
        st.markdown("<br>", unsafe_allow_html=True)  # separación entre tarjetas

if st.button("🔄 Recargar datos", key="recargar"):
    st.rerun()
