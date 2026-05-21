# ── ESTILOS MODERNOS - LETRAS GRANDES ───────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #f8fafc; }
    
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 1rem 1.8rem;
        border-radius: 12px;
        border-left: 6px solid #3b82f6;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.5rem; font-weight: 700; }
    .main-header p { color: #94a3b8; margin: 0.3rem 0 0 0; font-size: 0.9rem; }

    /* RECTÁNGULOS CON LETRAS GRANDES */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.3rem 0.8rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        height: 100%;
    }
    .kpi-card h1 {
        font-size: 2.9rem !important;
        font-weight: 700;
        margin: 0.1rem 0 0.4rem 0;
        line-height: 1;
    }
    .kpi-card p {
        font-size: 1.15rem !important;
        font-weight: 600;
        color: #1e293b;
        margin: 0;
    }
    .kpi-card .kpi-icon { font-size: 2.2rem; margin-bottom: 0.6rem; }

    .kpi-total h1 { color: #3b82f6; }
    .kpi-con-legajo h1 { color: #10b981; }
    .kpi-sin-legajo h1 { color: #f59e0b; }
    .kpi-pendiente h1 { color: #ef4444; }
    .kpi-mail h1 { color: #f97316; }
    .kpi-finalizado h1 { color: #10b981; }

    /* Inspectores */
    .inspector-card {
        background: white;
        border-radius: 10px;
        padding: 1rem 0.6rem;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .inspector-card h3 { font-size: 1.1rem !important; color: #10b981; margin-bottom: 0.4rem; }
    .inspector-card h1 { font-size: 2.2rem !important; font-weight: 700; }
    .inspector-card p { font-size: 1.05rem !important; }

    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; }
    .buscar-btn button { background: #3b82f6 !important; font-size: 1rem !important; }
    #MainMenu, footer, header { display: none !important; }
</style>
""", unsafe_allow_html=True)
