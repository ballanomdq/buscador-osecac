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
        # Forzamos la lectura como string para evitar errores de formato y facilitar la búsqueda
        df = pd.read_csv(url, dtype=str)
        return df
    except:
        return pd.DataFrame()

# URLs de las planillas
URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_PRACTICAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0"
URL_ESPECIALISTAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576"

# IMPORTANTE: Aquí debes poner el link de "Exportar a CSV" de la PLANILLA DE EXCEL de FABA, no el link de Looker Studio.
URL_FABA_CSV = "https://docs.google.com/spreadsheets/d/1894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)
df_practicas = cargar_datos(URL_PRACTICAS_CSV)
df_especialistas = cargar_datos(URL_ESPECIALISTAS_CSV)
df_faba = cargar_datos(URL_FABA_CSV)

# Inicializar historial de novedades si no existe
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP. Las novedades aparecerán aquí.", "fecha": "22/02/2026 00:00"}
    ]

# 3. CSS: DISEÑO PERSONALIZADO
st.markdown("""
    <style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes shine {
        0% { left: -100%; opacity: 0; }
        50% { opacity: 0.6; }
        100% { left: 100%; opacity: 0; }
    }
    @keyframes pulso {
        0% { box-shadow: 0 0 0 0px rgba(255, 75, 75, 0.7); }
        100% { box-shadow: 0 0 0 12px rgba(255, 75, 75, 0); }
    }

    .stApp { 
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }
    
    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }

    .punto-alerta {
        width: 12px; height: 12px;
        background-color: #ff4b4b;
        border-radius: 50%;
        display: inline-block;
        margin-right: 12px;
        animation: pulso 1.5s infinite;
        vertical-align: middle;
    }

    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini {
        position: relative; padding: 10px 30px;
        background: rgba(56, 189, 248, 0.05);
        border-radius: 35px; border: 1px solid rgba(56, 189, 248, 0.5);
        overflow: hidden; margin-bottom: 12px; display: inline-block;
    }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff; margin: 0; z-index: 2; position: relative; }
    .shimmer-efecto {
        position: absolute; top: 0; width: 100px; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.25), transparent);
        transform: skewX(-20deg); animation: shine 4s infinite linear; z-index: 1;
    }

    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
    .ficha-tramite { border-left: 6px solid #fbbf24; }
    .ficha-agenda { border-left: 6px solid #38bdf8; }
    .ficha-practica { border-left: 6px solid #10b981; } 
    .ficha-faba { border-left: 6px solid #f97316; }
    .ficha-novedad { border-left: 6px solid #ff4b4b; margin-top: 10px; }

    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; }
    .buscador-gestion { border: 2px solid #fbbf24 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-practica { border: 2px solid #10b981 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-faba { border: 2px solid #f97316 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-agenda { border: 2px solid #38bdf8 !important; border-radius: 12px; margin-bottom: 10px; }
    .buscador-novedades { border: 2px solid #ff4b4b !important; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# === CABECERA ===
st.markdown("""
    <div class="header-master">
        <div class="capsula-header-mini">
            <div class="shimmer-efecto"></div>
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
    st.link_button("📙 LINK DIRECTO FABA", "https://lookerstudio.google.com/u/0/reporting/894fde72-fb4b-4c3d-95b0-f3ff74af5fcd/page/1VncF")
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

# === SECCIÓN 4 - BUSCADOR FABA ===
st.markdown('<div class="buscador-faba">', unsafe_allow_html=True)
with st.expander("📙 **4. BUSCADOR NOMENCLADOR FABA**", expanded=False):
    busqueda_f = st.text_input("Ingresá código o nombre del análisis (FABA)...", key="search_f")
    if busqueda_f:
        if not df_faba.empty:
            # Búsqueda por aproximación: verifica si el texto está en cualquier columna de la fila
            mask = df_faba.apply(lambda row: row.astype(str).str.contains(busqueda_f, case=False, na=False).any(), axis=1)
            res_f = df_faba[mask]
            
            if not res_f.empty:
                for i, row in res_f.iterrows():
                    datos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val) and str(val).strip() != ""]
                    st.markdown(f'<div class="ficha ficha-faba">{"<br>".join(datos)}</div>', unsafe_allow_html=True)
            else:
                st.warning("No se encontraron coincidencias en FABA.")
        else:
            st.error("Error: No se pudo cargar la base de datos de FABA. Verifica el link del CSV.")
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 5: GESTIONES ===
st.markdown('<div class="buscador-gestion">', unsafe_allow_html=True)
with st.expander("📂 **5. GESTIONES / DATOS**", expanded=False):
    busqueda_t = st.text_input("Buscá trámites...", key="search_t")
    if busqueda_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(busqueda_t.lower(), na=False)]
        for i, row in res_t.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite"><b style="color:#fbbf24;">📋 {row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 6: PRÁCTICAS Y ESPECIALISTAS ===
st.markdown('<div class="buscador-practica">', unsafe_allow_html=True)
with st.expander("🩺 **6. PRÁCTICAS Y ESPECIALISTAS**", expanded=False):
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

# === SECCIÓN 7: AGENDAS ===
st.markdown('<div class="buscador-agenda">', unsafe_allow_html=True)
with st.expander("📞 **7. AGENDAS / MAILS**", expanded=False):
    busqueda_a = st.text_input("Buscá contactos...", key="search_a")
    if busqueda_a and not df_agendas.empty:
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(busqueda_a.lower(), case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            datos_completos = [f"<b>{col}:</b> {val}" for col, val in row.items() if pd.notna(val) and str(val).strip() != ""]
            st.markdown(f'<div class="ficha ficha-agenda">{"<br>".join(datos_completos)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SECCIÓN 8: NOVEDADES ===
st.markdown('<div class="buscador-novedades">', unsafe_allow_html=True)
with st.expander("📢 **8. NOVEDADES**", expanded=True):
    st.markdown("<div><span class='punto-alerta'></span><b>ÚLTIMOS COMUNICADOS</b></div>", unsafe_allow_html=True)
    for n in st.session_state.historial_novedades:
        st.markdown(f"""
        <div class="ficha ficha-novedad">
            <span class="novedad-fecha-grande">📅 FECHA: {n['fecha']}</span>
            <div class="novedad-texto">{n['mensaje']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.popover("✍️ PANEL DE CONTROL"):
        clave = st.text_input("Ingresar Clave:", type="password")
        if clave == PASSWORD_JEFE:
            st.subheader("Publicar Novedad")
            with st.form("form_novedad", clear_on_submit=True):
                msg = st.text_area("Nuevo comunicado:", height=150)
                if st.form_submit_button("📢 PUBLICAR"):
                    if msg:
                        ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                        nuevo_id = str(datetime.now().timestamp())
                        st.session_state.historial_novedades.insert(0, {"id": nuevo_id, "mensaje": msg, "fecha": ahora})
                        st.rerun()

            st.write("---")
            st.subheader("Gestionar Historial")
            for i, n in enumerate(st.session_state.historial_novedades):
                col_txt, col_btn = st.columns([0.8, 0.2])
                with col_txt:
                    st.write(f"**{n['fecha']}**: {n['mensaje'][:40]}...")
                with col_btn:
                    if st.button("🗑️", key=f"del_{n.get('id', i)}"):
                        st.session_state.historial_novedades.pop(i)
                        st.rerun()
        elif clave != "":
            st.error("Clave incorrecta")
st.markdown('</div>', unsafe_allow_html=True)
