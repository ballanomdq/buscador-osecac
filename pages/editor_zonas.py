import streamlit as st
from pypdf import PdfReader
import json

st.title("🔍 Inspector de Campos del PDF")

pdf_path = "PLANILLA INSPECTORES.pdf"   # Asegúrate que esté en la carpeta correcta

try:
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()

    if fields:
        st.success(f"Se encontraron **{len(fields)} campos** en el formulario")
        
        # Mostrar lista ordenada
        field_list = sorted(fields.keys())
        st.subheader("📋 Nombres de los campos (copia estos exactos):")
        for name in field_list:
            st.code(name, language="text")
        
        # Guardar en JSON para descargar
        field_dict = {name: "" for name in field_list}
        with open("campos_disponibles.json", "w", encoding="utf-8") as f:
            json.dump(field_dict, f, indent=4, ensure_ascii=False)
        
        with open("campos_disponibles.json", "rb") as f:
            st.download_button("⬇️ Descargar JSON con todos los campos", f, "campos_disponibles.json")
        
    else:
        st.warning("No se encontraron campos rellenables en el PDF.")

except Exception as e:
    st.error(f"Error: {e}")
