import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io
import os

st.set_page_config(layout="wide", page_title="Inspector de Coordenadas OSECAC")
st.title("🎯 Detector Exacto de Coordenadas PDF")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

# Verificar la existencia del archivo en el servidor
if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra el archivo '{PDF_PATH}' en la raíz del proyecto.")
    st.stop()

# ---------- ABRIR PDF ----------
doc = fitz.open(PDF_PATH)
page = doc[0]

# ---------- RENDER PDF A IMAGEN ----------
# Usamos una matriz de alta calidad (zoom x2) para ver nítidos los textos de la planilla
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# ---------- MOSTRAR METADATOS EN BARRA LATERAL ----------
st.sidebar.header("📐 Información del Documento")
st.sidebar.write(f"**Ancho Original:** {page.rect.width} pts")
st.sidebar.write(f"**Alto Original:** {page.rect.height} pts")
st.sidebar.write(f"**Rotación Interna:** {page.rotation}°")

st.sidebar.markdown("---")
st.sidebar.markdown("### ✏️ AJUSTE DE POSICIÓN")

# Control numérico preciso para desplazar el punto de mira
x_click = st.sidebar.number_input("Coordenada X", min_value=0, max_value=int(page.rect.width), value=100, step=1)
y_click = st.sidebar.number_input("Coordenada Y", min_value=0, max_value=int(page.rect.height), value=100, step=1)

# Selección del ángulo para el texto de prueba
angulo_texto = st.sidebar.selectbox("Ángulo de inyección (Rotate)", [270, 90, 0, 180], index=0)
texto_prueba = st.sidebar.text_input("Texto de prueba", "HOLA")

# ---------- CALCULAR ESCALAS Y DIBUJAR PUNTO ----------
img_render = img.copy()
draw = ImageDraw.Draw(img_render)

escala_x = pix.width / page.rect.width
escala_y = pix.height / page.rect.height

x_img = x_click * escala_x
y_img = y_click * escala_y

# Dibujamos un punto de mira rojo visible
draw.ellipse((x_img-8, y_img-8, x_img+8, y_img+8), fill="red")
draw.line((x_img-15, y_img, x_img+15, y_img), fill="red", width=2)
draw.line((x_img, y_img-15, x_img, y_img+15), fill="red", width=2)

# Desplegamos la imagen interactiva en el panel principal
st.image(img_render, caption=f"Posición actual en el PDF real: ({x_click}, {y_click})")

# ---------- BOTÓN DE INYECCIÓN DE PRUEBA ----------
st.sidebar.markdown("---")
if st.sidebar.button("⚙️ GENERAR PDF DE PRUEBA", use_container_width=True):
    try:
        doc2 = fitz.open(PDF_PATH)
        page2 = doc2[0]

        # Insertamos el texto usando las coordenadas elegidas y la rotación seleccionada
        page2.insert_text(
            (x_click, y_click),
            texto_prueba,
            fontsize=9,
            color=(1, 0, 0),
            rotate=angulo_texto
        )

        output = io.BytesIO()
        doc2.save(output)
        doc2.close()
        output.seek(0)

        st.sidebar.success("✅ ¡PDF modificado con éxito!")
        st.sidebar.download_button(
            label="📥 DESCARGAR PDF",
            data=output,
            file_name="prueba_coordenadas.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.sidebar.error(f"Error al procesar: {e}")
