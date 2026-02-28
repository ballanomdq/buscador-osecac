import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNCIÓN PARA GUARDAR EN GOOGLE SHEETS ---
def editar_celda_google_sheets(sheet_url, fila_idx, columna_nombre, nuevo_valor):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open_by_url(sheet_url)
        worksheet = sh.get_worksheet(0)
        headers = worksheet.row_values(1)
        col_idx = headers.index(columna_nombre) + 1
        worksheet.update_cell(fila_idx + 2, col_idx, str(nuevo_valor))
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# --- INICIALIZACIÓN DE SESIÓN ---
if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}]

# 2. CSS - DISEÑO RADICAL "AZUL PROFUNDO" (Profundo, limpio, legible)
st.markdown("""
    <style>
    /* Ocultar elementos por defecto */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    @keyframes gradientBG { 
        0% { background-position: 0% 50%; } 
        50% { background-position: 100% 50%; } 
        100% { background-position: 0% 50%; } 
    }

    /* --- FONDO PRINCIPAL: AZUL NOCHE --- */
    .stApp { 
        background: radial-gradient(circle, #091220 0%, #050914 100%) !important;
        color: #f1f5f9 !important; /* Texto principal blanquecino */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    /* Títulos de secciones: Blanco puro y en negrita */
    .stMarkdown p, label { color: #ffffff !important; font-weight: 600 !important; }

    /* --- BOTONES (LINKS): DISEÑO DE TARJETA --- */
    /* El selector div[data-testid="stMarkdownContainer"] div.stLinkButton > a es más profundo */
    div.stLinkButton > a {
        background-color: #0b1e3b !important; /* Azul cobalto oscuro */
        color: #ffffff !important;           /* Texto siempre blanco */
        border: 2px solid #2563eb !important; /* Borde azul eléctrico */
        border-radius: 12px !important;      /* Bordes más redondeados */
        padding: 0.75rem 1.5rem !important; /* Más padding para que parezca tarjeta */
        display: block !important;           /* Que ocupen todo el ancho si es posible */
        text-align: center !important;
        text-decoration: none !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2) !important;
        font-weight: 700 !important;
        margin-bottom: 5px !important;
    }

    /* ESTADO AL PASAR EL MOUSE (HOVER): BRILLO AZUL */
    div.stLinkButton > a:hover {
        background-color: #0b1e3b !important;   /* Mismo fondo */
        color: #ffffff !important;             /* Mismo texto */
        border-color: #38bdf8 !important;      /* Borde cambia a celeste brillante */
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5) !important; /* Resplandor celeste */
        transform: translateY(-2px) !important; /* Efecto de flotación */
    }

    /* Forzar el color de texto en los botones, sin importar qué */
    div.stLinkButton > a p { color: #ffffff !important; }

    /* --- INPUTS: BLANCO CON BORDE AZUL --- */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #2563eb !important;
        border-radius: 10px !important;
        color: #000000 !important;
    }
    input { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-weight: bold !important; 
    }

    /* --- EXPANDERS: TARJETAS SEMI-TRANSPARENTES --- */
    .stExpander { 
        background-color: rgba(11, 30, 59, 0.6) !important; /* Azul cobalto transparente */
        border-radius: 15px !important; 
        margin-bottom: 15px !important; 
        border: 1px solid rgba(37, 99, 235, 0.2) !important; /* Borde azul sutil */
        backdrop-filter: blur(5px) !important; /* Efecto de desenfoque */
    }
    .stExpander p { font-size: 1.1rem !important; }

    /* --- FICHAS DE RESULTADOS --- */
    .ficha { 
        background-color: #0b1321 !important; /* Azul casi negro */
        padding: 25px !important; 
        border-radius: 15px !important; 
        margin-bottom: 12px !important; 
        border-left: 8px solid #ccc !important; /* Borde izquierdo más grueso */
        color: #e2e8f0 !important; /* Texto claro */
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    .ficha-tramite { border-left-color: #fbbf24 !important; } /* Amarillo */
    .ficha-agenda { border-left-color: #38bdf8 !important; }  /* Celeste */
    .ficha-practica { border-left-color: #10b981 !important; } /* Verde */
    .ficha-especialista { border-left-color: #8b5cf6 !important; } /* Violeta */
    .ficha-novedad { border-left-color: #ff4b4b !important; } /* Rojo */

    .block-container { max-width: 1100px !important; padding-top: 2rem !important; }
    .header-master { text-align: center; margin-bottom: 15px; }
    
    /* Cápsula del header con azul más profundo */
    .capsula-header-mini { 
        position: relative; 
        padding: 15px 40px; 
        background: rgba(37, 99, 235, 0.1); 
        border-radius: 40px; 
        border: 2px solid rgba(56, 189, 248, 0.6); 
        display: inline-block; 
    }
    .titulo-mini { font-weight: 900; font-size: 1.6rem; color: #ffffff !important; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
    
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

URLs = {
    "agendas": "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/edit",
    "tramites": "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/edit",
    "practicas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit#gid=0",
    "especialistas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/edit#gid=1119565576",
    "faba": "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/edit",
    "osecac": "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/edit"
}

df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_especialistas = cargar_datos(URLs["especialistas"])
df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])

# --- HEADER ---
st.markdown('<div class="header-master"><div class="capsula-header-mini"><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)

try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:100px; margin-bottom:25px;"></center>', unsafe_allow_html=True)
except: pass

st.markdown("<hr style='border:1px solid rgba(255,255,255,0.1)'>", unsafe_allow_html=True)

# 1. NOMENCLADORES
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    
    # FILA: Lápiz - Check - Palabra
    c1, c2, c3, c4 = st.columns([0.6, 2, 0.6, 2])
    
    with c1:
        pop_f = st.popover("✏️")
        cl_f = pop_f.text_input("Clave FABA:", type="password", key="p_f")
    with c2:
        sel_faba = st.checkbox("FABA", value=True, key="chk_f")
        
    with c3:
        pop_o = st.popover("✏️")
        cl_o = pop_o.text_input("Clave OSECAC:", type="password", key="p_o")
    with c4:
        sel_osecac = st.checkbox("OSECAC", value=False, key="chk_o")

    # Lógica de selección
    opcion = "OSECAC" if sel_osecac else "FABA"
    cl_actual = cl_o if sel_osecac else cl_f
    df_u = df_osecac_busq if sel_osecac else df_faba
    url_u = URLs["osecac"] if sel_osecac else URLs["faba"]

    bus_nom = st.text_input(f"🔍 Buscar en {opcion}...", key="bus_n")
    
    if bus_nom:
        mask = df_u.apply(lambda row: all(p in str(row).lower() for p in bus_nom.lower().split()), axis=1)
        for i, row in df_u[mask].iterrows():
            st.markdown(f'<div class="ficha">{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
            
            if cl_actual == "*":
                with st.expander(f"📝 Editar fila {i}"):
                    c_edit = st.selectbox("Columna:", row.index, key=f"sel_{i}")
                    v_edit = st.text_input("Nuevo valor:", value=row[c_edit], key=f"val_{i}")
                    if st.button("Guardar Cambios", key=f"btn_{i}"):
                        if editar_celda_google_sheets(url_u, i, c_edit, v_edit):
                            st.success("¡Sincronizado!")
                            st.cache_data.clear()
                            st.rerun()

# 2. PEDIDOS
with st.expander("📝 **2. PEDIDOS**", expanded=False):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")
    st.link_button("📊 ESTADO DE PEDIDOS", "https://lookerstudio.google.com/reporting/21d6f3bf-24c1-4621-903c-8bc80f57fc84")

# 3. PÁGINAS ÚTILES
with st.expander("🌐 **3. PÁGINAS ÚTILES**", expanded=False):
    cols = st.columns(2)
    with cols[0]:
        st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
        st.link_button("🩺 GMS WEB", "https://www.gmssa.com/sistema-de-administracion-de-empresas-de-salud-s-a-e-s/")
        st.link_button("🆔 ANSES - CODEM", "https://servicioswww.anses.gob.ar/ooss2/")
    with cols[1]:
        st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
        st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")
        st.link_button("🧪 SISA", "https://sisa.msal.gov.ar/sisa/")

# 4. GESTIONES
with st.expander("📂 **4. GESTIONES / DATOS**", expanded=False):
    bus_t = st.text_input("Buscá trámites...", key="bus_t")
    if bus_t and not df_tramites.empty:
        res = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, row in res.iterrows():
            st.markdown(f'<div class="ficha ficha-tramite">📋 <b>{row["TRAMITE"]}</b><br>{row["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# 5. PRÁCTICAS Y ESPECIALISTAS
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**", expanded=False):
    bus_p = st.text_input("Buscá prácticas o especialistas...", key="bus_p")
    if bus_p:
        rp = df_practicas[df_practicas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in rp.iterrows():
            st.markdown(f'<div class="ficha ficha-practica">📑 <b>PRÁCTICA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
        re = df_especialistas[df_especialistas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in re.iterrows():
            st.markdown(f'<div class="ficha ficha-especialista">👨‍⚕️ <b>ESPECIALISTA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)

# 6. AGENDAS
with st.expander("📞 **6. AGENDAS / MAILS**", expanded=False):
    bus_a = st.text_input("Buscá contactos...", key="bus_a")
    if bus_a and not df_agendas.empty:
        res = df_agendas[df_agendas.astype(str).apply(lambda r: r.str.contains(bus_a, case=False, na=False).any(), axis=1)]
        for i, row in res.iterrows():
            datos = [f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)]
            st.markdown(f'<div class="ficha ficha-agenda">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

# 7. NOVEDADES
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha ficha-novedad">📅 {n["fecha"]}<br>{n["mensaje"]}</div>', unsafe_allow_html=True)
    with st.popover("✍️ PANEL"):
        if st.text_input("Clave de edición:", type="password", key="ed_pass") == "2026":
            with st.form("n_form", clear_on_submit=True):
                m = st.text_area("Nuevo comunicado:")
                if st.form_submit_button("PUBLICAR"):
                    st.session_state.historial_novedades.insert(0, {"id": str(time.time()), "mensaje": m, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")})
                    st.rerun()
