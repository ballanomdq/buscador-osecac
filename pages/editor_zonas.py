import streamlit as st
from pypdf import PdfReader, PdfWriter

st.title("🖊️ Rellenar Planilla Inspectores - SIMPLE")

# ====================== FUNCIÓN QUE FUNCIONA ======================
def completar_pdf(datos):
    reader = PdfReader("PLANILLA INSPECTORES.pdf")
    writer = PdfWriter()
    writer.append(reader)                     # importante
    writer.set_need_appearances_writer(True)
    
    writer.update_page_form_field_values(writer.pages[0], datos)
    
    salida = "PLANILLA_COMPLETADA.pdf"
    with open(salida, "wb") as f:
        writer.write(f)
    return salida

# ====================== FORMULARIO SIMPLE ======================

st.subheader("1. Datos Principales")
datos = {}

datos["APELLIDO Y NOMBRES INSPECTORRow1"] = st.text_input("Apellido y Nombres del Inspector")
datos["AREA DE FISCALIZACIONRow1"] = st.text_input("Área de Fiscalización")
datos["LUGAR Y FECHA"] = st.text_input("Lugar y Fecha")
datos["MES Y AÑO"] = st.text_input("Mes y Año")

st.subheader("2. Empresas (una por una)")

num = st.number_input("Cuántas empresas querés completar?", min_value=1, max_value=16, value=5)

for i in range(1, num+1):
    with st.expander(f"Empresa {i}", expanded=(i==1)):
        datos[f"EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow{i}"] = st.text_input(f"Empresa {i}", key=f"e{i}")
        datos[f"NRO DE  CUITRow{i}"] = st.text_input(f"CUIT {i}", key=f"c{i}")
        datos[f"EMPLE ADOSRow{i}"] = st.text_input(f"Cantidad Empleados {i}", key=f"emp{i}")
        datos[f"DEUDA DETERMINADARow{i}"] = st.text_input(f"Deuda {i}", key=f"d{i}")
        datos[f"OBSERVACIONESRow{i if i<=4 else 1}"] = st.text_input(f"Observaciones {i}", key=f"o{i}")

# ====================== TOTALES ======================
st.subheader("3. Totales")
col1, col2 = st.columns(2)
with col1:
    datos["EMPLE ADOSSUBTOTAL  TOTAL"] = st.text_input("Total Empleados")
    datos["DEUDA DETERMINADASUBTOTALTOTAL"] = st.text_input("Total Deuda")
with col2:
    datos["ACSUBTOTAL  TOTAL"] = st.text_input("Total AC")
    datos["AVSUBTOTAL  TOTAL"] = st.text_input("Total AV")

# ====================== BOTÓN ======================
if st.button("✅ GENERAR Y DESCARGAR PDF", type="primary", use_container_width=True):
    if not datos.get("APELLIDO Y NOMBRES INSPECTORRow1"):
        st.error("Poné al menos el nombre del inspector")
    else:
        with st.spinner("Creando el PDF..."):
            try:
                archivo = completar_pdf(datos)
                with open(archivo, "rb") as f:
                    st.download_button(
                        label="⬇️ DESCARGAR PDF COMPLETADO",
                        data=f,
                        file_name="PLANILLA_INSPECTORES_COMPLETADA.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success("¡Listo!")
            except Exception as e:
                st.error(f"Error: {e}")

st.caption("Versión simple - Escribí lo que quieras y descargá")
