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
/* Estilo para botones de impresión */
.print-button button {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 0.25rem 0.75rem !important;
    font-size: 0.8rem !important;
    transition: all 0.2s ease !important;
}
.print-button button:hover {
    background-color: #e2e8f0 !important;
    border-color: #94a3b8 !important;
}
/* Estilo para la lista scrollable de medicamentos */
.med-list {
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.5rem;
    background-color: #f8fafc;
}
.med-item {
    padding: 0.5rem;
    margin: 0.2rem 0;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
}
.med-item:hover {
    background-color: #e2e8f0;
}
.med-item.selected {
    background-color: #cbd5e1;
    font-weight: 600;
}
.program-card {
    background-color: #f8fafc;
    border-left: 4px solid #2563eb;
    padding: 1rem;
    border-radius: 8px;
    margin-top: 1rem;
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

# Lista de planillas con los nombres exactos e IDs
planillas = [
    ("F-PAD-2-219 CONSENTIMIENTO INFORMADO MEDICAMENTOS RECUPERO SUR", "1ISSigS6YBugt4xfS7tVz00pLfpdqkBR9"),
    ("F-PAD.2.74 Prescripción Oncológica 1ERA VEZ – Continuidad", "1AJidHwRGRAmczopQPqsYwRVPfTiTlhiK"),
    ("F-PAD-2-075 Prescripcion Oncologica Continuidad de Tratamiento", "1aslyVdHH56NU3nHacLl7fHu0opvbEueY")
]

for nombre, doc_id in planillas:
    url = f"https://drive.google.com/file/d/{doc_id}/view"
    st.markdown(f"- [{nombre}]({url})")

st.markdown("---")

# ================= SECCIÓN REQUISITOS =================
st.markdown("## 📋 Requisitos para medicación oncológica")

# Función para generar botón de impresión con JavaScript
def print_section(html_content, key):
    # Creamos un bloque de HTML que contiene el contenido y un botón que abre ventana de impresión
    # Usamos st.components.v1.html para inyectar JS que imprima el contenido.
    # El contenido se pasa como string.
    # Como el contenido puede ser largo, lo codificamos en el HTML.
    # Usaremos un iframe invisible o directamente un script.
    # Para simplificar, usaremos un botón que abre una nueva ventana con el contenido formateado y llama a print.
    # Esto es compatible con Streamlit.
    print_html = f"""
    <div style="margin-top: 0.5rem;">
        <button onclick="imprimirContenido()" style="background-color:#f1f5f9; border:1px solid #cbd5e1; border-radius:8px; padding:0.25rem 0.75rem; cursor:pointer;">🖨️ Imprimir</button>
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
    st.components.v1.html(print_html, height=80)

# Expander 1: Primera vez
with st.expander("💊 Primera vez (cápita y extracápita)"):
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
    print_section(contenido1, "print1")

# Expander 2: Continuidad extracápita
with st.expander("🔄 Continuidad extracápita"):
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
    print_section(contenido2, "print2")

# Expander 3: Continuidad cápita
with st.expander("🔄 Continuidad cápita"):
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
    print_section(contenido3, "print3")

st.markdown("---")

# ================= SECCIÓN MEDICAMENTOS =================
st.markdown("## 💊 MEDICAMENTOS")

# Datos completos de medicamentos (unión de no cápita y cápita)
# Para no repetir el enorme listado, usamos la lista que ya teníamos y la copiamos aquí.
# Voy a usar la misma estructura que antes, pero compactada en una lista de tuplas.
# Esta es la lista extensa de la circular.
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
    ("ZOLEDRÓNICO AC.", "ONCOLOGÍA NO S.U.R. / TRATAMIENTO DEL DOLOR ONCOLÓGICO (Receta Magistral)"),
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

# Extraer lista de nombres (para filtro)
nombres_med = [m[0] for m in medicamentos_completos]

# Buscador
busqueda = st.text_input("🔎 Buscar medicamento", placeholder="Escribí el principio activo...")

# Filtrar
if busqueda:
    filtro = [m for m in medicamentos_completos if busqueda.upper() in m[0].upper()]
else:
    filtro = medicamentos_completos

# Si hay resultados, mostrar lista scrollable
if filtro:
    # Crear un select de radio con los nombres filtrados, pero sin dropdown (es una lista vertical)
    # Usamos st.radio con una key y lo envolvemos en un div con scroll
    # Para que sea solo una lista, no un dropdown, st.radio por defecto muestra una columna vertical.
    # Podemos personalizar el contenedor con CSS para darle altura fija y scroll.
    st.markdown("""
    <style>
    div[data-testid="stRadio"] > div {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.5rem;
        background-color: #f8fafc;
    }
    div[data-testid="stRadio"] label {
        display: block;
        padding: 0.3rem 0.5rem;
        margin: 0;
        cursor: pointer;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Obtener lista de nombres filtrados
    nombres_filtrados = [m[0] for m in filtro]
    seleccion = st.radio(
        "Seleccioná un medicamento:",
        nombres_filtrados,
        index=0,
        key="med_selector"
    )
    # Encontrar el programa del seleccionado
    programa = next(m[1] for m in filtro if m[0] == seleccion)
    st.markdown(f"""
    <div class="program-card">
        <strong style="color:#2563eb;">Programa asociado:</strong><br>
        {programa}
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No se encontraron medicamentos con ese nombre.")

# ================= PIE DE PÁGINA =================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>Documentación actualizada periódicamente. Para consultas, contactar al área de Oncología.</p>", unsafe_allow_html=True)
