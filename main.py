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
        if '/edit' in url:
            csv_url = url.split('/edit')[0] + '/export?format=csv'
        else:
            csv_url = url
        return pd.read_csv(csv_url, dtype=str).fillna("")
    except:
        return pd.DataFrame()

# URLs de las planillas
URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_PRACTICAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0"
URL_ESPECIALISTAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576"
URL_NOMENCLADOR_UNIFICADO = "https://docs.google.com/spreadsheets/d/1pc0ioT9lWLzGHDiifJLYyrXHv-NFsT3UDIDt951CTGc/export?format=csv"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)
df_practicas = cargar_datos(URL_PRACTICAS_CSV)
df_especialistas = cargar_datos(URL_ESPECIALISTAS_CSV)
df_nomenclador = cargar_datos(URL_NOMENCLADOR_UNIFICADO)

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [
        {"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}
    ]

# 3. CSS: DISEÑO PERSONALIZADO
st.markdown("""
    <style>
    .stApp { background: #0b0e14; color: #e2e8f0; }
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 20px; border-radius: 12px; margin-bottom: 10px; border-left: 8px solid #f97316; }
    .ficha-osecac { border-left-color: #38bdf8; background-color: rgba(56, 189, 248, 0.05); }
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:white;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)
st.markdown("---")

# --- SECCIÓN 1: NOMENCLADORES (DIVIDIDO) ---
with st.expander("📂 **1. NOMENCLADORES**", expanded=True):
    tab_lab, tab_prac = st.tabs(["🔬 LABORATORIO (FABA)", "🩺 PRÁCTICAS (OSECAC)"])

    with tab_lab:
        bus_l = st.text_input("Buscá análisis o código FABA...", key="l_search")
        if bus_l and not df_nomenclador.empty:
            # Filtro: Filas con datos en Columna A (Código FABA)
            df_l = df_nomenclador[df_nomenclador.iloc[:, 0] != ""]
            terminos = bus_l.lower().split()
            mask = df_l.apply(lambda r: any(t in str(r).lower() for t in terminos), axis=1)
            res = df_l[mask].drop_duplicates()
            if not res.empty:
                for i, r in res.iterrows():
                    st.markdown(f"""<div class="ficha">
                        <b style="color:#f97316;">FABA:</b> {r.iloc[1]}<br>
                        <b style="color:#38bdf8;">OSECAC:</b> {r.iloc[3]}<br>
                        <hr style="margin:10px 0; border:0; border-top:1px solid rgba(255,255,255,0.1);">
                        <small><b>COD FABA:</b> {r.iloc[0]} | <b>COD OSECAC:</b> {r.iloc[2]}</small>
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("No se encontraron resultados en Laboratorio.")

    with tab_prac:
        bus_p = st.text_input("Buscá práctica o código OSECAC...", key="p_search")
        if bus_p and not df_nomenclador.empty:
            # Filtro: Filas con datos en Columna C (Código OSECAC)
            df_p = df_nomenclador[df_nomenclador.iloc[:, 2] != ""]
            terminos = bus_p.lower().split()
            mask = df_p.apply(lambda r: any(t in str(r).lower() for t in terminos), axis=1)
            res = df_p[mask].drop_duplicates()
            if not res.empty:
                for i, r in res.iterrows():
                    st.markdown(f"""<div class="ficha ficha-osecac">
                        <b style="color:#38bdf8;">PRÁCTICA:</b> {r.iloc[3]}<br>
                        <div style="margin-top:8px;">
                            <b>CÓDIGO OSECAC:</b> <code style="background:#1e293b; padding:2px 5px; color:white;">{r.iloc[2]}</code>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("No se encontraron resultados en Prácticas.")

# --- SECCIÓN 2: PEDIDOS ---
with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

# --- SECCIÓN 3: PÁGINAS ÚTILES ---
with st.expander("🌐 **3. PÁGINAS ÚTILES**"):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("💊 VADEMÉCUM", "https://www.osecac.org.ar/Vademecus")
    st.link_button("💻 OSECAC OFICIAL", "https://www.osecac.org.ar/")

# --- SECCIÓN 4: GESTIONES ---
with st.expander("📂 **4. GESTIONES / DATOS**"):
    bus_t = st.text_input("Buscá trámites...", key="t_search")
    if bus_t and not df_tramites.empty:
        res_t = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bus_t.lower(), na=False)]
        for i, r in res_t.iterrows():
            st.markdown(f'<div class="ficha" style="border-left-color:#fbbf24;"><b>📋 {r["TRAMITE"]}</b><br>{r["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# --- SECCIÓN 5: PRÁCTICAS Y ESPECIALISTAS ---
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**"):
    bus_pe = st.text_input("Buscá cartilla...", key="pe_search")
    if bus_pe:
        for df, tipo, color in [(df_practicas, "📑 PRÁCTICA", "#10b981"), (df_especialistas, "👨‍⚕️ ESPECIALISTA", "#10b981")]:
            if not df.empty:
                res = df[df.astype(str).apply(lambda row: row.str.contains(bus_pe.lower(), case=False).any(), axis=1)]
                for i, row in res.iterrows():
                    st.markdown(f'<div class="ficha" style="border-left-color:{color};"><b>{tipo}:</b> {", ".join(row.values)}</div>', unsafe_allow_html=True)

# --- SECCIÓN 6: AGENDAS ---
with st.expander("📞 **6. AGENDAS / MAILS**"):
    bus_a = st.text_input("Buscá contactos...", key="a_search")
    if bus_a and not df_agendas.empty:
        res_a = df_agendas[df_agendas.astype(str).apply(lambda row: row.str.contains(bus_a.lower(), case=False).any(), axis=1)]
        for i, row in res_a.iterrows():
            st.markdown(f'<div class="ficha" style="border-left-color:#38bdf8;">{", ".join(row.values)}</div>', unsafe_allow_html=True)

# --- SECCIÓN 7: NOVEDADES ---
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha" style="border-left-color:#ff4b4b;"><small>{n["fecha"]}</small><br>{n["mensaje"]}</div>', unsafe_allow_html=True)
    
    with st.popover("✍️ PANEL DE CONTROL"):
        if st.text_input("Clave:", type="password") == PASSWORD_JEFE:
            with st.form("form_nov", clear_on_submit=True):
                msg = st.text_area("Nuevo comunicado:")
                if st.form_submit_button("📢 PUBLICAR"):
                    st.session_state.historial_novedades.insert(0, {"id": str(datetime.now().timestamp()), "mensaje": msg, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")})
                    st.rerun()
