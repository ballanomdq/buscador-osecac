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

# 3. CSS PERSONALIZADO (Mantenemos tus fichas espectaculares)
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
    
    .block-container { max-width: 1200px !important; padding-top: 1.5rem !important; }

    .cabecera-centrada { 
        display: flex; flex-direction: column; align-items: center; 
        justify-content: center; text-align: center; width: 100%; 
    }
    
    .titulo-principal { font-weight: 900; color: #e2e8f0; font-size: 2.2rem !important; margin-bottom: 5px !important; }
    .subtitulo-equipo { color: #94a3b8; font-size: 14px; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 15px; }

    .logo-container img {
        max-width: 120px !important; height: auto;
        mix-blend-mode: screen; filter: brightness(1.1);
        margin: 10px auto; display: block;
    }

    .ficha-tramite {
        background-color: rgba(23, 32, 48, 0.9);
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #fbbf24;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .ficha-titulo { color: #fbbf24; font-size: 1.5rem; font-weight: bold; margin-bottom: 12px; }
    .ficha-contenido { white-space: pre-wrap; font-size: 15px; line-height: 1.6; color: #f1f5f9; }

    div.stLinkButton > a {
        border-radius: 8px !important; font-size: 12px !important; font-weight: 700 !important;
        text-transform: uppercase !important; letter-spacing: 1.2px !important;
        padding: 12px !important; width: 100% !important; text-align: center !important;
    }
    
    /* Estilo especial para los Expanders */
    .stExpander { 
        background-color: rgba(30, 41, 59, 0.6) !important; 
        border: 1px solid #fbbf24 !important; 
        border-radius: 12px !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA Y LOGO ===
st.markdown(f"""
    <div class="cabecera-centrada">
        <div class="titulo-principal">OSECAC MDP / AGENCIAS</div>
        <div class="subtitulo-equipo">PORTAL DE APOYO PARA COMPAÑEROS</div>
        <div class="logo-container">
            <img src="https://raw.githubusercontent.com/ballanomdq/buscador-osecac/main/LOGO.jpg" alt="Logo">
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SECCIÓN 1: BUSCADOR DE TRÁMITES (DENTRO DE BOTÓN/EXPANDER)
# ==========================================
with st.expander("🔍 **HACÉ CLIC AQUÍ PARA BUSCAR UN TRÁMITE**", expanded=False):
    busqueda_t = st.text_input("Escribí palabras relacionadas (ej: 'sordera', 'renuncia', 'leche')...", key="search_tramites")

    if busqueda_t:
        t = busqueda_t.lower().strip()
        res_t = df_tramites[
            df_tramites['TRAMITE'].str.lower().str.contains(t, na=False) | 
            df_tramites['PALABRA CLAVE'].str.lower().str.contains(t, na=False)
        ]
        
        if not res_t.empty:
            for i, row in res_t.iterrows():
                st.markdown(f"""
                    <div class="ficha-tramite">
                        <div class="ficha-titulo">📋 {row['TRAMITE']}</div>
                        <div class="ficha-contenido">{row['DESCRIPCIÓN Y REQUISITOS']}</div>
                    </div>
                """, unsafe_allow_html=True)
                st.link_button(f"📂 ABRIR CARPETA DE {row['TRAMITE']}", str(row['LINK CARPETA / ARCHIVOS']))
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("No se encontró ningún trámite con esa palabra.")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN 2: MENÚS DE ACCESO RÁPIDO
# ==========================================
col_m1, col_m2 = st.columns(2)
with col_m1:
    with st.expander("📂 NOMENCLADORES"):
        st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
        st.link_button("📙 NOMENCLADOR FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
        st.link_button("📗 NOMENCLADOR OSECAC", "https://lookerstudio.google.com/u/0/reporting/43183d76-61b2-4875-a2f8-341707dcac22/page/1VncF")

with col_m2:
    with st.expander("📝 PEDIDOS"):
        st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
        st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
        st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/u/0/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84/page/OoHdF")

with st.expander("🌐 PAGINAS ÚTILES"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🏛️ AFIP", "https://www.afip.gob.ar/")
    with c2:
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
    with c3:
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com.ar/")
        st.link_button("🧪 PORTAL MEDICAMENTOS", "http://servicios-externos.osecac.org.ar/SolicitudTramitesMpp/tramites")

st.markdown("---")

# ==========================================
# SECCIÓN 3: BUSCADOR DE AGENDAS / MAILS
# ==========================================
st.subheader("📞 AGENDAS / MAILS")
busqueda_a = st.text_input("Buscá un contacto, mail o delegación...", key="search_agendas")

if busqueda_a:
    q = busqueda_a.lower().strip()
    res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(q, case=False).any(), axis=1)]
    
    if not res_a.empty:
        st.dataframe(res_a, use_container_width=True, hide_index=True)
    else:
        st.info("No hay contactos que coincidan.")
