import streamlit as st
import base64
import os

st.set_page_config(
    page_title="OSECAC MDP - Documentos Oncológicos",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== CSS ==================
st.markdown("""
<style>
[data-testid="stSidebar"], #MainMenu, footer, header { display: none !important; }

.stApp {
    background-color: #ffffff !important;
    color: #1e293b !important;
}

.block-container {
    max-width: 1000px !important;
    padding-top: 1rem !important;
}

h1, h2, h3 {
    color: #0f172a !important;
}

hr {
    margin: 2rem 0;
}

/* SELECTBOX GRANDE Y SIN EXPANSIÓN */
div[data-baseweb="select"] > div {
    font-size: 1.1rem !important;
    min-height: 55px !important;
}

/* BOTONES */
.download-btn {
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px 10px;
    text-decoration: none;
    font-size: 0.8rem;
    color: #0f172a;
    margin-left: 10px;
}
.download-btn:hover {
    background-color: #e2e8f0;
}

.small-text {
    font-size: 0.75rem;
    color: #64748b;
    margin-left: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGO =================
logo_path = "logo osecac.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <div style="display:flex; justify-content:center; margin:1rem 0 2rem 0;">
        <img src="data:image/png;base64,{logo_base64}" style="width:300px;">
    </div>
    """, unsafe_allow_html=True)

# ================= TITULO =================
st.markdown("""
<div style="text-align:center;">
    <h1>PROGRAMAS Y PLANILLAS ONCOLOGICAS</h1>
    <div style="font-size:1rem; color:#64748b;">MDP</div>
</div>
""", unsafe_allow_html=True)

# ================= PLANILLAS =================
st.markdown("## 📄 PLANILLAS")

def fila_planilla(nombre, doc_id, editable=False):
    view_url = f"https://drive.google.com/file/d/{doc_id}/view"
    download_url = f"https://drive.google.com/uc?export=download&id={doc_id}"

    texto_extra = ""
    if editable:
        texto_extra = '<span class="small-text">Descargable y editable</span>'

    st.markdown(f"""
    <div style="margin-bottom:8px;">
        <a href="{view_url}" target="_blank">{nombre}</a>
        <a href="{download_url}" class="download-btn">⬇ Descargar</a>
        {texto_extra}
    </div>
    """, unsafe_allow_html=True)

# PLANILLAS
fila_planilla(
    "F-PAD-2-219 CONSENTIMIENTO INFORMADO MEDICAMENTOS RECUPERO SUR",
    "1ISSigS6YBugt4xfS7tVz00pLfpdqkBR9",
    editable=False
)

fila_planilla(
    "F-PAD.2.74 PRESCRIPCIÓN ONCOLÓGICA 1ERA VEZ – CONTINUIDAD",
    "1AJidHwRGRAmczopQPqsYwRVPfTiTlhiK",
    editable=True
)

fila_planilla(
    "F-PAD-2-075 PRESCRIPCIÓN ONCOLÓGICA CONTINUIDAD DE TRATAMIENTO",
    "1aslyVdHH56NU3nHacLl7fHu0opvbEueY",
    editable=True
)

st.markdown("---")

# ================= MEDICAMENTOS =================
st.markdown("## 💊 MEDICAMENTOS")

medicamentos_completos = [
    ("ABIRATERONA, ACETATO", "CÁNCER DE PRÓSTATA"),
    ("BEVACIZUMAB", "Cáncer de Colon / Mama / Pulmón / Riñón"),
    ("CISPLATINO", "ONCOLOGICOS CÁPITA"),
    ("IMATINIB", "LEUCEMIA MIELOIDE CRÓNICA"),
    ("RITUXIMAB", "LINFOMA NO HODGKIN"),
    ("TRASTUZUMAB", "CÁNCER DE MAMA")
]

medicamentos_completos.sort(key=lambda x: x[0])
nombres_med = [m[0] for m in medicamentos_completos]

col1, col2 = st.columns([1,1])

with col1:
    seleccion = st.selectbox(
        "BUSCAR MEDICAMENTO:",
        nombres_med,
        index=None,
        placeholder="Escribí para buscar...",
        key="med_selector"
    )

with col2:
    if seleccion:
        programa = next(m[1] for m in medicamentos_completos if m[0] == seleccion)
        st.markdown(f"""
        <div style="background:#f8fafc; border-left:4px solid #2563eb; padding:1rem; border-radius:8px;">
            <strong style="color:#2563eb;">PROGRAMA:</strong><br>
            {programa}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("<p style='text-align:center; font-size:0.8rem; color:#64748b;'>Documentación actualizada periódicamente</p>", unsafe_allow_html=True)
