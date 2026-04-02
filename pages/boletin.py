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
if df["fecha"].dt.tz is None:
    df["fecha"] = df["fecha"].dt.tz_localize('UTC').dt.tz_convert('America/Argentina/Buenos_Aires')
else:
    df["fecha"] = df["fecha"].dt.tz_convert('America/Argentina/Buenos_Aires')

# Agrupar por número de boletín y fecha
df["boletin_clave"] = df["boletin_numero"] + "_" + df["fecha"].dt.strftime("%Y%m%d")
boletines = df.groupby(["boletin_clave", "fecha", "boletin_numero"])

st.subheader("📖 Boletines disponibles")

# Convertir a lista y ordenar por fecha descendente
boletines_list = []
for (clave, fecha, numero), grupo in boletines:
    boletines_list.append({
        "clave": clave,
        "fecha": fecha,
        "numero": numero,
        "grupo": grupo
    })
boletines_list.sort(key=lambda x: x["fecha"], reverse=True)

# --- Función para determinar el motivo principal de un grupo de edictos ---
def obtener_motivo(grupo):
    textos = grupo["texto_completo"].str.lower().sum()
    if "quiebra" in textos:
        return "🚨 QUIEBRA"
    if "sucesorio" in textos or "sucesión" in textos:
        return "⚖️ SUCESORIO"
    if "concurso" in textos:
        return "📉 CONCURSO"
    if "transferencia" in textos:
        return "🔄 TRANSFERENCIA"
    return "⚪ INFORMATIVO"

# --- Mostrar tarjetas en cuadrícula (3 columnas) ---
cols = st.columns(3)
for idx, boletin in enumerate(boletines_list):
    col = cols[idx % 3]
    with col:
        grupo = boletin["grupo"]
        motivo = obtener_motivo(grupo)
        
        # Extraer todos los CUITs y nombres (en mayúsculas) de este boletín
        todos_cuits = set()
        todos_nombres = set()
        for _, row in grupo.iterrows():
            if row.get("cuit_detectados"):
                for c in row["cuit_detectados"].split(", "):
                    todos_cuits.add(c)
            if row.get("sujetos"):
                for s in row["sujetos"].split(", "):
                    todos_nombres.add(s)
        # Tomar un nombre representativo (el primero, o el que tenga mayúsculas largas)
        nombre_str = ", ".join(sorted(todos_nombres)[:2]) if todos_nombres else "SIN NOMBRE"
        
        # Construir título de la tarjeta
        titulo = f"{motivo} | {boletin['fecha'].strftime('%d/%m/%Y')} | {nombre_str}"
        if todos_cuits:
            titulo += f" | CUITs: {', '.join(sorted(todos_cuits)[:3])}"
            if len(todos_cuits) > 3:
                titulo += f" (+{len(todos_cuits)-3})"
        else:
            titulo += " | SIN CUIT"
        
        # Opcional: si el motivo es INFORMATIVO y no hay CUIT, se puede marcar para saltear visualmente
        if motivo == "⚪ INFORMATIVO" and not todos_cuits:
            titulo = "⏩ " + titulo  # indicador de que se puede saltar
        
        # Crear tarjeta expandible
        with st.expander(titulo):
            # Mostrar cada sección por separado
            for seccion in ["JUDICIAL", "OFICIAL"]:
                subgrupo = grupo[grupo["seccion"] == seccion]
                if not subgrupo.empty:
                    st.markdown(f"### {seccion}")
                    for _, row in subgrupo.iterrows():
                        # Alertas específicas
                        es_quiebra = "quiebra" in row["texto_completo"].lower()
                        if es_quiebra:
                            st.markdown(f"<span style='background-color:#ffcccc; padding:2px 6px; border-radius:10px;'>⚠️ QUIEBRA</span>", unsafe_allow_html=True)
                        st.markdown(f"**📍 {row['localidad']}**")
                        cuits = row.get("cuit_detectados")
                        if cuits:
                            st.markdown(f"**CUITs:** {cuits}")
                        if row.get("sujetos"):
                            st.markdown(f"**Sujetos:** {row['sujetos']}")
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
                        with st.expander("Ver texto completo"):
                            st.markdown(row["texto_completo"])
                        st.markdown("---")
        st.markdown("<br>", unsafe_allow_html=True)

if st.button("🔄 Recargar datos", key="recargar"):
    st.rerun()
