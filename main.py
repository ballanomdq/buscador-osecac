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
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# URLs de las planillas
URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_PRACTICAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0"
URL_ESPECIALISTAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)
df_practicas = cargar_datos(URL_PRACTICAS_CSV)
df_especialistas = cargar_datos(URL_ESPECIALISTAS_CSV)

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial.", "fecha": "22/02/2026"}]

# 3. CSS: DISEÑO DE LÍNEA DE COLOR ÚNICA
st.markdown("""
    <style>
    .stApp { 
        background-color: #0b0e14;
        color: #e2e8f0; 
    }
    
    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }

    /* ESTILO GENERAL DE LOS EXPANDERS PARA QUE PAREZCAN BOTONES DE COLOR */
    .stExpander {
        border: none !important;
        background-color: transparent !important;
        margin-bottom: 10px !important;
    }

    /* Forzar que el encabezado del expander sea una línea de color */
    .stExpander summary {
        border-radius: 8px !important;
        padding: 10px !important;
        color: white !important;
        font-weight: bold !important;
    }

    .stExpander summary p { color: white !important; font-size: 1.1rem !important; }
    .stExpander svg { fill: white !important; }

    /* COLORES ESPECÍFICOS POR SECCIÓN (LÍNEA ÚNICA) */
    /* Sección 4: Amarillo */
    div.buscador-gestion .stExpander summary { background-color: #fbbf24 !important; border: 1px solid #fbbf24 !important; }
    /* Sección 5: Esmeralda */
    div.buscador-practica .stExpander summary { background-color: #10b981 !important; border: 1px solid #10b981 !important; }
    /* Sección 6: Azul */
    div.buscador-agenda .stExpander summary { background-color: #38bdf8 !important; border: 1px solid #38bdf8 !important; }
    /* Sección 7: Rojo */
    div.buscador-novedades .stExpander summary { background-color: #ff4b4b !important; border: 1px solid #ff4b4b !important; }

    /* Fichas de resultados */
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 15px; border-radius: 8px; margin-top: 10px; border-left: 5px solid; }
    
    .header-master { text-align: center; margin-bottom: 20px; }
    .titulo-mini { color: white; font-size: 1.5rem; font-weight: 800; border: 1px solid #38bdf8; padding: 10px 20px; border-radius: 30px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown('<div class="header-master"><div class="titulo-mini">OSECAC MDP / AGENCIAS</div></div>', unsafe_allow_html=True)

# === LOGO ===
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:80px;"></center>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# === SECCIONES 1, 2 Y 3 (BOTONES ESTÁNDAR) ===
with st.expander("📂 **1. NOMENCLADORES**"):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

with st.expander("🌐 **3. PÁGINAS ÚTILES**"):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")

# === SECCIÓN 4: GESTIONES (AMARILLO) ===
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 4. GESTIONES / DATOS"):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busqueda_t.lower(), na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha" style="border-color:#fbbf24;"><b style="color:#fbbf24;">📋 {row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 5: PRÁCTICAS (ESMERALDA) ===
st.markdown('<div class="buscador-practica">', unsafe_allow_html=True)
with st.expander("🩺 5. PRÁCTICAS Y ESPECIALISTAS"):
    busqueda_p = st.text_input("Buscá prácticas o médicos...", key="search_p")
    if busqueda_p:
        # Combinamos búsqueda en ambas solapas
        for df, titulo in [(df_practicas, "📑 PRÁCTICA"), (df_especialistas, "👨‍⚕️ ESPECIALISTA")]:
            if not df.empty:
                res = df[df.astype(str).apply(lambda row: row.str.contains(busqueda_p.lower(), case=False).any(), axis=1)]
                for i, row in res.iterrows():
                    datos = "<br>".join([f"<b>{c}:</b> {v}" for c, v in row.items() if pd.notna(v)])
                    st.markdown(f'<div class="ficha" style="border-color:#10b981;"><span style="color:#10b981; font-weight:bold;">{titulo}</span><br>{datos}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 6: AGENDAS (AZUL) ===
st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 6. AGENDAS / MAILS"):
    busqueda_a = st.text_input("Buscá contactos...", key="search_a")
    if busqueda_a and not df_agendas.empty:
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(busqueda_a.lower(), case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            datos = "<br>".join([f"<b>{c}:</b> {v}" for c, v in row.items() if pd.notna(v)])
            st.markdown(f'<div class="ficha" style="border-color:#38bdf8;">{datos}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 7: NOVEDADES (ROJO) ===
st.markdown('<div class="buscador-novedades">', unsafe_allow_html=True)
with st.expander("📢 7. NOVEDADES", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha" style="border-color:#ff4b4b;"><b style="color:#ff4b4b;">📅 {n["fecha"]}</b><br>{n["mensaje"]}</div>', unsafe_allow_html=True)
    
    with st.popover("✍️ PANEL DE CONTROL"):
        clave = st.text_input("Clave:", type="password")
        if clave == PASSWORD_JEFE:
            msg = st.text_area("Nuevo comunicado:")
            if st.button("📢 PUBLICAR"):
                st.session_state.historial_novedades.insert(0, {"id": str(datetime.now().timestamp()), "mensaje": msg, "fecha": datetime.now().strftime("%d/%m/%Y")})
                st.rerun()
            for i, n in enumerate(st.session_state.historial_novedades):
                if st.button(f"🗑️ Borrar: {n['mensaje'][:15]}...", key=f"del_{i}"):
                    st.session_state.historial_novedades.pop(i)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
