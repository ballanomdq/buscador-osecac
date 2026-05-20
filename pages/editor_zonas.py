import streamlit as st
from pypdf import PdfReader, PdfWriter
from supabase import create_client
from datetime import datetime
import io
import os

# Conexión a Supabase
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

st.set_page_config(layout="centered")
st.title("📄 Prueba de Relleno de PDF")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

# Inspector fijo: GARCIA (legajo 7952)
INSPECTOR_LEGAJO = 7952
INSPECTOR_NOMBRE = "GARCIA, Juan Paulo"

# Obtener registros listos de GARCIA
registros = supabase.table("padron_deuda_presunta").select("*").eq("leg", INSPECTOR_LEGAJO).eq("mail_enviado", "SI").not_.is_("acta", "null").not_.is_("vto", "null").execute()

if registros.data:
    st.success(f"✅ Se encontraron {len(registros.data)} registros listos para GARCIA")
    
    # Tomar el primer registro para obtener fecha VTO
    primer_registro = registros.data[0]
    fecha_vto = primer_registro.get('vto', '')
    
    if fecha_vto:
        fecha_obj = datetime.strptime(fecha_vto, '%Y-%m-%d')
        mes_vto = fecha_obj.strftime('%m')
        año_vto = fecha_obj.strftime('%Y')
        
        st.info(f"📅 Fecha VTO de ejemplo: {fecha_vto} → Mes: {mes_vto}, Año: {año_vto}")
        
        if st.button("📄 GENERAR PDF DE PRUEBA", type="primary"):
            # Leer el PDF
            reader = PdfReader(PDF_PATH)
            writer = PdfWriter()
            writer.append(reader)
            writer.set_need_appearances_writer(True)
            
            # Datos a rellenar
            datos = {
                "AREA DE FISCALIZACIONRow1": "MAR DEL PLATA",
                "APELLIDO Y NOMBRES INSPECTORRow1": INSPECTOR_NOMBRE,
                "MES Y AÑORow1": f"{mes_vto} {año_vto}",
            }
            
            # Actualizar campos
            writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=False)
            
            # Guardar
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            
            st.success("✅ PDF generado")
            st.download_button(
                label="📥 DESCARGAR PDF",
                data=output,
                file_name=f"prueba_garcia.pdf",
                mime="application/pdf"
            )
else:
    st.error(f"❌ No hay registros listos para GARCIA (legajo {INSPECTOR_LEGAJO})")
