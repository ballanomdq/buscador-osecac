import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDP", layout="wide")

# 2. CSS: DISEÑO Y CENTRADO
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e2e8f0; }
    .block-container { max-width: 1200px !important; padding-top: 2rem !important; }
    .cabecera-centrada { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; margin-bottom: 20px; }
    [data-testid="stImage"] img { mix-blend-mode: screen; filter: brightness(1.1); }

    /* ESTILO BOTONES */
    div.stLinkButton > a {
        border-radius: 6px !important; font-size: 11px !important; font-weight: 700 !important;
        text-transform: uppercase !important; letter-spacing: 1.5px !important;
        padding: 10px 15px !important; display: inline-block !important;
        width: 100% !important; text-align: center !important; transition: all 0.3s ease !important;
    }

    /* COLORES BOTONES */
    div.stLinkButton > a[href*="notebook"], div.stLinkButton > a[href*="reporting"] { color: #38bdf8 !important; border: 1px solid #00529b !important; background-color: rgba(0, 82, 155, 0.2) !important; }
    div.stLinkButton > a[href*="Aj2BBSfXFwXR"] { color: #ff85a2 !important; border: 1px solid #ff85a2 !important; background-color: rgba(255, 133, 162, 0.1) !important; }
    div.stLinkButton > a[href*="MlwRSUf6dAww"] { color: #2dd4bf !important; border: 1px solid #2dd4bf !important; background-color: rgba(45, 212, 191, 0.1) !important; }
    div.stLinkButton > a[href*="21d6f3bf-24c1"] { color: #a78bfa !important; border: 1px solid #a78bfa !important; background-color: rgba(167, 139, 250, 0.1) !important; }

    .stExpander { background-color: rgba(23, 32, 48, 0.8) !important; border: 1px solid #1e293b !important; border-radius: 10px !important; }
    h1 { font-weight: 900; color: #e2e8f0; margin-bottom: 0px !important; font-size: 2.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown('<div class="cabecera-centrada">', unsafe_allow_html=True)
st.title("OSECAC MDP / AGENCIAS")
try: st.image("LOGO.jpg", width=95)
except: pass
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# MENÚS
# ==========================================
with st.expander("NOMENCLADORES"):
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    with c2: st.link_button("NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
    with c3: st.link_button("NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with st.expander("PEDIDOS"):
    c_l, c_s, c_e = st.columns(3)
    with c_l: st.link_button("PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    with c_s: st.link_button("PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    with c_e: st.link_button("ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF&disable_select=true")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BUSCADOR CON CLIC DIRECTO
# ==========================================
@st.cache_data(ttl=600)
def cargar_datos():
    try:
        url = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
        return pd.read_csv(url)
    except: return pd.DataFrame()

df = cargar_datos()

st.subheader("AGENDAS/MAILS")
pregunta = st.text_input("Buscador", placeholder="Escribí para buscar...", label_visibility="collapsed")

if pregunta:
    pregunta = pregunta.strip()
    res = df[df.astype(str).apply(lambda row: row.str.contains(pregunta, case=False, na=False).any(), axis=1)]
    
    if not res.empty:
        # AQUÍ ESTÁ EL TRUCO: Configuramos las columnas como Enlaces (LinkColumn)
        st.data_editor(
            res,
            use_container_width=True,
            hide_index=True,
            disabled=True,
            column_config={
                "Mail": st.column_config.LinkColumn("Mail", display_text="Enviar Mail"),
                "Direccion": st.column_config.LinkColumn("Direccion", display_text="Ver Mapa"),
                "Web": st.column_config.LinkColumn("Web")
            }
        )
    else:
        st.info("Sin resultados.")
else:
    st.write("Escribí arriba para buscar.")
    
