import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OSECAC MDP - Portal", layout="wide")
PASSWORD_JEFE = "2026"

@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        if '/edit' in url:
            csv_url = url.split('/edit')[0] + '/export?format=csv'
        else:
            csv_url = url
        df = pd.read_csv(csv_url, dtype=str)
        return df.fillna("N/A")
    except:
        return pd.DataFrame()

# URLs
URL_AGENDAS_CSV = "https://docs.google.com/spreadsheets/d/1zhaeWLjoz2iIRj8WufTT1y0dCUAw2-TqIOV33vYT_mg/export?format=csv"
URL_TRAMITES_CSV = "https://docs.google.com/spreadsheets/d/1dyGnXrqr_9jSUGgWpxqiby-QpwAtcvQifutKrSj4lO0/export?format=csv"
URL_PRACTICAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=0"
URL_ESPECIALISTAS_CSV = "https://docs.google.com/spreadsheets/d/1DfdEQPWfbR_IpZa1WWT9MmO7r5I-Tpp2uIZEfXdskR0/export?format=csv&gid=1119565576"
URL_NOMENCLADOR_UNIFICADO = "https://docs.google.com/spreadsheets/d/1pc0ioT9lWLzGHDiifJLYyrXHv-NFsT3UDIDt951CTGc/edit?usp=sharing"

df_agendas = cargar_datos(URL_AGENDAS_CSV)
df_tramites = cargar_datos(URL_TRAMITES_CSV)
df_practicas = cargar_datos(URL_PRACTICAS_CSV)
df_especialistas = cargar_datos(URL_ESPECIALISTAS_CSV)
df_nomenclador = cargar_datos(URL_NOMENCLADOR_UNIFICADO)

if 'historial_novedades' not in st.session_state:
    st.session_state.historial_novedades = [{"id": "0", "mensaje": "Bienvenidos al portal oficial de Agencias OSECAC MDP.", "fecha": "22/02/2026 00:00"}]

# 3. CSS MEJORADO
st.markdown("""
    <style>
    .stApp { background: #0b0e14; color: #e2e8f0; }
    .ficha { background-color: rgba(23, 32, 48, 0.9); padding: 15px; border-radius: 10px; margin-bottom: 8px; border-left: 6px solid #ccc; }
    .ficha-faba { border-left-color: #f97316; }
    .stExpander { background-color: rgba(30, 41, 59, 0.6) !important; border-radius: 12px !important; }
    /* Estilo para tabla compacta */
    .tabla-compacta { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    .tabla-compacta th { background: #1e293b; color: #f97316; padding: 8px; text-align: left; border-bottom: 2px solid #f97316; }
    .tabla-compacta td { padding: 8px; border-bottom: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 style="text-align:center; color:white;">OSECAC MDP / AGENCIAS</h1>', unsafe_allow_html=True)
st.markdown("---")

# --- SECCIÓN 1: NOMENCLADORES ---
with st.expander("📂 **1. NOMENCLADORES**", expanded=False):
    st.link_button("📘 NOMENCLADOR IA", "https://notebooklm.google.com/notebook/f2116d45-03f5-4102-b8ff-f1e1fa965ffc")
    st.markdown("---")
    st.write("🔍 **BUSCADOR (Códigos o Nombres)**")
    busqueda_n = st.text_input("Tip: Pegá códigos o nombres separados por espacio o coma", key="search_n")
    
    if busqueda_n:
        if not df_nomenclador.empty:
            # Limpieza de términos
            terminos = [t.strip().lower() for t in busqueda_n.replace(',', ' ').split() if len(t.strip()) > 2]
            
            if terminos:
                # Filtrado
                mask = df_nomenclador.apply(lambda row: any(t in str(row).lower() for t in terminos), axis=1)
                res_n = df_nomenclador[mask].drop_duplicates().head(20) # Limitamos a 20 para evitar el lío
                
                if not res_n.empty:
                    # MODO TABLA SI HAY MUCHOS RESULTADOS
                    if len(res_n) > 3:
                        st.write(f"📊 Se encontraron {len(res_n)} coincidencias. Mostrando vista compacta:")
                        st.dataframe(res_n, use_container_width=True, hide_index=True)
                    # MODO FICHA SI SON POQUITOS (Más visual)
                    else:
                        for i, row in res_n.iterrows():
                            # Identificar columnas
                            col_faba = [c for c in res_n.columns if 'FABA' in c.upper() and 'DESCRIP' in c.upper()]
                            col_osecac = [c for c in res_n.columns if 'OSECAC' in c.upper() and 'DESCRIP' in c.upper()]
                            
                            st.markdown(f"""
                            <div class="ficha ficha-faba">
                                <b style="color:#f97316;">FABA:</b> {row[col_faba[0]] if col_faba else 'N/A'}<br>
                                <b style="color:#38bdf8;">OSECAC:</b> {row[col_osecac[0]] if col_osecac else 'N/A'}<br>
                                <small><b>COD FABA:</b> {row.get('CODIGO FABA','-')} | <b>COD OSECAC:</b> {row.get('CODIGO OSECAC','-')}</small>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("No se encontró nada con esas palabras.")
            else:
                st.info("Escribí al menos 3 letras para buscar.")

# --- SECCIONES RESTANTES (Mismo formato que antes) ---
with st.expander("📝 **2. PEDIDOS**"):
    st.link_button("🍼 PEDIDO DE LECHES", "https://docs.google.com/forms/d/e/1FAIpQLSdieAj2BBSfXFwXR_3iLN0dTrCXtMTcQRTM-OElo5i7JsxMkg/viewform")
    st.link_button("📦 PEDIDO SUMINISTROS", "https://docs.google.com/forms/d/e/1FAIpQLSfMlwRSUf6dAwwpl1k8yATOe6g0slMVMV7ulFao0w_XaoLwMA/viewform")

with st.expander("🌐 **3. PÁGINAS ÚTILES**"):
    st.link_button("🏥 SSSALUD", "https://www.sssalud.gob.ar/consultas/")
    st.link_button("💻 OSECAC", "https://www.osecac.org.ar/")

# --- GESTIONES ---
with st.expander("📂 **4. GESTIONES / DATOS**"):
    bt = st.text_input("Buscá trámites...", key="st")
    if bt and not df_tramites.empty:
        rt = df_tramites[df_tramites['TRAMITE'].str.lower().str.contains(bt.lower(), na=False)]
        for i, r in rt.iterrows():
            st.markdown(f'<div class="ficha" style="border-left-color:#fbbf24;"><b>📋 {r["TRAMITE"]}</b><br>{r["DESCRIPCIÓN Y REQUISITOS"]}</div>', unsafe_allow_html=True)

# --- PRÁCTICAS ---
with st.expander("🩺 **5. PRÁCTICAS Y ESPECIALISTAS**"):
    bp = st.text_input("Buscá prácticas...", key="sp")
    if bp:
        for df, t in [(df_practicas, "📑"), (df_especialistas, "👨‍⚕️")]:
            if not df.empty:
                r = df[df.astype(str).apply(lambda row: row.str.contains(bp.lower(), case=False).any(), axis=1)]
                for i, row in r.iterrows():
                    st.markdown(f'<div class="ficha" style="border-left-color:#10b981;">{t} {list(row.values)[0]}<br><small>{", ".join(row.values[1:])}</small></div>', unsafe_allow_html=True)

# --- NOVEDADES ---
with st.expander("📢 **7. NOVEDADES**", expanded=True):
    for n in st.session_state.historial_novedades:
        st.markdown(f'<div class="ficha" style="border-left-color:#ff4b4b;"><small>{n["fecha"]}</small><br>{n["mensaje"]}</div>', unsafe_allow_html=True)
