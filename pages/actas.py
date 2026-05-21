<style>
    .stApp { background: #f8fafc; }
    
    /* HEADER */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.35rem; font-weight: 600; }
    .main-header p { color: #94a3b8; margin: 0; font-size: 0.78rem; }

    /* === KPI CARDS - CONTENIDO MÁS GRANDE === */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 0.6rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
    }
    
    /* AUMENTO IMPORTANTE DE TAMAÑO DE LETRA */
    .kpi-card h1 {
        font-size: 2.4rem !important;     /* ← Número principal más grande */
        font-weight: 700;
        margin: 0.1rem 0 0.3rem 0;
        line-height: 1;
    }
    .kpi-card p {
        font-size: 0.95rem !important;    /* ← Texto descriptivo más grande */
        font-weight: 500;
        margin: 0;
        color: #334155;
    }
    .kpi-card .kpi-icon {
        font-size: 1.8rem;
        margin-bottom: 0.4rem;
    }

    .kpi-total h1 { color: #3b82f6; }
    .kpi-con-legajo h1 { color: #10b981; }
    .kpi-sin-legajo h1 { color: #f59e0b; }
    .kpi-pendiente h1 { color: #ef4444; }
    .kpi-mail h1 { color: #f97316; }
    .kpi-finalizado h1 { color: #10b981; }

    /* === TARJETAS DE INSPECTORES - MÁS GRANDES === */
    .inspector-card {
        background: white;
        border-radius: 10px;
        padding: 0.8rem 0.4rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .inspector-card:hover {
        transform: translateY(-2px);
        border-color: #10b981;
    }
    .inspector-card h3 {
        font-size: 0.95rem !important;
        color: #10b981;
        margin: 0 0 0.3rem 0;
        font-weight: 600;
    }
    .inspector-card h1 {
        font-size: 1.65rem !important;   /* ← Número del inspector más grande */
        font-weight: 700;
        color: #1e293b;
        margin: 0.1rem 0;
    }
    .inspector-card p {
        font-size: 0.85rem !important;   /* ← Legajo más visible */
        color: #475569;
        margin: 0;
    }

    /* Resto de estilos (mantengo los que ya tenías) */
    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; }
    .buscar-btn button { background: #3b82f6 !important; font-size: 0.9rem !important; }
    .streamlit-expanderHeader { background: #f1f5f9 !important; border-radius: 10px !important; }
    #MainMenu, footer, header { display: none !important; }
</style>
