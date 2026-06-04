import streamlit as st
import base64
import os

st.set_page_config(
    page_title="OSECAC MDP - Documentos Cirugía",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== CSS (mismo estilo que Oncología) ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #ffffff !important; color: #1e293b !important; }
.block-container { max-width: 1100px !important; padding-top: 1rem !important; }

/* Aumentar tamaño de fuente general */
body, .stMarkdown, .stTextInput, .stSelectbox, label, p, li, .stExpander {
    font-size: 1.2rem !important;
}
h1 { font-size: 2.8rem !important; }
h2 { font-size: 2rem !important; }
h3 { font-size: 1.6rem !important; }

hr { margin: 2rem 0; }

/* Botones de carpeta */
.carpeta-button a {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 0.4rem 1rem !important;
    text-decoration: none !important;
    display: inline-block !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
}
.carpeta-button a:hover {
    background-color: #e2e8f0 !important;
    border-color: #94a3b8 !important;
}

/* Botones de impresión */
.print-button button {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 0.3rem 0.8rem !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
}
.print-button button:hover {
    background-color: #e2e8f0 !important;
    border-color: #94a3b8 !important;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGO CENTRADO =================
logo_path = "logo osecac.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 1rem 0 1rem 0;">
            <img src="data:image/png;base64,{logo_base64}" 
                 style="width: 300px; height: auto;" 
                 alt="Logo OSECAC">
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="display: flex; justify-content: center; margin: 1rem 0 1rem 0;">
            <div style="width:300px; height:150px; background: #e2e8f0; border-radius:16px; border:1px solid #cbd5e1;"></div>
        </div>
    """, unsafe_allow_html=True)

# ================= TÍTULO PRINCIPAL =================
st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h1 style="font-size: 2.8rem; font-weight: 600;">PROGRAMAS Y PLANILLAS DE CIRUGÍA</h1>
        <p style="font-size: 1.4rem; color: #475569;">MDP</p>
    </div>
""", unsafe_allow_html=True)

# ================= FUNCIÓN PARA BOTÓN DE IMPRESIÓN =================
def print_button(html_content, key_suffix=""):
    """Crea un botón de impresión para una sección específica"""
    btn_html = f"""
    <div style="margin-top: 0.8rem;">
        <button onclick="imprimirContenido_{key_suffix}()" style="background-color:#f1f5f9; border:1px solid #cbd5e1; border-radius:8px; padding:0.4rem 0.8rem; cursor:pointer; font-size:0.9rem;">🖨️ Imprimir requisitos</button>
        <script>
            function imprimirContenido_{key_suffix}() {{
                var ventana = window.open('', '_blank');
                ventana.document.write(`
                    <html>
                    <head>
                        <title>Requisitos OSECAC</title>
                        <style>
                            body {{ font-family: sans-serif; padding: 2rem; }}
                            h3 {{ color: #1e293b; }}
                            ul {{ line-height: 1.6; }}
                            li {{ margin: 0.5rem 0; }}
                        </style>
                    </head>
                    <body>
                        {html_content}
                        <hr>
                        <p style="color: #64748b; font-size: 0.8rem;">Documento generado desde OSECAC MDP - Cirugía</p>
                    </body>
                    </html>
                `);
                ventana.document.close();
                ventana.print();
            }}
        </script>
    </div>
    """
    st.components.v1.html(btn_html, height=80)

# ================= SECCIÓN: CARPETA PRINCIPAL =================
st.markdown("---")
st.markdown("## 📂 ACCESO A CARPETA COMPLETA")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("**Todas las planillas organizadas por especialidad**")
with col2:
    st.markdown(f"""
    <div class="carpeta-button" style="text-align: right;">
        <a href="https://drive.google.com/drive/folders/1GMWFh5ddSYEGS34Pef0to135j_eC4KIS?usp=sharing" target="_blank">
            📁 ABRIR CARPETA PRINCIPAL
        </a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ================= 1. VASECTOMÍA =================
with st.expander("✂️ VASECTOMÍA", expanded=True):
    contenido_vasectomia = """
    <h3>Requisitos para Vasectomía</h3>
    <ul>
        <li>Planilla consentimiento para cirugía de vasectomía F-PAD-2-19</li>
        <li>Planilla consentimiento para intervención quirúrgica FAP 2-216</li>
        <li>Planilla consentimiento informado F-PAD-2-92</li>
        <li>Pedido de cirugía con clave de práctica y fecha estimativa de cirugía</li>
        <li>Resumen de Historia Clínica</li>
        <li>Pedido de Anestesia</li>
        <li>Estudios Previos</li>
        <li>Fot. de D.N.I. - Carnet (Tit y caus) - último recibo de haberes - 6 últimos pagos de monot.</li>
        <li>Codem y Certificación Negativa - Anses</li>
        <li>Consentimiento covid (parcial o total según el caso)</li>
    </ul>
    """
    
    col_v1, col_v2 = st.columns([3, 1])
    with col_v1:
        st.markdown(contenido_vasectomia, unsafe_allow_html=True)
    with col_v2:
        st.markdown(f"""
        <div class="carpeta-button" style="margin-top: 0.5rem;">
            <a href="https://drive.google.com/drive/folders/18jwii0AXpqGHSzwyzFhvOzntQ54Xqk6l?usp=sharing" target="_blank">
                📁 VER PLANILLAS
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    print_button(contenido_vasectomia, "vasectomia")

# ================= 2. CIRUGÍA CON MATERIALES - MAYORES =================
with st.expander("🔧 CIRUGÍA CON MATERIALES - MAYORES DE EDAD"):
    contenido_con_mayores = """
    <h3>Requisitos para Cirugía con Materiales - MAYORES de edad</h3>
    <ul>
        <li>Planilla consentimiento para intervención quirúrgica NUEVO FAP 2-267</li>
        <li>Planilla consentimiento informado F-PAD-2-92</li>
        <li>Pedido de cirugía con clave de práctica y fecha estimativa de cirugía</li>
        <li>Resumen de Historia Clínica</li>
        <li>Pedido de Anestesia</li>
        <li>Estudios Previos</li>
        <li>Fot. de D.N.I. - Carnet (Tit y caus) - último recibo de haberes - 6 últimos pagos de monot.</li>
        <li>Codem y Certificación Negativa - Anses</li>
        <li>Formul 2-5-1 nuevo materiales</li>
    </ul>
    """
    
    col_cm1, col_cm2 = st.columns([3, 1])
    with col_cm1:
        st.markdown(contenido_con_mayores, unsafe_allow_html=True)
    with col_cm2:
        st.markdown(f"""
        <div class="carpeta-button" style="margin-top: 0.5rem;">
            <a href="https://drive.google.com/drive/folders/1c-HmhzjF7_GqWt1y37ziMa21JG3-nAZV?usp=sharing" target="_blank">
                📁 VER PLANILLAS
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    print_button(contenido_con_mayores, "con_mayores")

# ================= 3. CIRUGÍA CON MATERIALES - MENORES =================
with st.expander("🔧 CIRUGÍA CON MATERIALES - MENORES DE EDAD"):
    contenido_con_menores = """
    <h3>Requisitos para Cirugía con Materiales - MENORES de edad</h3>
    <ul>
        <li>PLLA CIRUGIA PEDIATRICA F-PAD -2-6</li>
        <li>Planilla consentimiento informado F-PAD-2-92</li>
        <li>Formul 2-5-1 nuevo materiales</li>
        <li>Pedido de cirugía con clave de práctica y fecha estimativa de cirugía</li>
        <li>Resumen de Historia Clínica</li>
        <li>Pedido de Anestesia</li>
        <li>Estudios Previos</li>
        <li>Fot. de D.N.I. - Carnet (Tit y caus) - último recibo de haberes - 6 últimos pagos de monot.</li>
        <li>Codem y Certificación Negativa - Anses</li>
    </ul>
    """
    
    col_cm1, col_cm2 = st.columns([3, 1])
    with col_cm1:
        st.markdown(contenido_con_menores, unsafe_allow_html=True)
    with col_cm2:
        st.markdown(f"""
        <div class="carpeta-button" style="margin-top: 0.5rem;">
            <a href="https://drive.google.com/drive/folders/1M4RFCqh5gieRmL_5OIj9vfTmIDfr1ASq?usp=sharing" target="_blank">
                📁 VER PLANILLAS
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    print_button(contenido_con_menores, "con_menores")

# ================= 4. CIRUGÍA SIN MATERIALES - MAYORES =================
with st.expander("📄 CIRUGÍA SIN MATERIALES - MAYORES DE EDAD"):
    contenido_sin_mayores = """
    <h3>Requisitos para Cirugía SIN Materiales - MAYORES de edad</h3>
    <ul>
        <li>Planilla consentimiento para intervención quirúrgica FAP 2-216</li>
        <li>Planilla consentimiento informado F-PAD-2-92</li>
        <li>Pedido de cirugía con clave de práctica y fecha estimativa de cirugía</li>
        <li>Resumen de Historia Clínica</li>
        <li>Pedido de Anestesia</li>
        <li>Estudios Previos</li>
        <li>Fot. de D.N.I. - Carnet (Tit y caus) - último recibo de haberes - 6 últimos pagos de monot.</li>
        <li>Codem y Certificación Negativa - Anses</li>
        <li>Consentimiento covid (parcial o total según el caso)</li>
    </ul>
    """
    
    col_sm1, col_sm2 = st.columns([3, 1])
    with col_sm1:
        st.markdown(contenido_sin_mayores, unsafe_allow_html=True)
    with col_sm2:
        st.markdown(f"""
        <div class="carpeta-button" style="margin-top: 0.5rem;">
            <a href="https://drive.google.com/drive/folders/1YpkNFer_VvgZz2QRXr6cSQqNy_bw5yxl?usp=sharing" target="_blank">
                📁 VER PLANILLAS
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    print_button(contenido_sin_mayores, "sin_mayores")

# ================= 5. CIRUGÍA SIN MATERIALES - MENORES =================
with st.expander("📄 CIRUGÍA SIN MATERIALES - MENORES DE EDAD"):
    contenido_sin_menores = """
    <h3>Requisitos para Cirugía SIN Materiales - MENORES de edad</h3>
    <ul>
        <li>PLLA CIRUGIA PEDIATRICA F-FAP 2-216</li>
        <li>Planilla consentimiento informado F-PAD-2-92</li>
        <li>Pedido de cirugía con clave de práctica y fecha estimativa de cirugía</li>
        <li>Resumen de Historia Clínica</li>
        <li>Pedido de Anestesia</li>
        <li>Estudios Previos</li>
        <li>Fot. de D.N.I. - Carnet (Tit y caus) - último recibo de haberes - 6 últimos pagos de monot.</li>
        <li>Codem y Certificación Negativa - Anses</li>
        <li>Consentimiento covid (parcial o total según el caso)</li>
    </ul>
    """
    
    col_sm1, col_sm2 = st.columns([3, 1])
    with col_sm1:
        st.markdown(contenido_sin_menores, unsafe_allow_html=True)
    with col_sm2:
        st.markdown(f"""
        <div class="carpeta-button" style="margin-top: 0.5rem;">
            <a href="https://drive.google.com/drive/folders/1V9N3RLO0fOjvM_gUHc1z62nTedIYSOKP?usp=sharing" target="_blank">
                📁 VER PLANILLAS
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    print_button(contenido_sin_menores, "sin_menores")

# ================= 6. CESÁREA =================
with st.expander("🤰 CESÁREA"):
    contenido_cesarea = """
    <h3>Requisitos para Cesárea</h3>
    <ul>
        <li>Planilla consentimiento para intervención quirúrgica FAP 2-267</li>
        <li>Pedido de cirugía con clave de práctica y fecha estimativa de cirugía</li>
        <li>Pedido de Anestesia</li>
        <li>Estudios Previos</li>
        <li>Fot. de D.N.I. - Carnet (Tit y caus) - último recibo de haberes - 6 últimos pagos de monot.</li>
        <li>Codem y Certificación Negativa - Anses</li>
    </ul>
    """
    
    col_c1, col_c2 = st.columns([3, 1])
    with col_c1:
        st.markdown(contenido_cesarea, unsafe_allow_html=True)
    with col_c2:
        st.markdown(f"""
        <div class="carpeta-button" style="margin-top: 0.5rem;">
            <a href="https://drive.google.com/drive/folders/1bDRqAV70lq92g75xb95Ns6sL8G4lLr5X?usp=sharing" target="_blank">
                📁 VER PLANILLAS
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    print_button(contenido_cesarea, "cesarea")

# ================= PIE DE PÁGINA SIMPLIFICADO =================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1rem;'>OSECAC MDP - Área Cirugía</p>", unsafe_allow_html=True)
