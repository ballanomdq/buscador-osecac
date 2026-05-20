import streamlit as st
import fitz
from PIL import Image, ImageDraw
import io

st.set_page_config(layout="wide")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

st.title("🎯 Detector Exacto de Coordenadas PDF")

# ---------- ABRIR PDF ----------
doc = fitz.open(PDF_PATH)
page = doc[0]

# ---------- RENDER PDF A IMAGEN ----------
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

st.image(img, caption="PDF")

# ---------- MOSTRAR INFO ----------
st.write("ANCHO PDF:", page.rect.width)
st.write("ALTO PDF:", page.rect.height)
st.write("ROTACION:", page.rotation)

# ---------- CLICK MANUAL ----------
st.markdown("## ✏️ INGRESÁ POSICIÓN MANUAL")

col1, col2 = st.columns(2)

with col1:
    x_click = st.number_input("X", value=100)

with col2:
    y_click = st.number_input("Y", value=100)

# ---------- DIBUJAR PUNTO ----------
img2 = img.copy()
draw = ImageDraw.Draw(img2)

escala_x = pix.width / page.rect.width
escala_y = pix.height / page.rect.height

x_img = x_click * escala_x
y_img = y_click * escala_y

draw.ellipse(
    (x_img-8, y_img-8, x_img+8, y_img+8),
    fill="red"
)

st.image(img2, caption=f"Posición PDF REAL: ({x_click}, {y_click})")

# ---------- PROBAR TEXTO ----------
texto = st.text_input("Texto de prueba", "HOLA")

if st.button("GENERAR PDF DE PRUEBA"):

    doc2 = fitz.open(PDF_PATH)
    page2 = doc2[0]

    page2.insert_text(
        (x_click, y_click),
        texto,
        fontsize=9,
        color=(1, 0, 0),
        rotate=90
    )

    output = io.BytesIO()
    doc2.save(output)
    output.seek(0)

    st.download_button(
        "📥 DESCARGAR PDF",
        output,
        file_name="prueba.pdf",
        mime="application/pdf"
    )
