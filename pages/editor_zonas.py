import streamlit as st
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="Planilla Inspectores", layout="wide")
st.title("🖊️ Planilla Inspectores - Visual")

# ====================== FUNCIÓN PDF ======================
def completar_pdf(datos):
    reader = PdfReader("PLANILLA INSPECTORES.pdf")
    writer = PdfWriter()
    writer.append(reader)
    writer.set_need_appearances_writer(True)
    writer.update_page_form_field_values(writer.pages[0], datos)
    
    with open("PLANILLA_COMPLETADA.pdf", "wb") as f:
        writer.write(f)
    return "PLANILLA_COMPLETADA.pdf"

# ====================== DATOS SUPERIORES ======================
col1, col2, col3, col4 = st.columns([3, 3, 2, 2])

with col1:
    inspector = st.text_input("1. APELLIDO Y NOMBRES INSPECTOR", key="inspector")
with col2:
    area = st.text_input("2. AREA DE FISCALIZACION", key="area")
with col3:
    mes_anio = st.text_input("3. MES Y AÑO", key="mesanio")
with col4:
    folio = st.text_input("FOLIO", key="folio")

# ====================== TABLA PRINCIPAL ======================
st.subheader("Tabla Principal de Empresas")

datos = {}

for i in range(1, 17):   # 16 filas
    with st.expander(f"🔹 Fila {i}", expanded=(i <= 2)):
        c = st.columns([2.5, 2, 1, 1, 1, 1, 1, 1.2, 1.5, 2, 2])   # ajustá el ancho según necesites
        
        with c[0]:
            datos[f"EMPRESA VISITADA RAZON SOCIAL  DIRECCIONRow{i}"] = st.text_input("Empresa / Dirección", key=f"emp{i}")
        with c[1]:
            datos[f"NRO DE  CUITRow{i}"] = st.text_input("CUIT", key=f"cuit{i}")
        with c[2]:
            datos[f"AV{i if i<17 else 1}"] = st.text_input("AV", key=f"av{i}")
        with c[3]:
            datos[f"AC{i if i<17 else 1}"] = st.text_input("AC", key=f"ac{i}")
        with c[4]:
            datos[f"RT{i if i<17 else 1}"] = st.text_input("RT", key=f"rt{i}")
        with c[5]:
            datos[f"NRORow{i}"] = st.text_input("NRO", key=f"nro{i}")
        with c[6]:
            datos[f"EMPLE ADOSRow{i}"] = st.text_input("Empleados", key=f"empados{i}")
        with c[7]:
            datos[f"M E S E SRow{i}"] = st.text_input("Meses", key=f"meses{i}")
        with c[8]:
            datos[f"DEUDA DETERMINADARow{i}"] = st.text_input("Deuda Determinada", key=f"deuda{i}")
        with c[9]:
            datos[f"OBSERVACIONESRow{i if i<=4 else 1}"] = st.text_input("Observaciones", key=f"obs{i}")

# ====================== TOTALES ======================
st.subheader("Totales")
colt = st.columns(5)
with colt[0]: datos["EMPLE ADOSSUBTOTAL  TOTAL"] = st.text_input("Total Empleados")
with colt[1]: datos["DEUDA DETERMINADASUBTOTALTOTAL"] = st.text_input("Total Deuda")
with colt[2]: datos["ACSUBTOTAL  TOTAL"] = st.text_input("Total AC")
with colt[3]: datos["AVSUBTOTAL  TOTAL"] = st.text_input("Total AV")
with colt[4]: datos["RTSUBTOTAL  TOTAL"] = st.text_input("Total RT")

# ====================== ASIGNAR CAMPOS FIJOS ======================
datos["APELLIDO Y NOMBRES INSPECTORRow1"] = inspector
datos["AREA DE FISCALIZACIONRow1"] = area
datos["MES Y AÑO"] = mes_anio
datos["LUGAR Y FECHA"] = mes_anio   # suele ser el mismo

# ====================== BOTÓN ======================
if st.button("✅ GENERAR Y DESCARGAR PDF", type="primary", use_container_width=True):
    if not inspector:
        st.error("Completá el nombre del inspector")
    else:
        with st.spinner("Generando PDF..."):
            try:
                archivo = completar_pdf(datos)
                with open(archivo, "rb") as f:
                    st.download_button(
                        "⬇️ DESCARGAR PDF COMPLETADO",
                        data=f,
                        file_name="PLANILLA_INSPECTORES_COMPLETADA.pdf",
                        mime="application/pdf"
                    )
                st.success("¡PDF generado!")
            except Exception as e:
                st.error(f"Error: {e}")
