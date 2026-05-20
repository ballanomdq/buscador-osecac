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
st.title("📄 Rellenar PDF - Usando PDF Numerado")

PDF_PATH = "ORIGINAL.pdf"  # El PDF que subiste con números

# Inspector fijo: GARCIA (legajo 7952)
INSPECTOR_LEGAJO = 7952
INSPECTOR_NOMBRE = "GARCIA, Juan Paulo"

# Obtener registros listos de GARCIA
registros = supabase.table("padron_deuda_presunta").select("*").eq("leg", INSPECTOR_LEGAJO).eq("mail_enviado", "SI").not_.is_("acta", "null").not_.is_("vto", "null").execute()

if registros.data:
    st.success(f"✅ Se encontraron {len(registros.data)} registros listos")
    
    primer_registro = registros.data[0]
    fecha_vto = primer_registro.get('vto', '')
    
    if fecha_vto:
        fecha_obj = datetime.strptime(fecha_vto, '%Y-%m-%d')
        mes_vto = fecha_obj.strftime('%m')
        año_vto = fecha_obj.strftime('%Y')
        
        st.info(f"📅 Fecha VTO: {fecha_vto} → Mes: {mes_vto}, Año: {año_vto}")
        
        if st.button("📄 GENERAR PDF", type="primary"):
            reader = PdfReader(PDF_PATH)
            writer = PdfWriter()
            writer.append(reader)
            writer.set_need_appearances_writer(True)
            
            # Usando los números de campo que me indicaste
            # Campo 1 = AREA DE FISCALIZACION
            # Campo 2 = APELLIDO Y NOMBRES INSPECTOR
            # Campo 153 = Año VTO
            # Campo 154 = Mes VTO
            
            # Obtener los nombres reales de los campos según su posición
            fields = reader.get_fields()
            nombres_campos = list(fields.keys())
            
            datos = {
                nombres_campos[0]: "MAR DEL PLATA",      # Campo 1
                nombres_campos[1]: INSPECTOR_NOMBRE,     # Campo 2
                nombres_campos[152]: año_vto,            # Campo 153 (índice 152)
                nombres_campos[153]: mes_vto,            # Campo 154 (índice 153)
            }
            
            writer.update_page_form_field_values(writer.pages[0], datos, auto_regenerate=True)
            
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            
            st.success("✅ PDF generado correctamente")
            st.download_button(
                label="📥 DESCARGAR PDF",
                data=output,
                file_name=f"informe_garcia.pdf",
                mime="application/pdf"
            )
else:
    st.error(f"❌ No hay registros listos para GARCIA")
