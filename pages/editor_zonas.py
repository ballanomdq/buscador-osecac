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
st.title("📄 Relleno de PDF - Campos Correctos")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

# Inspector fijo: GARCIA (legajo 7952)
INSPECTOR_LEGAJO = 7952
INSPECTOR_NOMBRE = "GARCIA, Juan Paulo"

# Obtener registros listos de GARCIA
registros = supabase.table("padron_deuda_presunta").select("*").eq("leg", INSPECTOR_LEGAJO).eq("mail_enviado", "SI").not_.is_("acta", "null").not_.is_("vto", "null").execute()

if registros.data:
    st.success(f"✅ Se encontraron {len(registros.data)} registros listos para GARCIA")
    
    primer_registro = registros.data[0]
    fecha_vto = primer_registro.get('vto', '')
    
    if fecha_vto:
        fecha_obj = datetime.strptime(fecha_vto, '%Y-%m-%d')
        mes_vto = fecha_obj.strftime('%m')   # 01, 02, 03...
        año_vto = fecha_obj.strftime('%Y')   # 2024, 2025, 2026...
        
        st.info(f"📅 Fecha VTO: {fecha_vto} → Campo 154 (MES): '{mes_vto}' | Campo 153 (AÑO): '{año_vto}'")
        
        if st.button("📄 GENERAR PDF", type="primary"):
            reader = PdfReader(PDF_PATH)
            writer = PdfWriter()
            writer.append(reader)
            writer.set_need_appearances_writer(True)
            
            # Datos en los campos correctos según numeración
            datos = {
                "AREA DE FISCALIZACIONRow1": "MAR DEL PLATA",
                "APELLIDO Y NOMBRES INSPECTORRow1": INSPECTOR_NOMBRE,
                "VTOAÑO1": año_vto,    # Campo 153 - Año
                "VTOMES1": mes_vto,    # Campo 154 - Mes
            }
            
            writer.update_page_form_field_values(
                writer.pages[0], 
                datos, 
                auto_regenerate=True
            )
            
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            
            st.success("✅ PDF generado")
            st.download_button(
                label="📥 DESCARGAR PDF",
                data=output,
                file_name=f"prueba_garcia_campos_correctos.pdf",
                mime="application/pdf"
            )
else:
    st.error(f"❌ No hay registros listos para GARCIA (legajo {INSPECTOR_LEGAJO})")
