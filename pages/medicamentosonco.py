import streamlit as st
import base64
import os

st.set_page_config(
    page_title="OSECAC MDP - Documentos Oncológicos",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== CSS (fondo blanco, tipografía más grande) ==================
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

/* Botones de descarga más grandes */
.download-button a {
    font-size: 1rem !important;
    padding: 0.4rem 1rem !important;
    display: inline-block;
    margin-left: 1rem;
}

/* Para el menú de medicamentos: dropdown con scroll y tamaño contenido */
div[data-testid="stSelectbox"] div[data-baseweb="select"] ul {
    max-height: 300px !important;
    overflow-y: auto !important;
}
/* Aumentar tamaño del selectbox */
div[data-testid="stSelectbox"] label {
    font-size: 1.2rem !important;
}
div[data-baseweb="select"] {
    font-size: 1.1rem !important;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGO CENTRADO (300px) =================
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
        <h1 style="font-size: 2.8rem; font-weight: 600;">PROGRAMAS Y PLANILLAS ONCOLOGICAS</h1>
        <p style="font-size: 1.4rem; color: #475569;">MDP</p>
    </div>
""", unsafe_allow_html=True)

# ================= SECCIÓN PLANILLAS =================
st.markdown("## 📄 PLANILLAS")

# IDs y nombres
planillas = [
    ("F-PAD-2-219 CONSENTIMIENTO INFORMADO MEDICAMENTOS RECUPERO SUR", "1ISSigS6YBugt4xfS7tVz00pLfpdqkBR9", False),
    ("F-PAD.2.74 PRESCRIPCIÓN ONCOLÓGICA 1ERA VEZ – CONTINUIDAD", "1AJidHwRGRAmczopQPqsYwRVPfTiTlhiK", True),
    ("F-PAD-2-075 PRESCRIPCIÓN ONCOLÓGICA CONTINUIDAD DE TRATAMIENTO", "1aslyVdHH56NU3nHacLl7fHu0opvbEueY", True)
]

for nombre, doc_id, editable in planillas:
    url_vista = f"https://drive.google.com/file/d/{doc_id}/view"
    url_descarga = f"https://drive.google.com/uc?export=download&id={doc_id}"
    
    # Usar columnas para alinear
    cols = st.columns([4, 1.2, 0.8])
    with cols[0]:
        st.markdown(f"- [{nombre}]({url_vista})")
    with cols[1]:
        if editable:
            st.markdown(f"""
            <div style="text-align: right;">
                <a href="{url_descarga}" download class="download-button" style="background-color:#f1f5f9; border:1px solid #cbd5e1; border-radius:6px; padding:0.4rem 1rem; text-decoration:none; color:#1e293b; font-size:1rem;" title="Descargar – editable al abrir en PC">⬇️ Descargar</a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: right;">
                <a href="{url_descarga}" download class="download-button" style="background-color:#f1f5f9; border:1px solid #cbd5e1; border-radius:6px; padding:0.4rem 1rem; text-decoration:none; color:#1e293b; font-size:1rem;">⬇️ Descargar</a>
            </div>
            """, unsafe_allow_html=True)
    with cols[2]:
        if editable:
            st.markdown('<span style="color: #15803d; font-weight: bold; font-size: 1rem;">EDITABLE</span>', unsafe_allow_html=True)

st.markdown("---")

# ================= SECCIÓN REQUISITOS =================
st.markdown("## 📋 REQUISITOS PARA MEDICACIÓN ONCOLÓGICA")

def print_button(html_content):
    btn_html = f"""
    <div style="margin-top: 0.5rem;">
        <button onclick="imprimirContenido()" style="background-color:#f1f5f9; border:1px solid #cbd5e1; border-radius:8px; padding:0.4rem 0.8rem; cursor:pointer; font-size:1rem;">🖨️ Imprimir</button>
        <script>
            function imprimirContenido() {{
                var ventana = window.open('', '_blank');
                ventana.document.write(`
                    <html>
                    <head><title>Imprimir requisitos</title></head>
                    <body style="font-family: sans-serif; padding: 2rem;">
                        {html_content}
                    </body>
                    </html>
                `);
                ventana.document.close();
                ventana.print();
            }}
        </script>
    </div>
    """
    st.components.v1.html(btn_html, height=100)

with st.expander("💊 PRIMERA VEZ (CÁPITA Y EXTRACÁPITA)"):
    contenido1 = """
    <h3>Requisitos Primera Vez</h3>
    <ul>
        <li>FORM PRESCRIPCION ONCOLOGICA F-PAD-74</li>
        <li>RECETA</li>
        <li>CARTA COMPROMISO</li>
        <li>CONSENTIMIENTO INFORMADO</li>
        <li>FORM RESUMEN DE H.C.</li>
        <li>LABORATORIO PATOLOGICO</li>
        <li>FOT DNI – CARNET – TIT Y CAUSANTE</li>
        <li>FOT REC SUELDO / COBRO JUB / ÚLTIMOS 6 PAGOS DEL MONOTRIBUTO</li>
        <li>CODEM ANSES Y CERTIF NEGATIVA (MES EN CURSO) TIT Y CAUS</li>
        <li>RP indicando la cantidad de envases que usará semestralmente. Para los meses de enero y julio el médico deberá indicar la cantidad de envases que necesitará por el lapso de 6 meses.</li>
    </ul>
    """
    st.markdown(contenido1, unsafe_allow_html=True)
    print_button(contenido1)

with st.expander("🔄 CONTINUIDAD EXTRACÁPITA"):
    contenido2 = """
    <h3>Requisitos Continuidad Extracápita</h3>
    <ul>
        <li>FORMULARIO PRESCRIPCION ONCOLOGICA CONTINUIDAD</li>
        <li>RECETA DE OSECAC</li>
        <li>CARTA COMPROMISO</li>
        <li>CONSENTIMIENTO INFORMADO</li>
        <li>FORM DE RESUMEN HIST CLINICA</li>
        <li>FORMULARIO DE TUTELAJE</li>
        <li>LABORATORIO PATOLOGICO</li>
        <li>CODEM Y CERTIF NEGATIVA TIT Y CAUS</li>
        <li>CERTIF DE DISCAPACIDAD (SI CORRESPONDE)</li>
        <li>EN CASO DE CAMBIO DE DOSIS (JUSTIFICACION DEL MEDICO)</li>
        <li>Para la medicación de los meses de enero y julio, el beneficiario deberá presentar una orden médica donde el médico tratante indique cuántos envases necesitará por el lapso de 6 meses.</li>
    </ul>
    """
    st.markdown(contenido2, unsafe_allow_html=True)
    print_button(contenido2)

with st.expander("🔄 CONTINUIDAD CÁPITA"):
    contenido3 = """
    <h3>Requisitos Continuidad Cápita</h3>
    <ul>
        <li>FORMULARIO F-PAD-2-75</li>
        <li>RECETARIOS OFICIALES CON DOSIS MENSUALES</li>
        <li>FOT DNI – CARNET – REC DE SUELDO / COBRO JUB / ULTIMOS 6 PAGOS MONOTRIBUTO</li>
        <li>CODEM Y CERTIF NEGATIVA TIT Y CAUS</li>
        <li>CERTIF DE DISCAPACIDAD (SI CORRESPONDE)</li>
        <li>EN CASO DE CAMBIO DE DOSIS (JUSTIFICACION DEL MEDICO)</li>
    </ul>
    """
    st.markdown(contenido3, unsafe_allow_html=True)
    print_button(contenido3)

st.markdown("---")

# ================= SECCIÓN MEDICAMENTOS =================
st.markdown("## 💊 MEDICAMENTOS")

# Lista completa de medicamentos (ordenada alfabéticamente)
medicamentos_completos = [
    ("5-AZACETIDINA", "Leucemia Mieloide Aguda / Síndrome Mielodisplásico"),
    ("ABACAVIR + LAMIVUDINA + ZIDOVUDINA", "Melanoma Metastásico / Mieloma Múltiple"),
    ("ABIRATERONA, ACETATO", "CÁNCER DE PRÓSTATA"),
    ("APREPITANT", "ONCOLOGÍA NO S.U.R."),
    ("ASPARAGINASA", "Leucemia Linfoblástica Aguda"),
    ("AXITINIB", "CÁNCER DE RIÑÓN"),
    ("AZACITIDINA", "Leucemia Mieloide Aguda / Síndrome Mielodisplásico"),
    ("BENDAMUSTINA, CLORHIDRATO", "Leucemia Linfática Crónica / Linfoma No Hodgkin Folicular / Mieloma Múltiple"),
    ("BEVACIZUMAB", "Cáncer de Colon / CÁNCER DE MAMA / Cáncer de Pulmón / CÁNCER DE RIÑÓN / Cáncer Ovárico Ep. T. de Falopio / Glioblastoma"),
    ("BEXAROTENO", "Linfoma Cutáneo"),
    ("BLEOMICINA", "ONCOLOGICOS CÁPITA"),
    ("BORTEZOMIB", "Linfoma de Células del Manto / Mieloma Múltiple"),
    ("BRENTUXIMAB VEDOTIN", "ONCOLOGÍA NO S.U.R."),
    ("CABAZITAXEL", "CÁNCER DE PRÓSTATA"),
    ("CAPECITABINA", "ONCOLOGÍA NO S.U.R."),
    ("CETUXIMAB", "Cáncer de Colon / Cáncer de Reg. Cabeza y Cuello / Glioblastoma"),
    ("CICLOFOSFAMIDA", "ONCOLOGICOS CÁPITA"),
    ("CIPROTERONA", "ONCOLOGICOS CÁPITA"),
    ("CISPLATINO", "ONCOLOGICOS CÁPITA"),
    ("CITARABINA", "ONCOLOGICOS CÁPITA"),
    ("CLOFAMBUCILO", "ONCOLOGICOS CÁPITA"),
    ("CLOFARABINA", "Leucemia Linfoblástica Aguda"),
    ("CRIZOTINIB", "Cáncer de Pulmón"),
    ("DACARBAZINA", "ONCOLOGICOS CÁPITA"),
    ("DACTINOMICINA", "ONCOLOGICOS CÁPITA"),
    ("DASATINIB", "Leucemia Linfoblástica Aguda / LEUCEMIA MIELOIDE CRÓNICA"),
    ("DECITABINE", "Síndrome Mielodisplásico"),
    ("DENOSUMAB", "ONCOLOGÍA NO S.U.R."),
    ("DEXAMETASONA", "ONCOLOGICOS CÁPITA"),
    ("DOCETAXEL", "ONCOLOGICOS CÁPITA"),
    ("DOXORRUBICINA LIPOSOMAL", "ONCOLOGÍA NO S.U.R."),
    ("ENZALUTAMIDA", "CÁNCER DE PRÓSTATA"),
    ("ERITROPOYETINA RECOMB. HUMANA", "ONCOLOGICOS CÁPITA"),
    ("ERLOTINIB", "Cáncer de Páncreas / Cáncer de Pulmón"),
    ("ERWINIA CRISANTASPASA", "Leucemia Linfoblástica Aguda"),
    ("ETOPÓSIDO", "ONCOLOGICOS CÁPITA"),
    ("EVEROLIMUS", "CÁNCER DE MAMA / Cáncer de Páncreas / CÁNCER DE RIÑÓN"),
    ("EXEMESTANO", "ONCOLOGICOS CÁPITA"),
    ("FILGRASTIM", "ONCOLOGICOS CÁPITA"),
    ("FLUDARABINA", "ONCOLOGICOS CÁPITA"),
    ("FLUTAMIDA", "ONCOLOGICOS CÁPITA"),
    ("FOSAPREPITANT DIMEGLUMINA", "Efectos adversos ONCO"),
    ("FULVESTRANT", "CÁNCER DE MAMA"),
    ("GEFITINIB", "Cáncer de Pulmón"),
    ("GEMCITABINA", "ONCOLOGICOS CÁPITA"),
    ("HIDROCORTISONA", "ONCOLOGICOS CÁPITA"),
    ("HIDROXIUREA", "ONCOLOGICOS CÁPITA"),
    ("IBRUTINIB", "ONCOLOGÍA NO S.U.R."),
    ("IDARRUBICINA", "ONCOLOGICOS CÁPITA"),
    ("IFOSFAMIDA", "ONCOLOGICOS CÁPITA"),
    ("IMATINIB", "CÁNCER GASTROINTESTINAL / Dermatofibrosarcoma Protuberans / Leucemia Linfoblástica Aguda / LEUCEMIA MIELOIDE CRÓNICA / Mastocitosis Sistémica Agresiva / Síndrome Hipereosinofílico / Síndrome Mielodisplásico"),
    ("IPILIMUMAB", "Melanoma Metastásico"),
    ("IRINOTECÁN", "ONCOLOGICOS CÁPITA"),
    ("IXABEPILONA", "CÁNCER DE MAMA"),
    ("IXAZOMIB", "Mieloma Múltiple"),
    ("LANREOTIDO", "Cáncer Hipofisario Productor de Somatrotrofina / Tumores Endocrinos Gastro-Entero-Pancreáticos Funcionales"),
    ("LAPATINIB", "CÁNCER DE MAMA"),
    ("LENALIDOMIDA", "Mieloma Múltiple / Síndrome Mielodisplásico"),
    ("LETROZOL", "ONCOLOGICOS CÁPITA"),
    ("MEDROXIPROGESTERONA", "ONCOLOGICOS CÁPITA"),
    ("MEGESTROL", "ONCOLOGICOS CÁPITA"),
    ("MELFALANO", "ONCOLOGICOS CÁPITA"),
    ("MERCAPTOPURINA", "ONCOLOGICOS CÁPITA"),
    ("METIL-PREDNISOLONA", "ONCOLOGICOS CÁPITA"),
    ("METOTREXATO", "ONCOLOGICOS CÁPITA"),
    ("MITOMICINA", "ONCOLOGICOS CÁPITA"),
    ("MITOTANO", "ONCOLOGÍA NO S.U.R."),
    ("MITOXANTRONA", "ONCOLOGICOS CÁPITA"),
    ("NANDROLONA", "ONCOLOGICOS CÁPITA"),
    ("NILOTINIB", "LEUCEMIA MIELOIDE CRÓNICA"),
    ("NIMOTUZUMAB", "Cáncer de Reg. Cabeza y Cuello"),
    ("OCTREOTIDA", "Cáncer Hipofisario Productor de Somatrotrofina / Tumores Endocrinos Gastro-Entero-Pancreáticos Funcionales"),
    ("OLAPARIB", "ONCOLOGÍA NO S.U.R."),
    ("ONDANSETRÓN", "ONCOLOGICOS CÁPITA"),
    ("OSIMERTINIB", "ONCOLOGÍA NO S.U.R."),
    ("OXALIPLATINO", "ONCOLOGICOS CÁPITA"),
    ("PACLITAXEL", "ONCOLOGICOS CÁPITA"),
    ("PACLITAXEL + ALBÚMINA", "Cáncer de Páncreas"),
    ("PAMIDRONATO DISÓDICO", "ONCOLOGICOS CÁPITA"),
    ("PANITUMUMAB", "Cáncer de Colon"),
    ("PAZOPANIB", "CÁNCER DE RIÑÓN / Sarcoma de Partes Blandas"),
    ("PEG ASPARAGINASA", "Leucemia Linfoblástica Aguda"),
    ("PEGINTERFERON ALFA-2A", "Melanoma Metastásico"),
    ("PEMETREXED", "ONCOLOGÍA NO S.U.R."),
    ("PERTUZUMAB", "CÁNCER DE MAMA"),
    ("PERTUZUMAB + TRASTUZUMAB", "CÁNCER DE MAMA"),
    ("RITUXIMAB", "LEUCEMIA LINFÁTICA CRÓNICA / LINFOMA NO HODGKIN FOLICULAR"),
    ("RUXOLITINIB", "Mielofibrosis"),
    ("SORAFENIB", "CÁNCER DE HÍGADO (CHC) / CÁNCER DE RIÑÓN"),
    ("SUNITINIB", "Cáncer de Páncreas / CÁNCER DE RIÑÓN / CÁNCER GASTROINTESTINAL"),
    ("TALIDOMIDA", "ONCOLOGÍA NO S.U.R."),
    ("TAMOXIFENO", "ONCOLOGICOS CÁPITA"),
    ("TEMOZOLOMIDA", "Astrocitoma Anaplásico / Glioblastoma / Melanoma Metastásico"),
    ("TEMSIROLIMUS", "CÁNCER DE RIÑÓN"),
    ("TIOGUANINA", "ONCOLOGICOS CÁPITA"),
    ("TRABECTEDINA", "Sarcoma de Partes Blandas"),
    ("TRASTUZUMAB", "CÁNCER DE MAMA / CÁNCER GASTROINTESTINAL"),
    ("TRASTUZUMAB + EMTANSINA", "CÁNCER DE MAMA"),
    ("TRETINOÍNA", "ONCOLOGICOS CÁPITA"),
    ("TRIOXIDO DE ARSÉNICO", "Leucemia Promielocítica"),
    ("VEMURAFENIB", "Melanoma Metastásico"),
    ("VINBLASTINA", "ONCOLOGICOS CÁPITA"),
    ("VINCRISTINA", "ONCOLOGICOS CÁPITA"),
    ("VINORELBINA", "ONCOLOGICOS CÁPITA"),
    ("ZOLEDRÓNICO AC.", "ONCOLOGÍA NO S.U.R. / TRATAMIENTO DEL DOLOR ONCOLÓGICO (Receta Magistral)")
]

# Ordenar alfabéticamente
medicamentos_completos.sort(key=lambda x: x[0])

# Crear lista de nombres
nombres = [m[0] for m in medicamentos_completos]

# ===== Widget de selección con búsqueda y sin despliegue masivo =====
col_busqueda, col_programa = st.columns([1, 1])

with col_busqueda:
    # Campo de búsqueda
    busqueda = st.text_input("🔎 Buscar medicamento", placeholder="Escribí para filtrar...")
    
    # Filtrar nombres según búsqueda
    if busqueda:
        nombres_filtrados = [n for n in nombres if busqueda.upper() in n.upper()]
    else:
        nombres_filtrados = nombres
    
    # Selector: solo muestra un elemento a la vez, usa flechas del teclado para navegar
    # Si hay muchos resultados, el dropdown aparecerá con scroll (lo limitamos con CSS)
    if nombres_filtrados:
        seleccion = st.selectbox(
            "SELECCIONÁ UN MEDICAMENTO:",
            nombres_filtrados,
            index=0,
            key="med_selector"
        )
    else:
        st.warning("No se encontraron medicamentos con ese nombre.")
        seleccion = None

with col_programa:
    if seleccion:
        programa = next(m[1] for m in medicamentos_completos if m[0] == seleccion)
        st.markdown(f"""
        <div style="background-color:#f8fafc; border-left:4px solid #2563eb; padding:1rem; border-radius:8px; margin-top: 2.2rem;">
            <strong style="color:#2563eb;">PROGRAMA ASOCIADO:</strong><br>
            {programa}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Seleccioná un medicamento para ver su programa.")

# ================= PIE DE PÁGINA =================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1rem;'>Documentación actualizada periódicamente. Para consultas, contactar al área de Oncología.</p>", unsafe_allow_html=True)
