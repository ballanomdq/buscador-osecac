import streamlit as st

# --- ESTILO 3: VENTANA FLOTANTE Y MENU INFERIOR ---
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050914; color: white; padding-bottom: 70px; } /* Espacio para el menú */
    
    /* Ventana de Novedad (Card) */
    .novedad-card {
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid #2563eb;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .novedad-card h4 { color: #38bdf8 !important; }
    
    /* MENU INFERIOR FIJO */
    .menu-inferior {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0b1e3b;
        border-top: 2px solid #2563eb;
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        padding: 10px;
        text-align: center;
        z-index: 1000;
    }
    .menu-inferior div span { font-size: 1.5rem; color: #38bdf8; }
    .menu-inferior div p { margin: 0; font-size: 0.8rem; color: white; }
    
    </style>
    """, unsafe_allow_html=True)

st.markdown("<center><h2 style='color:white;'>Portal OSECAC</h2></center>", unsafe_allow_html=True)

# Ventana Central de Novedades
st.markdown("### 📢 Últimos Avisos")
st.markdown("""
<div class="novedad-card">
    <small>27/02/2026</small>
    <h4>Actualización de Vademécum</h4>
    <p>Se han cargado nuevos códigos para farmacia.</p>
</div>
""", unsafe_allow_html=True)
st.button("📥 Descargar PDF")

# MENU INFERIOR FIJO (Simulado)
st.markdown("""
<div class="menu-inferior">
    <div><span>🏠</span><p>Inicio</p></div>
    <div><span>📂</span><p>Nomenclador</p></div>
    <div><span>🍼</span><p>Pedidos</p></div>
    <div><span>📞</span><p>Agenda</p></div>
</div>
""", unsafe_allow_html=True)
