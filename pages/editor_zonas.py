import streamlit as st
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="Planilla Inspectores", layout="wide")
st.title("🖊️ Editor Planilla Inspectores OSECAC")

# ====================== FUNCIÓN PARA RELLENAR PDF ======================
def completar_planilla(datos: dict, input_pdf="PLANILLA INSPECTORES.pdf"):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.update_page_form_field_values(writer.pages[0], datos)

    output_path = "PLANILLA_INSPECTORES_COMPLETADA.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)
    
    return output_path

# ====================== DATOS GENERALES ======================
st.subheader("📌 Datos Generales")

col1, col2, col3 = st.columns(3)

with col1:
    inspector = st.text_input("APELLIDO Y NOMBRES INSPECTOR", key="inspector")
    area = st.text_input("AREA DE FISCALIZACION", key="area")

with col2:
    lugar_fecha = st.text_input("LUGAR Y FECHA", key="lugar_fecha")
    mes_anio = st.text_input("MES Y AÑO", key="mes_anio")

with col3:
    empresa_row1 = st.text_input("EMPRESA VISITADA (Row1)", key="empresa1")

# ====================== TABLA DE 16 FILAS ======================
st.subheader("📋 Empresas Visitadas (hasta 16 filas)")

datos = {}

for i in range(1, 17):
    with st.expander(f"Empresa {i}", expanded=(i <= 2)):
        c1, c2, c3, c4 = st.columns([3.5, 2, 1.5, 2])
        
        with c1:
            datos[f"EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow{i}"] = st.text_input(
                "Razón Social / Dirección", key=f"emp_{i}")
            datos[f"NRO DE  CUITRow{i}"] = st.text_input("CUIT", key=f"cuit_{i}")
        
        with c2:
            datos[f"NRORow{i}"] = st.text_input("NRO", key=f"nro_{i}")
            datos[f"FOLIORow{i}"] = st.text_input("FOLIO", key=f"folio_{i}")
        
        with c3:
            datos[f"EMPLE ADOSRow{i}"] = st.text_input("Empleados", key=f"empados_{i}")
            datos[f"M E S E SRow{i}"] = st.text_input("Meses", key=f"meses_{i}")
        
        with c4:
            datos[f"DEUDA DETERMINADARow{i}"] = st.text_input("Deuda Determinada", key=f"deuda_{i}")
            datos[f"OBSERVACIONESRow{i if i <= 4 else 1}"] = st.text_input("Observaciones", key=f"obs_{i}")

# ====================== TOTALES ======================
st.subheader("📊 Totales")

col_t1, col_t2 = st.columns(2)

with col_t1:
    datos["EMPLE ADOSSUBTOTAL  TOTAL"] = st.text_input("Total Empleados")
    datos["DEUDA DETERMINADASUBTOTALTOTAL"] = st.text_input("Total Deuda Determinada")
    datos["ACSUBTOTAL  TOTAL"] = st.text_input("Total AC")

with col_t2:
    datos["AVSUBTOTAL  TOTAL"] = st.text_input("Total AV")
    datos["IMPORTE CANCELADOSUBTOTAL  TOTAL"] = st.text_input("Total Importe Cancelado")
    datos["RTSUBTOTAL  TOTAL"] = st.text_input("Total RT")

# ====================== CAMPOS ADICIONALES (si los necesitas) ======================
with st.expander("Otros campos (AC, AV, RT, etc.)"):
    # Aquí puedes agregar más inputs si quieres controlarlos manualmente
    st.info("La mayoría de los campos AC, AV, RT, etc. se pueden completar manualmente aquí si es necesario.")

# ====================== ASIGNAR DATOS GENERALES ======================
datos["APELLIDO Y NOMBRES INSPECTORRow1"] = inspector
datos["AREA DE FISCALIZACIONRow1"] = area
datos["LUGAR Y FECHA"] = lugar_fecha
datos["MES Y AÑO"] = mes_anio
datos["EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow1"] = empresa_row1

# ====================== BOTÓN PRINCIPAL ======================
if st.button("✅ Generar PDF Completado", type="primary", use_container_width=True):
    if not inspector.strip():
        st.error("❌ Debes completar el nombre del Inspector")
    else:
        with st.spinner("Generando PDF..."):
            try:
                ruta = completar_planilla(datos)
                st.success("¡PDF generado correctamente!")
                
                with open(ruta, "rb") as f:
                    st.download_button(
                        "⬇️ Descargar PLANILLA COMPLETADA.pdf",
                        data=f,
                        file_name="PLANILLA_INSPECTORES_COMPLETADA.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.caption("Tip: Los nombres de los campos coinciden exactamente con los del PDF.")
