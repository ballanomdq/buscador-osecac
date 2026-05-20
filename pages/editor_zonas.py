import streamlit as st
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="Planilla Inspectores", layout="wide")
st.title("🖊️ Planilla Inspectores - Visual")

# ====================== FUNCIÓN PARA RELLENAR PDF ======================
def completar_pdf(datos):
    reader = PdfReader("PLANILLA INSPECTORES.pdf")
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)
    writer.update_page_form_field_values(writer.pages[0], datos)
    
    with open("PLANILLA_COMPLETADA.pdf", "wb") as f:
        writer.write(f)
    return "PLANILLA_COMPLETADA.pdf"

# ====================== DATOS GENERALES (arriba como en la planilla) ======================
st.subheader("Datos del Inspector y Fecha")
col_gen1, col_gen2, col_gen3 = st.columns([3, 2, 2])

with col_gen1:
    inspector = st.text_input("APELLIDO Y NOMBRES DEL INSPECTOR", key="inspector")
with col_gen2:
    area = st.text_input("ÁREA DE FISCALIZACIÓN", key="area")
with col_gen3:
    fecha = st.text_input("LUGAR Y FECHA / MES Y AÑO", key="fecha")

# ====================== TABLA PRINCIPAL (lo más parecida posible) ======================
st.subheader("Tabla de Empresas Visitadas")

# Creamos una tabla visual
datos = {}

headers = ["NRO", "Empresa / Dirección", "CUIT", "FOLIO", "Empleados", "Meses", "Deuda Determinada", "Observaciones"]
data_rows = []

for i in range(1, 17):
    cols = st.columns([0.8, 3.5, 2, 1.2, 1.5, 1.2, 2, 2.5])
    
    with cols[0]:
        nro = st.text_input("NRO", value="", key=f"nro_{i}", label_visibility="collapsed")
        datos[f"NRORow{i}"] = nro
    
    with cols[1]:
        empresa = st.text_input("Empresa", value="", key=f"emp_{i}", label_visibility="collapsed")
        datos[f"EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow{i}"] = empresa
    
    with cols[2]:
        cuit = st.text_input("CUIT", value="", key=f"cuit_{i}", label_visibility="collapsed")
        datos[f"NRO DE  CUITRow{i}"] = cuit
    
    with cols[3]:
        folio = st.text_input("FOLIO", value="", key=f"folio_{i}", label_visibility="collapsed")
        datos[f"FOLIORow{i}"] = folio
    
    with cols[4]:
        empleados = st.text_input("Emp.", value="", key=f"empados_{i}", label_visibility="collapsed")
        datos[f"EMPLE ADOSRow{i}"] = empleados
    
    with cols[5]:
        meses = st.text_input("Meses", value="", key=f"meses_{i}", label_visibility="collapsed")
        datos[f"M E S E SRow{i}"] = meses
    
    with cols[6]:
        deuda = st.text_input("Deuda", value="", key=f"deuda_{i}", label_visibility="collapsed")
        datos[f"DEUDA DETERMINADARow{i}"] = deuda
    
    with cols[7]:
        obs = st.text_input("Obs.", value="", key=f"obs_{i}", label_visibility="collapsed")
        if i <= 4:
            datos[f"OBSERVACIONESRow{i}"] = obs
        else:
            datos["OBSERVACIONESRow1"] = obs  # fallback

# ====================== TOTALES ======================
st.subheader("Totales")
col_t = st.columns(4)
with col_t[0]:
    datos["EMPLE ADOSSUBTOTAL  TOTAL"] = st.text_input("Total Empleados")
with col_t[1]:
    datos["DEUDA DETERMINADASUBTOTALTOTAL"] = st.text_input("Total Deuda")
with col_t[2]:
    datos["ACSUBTOTAL  TOTAL"] = st.text_input("Total AC")
with col_t[3]:
    datos["AVSUBTOTAL  TOTAL"] = st.text_input("Total AV")

# ====================== CAMPOS GENERALES ======================
datos["APELLIDO Y NOMBRES INSPECTORRow1"] = inspector
datos["AREA DE FISCALIZACIONRow1"] = area
datos["LUGAR Y FECHA"] = fecha
datos["MES Y AÑO"] = fecha

# ====================== BOTÓN ======================
if st.button("✅ GENERAR PDF", type="primary", use_container_width=True):
    if not inspector:
        st.error("Completá el nombre del inspector")
    else:
        with st.spinner("Rellenando PDF..."):
            try:
                archivo = completar_pdf(datos)
                with open(archivo, "rb") as f:
                    st.download_button(
                        "⬇️ DESCARGAR PDF COMPLETADO",
                        data=f,
                        file_name="PLANILLA_INSPECTORES_COMPLETADA.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error: {e}")
