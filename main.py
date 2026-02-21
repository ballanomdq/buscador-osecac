import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDP", layout="wide")

# 2. CSS: DISEÑO ORIGINAL CON DEGRADADO SUTIL
st.markdown("""
    <style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    .block-container { max-width: 1250px !important; padding-top: 1.5rem !important; }
    
    .cabecera-centrada { 
        display: flex; flex-direction: column; align-items: center; 
        justify-content: center; text-align: center; width: 100%; margin-bottom: 10px; 
    }
    
    .subtitulo-equipo {
        color: #94a3b8; /* Azul clarito elegante */
        font-size: 15px;
        font-weight: 400;
        margin-top: -5px;
        margin-bottom: 15px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    [data-testid="stImage"] img { mix-blend-mode: screen; filter: brightness(1.1); margin-top: 5px; }
    
    div.stLinkButton > a {
        border-radius: 6px !important; font-size: 11px !important; font-weight: 700 !important;
        text-transform: uppercase !important; letter-spacing: 1.5px !important;
        padding: 10px 15px !important; display: inline-block !important;
        width: 100% !important; text-align: center !important; transition: all 0.3s ease !important;
    }
    
    div.stLinkButton > a[href*="notebook"], div.stLinkButton > a[href*="reporting"] { color: #38bdf8 !important; border: 1px solid #00529b !important; background-color: rgba(0, 82, 155, 0.2) !important; }
    div.stLinkButton > a[href*="Aj2BBSfXFwXR"] { color: #ff85a2 !important; border: 1px solid #ff85a2 !important; background-color: rgba(255, 133, 162, 0.1) !important; }
    div.stLinkButton > a[href*="MlwRSUf6dAww"] { color: #2dd4bf !important; border: 1px solid #2dd4bf !important; background-color: rgba(45, 212, 191, 0.1) !important; }
    div.stLinkButton > a[href*="21d6f3bf-24c1"] { color: #a78bfa !important; border: 1px solid #a78bfa !important; background-color: rgba(167, 139, 250, 0.1) !important; }
    div.stLinkButton > a[href*="sssalud"], div.stLinkButton > a[href*="anses"], div.stLinkButton > a[href*="afip"], 
    div.stLinkButton > a[href*="osecac"], div.stLinkButton > a[href*="gmssa"], div.stLinkButton > a[href*="kairos"], div.stLinkButton > a[href*="alfabeta"], div.stLinkButton > a[href*="SolicitudTramitesMpp"] { 
        color: #fbbf24 !important; border: 1px solid #b45309 !important; background-color: rgba(180, 83, 9, 0.1) !important; 
    }
    
    .stExpander { background-color: rgba(23, 32, 48, 0.8) !important; border: 1px solid #1e293b !important; border-radius: 10px !important; }
    .stTextInput > div > div > input { background-color: #172030 !important; color: white !important; height: 45px !important; }
    h1 { font-weight: 900; color: #e2e8f0; text-align: center; margin-bottom: 0px !important; font-size: 2.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown('<div class="cabecera-centrada">', unsafe_allow_html=True)
st.title("OSECAC MDP / AGENCIAS")
st.markdown('<div class="subtitulo-equipo">PORTAL DE APOYO PARA COMPAÑEROS</div>', unsafe_allow_html=True)
try: st.image("LOGO.jpg", width=100)
except: pass
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# MENÚS PRINCIPALES
# ==========================================
col1, col2 = st.columns(2)
with col1:
    with st.expander("📂 NOMENCLADORES"):
        st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
        st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
        st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with col2:
    with st.expander("📝 PEDIDOS"):
        st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
        st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
        st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true")

# ==========================================
# SECCIÓN: PAGINAS
# ==========================================
with st.expander("🌐 PAGINAS"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.link_button("🏥 SSSALUD - PADRÓN", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🏛️ AFIP", "https://www.afip.gob.ar/")
        st.link_button("💊 VADEMÉCUM OSECAC", "https://www.osecac.org.ar/Vademecus")
    with c2:
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
        st.link_button("🏢 OSECAC WEB", "https://www.osecac.org.ar/")
        st.link_button("📖 PRECIOS ALFABETA", "https://www.alfabeta.net/vademecum/")
    with c3:
        st.link_button("❌ CERTIF. NEGATIVA", "https://servicioswww.anses.gob.ar/censite/index.aspx")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com.ar/")
    with c4:
        st.link_button("💻 PORTAL SAES", "http://portal.gmssa.com.ar/saes/Login.aspx")
        st.link_button("🧪 PORTAL MEDICAMENTOS", "http://servicios-externos.osecac.org.ar/SolicitudTramitesMpp/tramites")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BUSCADOR AGENDAS
# ==========================================
@st.cache_data(ttl=600)
def cargar_datos():
    try:
        url = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = cargar_datos()
st.subheader("AGENDAS/MAILS")
pregunta = st.text_input("Buscador", placeholder="Escribí para buscar...", label_visibility="collapsed")

if pregunta:
    pregunta = pregunta.strip()
    res = df[df.astype(str).apply(lambda row: row.str.contains(pregunta, case=False, na=False).any(), axis=1)]
    if not res.empty:
        st.data_editor(
            res,
            use_container_width=True,
            hide_index=True,
            disabled=True,
            height=450,
            column_config={
                "MAIL/DIR": st.column_config.LinkColumn("MAIL/DIR", width="large"),
                "DIRECCION": st.column_config.LinkColumn("DIRECCION", width="large"),
            }
        )
    else:
        st.info("Sin coincidencias.")
else:
    st.write("Escribí arriba para filtrar los datos.")
