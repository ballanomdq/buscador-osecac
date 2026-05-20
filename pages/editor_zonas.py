import streamlit as st
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="Planilla Inspectores", layout="wide")
st.title("🖊️ Planilla Inspectores - Solo Campos Importantes")

def completar_pdf(datos):
    try:
        reader = PdfReader("PLANILLA INSPECTORES.pdf")
        writer = PdfWriter()
        writer.append(reader)
        writer.set_need_appearances_writer(True)
        
        writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=False)
        
        with open("PLANILLA_COMPLETADA.pdf", "wb") as f:
            writer.write(f)
        return "PLANILLA_COMPLETADA.pdf"
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return None

# ==================== DATOS DEL INSPECTOR ====================
col1, col2, col3 = st.columns([3, 3, 2])
with col1:
    inspector = st.text_input("**APELLIDO Y NOMBRES INSPECTOR**", key="inspector")
with col2:
    area = st.text_input("**ÁREA DE FISCALIZACIÓN**", key="area", value="MAR DEL PLATA")
with col3:
    fecha = st.text_input("**MES Y AÑO / LUGAR Y FECHA**", key="fecha")

# ==================== TABLA DE EMPRESAS ====================
st.subheader("📋 Empresas Visitadas (solo los campos que te importan)")

datos = {}

for i in range(1, 17):
    with st.expander(f"Fila {i}", expanded=(i <= 3)):
        c = st.columns([3.5, 2.2, 1.1, 1.1, 1.1, 1.3, 2, 2])
        
        with c[0]:
            datos[f"EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow{i}"] = st.text_input("Empresa / Dirección", key=f"emp{i}")
        with c[1]:
            datos[f"NRO DE  CUITRow{i}"] = st.text_input("CUIT", key=f"cuit{i}")
        with c[2]:
            datos[f"AV{i if i <=16 else 1}"] = st.text_input("AV", key=f"av{i}")
        with c[3]:
            datos[f"RT{i if i <=16 else 1}"] = st.text_input("RT", key=f"rt{i}")
        with c[4]:
            datos[f"AC{i if i <=16 else 1}"] = st.text_input("AC", key=f"ac{i}")
        with c[5]:
            datos[f"EMPLE ADOSRow{i}"] = st.text_input("Empleados", key=f"emple{i}")
        with c[6]:
            datos[f"DEUDA DETERMINADARow{i}"] = st.text_input("Deuda Determinada", key=f"deuda{i}")
        with c[7]:
            datos[f"OBSERVACIONESRow{i if i<=4 else 1}"] = st.text_input("Observaciones", key=f"obs{i}")

# ==================== TOTALES ====================
st.subheader("Totales")
colt = st.columns(4)
with colt[0]:
    datos["EMPLE ADOSSUBTOTAL  TOTAL"] = st.text_input("Total Empleados")
with colt[1]:
    datos["DEUDA DETERMINADASUBTOTALTOTAL"] = st.text_input("Total Deuda")
with colt[2]:
    datos["ACSUBTOTAL  TOTAL"] = st.text_input("Total AC")
with colt[3]:
    datos["AVSUBTOTAL  TOTAL"] = st.text_input("Total AV")

# Asignar datos fijos
datos["APELLIDO Y NOMBRES INSPECTORRow1"] = inspector
datos["AREA DE FISCALIZACIONRow1"] = area
datos["LUGAR Y FECHA"] = fecha
datos["MES Y AÑO"] = fecha

# ==================== BOTÓN ====================
if st.button("✅ GENERAR PDF", type="primary", use_container_width=True):
    if not inspector:
        st.error("❌ Poné el nombre del inspector")
    else:
        with st.spinner("Rellenando PDF..."):
            archivo = completar_pdf(datos)
            if archivo:
                with open(archivo, "rb") as f:
                    st.download_button(
                        "⬇️ DESCARGAR PDF COMPLETADO",
                        data=f,
                        file_name="PLANILLA_INSPECTORES_COMPLETADA.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success("¡PDF generado correctamente!")
