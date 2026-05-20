import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io

st.set_page_config(layout="wide", page_title="Inspector de Coordenadas OSECAC")
st.title("🎯 Inspector Visual de Coordenadas (Modo Profesional)")
st.markdown("Ajustá los valores de X e Y para mover el punto rojo. Cuando caiga en el casillero deseado, anotá las coordenadas.")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not fitz.sys_info(): # Verificar librería activa
    st.error("Error con PyMuPDF")

# 1. LEER ESTRUCTURA ORIGINAL DEL PDF
doc = fitz.open(PDF_PATH)
page = doc[0]

ancho_pdf = page.rect.width
alto_pdf = page.rect.height
rotacion_pdf = page.rotation

# 2. RENDERIZAR EN ALTA CALIDAD (Matriz x2 para nitidez del formulario)
zoom = 2
matrix = fitz.Matrix(zoom, zoom)
pix = page.get_pixmap(matrix=matrix)
img_original = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# Factores de conversión exactos entre los píxeles de la imagen y los puntos del PDF
escala_x = pix.width / ancho_pdf
escala_y = pix.height / alto_pdf

# 3. INTERFAZ LATERAL DE CONTROL
st.sidebar.header("🛠️ Controles de Posicionamiento")
st.sidebar.info(f"**Ancho PDF:** {ancho_pdf} pts\n\n**Alto PDF:** {alto_pdf} pts\n\n**Rotación:** {rotacion_pdf}°")

# selectores numéricos para ajustar al milímetro
x_pdf = st.sidebar.number_input("Coordenada X (PDF)", min_value=0, max_value=int(ancho_pdf), value=150, step=5)
y_pdf = st.sidebar.number_input("Coordenada Y (PDF)", min_value=0, max_value=int(alto_pdf), value=150, step=5)

# Selector de rotación para la prueba de texto
angulo_prueba = st.sidebar.selectbox("Giro del Texto (Prueba)", [270, 90, 0, 180], index=0)
texto_prueba = st.sidebar.text_input("Texto de Prueba", "30-12345678-9")

# 4. DIBUJAR PUNTO DE CONTROL EN LA IMAGEN
img_render = img_original.copy()
draw = ImageDraw.Draw(img_render)

# Convertimos los puntos que ingresaste a los píxeles reales de la imagen renderizada
x_pixel = x_pdf * escala_x
y_pixel = y_pdf * escala_y

# Dibujamos una cruz y un círculo rojo sobre el casillero apuntado
draw.ellipse((x_pixel-10, y_pixel-10, x_pixel+10, y_pixel+10), outline="red", width=3)
draw.line((x_pixel-20, y_pixel, x_pixel+20, y_pixel), fill="red", width=2)
draw.line((x_pixel, y_pixel-20, x_pixel, y_pixel+20), fill="red", width=2)

# Mostrar el mapa visual en el centro de la pantalla
st.image(img_render, caption=f"Punto de mira actual en coordenadas PDF: X={x_pdf}, Y={y_pdf}", use_container_width=True)

# 5. BOTÓN DE VERIFICACIÓN: INYECTAR TEXTO EN EL DOCUMENTO REAL
st.sidebar.markdown("---")
if st.sidebar.button("🚀 PROBAR INYECCIÓN EN PDF", type="primary", use_container_width=True):
    try:
        doc_test = fitz.open(PDF_PATH)
        page_test = doc_test[0]
        
        # Insertamos el texto con el ángulo seleccionado para comprobar lectura horizontal
        page_test.insert_text(
            (x_pdf, y_pdf),
            texto_prueba,
            fontsize=10,
            color=(1, 0, 0), # Rojo para destacar
            rotate=angulo_prueba
        )
        
        output = io.BytesIO()
        doc_test.save(output)
        doc_test.close()
        output.seek(0)
        
        st.sidebar.success("¡PDF de prueba generado!")
        st.sidebar.download_button(
            label="📥 DESCARGAR Y
