import streamlit as st
import pandas as pd
import base64
import time
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="OSECAC MDP - Portal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACIÓN DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'animado' not in st.session_state:
    st.session_state.animado = False
if 'toques' not in st.session_state:
    st.session_state.toques = []
if 'ultimo_toque' not in st.session_state:
    st.session_state.ultimo_toque = time.time()

# 2. CSS COMPLETO (Tu estética original + arreglos + texto blanco en títulos y labels)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes shine { 0% { left: -100%; opacity: 0; } 50% { opacity: 0.6; } 100% { left: 100%; opacity: 0; } }

    .stApp { 
        background-color: #0b0e14;
        background: linear-gradient(-45deg, #0b0e14, #111827, #0b0e14, #1e1b2e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0; 
    }

    /* --- NUEVAS REGLAS PARA TEXTOS BLANCOS (ETIQUETAS Y TÍTULOS) --- */
    /* Esta regla hace que todas las etiquetas (labels) y textos de ayuda sean blancos */
    label, .stRadio label, .stRadio div[data-testid="stMarkdown"] p, .stTextInput label, .st-emotion-cache-15ruxrl, .st-emotion-cache-1v0mbdj p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Si el texto del placeholder "🔍 Buscar en nomencladores..." no se vuelve blanco con la regla anterior, forzamos el color del placeholder */
    input::placeholder {
        color: #d1d5db !important;  /* Un gris muy claro, casi blanco */
        opacity: 1 !important;
    }
    
    /* Para asegurar que el texto de los radios "FABA" y "OSECAC" sea blanco */
    .stRadio div[role="radiogroup"] label p {
        color: #ffffff !important;
    }
    
    /* Para el título "Origen:" específicamente, si no hereda el blanco */
    .stRadio label {
        color: #ffffff !important;
    }
    /* -------------------------------------------------------------- */

    /* BUSCADOR BLANCO/NEGRO - Esto solo afecta al INPUT, no a las labels */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
    }
    /* Este es el color del TEXTO DENTRO del input. Se queda en negro. */
    input { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-weight: bold !important; 
    }

    /* ESTÉTICA DE FICHAS */
    .block-container { max-width: 1000px !important; padding-top: 1.5rem !important; }
    .header-master { text-align: center; margin-bottom: 10px; }
    .capsula-header-mini { position: relative; padding: 10px 30px; background: rgba(56, 189, 248, 0.05); border-radius: 35px; border: 1px solid rgba(56, 189, 248, 0.5); display: inline-block; }
    .titulo-mini { font-weight: 800; font-size: 1.4rem; color: #ffffff !important; margin: 0; }
    .shimmer-efecto { position: absolute; top: 0; width: 100px; height: 100%; background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.25), transparent); transform: skewX(-20deg); animation: shine 4s infinite linear; }
    
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; border-left: 6px solid #ccc; color: #ffffff !important; }
    .ficha-tramite { border-left-color: #fbbf24; }
    .ficha-agenda { border-left-color: #38bdf8; }
    .ficha-practica { border-left-color: #10b981; } 
    .ficha-especialista { border-left-color: #8b5cf6; }
    .ficha-novedad { border-left-color: #ff4b4b; }

    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; margin-bottom: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    
    /* ESTILOS PARA TAP SEQUENCE */
    .logo-tap-container {
        cursor: pointer;
        transition: all 0.1s;
        animation: breathe 3s infinite;
        text-align: center;
        margin: 30px 0;
    }
    .logo-tap-container:active {
        transform: scale(0.95);
    }
    @keyframes breathe {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.9; }
        100% { transform: scale(1); opacity: 1; }
    }
    .tap-indicator {
        display: flex;
        gap: 15px;
        justify-content: center;
        margin: 30px 0;
    }
    .tap-dot {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: #334155;
        transition: all 0.3s ease;
        border: 2px solid #38bdf8;
    }
    .tap-dot.active {
        background: #38bdf8;
        box-shadow: 0 0 20px #38bdf8;
        transform: scale(1.2);
    }
    .mensaje-secreto {
        color: #94a3b8;
        text-align: center;
        font-size: 0.9rem;
        margin-top: 20px;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PASO 1: LOGIN CON TAP SEQUENCE ---
if not st.session_state.autenticado:
    _, col2, _ = st.columns([1,2,1])
    with col2:
        st.markdown('<br><br>', unsafe_allow_html=True)
        
        # Secuencia secreta: 3 toques + pausa + 2 toques
        SECUENCIA = [3, 2]  # Puedes cambiar la secuencia aquí
        
        try:
            with open("LOGO1.png", "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            
            st.markdown("<h3 style='text-align:center; color:#ffffff; margin-bottom:30px;'>🔐 ACCESO TÁCTIL</h3>", unsafe_allow_html=True)
            
            # Logo clickeable
            logo_clicked = st.button("", key="logo_tap", help="TOCÁ EL LOGO EN SECUENCIA")
            
            st.markdown(f'''
            <div class="logo-tap-container">
                <img src="data:image/png;base64,{img_b64}" style="width:150px;">
            </div>
            ''', unsafe_allow_html=True)
            
            if logo_clicked:
                ahora = time.time()
                
                # Si pasó más de 2 segundos, reiniciar secuencia
                if ahora - st.session_state.ultimo_toque > 2:
                    st.session_state.toques = []
                
                st.session_state.toques.append(ahora)
                st.session_state.ultimo_toque = ahora
            
            # Mostrar indicadores visuales según la secuencia
            total_dots = sum(SECUENCIA)
            dots_html = []
            
            for i in range(total_dots):
                if i < len(st.session_state.toques):
                    dots_html.append('<span class="tap-dot active"></span>')
                else:
                    dots_html.append('<span class="tap-dot"></span>')
            
            st.markdown(f'<div class="tap-indicator">{"".join(dots_html)}</div>', unsafe_allow_html=True)
            
            # Mostrar mensaje según estado
            if len(st.session_state.toques) == 0:
                st.markdown('<p class="mensaje-secreto">👆 TOCÁ EL LOGO 3 VECES</p>', unsafe_allow_html=True)
            elif len(st.session_state.toques) < SECUENCIA[0]:
                restantes = SECUENCIA[0] - len(st.session_state.toques)
                st.markdown(f'<p class="mensaje-secreto">👉 {restantes} toques más...</p>', unsafe_allow_html=True)
            elif len(st.session_state.toques) == SECUENCIA[0]:
                st.markdown('<p class="mensaje-secreto" style="color:#fbbf24;">⏸️ PAUSA UN MOMENTO...</p>', unsafe_allow_html=True)
            elif len(st.session_state.toques) > SECUENCIA[0]:
                segundo_grupo = len(st.session_state.toques) - SECUENCIA[0]
                if segundo_grupo < SECUENCIA[1]:
                    restantes = SECUENCIA[1] - segundo_grupo
                    st.markdown(f'<p class="mensaje-secreto" style="color:#38bdf8;">👉 {restantes} toques finales...</p>', unsafe_allow_html=True)
            
            # Verificar secuencia completa
            if len(st.session_state.toques) == total_dots:
                # Verificar que los primeros 3 toques fueron rápidos
                primer_grupo = st.session_state.toques[:SECUENCIA[0]]
                segundo_grupo = st.session_state.toques[SECUENCIA[0]:]
                
                # Verificar pausa (al menos 0.5 seg entre grupos)
                pausa = segundo_grupo[0] - primer_grupo[-1]
                
                if pausa > 0.5 and pausa < 3:  # Pausa razonable
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("❌ Secuencia incorrecta")
                    st.session_state.toques = []
                    time.sleep(1)
                    st.rerun()
            
            # Botón para reiniciar manualmente
            if st.button("🔄 REINICIAR", use_container_width=True):
                st.session_state.toques = []
                st.rerun()
                
        except Exception as e:
            st.error("⚠️ Esperando archivo LOGO1.png...")
            st.markdown("<p style='text-align:center;'>Para probar, toca donde iría el logo</p>", unsafe_allow_html=True)
            
            # Versión sin logo para prueba
            if st.button("👆 TOCÁ AQUÍ PARA SIMULAR", use_container_width=True, type="primary"):
                # Simulación simple para prueba
                st.session_state.autenticado = True
                st.rerun()
    
    st.stop()

# --- PASO 2: ANIMACIÓN DE CARGA ---
if not st.session_state.animado:
    ph = st.empty()
    with ph.container():
        st.markdown("<br><br><h2 style='text-align:center; color:#38bdf8;'>🚀 INICIANDO PROTOCOLO MDP...</h2>", unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            bar.progress(i + 1)
    st.session_state.animado = True
    ph.empty()

# --- PASO 3: CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv' if '/edit' in url else url
        return pd.read_csv(csv_url, dtype=str)
    except: return pd.DataFrame()

URLs = {
    "agendas": "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv",
    "tramites": "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv",
    "practicas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0",
    "especialistas": "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576",
    "faba": "https://docs.google.com/spreadsheets/d/1GyMKYmZt_w3_1GNO-aYQZiQgIK4Bv9_N4KCnWHq7ak0/export?format=csv",
    "osecac": "https://docs.google.com/spreadsheets/d/1yUhuOyvnuLXQSzCGxEjDwCwiGE1RewoZjJWshZv-Kr0/export?format=csv"
}

df_agendas = cargar_datos(URLs["agendas"])
df_tramites = cargar_datos(URLs["tramites"])
df_practicas = cargar_datos(URLs["practicas"])
df_especialistas = cargar_datos(URLs["especialistas"])
df_faba = cargar_datos(URLs["faba"])
df_osecac_busq = cargar_datos(URLs["osecac"])

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}]

# --- INTERFAZ DEL PORTAL ---
st.markdown('<div class="header-master"><div class="capsula-header-mini"><div class="shimmer-efecto"></div><h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1></div></div>', unsafe_allow_html=True)
try:
    with open("LOGO1.png", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:85px; margin-bottom:20px;"></center>', unsafe_allow_html=True)
except: pass

st.markdown("---")

# 1. NOMENCLADORES
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    opcion = st.radio("Origen:", ["FABA", "OSECAC"], horizontal=True, key="rad_nom")
    bus_nom = st.text_input("🔍 Buscar en nomencladores...", key="bus_n")
    if bus_nom:
        df_u = df_faba if opcion == "FABA" else df_osecac_busq
        mask = df_u.apply(lambda row: all(p in str(row).lower() for p in bus_nom.lower().split()), axis=1)
        for i, row in df_u[mask].iterrows():
            datos = [f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)]
            st.markdown(f'<div class="ficha">{"<br>".join(datos)}</div>', unsafe_allow_html=True)

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

# 5. PRÁCTICAS Y ESPECIALISTAS (Doble Búsqueda)
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**", expanded=False):
    bus_p = st.text_input("Buscá prácticas o especialistas...", key="bus_p")
    if bus_p:
        # Prácticas
        rp = df_practicas[df_practicas.astype(str).apply(lambda r: r.str.contains(bus_p, case=False, na=False).any(), axis=1)]
        for i, row in rp.iterrows():
            st.markdown(f'<div class="ficha ficha-practica">📑 <b>PRÁCTICA:</b><br>{"<br>".join([f"<b>{c}:</b> {v}" for c,v in row.items() if pd.notna(v)])}</div>', unsafe_allow_html=True)
        # Especialistas
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
