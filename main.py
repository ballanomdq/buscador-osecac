import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDP - Gestión Operativa", layout="wide")

# 2. CSS PERSONALIZADO: LIMPIO, MODERNO Y TECNOLÓGICO
st.markdown("""
    <style>
    /* Fondo con identidad OSECAC */
    .stApp { 
        background: radial-gradient(circle at top left, #0e1726, #050a12); 
        color: #e2e8f0; 
    }
    
    /* Animación de entrada suave */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .block-container { 
        animation: fadeIn 0.6s ease-out;
        max-width: 1200px !important; 
    }

    /* Cabecera Médica/Tecnológica */
    .cabecera-box {
        background: linear-gradient(135deg, rgba(0, 82, 155, 0.2) 0%, rgba(0, 0, 0, 0) 100%);
        border-left: 5px solid #00529b;
        padding: 25px;
        border-radius: 0 15px 15px 0;
        margin-bottom: 30px;
        backdrop-filter: blur(5px);
    }

    /* Botones Estilo 'Health-Tech' */
    div.stLinkButton > a {
        border-radius: 10px !important; 
        font-size: 11px !important; 
        font-weight: 700 !important;
        text-transform: uppercase !important; 
        letter-spacing: 1px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    div.stLinkButton > a:hover {
        transform: scale(1.02) !important;
        filter: brightness(1.2);
        box-shadow: 0 5px 15px rgba(0, 82, 155, 0.3) !important;
    }

    /* Colores según identidad */
    /* Nomencladores - Azul OSECAC */
    div.stLinkButton > a[href*="notebook"], div.stLinkButton > a[href*="reporting"] { 
        color: #ffffff !important; background-color: #00529b !important; border: none !important; 
    }
    /* Pedidos - Estilo Salud (Suave) */
    div.stLinkButton > a[href*="Aj2BBSfXFwXR"], div.stLinkButton > a[href*="MlwRSUf6dAww"], div.stLinkButton > a[href*="21d6f3bf-24c1"] { 
        color: #ffffff !important; background-color: #10b981 !important; border: none !important; 
    }
    /* Páginas - Amarillo Institucional */
    div.stLinkButton > a[href*="sssalud"], div.stLinkButton > a[href*="anses"], div.stLinkButton > a[href*="afip"], 
    div.stLinkButton > a[href*="osecac"], div.stLinkButton > a[href*="gmssa"], div.stLinkButton > a[href*="kairos"], 
    div.stLinkButton > a[href*="alfabeta"], div.stLinkButton > a[href*="SolicitudTramitesMpp"] { 
        color: #000000 !important; background-color: #fbbf24 !important; border: none !important; 
    }

    /* Expanders Modernos */
    .stExpander { 
        border: 1px solid rgba(255, 255, 255, 0.05) !important; 
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }

    /* Input de búsqueda */
    .stTextInput > div > div > input { 
        background-color: #1a2234 !important; 
        border: 1px solid #00529b !important;
        border-radius: 12px !important;
        height: 50px !important;
    }
    
    h1 { color: #ffffff; font-size: 2.2rem !important; margin-bottom: 0px !important; }
    h2, h3 { color: #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
col_header_1, col_header_2 = st.columns([4, 1])

with col_header_1:
    st.markdown("""
        <div class="cabecera-box">
            <h1>OSECAC MDP / AGENCIAS</h1>
            <p style='color: #38bdf8; font-weight: 600; font-size: 1rem; margin-top: 5px;'>
                Portal de Gestión Sanitaria y Consultas Operativas
            </p>
        </div>
        """, unsafe_allow_html=True)

with col_header_2:
    try: st.image("LOGO.jpg", width=120)
    except: pass

st.markdown("---")

# ==========================================
# SECCIÓN PRINCIPAL: NOMENCLADORES Y PEDIDOS
# ==========================================
col_top_1, col_top_2 = st.columns(2)

with col_top_1:
    st.markdown("### 📂 NOMENCLADORES")
    with st.container():
        st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
        st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
        st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with col_top_2:
    st.markdown("### 📝 GESTIÓN DE PEDIDOS")
    with st.container():
        st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
        st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
        st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN: ENLACES EXTERNOS
# ==========================================
with st.expander("🌐 ACCESOS RÁPIDOS A PORTALES OFICIALES", expanded=False):
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
# SECCIÓN: BUSCADOR DE AGENDAS (DATA)
# ==========================================
st.markdown("### 🔍 CENTRAL DE CONTACTOS / AGENDAS")

@st.cache_data(ttl=600)
def cargar_datos():
    try:
        url = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

df = cargar_datos()
pregunta = st.text_input("Buscador", placeholder="Escribí el nombre de una oficina, farmacia o localidad...", label_visibility="collapsed")

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
                "MAIL/DIR": st.column_config.LinkColumn("📧 CONTACTO / LINK", width="large"),
                "DIRECCION": st.column_config.LinkColumn("📍 DIRECCIÓN", width="large"),
            }
        )
    else:
        st.warning("No se encontraron resultados para tu búsqueda.")
else:
    st.info("Utilizá el cuadro de búsqueda superior para encontrar información de contacto.")

# Pie de página simple
st.markdown("""
    <div style='text-align: center; color: #475569; font-size: 0.8rem; margin-top: 50px;'>
        Sistema de Apoyo Interno - OSECAC Mar del Plata
    </div>
    """, unsafe_allow_html=True)
