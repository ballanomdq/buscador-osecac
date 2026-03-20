import streamlit as st
import base64
import os

st.set_page_config(
    page_title="OSECAC MDP - Documentos Oncológicos",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== CSS (fondo blanco, estilo sobrio) ==================
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], #MainMenu, footer, header { display: none !important; }
.stApp { background-color: #ffffff !important; color: #1e293b !important; }
.block-container { max-width: 1000px !important; padding-top: 1rem !important; }
h1, h2, h3 { color: #0f172a !important; }
hr { margin: 2rem 0; }
.stButton > button {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 0.25rem 0.75rem !important;
    font-size: 0.8rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #e2e8f0 !important;
    border-color: #94a3b8 !important;
}
.expander-header {
    font-weight: 600;
    font-size: 1.2rem;
    margin: 0;
}
a {
    color: #2563eb;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGO CENTRADO (3 VECES MÁS GRANDE) =================
logo_path = "logo osecac.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 1rem 0 2rem 0;">
            <img src="data:image/png;base64,{logo_base64}" 
                 style="width: 300px; height: auto;" 
                 alt="Logo OSECAC">
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="display: flex; justify-content: center; margin: 1rem 0 2rem 0;">
            <div style="width:300px; height:150px; background: #e2e8f0; border-radius:16px; border:1px solid #cbd5e1;"></div>
        </div>
    """, unsafe_allow_html=True)

# ================= SECCIÓN PLANILLAS =================
st.markdown("## 📄 PLANILLAS")

# IDs
id_consentimiento = "1ISSigS6YBugt4xfS7tVz00pLfpdqkBR9"
id_presc_nuevo = "1AJidHwRGRAmczopQPqsYwRVPfTiTlhiK"
id_presc_continuidad = "1aslyVdHH56NU3nHacLl7fHu0opvbEueY"

documentos = [
    ("F-PAD-2-219 CONSENTIMIENTO INFORMADO MEDICAMENTOS RECUPERO SUR", id_consentimiento),
    ("F-PAD.2.74 Prescripción Oncológica 1ERA VEZ – Continuidad", id_presc_nuevo),
    ("F-PAD-2-075 Prescripcion Oncologica Continuidad de Tratamiento", id_presc_continuidad)
]

for nombre, doc_id in documentos:
    url = f"https://drive.google.com/file/d/{doc_id}/view"
    st.markdown(f"- [{nombre}]({url})")

st.markdown("---")

# ================= SECCIÓN REQUISITOS =================
st.markdown("## 📋 Requisitos para medicación oncológica")

# Función para generar botón de imprimir (usa JavaScript)
def imprimir_contenido(titulo, contenido):
    # Escapamos el contenido para HTML
    contenido_html = contenido.replace("\n", "<br>")
    html = f"""
    <html>
    <head><title>{titulo}</title></head>
    <body>
    <h1>{titulo}</h1>
    <pre style="font-family: monospace;">{contenido}</pre>
    <script>window.print();</script>
    </body>
    </html>
    """
    # Creamos un archivo temporal y lo mostramos en una nueva ventana
    # Usamos st.components.v1.html para abrir una ventana emergente con el contenido y llamar a print()
    st.components.v1.html(html, height=0, scrolling=False)

# Expander 1: Primera vez
with st.expander("💊 Primera vez (cápita y extracápita)"):
    requisitos1 = """REQUISITOS PRIMERA VEZ ONCOLÓGICA

- FORM PRESCRIPCION ONCOLOGICA F-PAD-74
- RECETA
- CARTA COMPROMISO
- CONSENTIMIENTO INFORMADO
- FORM RESUMEN DE H.C.
- LABORATORIO PATOLOGICO
- FOT DNI – CARNET – TIT Y CAUSANTE
- FOT REC SUELDO / COBRO JUB / ÚLTIMOS 6 PAGOS DEL MONOTRIBUTO
- CODEM ANSES Y CERTIF NEGATIVA (MES EN CURSO) TIT Y CAUS
- RP indicando la cantidad de envases que usará semestralmente. Para los meses de enero y julio el médico deberá indicar la cantidad de envases que necesitará por el lapso de 6 meses."""
    st.markdown(requisitos1.replace("\n", "\n\n"))
    if st.button("🖨️ Imprimir", key="print_primera"):
        imprimir_contenido("Requisitos Primera Vez", requisitos1)

# Expander 2: Continuidad extracápita
with st.expander("🔄 Continuidad extracápita"):
    requisitos2 = """REQUISITOS CONTINUIDAD EXTRACÁPITA

- FORMULARIO PRESCRIPCION ONCOLOGICA CONTINUIDAD
- RECETA DE OSECAC
- CARTA COMPROMISO
- CONSENTIMIENTO INFORMADO
- FORM DE RESUMEN HIST CLINICA
- FORMULARIO DE TUTELAJE
- LABORATORIO PATOLOGICO
- CODEM Y CERTIF NEGATIVA TIT Y CAUS
- CERTIF DE DISCAPACIDAD (SI CORRESPONDE)
- EN CASO DE CAMBIO DE DOSIS (JUSTIFICACION DEL MEDICO)
- Para la medicación de los meses de enero y julio, el beneficiario deberá presentar una orden médica donde el médico tratante indique cuántos envases necesitará por el lapso de 6 meses."""
    st.markdown(requisitos2.replace("\n", "\n\n"))
    if st.button("🖨️ Imprimir", key="print_extra"):
        imprimir_contenido("Requisitos Continuidad Extracápita", requisitos2)

# Expander 3: Continuidad cápita
with st.expander("🔄 Continuidad cápita"):
    requisitos3 = """REQUISITOS CONTINUIDAD CÁPITA

- FORMULARIO F-PAD-2-75
- RECETARIOS OFICIALES CON DOSIS MENSUALES
- FOT DNI – CARNET – REC DE SUELDO / COBRO JUB / ULTIMOS 6 PAGOS MONOTRIBUTO
- CODEM Y CERTIF NEGATIVA TIT Y CAUS
- CERTIF DE DISCAPACIDAD (SI CORRESPONDE)
- EN CASO DE CAMBIO DE DOSIS (JUSTIFICACION DEL MEDICO)"""
    st.markdown(requisitos3.replace("\n", "\n\n"))
    if st.button("🖨️ Imprimir", key="print_capita"):
        imprimir_contenido("Requisitos Continuidad Cápita", requisitos3)

st.markdown("---")

# ================= SECCIÓN MEDICAMENTOS =================
st.markdown("## 💊 MEDICAMENTOS")

# Datos completos (como antes)
no_capita = [
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
    ("BORTEZOMIB", "Linfoma de Células del Manto / Mieloma Múltiple"),
    ("BRENTUXIMAB VEDOTIN", "ONCOLOGÍA NO S.U.R."),
    ("CABAZITAXEL", "CÁNCER DE PRÓSTATA"),
    ("CAPECITABINA", "ONCOLOGÍA NO S.U.R."),
    ("CETUXIMAB", "Cáncer de Colon / Cáncer de Reg. Cabeza y Cuello / Glioblastoma"),
    ("CLOFARABINA", "Leucemia Linfoblástica Aguda"),
    ("CRIZOTINIB", "Cáncer de Pulmón"),
    ("DASATINIB", "Leucemia Linfoblástica Aguda / LEUCEMIA MIELOIDE CRÓNICA"),
    ("DECITABINE", "Síndrome Mielodisplásico"),
    ("DENOSUMAB", "ONCOLOGÍA NO S.U.R."),
    ("DOXORRUBICINA LIPOSOMAL", "ONCOLOGÍA NO S.U.R."),
    ("ENZALUTAMIDA", "CÁNCER DE PRÓSTATA"),
    ("ERLOTINIB", "Cáncer de Páncreas / Cáncer de Pulmón"),
    ("ERWINIA CRISANTASPASA", "Leucemia Linfoblástica Aguda"),
    ("EVEROLIMUS", "CÁNCER DE MAMA / Cáncer de Páncreas / CÁNCER DE RIÑÓN"),
    ("FOSAPREPITANT DIMEGLUMINA", "Efectos adversos ONCO"),
    ("FULVESTRANT", "CÁNCER DE MAMA"),
    ("GEFITINIB", "Cáncer de Pulmón"),
    ("IBRUTINIB", "ONCOLOGÍA NO S.U.R."),
    ("IMATINIB", "CÁNCER GASTROINTESTINAL / Dermatofibrosarcoma Protuberans / Leucemia Linfoblástica Aguda / LEUCEMIA MIELOIDE CRÓNICA / Mastocitosis Sistémica Agresiva / Síndrome Hipereosinofílico / Síndrome Mielodisplásico"),
    ("IPILIMUMAB", "Melanoma Metastásico"),
    ("IXABEPILONA", "CÁNCER DE MAMA"),
    ("IXAZOMIB", "Mieloma Múltiple"),
    ("LANREOTIDO", "Cáncer Hipofisario Productor de Somatrotrofina / Tumores Endocrinos Gastro-Entero-Pancreáticos Funcionales"),
    ("LAPATINIB", "CÁNCER DE MAMA"),
    ("LENALIDOMIDA", "Mieloma Múltiple / Síndrome Mielodisplásico"),
    ("MITOTANO", "ONCOLOGÍA NO S.U.R."),
    ("NILOTINIB", "LEUCEMIA MIELOIDE CRÓNICA"),
    ("NIMOTUZUMAB", "Cáncer de Reg. Cabeza y Cuello"),
    ("OCTREOTIDA", "Cáncer Hipofisario Productor de Somatrotrofina / Tumores Endocrinos Gastro-Entero-Pancreáticos Funcionales"),
    ("OLAPARIB", "ONCOLOGÍA NO S.U.R."),
    ("OSIMERTINIB", "ONCOLOGÍA NO S.U.R."),
    ("PACLITAXEL + ALBÚMINA", "Cáncer de Páncreas"),
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
    ("TEMOZOLOMIDA", "Astrocitoma Anaplásico / Glioblastoma / Melanoma Metastásico"),
    ("TEMSIROLIMUS", "CÁNCER DE RIÑÓN"),
    ("TRABECTEDINA", "Sarcoma de Partes Blandas"),
    ("TRASTUZUMAB", "CÁNCER DE MAMA / CÁNCER GASTROINTESTINAL"),
    ("TRASTUZUMAB + EMTANSINA", "CÁNCER DE MAMA"),
    ("TRIOXIDO DE ARSÉNICO", "Leucemia Promielocítica"),
    ("VEMURAFENIB", "Melanoma Metastásico"),
    ("ZOLEDRÓNICO AC.", "ONCOLOGÍA NO S.U.R. / TRATAMIENTO DEL DOLOR ONCOLÓGICO (Receta Magistral)")
]

capita = [
    ("BLEOMICINA", "ONCOLOGICOS CÁPITA"),
    ("CICLOFOSFAMIDA", "ONCOLOGICOS CÁPITA"),
    ("CIPROTERONA", "ONCOLOGICOS CÁPITA"),
    ("CISPLATINO", "ONCOLOGICOS CÁPITA"),
    ("CITARABINA", "ONCOLOGICOS CÁPITA"),
    ("CLOFAMBUCILO", "ONCOLOGICOS CÁPITA"),
    ("DACARBAZINA", "ONCOLOGICOS CÁPITA"),
    ("DACTINOMICINA", "ONCOLOGICOS CÁPITA"),
    ("DEXAMETASONA", "ONCOLOGICOS CÁPITA"),
    ("DOCETAXEL", "ONCOLOGICOS CÁPITA"),
    ("ERITROPOYETINA RECOMB. HUMANA", "ONCOLOGICOS CÁPITA"),
    ("ETOPÓSIDO", "ONCOLOGICOS CÁPITA"),
    ("EXEMESTANO", "ONCOLOGICOS CÁPITA"),
    ("FILGRASTIM", "ONCOLOGICOS CÁPITA"),
    ("FLUDARABINA", "ONCOLOGICOS CÁPITA"),
    ("FLUTAMIDA", "ONCOLOGICOS CÁPITA"),
    ("GEMCITABINA", "ONCOLOGICOS CÁPITA"),
    ("HIDROCORTISONA", "ONCOLOGICOS CÁPITA"),
    ("HIDROXIUREA", "ONCOLOGICOS CÁPITA"),
    ("IDARRUBICINA", "ONCOLOGICOS CÁPITA"),
    ("IFOSFAMIDA", "ONCOLOGICOS CÁPITA"),
    ("IRINOTECÁN", "ONCOLOGICOS CÁPITA"),
    ("LETROZOL", "ONCOLOGICOS CÁPITA"),
    ("MEDROXIPROGESTERONA", "ONCOLOGICOS CÁPITA"),
    ("MEGESTROL", "ONCOLOGICOS CÁPITA"),
    ("MELFALANO", "ONCOLOGICOS CÁPITA"),
    ("MERCAPTOPURINA", "ONCOLOGICOS CÁPITA"),
    ("METIL-PREDNISOLONA", "ONCOLOGICOS CÁPITA"),
    ("METOTREXATO", "ONCOLOGICOS CÁPITA"),
    ("MITOMICINA", "ONCOLOGICOS CÁPITA"),
    ("MITOXANTRONA", "ONCOLOGICOS CÁPITA"),
    ("NANDROLONA", "ONCOLOGICOS CÁPITA"),
    ("ONDANSETRÓN", "ONCOLOGICOS CÁPITA"),
    ("OXALIPLATINO", "ONCOLOGICOS CÁPITA"),
    ("PACLITAXEL", "ONCOLOGICOS CÁPITA"),
    ("PAMIDRONATO DISÓDICO", "ONCOLOGICOS CÁPITA"),
    ("TAMOXIFENO", "ONCOLOGICOS CÁPITA"),
    ("TIOGUANINA", "ONCOLOGICOS CÁPITA"),
    ("TRETINOÍNA", "ONCOLOGICOS CÁPITA"),
    ("VINBLASTINA", "ONCOLOGICOS CÁPITA"),
    ("VINCRISTINA", "ONCOLOGICOS CÁPITA"),
    ("VINORELBINA", "ONCOLOGICOS CÁPITA")
]

todos_medicamentos = no_capita + capita

# Crear dos listas para el selectbox: una con los nombres y otra con los programas correspondientes
nombres = [m[0] for m in todos_medicamentos]
programas = [m[1] for m in todos_medicamentos]

# Selector para medicamento
med_seleccionado = st.selectbox(
    "Seleccioná un principio activo",
    options=nombres,
    index=0,
    key="med_selector"
)

# Buscar el programa correspondiente
idx = nombres.index(med_seleccionado)
programa_correspondiente = programas[idx]

# Mostrar el programa en un recuadro destacado
st.markdown(f"""
<div style="background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 1rem; margin: 1rem 0; border-radius: 8px;">
    <strong style="font-size: 1.1rem;">Programa asociado:</strong><br>
    <span style="font-size: 1rem; color: #1e293b;">{programa_correspondiente}</span>
</div>
""", unsafe_allow_html=True)

# Pie de página
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>Documentación actualizada periódicamente. Para consultas, contactar al área de Oncología.</p>", unsafe_allow_html=True)
