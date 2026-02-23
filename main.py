import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# --- CLAVE DE ACCESO PERSONALIZADA ---
PASSWORD_JEFE = "2026"

# 2. CARGA DE DATOS (CSV DESDE GOOGLE SHEETS)
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        if '/edit' in url:
            csv_url = url.split('/edit')[0] + '/export?format=csv'
        else:
            csv_url = url
        return pd.read_csv(csv_url, dtype=str)
    except:
        return pd.DataFrame()

# URLs de las planillas
URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_PRACTICAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0"
URL_ESPECIALISTAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576"
URL_FABA = "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv"
URL_OSECAC = "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)
df_practicas = cargar_datos(URL_PRACTICAS_CSV)
df_especialistas = cargar_datos(URL_ESPECIALISTAS_CSV)
df_faba = cargar_datos(URL_FABA)
df_osecac_busq = cargar_datos(URL_OSECAC)

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}
    ]

# 3. CSS: DISEÑO COMPATIBLE CON NAVEGADORES VIEJOS
st.markdown("""
    <style>
    /* Fondo sólido de respaldo para Chrome viejo */
    .stApp { 
        background-color: #0b0e14;
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        color: #ffffff !important; 
    }
    
    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }
    
    /* Encabezado con colores sólidos */
    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini { 
        padding: 10px 30px; 
        background-color: #1e293b; /* Fallback */
        background: rgba(56, 189, 248, 0.1); 
        border-radius: 35px; 
        border: 2px solid #38bdf8; 
        display: inline-block; 
    }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff !important; margin: 0; }
    
    /* Fichas con bordes más gruesos para que se noten en pantallas viejas */
    .ficha { 
        background-color: #172030; 
        padding: 20px; 
        border-radius: 12px; 
        margin-bottom: 10px; 
        border-left: 8px solid #ccc;
        color: #ffffff !important;
    }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-agenda { border-left-color: #38bdf8; }
    .ficha-practica { border-left-color: #10b981; } 
    .ficha-faba { border-left-color: #f97316; }
    .ficha-novedad { border-left-color: #ff4b4b; }

    /* Asegurar visibilidad de expanders */
    .stExpander { border: 1px solid #334155 !important; background-color: #1e293b !important; }
    
    /* Forzar color de texto en inputs */
    input { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown('<div class="header-master"><div class="capsula-header-mini"><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)

# === LOGO ===
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# --- SECCIÓN 1: NOMENCLADORES ---
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    
    # BUSCADOR FABA
    st.write("🔍 **BUSCADOR FABA**")
    busqueda_faba = st.text_input("Ingresá código o nombre en FABA...", key="search_faba")
    if busqueda_faba:
        if not df_faba.empty:
            mask = df_faba.apply(lambda row: all(p in str(row).lower() for p in busqueda_faba.lower().split()), axis=1)
            res_f = df_faba[mask]
            for i, row in res_f.iterrows():
                datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val)]
                st.markdown(f'<div class="ficha ficha-faba">{"<br>".join(datos)}</div>', unsafe_allow_html=True)
        else: st.error("Error base FABA")

    st.markdown("---")

    # BUSCADOR OSECAC
    st.write("🔍 **BUSCADOR OSECAC**")
    busqueda_osecac = st.text_input("Ingresá código o nombre en OSECAC...", key="search_osecac")
    if busqueda_osecac:
        if not df_osecac_busq.empty:
            mask = df_osecac_busq.apply(lambda row: all(p in str(row).lower() for p in busqueda_osecac.lower().split()), axis=1)
            res_o = df_osecac_busq[mask]
            for i, row in res_o.iterrows():
                datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val)]
                st.markdown(f'<div class="ficha ficha-agenda" style="border-left-color: #38bdf8;">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

# --- RESTO DE SECCIONES (IGUALES) ---
with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")

with st.expander("🌐 **3. PÁGINAS ÚTILES**", expanded=False):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")
    st.link_button("🆔 ANSES", "https://servicioswww.anses.gob.ar/ooss2/")

with st.expander("📂 **4. GESTIONES**", expanded=False):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busqueda_t.lower(), na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><b>📋 {row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

with st.expander("🩺 **5. PRÁCTICAS**", expanded=False):
    busqueda_p = st.text_input("Buscá prácticas...", key="search_p")
    if busqueda_p:
        for df_actual, tipo in [(df_practicas, "📑 PRÁCTICA"), (df_especialistas, "👨‍⚕️ ESPECIALISTA")]:
            if not df_actual.empty:
                res = df_actual[df_actual.astype(str).apply(lambda row: row.str.contains(busqueda_p.lower(), case=False).any(), axis=1)]
                for i, row in res.iterrows():
                    datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val)]
                    st.markdown(f'<div class="ficha ficha-practica">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

with st.expander("📞 **6. AGENDAS**", expanded=False):
    busqueda_a = st.text_input("Buscá contactos...", key="search_a")
    if busqueda_a and not df_agendas.empty:
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(busqueda_a.lower(), case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val)]
            st.markdown(f'<div class="ficha ficha-agenda">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha ficha-novedad"><b>📅 {n["fecha"]}</b><br>{n["mensaje"]}</div>', unsafe_allow_html=True)
    
    with st.popover("✍️ PANEL"):
        clave = st.text_input("Clave:", type="password")
        if clave == PASSWORD_JEFE:
            with st.form("form_nov", clear_on_submit=True):
                msg = st.text_area("Nuevo:")
                if st.form_submit_button("📢"):
                    st.session_state.historial_novedades.insert(0, {"id": str(datetime.now().timestamp()), "mensaje": msg, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")})
                    st.rerun()
