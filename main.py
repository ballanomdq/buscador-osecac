import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)

# 3. CSS: CENTRADO TOTAL, CARTEL CHICO Y MARGEN SUPERIOR
st.markdown("""
    <style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes shine {
        0% { left: -100%; opacity: 0; }
        50% { opacity: 0.7; }
        100% { left: 100%; opacity: 0; }
    }

    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    .block-container { max-width: 1000px !important; padding-top: 1rem !important; }

    /* CONTENEDOR MAESTRO DE CABECERA */
    .cabecera-bloque {
        display: flex;
        flex-direction: column;
        align-items: center; /* ESTO CENTRA TODO */
        justify-content: center;
        width: 100%;
        margin-top: 50px; /* MARGEN DE SEPARACIÓN DESDE ARRIBA */
        margin-bottom: 30px;
    }

    /* Cartel OSECAC más chico */
    .capsula-header-mini {
        position: relative;
        padding: 6px 20px;
        background: rgba(56, 189, 248, 0.05);
        border-radius: 25px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        overflow: hidden;
        margin-bottom: 15px;
    }

    .titulo-mini {
        font-family: 'sans-serif';
        font-weight: 800;
        font-size: 1.2rem; /* TAMAÑO MÁS CHICO */
        color: #e2e8f0;
        margin: 0;
        z-index: 2;
        position: relative;
    }

    .shimmer-efecto {
        position: absolute;
        top: 0;
        width: 80px;
        height: 100%;
        background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.3), transparent);
        transform: skewX(-25deg);
        animation: shine 4s infinite linear;
        z-index: 1;
    }

    .subtitulo-lema {
        color: #94a3b8;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 0;
        text-align: center;
        width: 100%;
    }

    /* Logo centrado debajo del lema */
    .logo-final {
        margin-top: 15px;
        display: flex;
        justify-content: center;
    }

    /* FICHAS ORIGINALES */
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
    .ficha-tramite { border-left: 6px solid #fbbf24; }
    .titulo-tramite { color: #fbbf24; font-size: 1.4rem; font-weight: bold; margin-bottom: 10px; }
    .ficha-agenda { border-left: 6px solid #38bdf8; }
    .titulo-agenda { color: #38bdf8; font-size: 1.3rem; font-weight: bold; margin-bottom: 8px; }
    .cuerpo-ficha { white-space: pre-wrap; font-size: 15px; line-height: 1.6; color: #f1f5f9; }

    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA CENTRADA TOTAL ===
st.markdown('<div class="cabecera-bloque">', unsafe_allow_html=True)

# 1. El Cartel (Más chico)
st.markdown("""
    <div class="capsula-header-mini">
        <div class="shimmer-efecto"></div>
        <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
    </div>
    """, unsafe_allow_html=True)

# 2. La frase (Centrada)
st.markdown('<p class="subtitulo-lema">PORTAL DE APOYO PARA COMPAÑEROS</p>', unsafe_allow_html=True)

# 3. El Logo (Debajo y centrado)
st.markdown('<div class="logo-final">', unsafe_allow_html=True)
try:
    st.image("LOGO1.png", width=80)
except:
    st.write("")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Cierra cabecera-bloque

st.markdown("---")

# ==========================================
# SECCIONES: 1, 2 y 3
# ==========================================
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

# ==========================================
# SECCIÓN 4: GESTIONES (BUSCADOR AMARILLO)
# ==========================================
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    busqueda_t = st.text_input("Buscá trámites, prácticas o prestadores...", key="search_tramites")
    if busqueda_t:
        t = busqueda_t.lower().strip()
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(t, na=False) | df_tramites['PALABRA CLAVE'].str.lower().str.contains(t, na=False)]
        if not res_t.empty:
            for i, row in res_t.iterrows():
                st.markdown(f'<div class="ficha ficha-tramite"><div class="titulo-tramite">📋 {row["TRAMITE"]}</div><div class="cuerpo-ficha">{row["DESCRIPCIÓN Y REQUISITOS"]}</div></div>', unsafe_allow_html=True)
                st.link_button(f"📂 ABRIR CARPETA DE {row['TRAMITE']}", str(row['LINK CARPETA / ARCHIVOS']))
                st.markdown("<br>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECCIÓN 5: AGENDAS (BUSCADOR CELESTE)
# ==========================================
st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **5. AGENDAS / MAILS**", expanded=False):
    busqueda_a = st.text_input("Buscá un contacto, delegación o mail...", key="search_agendas")
    if busqueda_a:
        q = busqueda_a.lower().strip()
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(q, case=False).any(), axis=1)]
        if not res_a.empty:
            for i, row in res_a.iterrows():
                contenido_agenda = "".join([f"**{col}:** {row[col]}  \n" for col in df_agendas.columns if pd.notna(row[col])])
                st.markdown(f'<div class="ficha ficha-agenda"><div class="titulo-agenda">👤 {row.iloc[0]}</div><div class="cuerpo-ficha">{contenido_agenda}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
