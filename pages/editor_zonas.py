import io
import streamlit as st
from pypdf import PdfReader, PdfWriter
from pypdf.generic import AnnotationBuilder

# Configuración de la página de Streamlit
st.set_page_config(page_title="Generador de Planilla OSECAC", layout="centered")
st.title("Prueba de Coordenadas - Formulario 101150")
st.write("Presioná el botón de abajo para descargar la planilla con todos los casilleros numerados secuencialmente.")

def generar_pdf_marcado(pdf_origen_path):
    reader = PdfReader(pdf_origen_path)
    writer = PdfWriter()
    
    # Traemos la primera página (el formulario)
    page = reader.pages[0]
    
    # Lista para acumular todas las anotaciones de texto
    anotaciones = []
    contador = 1
    
    # -------------------------------------------------------------
    # 1. CAMPOS DE CABECERA
    # -------------------------------------------------------------
    # Nombre del Inspector
    anotaciones.append(AnnotationBuilder.free_text(
        f"{contador}", rect=(170, 760, 220, 775), font_size="10pt", border_color="FF0000"
    ))
    contador += 1
    
    # Mes y Año (Arriba a la derecha)
    anotaciones.append(AnnotationBuilder.free_text(
        f"{contador}", rect=(480, 760, 530, 775), font_size="10pt", border_color="FF0000"
    ))
    contador += 1
    
    # Folio / De
    anotaciones.append(AnnotationBuilder.free_text(
        f"{contador}", rect=(550, 760, 575, 775), font_size="10pt", border_color="FF0000"
    ))
    contador += 1

    # -------------------------------------------------------------
    # 2. GRILLA PRINCIPAL (8 FILAS)
    # -------------------------------------------------------------
    # Definimos los límites en X para cada columna importante
    columnas_x = {
        "Razon Social": (20, 160),
        "CUIT": (170, 230),
        "Nro Actuacion": (280, 310),
        "Fecha Vto": (320, 350),
        "Empleados": (360, 375),
        "Periodo Verificado": (385, 430),
        "Deuda Determinada": (440, 480)
    }
    
    # Alturas aproximadas de las 8 filas en base al origen BOTTOM-LEFT de pypdf
    # Fila 1 empieza arriba (~670) y van bajando de a 45 puntos
    alturas_y = [
        (665, 695),  # Fila 1
        (620, 650),  # Fila 2
        (575, 605),  # Fila 3
        (530, 560),  # Fila 4
        (485, 515),  # Fila 5
        (440, 470),  # Fila 6
        (395, 425),  # Fila 7
        (350, 380)   # Fila 8
    ]
    
    # Recorremos fila por fila y rellenamos cada columna con el número secuencial
    for i, (y_min, y_max) in enumerate(alturas_y):
        for col_nombre, (x_min, x_max) in columnas_x.items():
            anotaciones.append(AnnotationBuilder.free_text(
                f"{contador}",
                rect=(x_min, y_min, x_max, y_max),
                font_size="9pt",
                border_color="0000FF"  # Azul para la tabla principal
            ))
            contador += 1

    # -------------------------------------------------------------
    # 3. CAMPOS INFERIORES (PIE DE PÁGINA)
    # -------------------------------------------------------------
    # Observaciones
    anotaciones.append(AnnotationBuilder.free_text(
        f"{contador}", rect=(20, 220, 350, 290), font_size="10pt", border_color="FF0000"
    ))
    contador += 1
    
    # Lugar y Fecha
    anotaciones.append(AnnotationBuilder.free_text(
        f"{contador}", rect=(360, 220, 420, 290), font_size="9pt", border_color="FF0000"
    ))

    # Agregamos todas las marcas generadas a la página
    for anotacion in anotaciones:
        writer.add_annotation(page_number=0, annotation=anotacion)
        
    writer.add_page(page)
    
    # Guardamos el resultado en memoria para la descarga web
    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    return output_stream

# Interfaz del botón de descarga en tu portal
try:
    # IMPORTANTE: Reemplazá este nombre por el de tu archivo local en el servidor
    path_planilla_original = "EJEMPLO INFORME MENSUAL DE INSPECTORES 101150.pdf" 
    
    pdf_listo = generar_pdf_marcado(path_planilla_original)
    
    st.download_button(
        label="📥 Descargar Planilla Rellena (Prueba 1-2-3)",
        data=pdf_listo,
        file_name="PLANILLA_OSECAC_TEST_RELLENO.pdf",
        mime="application/pdf"
    )
except FileNotFoundError:
    st.error("Por favor, asegurate de tener el archivo 'EJEMPLO INFORME MENSUAL DE INSPECTORES 101150.pdf' en la misma carpeta que este script.")
