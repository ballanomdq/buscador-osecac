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

# Inicializar historial de novedades si no existe
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP. Las novedades aparecerán aquí.", "fecha": "22/02/2026 00:00"}
    ]

# 3. CSS: ATAQUE TOTAL AL FONDO BLANCO
st.markdown("""
    <style>
    /* 1. Fondo general de la App */
    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    /* 2. ELIMINAR EL COLOR BLANCO DE LOS EXPANDERS (BOTONES) */
    /* Forzamos fondo transparente y texto blanco en todos los estados */
    div[data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }

    /* Título del botón (Summary) */
    div[data-testid="stExpander"] summary {
        background-color: transparent !important;
        color: white !important;
    }

    /* Cuando pasas el mouse o sacas el cursor (hover y focus) */
    div[data-testid="stExpander"]:hover, 
    div[data-testid="stExpander"]:focus,
    div[data-testid="stExpander"]:focus-visible,
    div[data-testid="stExpander"]:focus-within {
        background-color: rgba(255, 255, 255, 0.07) !important;
        outline: none !important;
    }

    /* Texto dentro del botón */
    div[data-testid="stExpander"] summary p {
        color: white !important;
    }

    /* Icono de flecha */
    div[data-testid="stExpander"] svg {
        fill: white !important;
    }

    /* Eliminar cualquier sombra blanca que pone Streamlit al hacer click */
    .st-emotion-cache-p5msec:focus:not(:active) {
        background-color: transparent !important;
        color: white !important;
    }

    /* 3. ESTILOS DE FICHAS Y OTROS (MANTENIENDO LO ANTERIOR) */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }

    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
    .ficha-tramite { border-left: 6px solid #fbbf24; }
    .ficha-agenda { border-left: 6px solid #38bdf8; }
    .ficha-practica { border-left: 6px solid #10b981; }
    .ficha-novedad { border-left: 6px solid #ff4b4b; margin-top: 10px; }
    
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; padding: 5px; }
    .buscador-practica { border: 2px solid #10b981 !important; border-radius: 12px; margin-bottom: 10px; padding: 5px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; padding: 5px; }
    .buscador-novedades { border: 2px solid #ff4b4b !important; border-radius: 12px; margin-bottom: 10px; padding: 5px; }
    
    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini {
        position: relative; padding: 10px 30px;
        background: rgba(56, 189, 248, 0.05);
        border-radius: 35px; border: 1px solid rgba(56, 189, 248, 0.5);
        display: inline-block;
    }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown("""
    <div class="header-master">
        <div class="capsula-header-mini">
            <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === LOGO ===
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# === SECCIONES 1, 2 Y 3 ===
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")

with st.expander("🌐 **3. PÁGINAS ÚTILES**", expanded=False):
    st.link_button("🏥 SSSALUD (Consultas)", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")
    st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
    st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")
    st.link_button("🧪 SISA", "https://sisa.msal.gov.ar/sisa/")

# === SECCIÓN 4: GESTIONES ===
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busqueda_t.lower(), na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><b style="color:#fbbf24;">📋 {row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 5: PRÁCTICAS Y ESPECIALISTAS ===
st.markdown('<div class="buscador-practica">', unsafe_allow_html=True)
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**", expanded=False):
    busqueda_p = st.text_input("Buscá prácticas o especialistas...", key="search_p")
    if busqueda_p:
        if not df_practicas.empty:
            res_p = df_practicas[df_practicas.astype(str).apply(lambda row: row.str.contains(busqueda_p.lower(), case=False).any(), axis=1)]
            for i, row in res_p.iterrows():
                datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val) and str(val).strip() != ""]
                st.markdown(f'<div class="ficha ficha-practica"><span style="color:#10b981; font-weight:bold;">📑 PRÁCTICA:</span><br>{"<br>".join(datos)}</div>', unsafe_allow_html=True)
        if not df_especialistas.empty:
            res_e = df_especialistas[df_especialistas.astype(str).apply(lambda row: row.str.contains(busqueda_p.lower(), case=False).any(), axis=1)]
            for i, row in res_e.iterrows():
                datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val) and str(val).strip() != ""]
                st.markdown(f'<div class="ficha ficha-practica"><span style="color:#10b981; font-weight:bold;">👨‍⚕️ ESPECIALISTA:</span><br>{"<br>".join(datos)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 6: AGENDAS ===
st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **6. AGENDAS / MAILS**", expanded=False):
    busqueda_a = st.text_input("Buscá contactos...", key="search_a")
    if busqueda_a and not df_agendas.empty:
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(busqueda_a.lower(), case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            datos_completos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val) and str(val).strip() != ""]
            st.markdown(f'<div class="ficha ficha-agenda">{"<br>".join(datos_completos)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 7: NOVEDADES ===
st.markdown('<div class="buscador-novedades">', unsafe_allow_html=True)
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f"""
        <div class="ficha ficha-novedad">
            <span style="color:#ff4b4b; font-weight:bold;">📅 {n['fecha']}</span><br>
            <div style="font-size:18px;">{n['mensaje']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.popover("✍️ PANEL DE CONTROL"):
        clave = st.text_input("Ingresar Clave:", type="password")
        if clave == PASSWORD_JEFE:
            with st.form("form_novedad", clear_on_submit=True):
                msg = st.text_area("Nuevo comunicado:", height=150)
                if st.form_submit_button("📢 PUBLICAR"):
                    if msg:
                        ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                        nuevo_id = str(datetime.now().timestamp())
                        st.session_state.historial_novedades.insert(0, {"id": nuevo_id, "mensaje": msg, "fecha": ahora})
                        st.rerun()
            for i, n in enumerate(st.session_state.historial_novedades):
                if st.button(f"🗑️ Borrar: {n['mensaje'][:20]}...", key=f"del_{n.get('id', i)}"):
                    st.session_state.historial_novedades.pop(i)
                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
