import streamlit as st
import pandas as pd
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
.stButton > button, .stDownloadButton > button {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 0.25rem 0.75rem !important;
    font-size: 0.8rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
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

# ================= LOGO CENTRADO (MÁS GRANDE) =================
logo_path = "logo osecac.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 1rem 0 2rem 0;">
            <img src="data:image/png;base64,{logo_base64}" 
                 style="width: 200px; height: auto;" 
                 alt="Logo OSECAC">
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="display: flex; justify-content: center; margin: 1rem 0 2rem 0;">
            <div style="width:200px; height:100px; background: #e2e8f0; border-radius:16px; border:1px solid #cbd5e1;"></div>
        </div>
    """, unsafe_allow_html=True)

# ================= SECCIÓN PLANILLAS =================
st.markdown("## 📄 PLANILLAS")
st.markdown("Acceso directo a los formularios oficiales:")

# IDs reales que ya tenés
id_presc_nuevo = "1AJidHwRGRAmczopQPqsYwRVPfTiTlhiK"
id_presc_continuidad = "1aslyVdHH56NU3nHacLl7fHu0opvbEueY"
# IDs pendientes (reemplazá cuando los tengas)
id_consentimiento = ""   # Ej: "1XyZabc..."
id_listado = ""          # Ej: "1AbCdEf..."

documentos = [
    ("📋 Listado de programas según patología oncológica", id_listado),
    ("📝 Consentimiento Informado (F-PAD 2-219)", id_consentimiento),
    ("💊 Prescripción Oncológica – Nuevo Tratamiento", id_presc_nuevo),
    ("🔄 Prescripción Oncológica – Continuidad", id_presc_continuidad)
]

for nombre, doc_id in documentos:
    if doc_id:
        url = f"https://drive.google.com/file/d/{doc_id}/view"
        st.markdown(f"- [{nombre}]({url})")
    else:
        st.markdown(f"- {nombre} *(enlace pendiente de configuración)*")

st.markdown("---")

# ================= SECCIÓN REQUISITOS =================
st.markdown("## 📋 Requisitos para medicación oncológica")

# Expander 1: Primera vez
with st.expander("💊 Primera vez (cápita y extracápita)"):
    st.markdown("""
    **Requisitos:**
    - FORM PRESCRIPCION ONCOLOGICA F-PAD-74
    - RECETA
    - CARTA COMPROMISO
    - CONSENTIMIENTO INFORMADO
    - FORM RESUMEN DE H.C.
    - LABORATORIO PATOLOGICO
    - FOT DNI – CARNET – TIT Y CAUSANTE
    - FOT REC SUELDO / COBRO JUB / ÚLTIMOS 6 PAGOS DEL MONOTRIBUTO
    - CODEM ANSES Y CERTIF NEGATIVA (MES EN CURSO) TIT Y CAUS
    - RP indicando la cantidad de envases que usará semestralmente. Para los meses de enero y julio el médico deberá indicar la cantidad de envases que necesitará por el lapso de 6 meses.
    """)
    st.download_button(
        label="🖨️ Descargar / Imprimir",
        data="REQUISITOS PRIMERA VEZ ONCOLÓGICA\n\n- FORM PRESCRIPCION ONCOLOGICA F-PAD-74\n- RECETA\n- CARTA COMPROMISO\n- CONSENTIMIENTO INFORMADO\n- FORM RESUMEN DE H.C.\n- LABORATORIO PATOLOGICO\n- FOT DNI – CARNET – TIT Y CAUSANTE\n- FOT REC SUELDO / COBRO JUB / ÚLTIMOS 6 PAGOS DEL MONOTRIBUTO\n- CODEM ANSES Y CERTIF NEGATIVA (MES EN CURSO) TIT Y CAUS\n- RP indicando la cantidad de envases que usará semestralmente. Para los meses de enero y julio el médico deberá indicar la cantidad de envases que necesitará por el lapso de 6 meses.",
        file_name="requisitos_primera_vez.txt",
        mime="text/plain",
        key="download_primera"
    )

# Expander 2: Continuidad extracápita
with st.expander("🔄 Continuidad extracápita"):
    st.markdown("""
    **Requisitos:**
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
    - Para la medicación de los meses de enero y julio, el beneficiario deberá presentar una orden médica donde el médico tratante indique cuántos envases necesitará por el lapso de 6 meses.
    """)
    st.download_button(
        label="🖨️ Descargar / Imprimir",
        data="REQUISITOS CONTINUIDAD EXTRACÁPITA\n\n- FORMULARIO PRESCRIPCION ONCOLOGICA CONTINUIDAD\n- RECETA DE OSECAC\n- CARTA COMPROMISO\n- CONSENTIMIENTO INFORMADO\n- FORM DE RESUMEN HIST CLINICA\n- FORMULARIO DE TUTELAJE\n- LABORATORIO PATOLOGICO\n- CODEM Y CERTIF NEGATIVA TIT Y CAUS\n- CERTIF DE DISCAPACIDAD (SI CORRESPONDE)\n- EN CASO DE CAMBIO DE DOSIS (JUSTIFICACION DEL MEDICO)\n- Para la medicación de los meses de enero y julio, el beneficiario deberá presentar una orden médica donde el médico tratante indique cuántos envases necesitará por el lapso de 6 meses.",
        file_name="requisitos_continuidad_extra.txt",
        mime="text/plain",
        key="download_extra"
    )

# Expander 3: Continuidad cápita
with st.expander("🔄 Continuidad cápita"):
    st.markdown("""
    **Requisitos:**
    - FORMULARIO F-PAD-2-75
    - RECETARIOS OFICIALES CON DOSIS MENSUALES
    - FOT DNI – CARNET – REC DE SUELDO / COBRO JUB / ULTIMOS 6 PAGOS MONOTRIBUTO
    - CODEM Y CERTIF NEGATIVA TIT Y CAUS
    - CERTIF DE DISCAPACIDAD (SI CORRESPONDE)
    - EN CASO DE CAMBIO DE DOSIS (JUSTIFICACION DEL MEDICO)
    """)
    st.download_button(
        label="🖨️ Descargar / Imprimir",
        data="REQUISITOS CONTINUIDAD CÁPITA\n\n- FORMULARIO F-PAD-2-75\n- RECETARIOS OFICIALES CON DOSIS MENSUALES\n- FOT DNI – CARNET – REC DE SUELDO / COBRO JUB / ULTIMOS 6 PAGOS MONOTRIBUTO\n- CODEM Y CERTIF NEGATIVA TIT Y CAUS\n- CERTIF DE DISCAPACIDAD (SI CORRESPONDE)\n- EN CASO DE CAMBIO DE DOSIS (JUSTIFICACION DEL MEDICO)",
        file_name="requisitos_continuidad_capita.txt",
        mime="text/plain",
        key="download_capita"
    )

st.markdown("---")

# ================= SECCIÓN MEDICAMENTOS =================
st.markdown("## 💊 MEDICAMENTOS")
st.markdown("Listado completo de principios activos y su programa asociado:")

# ========== DATOS DE MEDICAMENTOS (tomados de la circular) ==========
# No Cápita (con sus programas)
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

# Cápita
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

# Unir ambas listas
todos_medicamentos = no_capita + capita

# Crear DataFrame
df_meds = pd.DataFrame(todos_medicamentos, columns=["Principio Activo", "Programa"])

# Mostrar tabla con scroll
st.dataframe(
    df_meds,
    use_container_width=True,
    height=500,
    hide_index=True
)

# ================= PIE DE PÁGINA =================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>Documentación actualizada periódicamente. Para consultas, contactar al área de Oncología.</p>", unsafe_allow_html=True)
