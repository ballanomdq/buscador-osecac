import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# CARGA DE DATOS (Mantenemos tus funciones)
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

# URLs (Tus links originales)
URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_PRACTICAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0"
URL_ESPECIALISTAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576"
URL_FABA = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
URL_OSECAC_BUSQ = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)
df_practicas = cargar_datos(URL_PRACTICAS_CSV)
df_especialistas = cargar_datos(URL_ESPECIALISTAS_CSV)
df_faba = cargar_datos(URL_FABA)
df_osecac_busq = cargar_datos(URL_OSECAC_BUSQ)

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"mensaje": "Portal OSECAC MDP activo.", "fecha": "22/02/2026"}]

# CSS MÍNIMO (Solo estética de fichas, NO tocamos inputs aquí)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; }
    .ficha { background: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #38bdf8; margin-bottom: 10px; }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 OSECAC MDP / AGENCIAS")

# SECCIÓN BUSCADOR PRINCIPAL
with st.container():
    col1, col2 = st.columns([1, 3])
    with col1:
        opcion = st.selectbox("Origen:", ["FABA", "OSECAC"])
    with col2:
        busqueda = st.text_input("🔍 Escribe aquí para buscar...")

    if busqueda:
        df = df_faba if opcion == "FABA" else df_osecac_busq
        res = df[df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)]
        for _, row in res.iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# SECCIONES (Expanders)
with st.expander("📞 AGENDAS"):
    b_a = st.text_input("Buscar contacto...")
    if b_a and not df_agendas.empty:
        res_a = df_agendas[df_agendas.astype(str).apply(lambda x: x.str.contains(b_a, case=False)).any(axis=1)]
        for _, row in res_a.iterrows():
            st.markdown(f'<div class="ficha">{row.to_string()}</div>', unsafe_allow_html=True)
