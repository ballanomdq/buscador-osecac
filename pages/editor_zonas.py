import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io
import os

st.set_page_config(layout="wide", page_title="Inspector Interactivo OSECAC")
st.title("🎯 Detector de Coordenadas por Clic Directo")
st.markdown("### Haz clic en cualquier parte de la planilla para registrar la coordenada exacta.")

PDF_PATH = "PLANILLA INSPECTORES.pdf"

if not os.path.exists(PDF_PATH):
    st.error(f"❌ No se encuentra el archivo '{PDF_PATH}'")
    st.stop()

# 1. CARGAR ESTRUCTURA DEL PDF
@st.cache_resource
def cargar_base_pdf():
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    # Renderizar una sola vez a alta resolución (Matriz x2) para guardar en caché
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img_base = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img_base, page.rect.width, page.rect.height, page.rotation

img_original, ancho_pdf, alto_pdf, rotacion_pdf = cargar_base_pdf()

# Inicializar las variables de posición en el estado de la sesión si no existen
if "x_real" not in st.session_state:
    st.session_state.x_real = 100
if "y_real" not in st.session_state:
    st.session_state.y_real = 100

# 2. CAPTURAR EL CLIC DIRECTO EN LA IMAGEN
# st.image en sus últimas versiones permite capturar el evento de click devolviendo un diccionario
value = st.image(img_original, caption="Hacé clic sobre el casillero que quieras medir", use_container_width=False, output_format="PNG")

# Si el usuario hace clic, capturamos las coordenadas del píxel de la imagen en pantalla
if value and "click_events" in value and value["click_events"]:
    click = value["click_events"][-1]  # Traer el último clic
    x_img_click = click["x"]
    y_img_click = click["y"]
    
    # Conseguimos el tamaño actual de la imagen renderizada en el navegador
    ancho_renderizado = value["width"]
    alto_renderizado = value["height"]
    
    # Convertimos los píxeles de la pantalla web a los puntos reales del PDF
    st.session_state.x_real = int((x_img_click / ancho_renderizado) * ancho_pdf)
    st.session_state.y_real = int((y_img_click / alto_renderizado) * alto_pdf)

# 3. MOSTRAR COORDENADAS DETECTADAS
st.sidebar.header("📍 Coordenada Capturada")
st.sidebar.success(f"**X Actual:** {st.session_state.x_real}\n\n**Y Actual:** {st.session_state.y_real}")

# Dibujar la cruz roja en la previsualización del panel lateral para confirmación rápida
img_miniatura = img_original.copy()
draw = ImageDraw.Draw(img_miniatura)

# Escala interna para la miniatura
escala_x = img_original.width / ancho_pdf
escala_y = img_original.height / alto_pdf
x_p_min = st.session_state.x_real * escala_x
y_p_min = st.session_state.y_real * escala_y

draw.ellipse((x_p_min-12, y_p_min-12, x_p_min+12, y_p_min+12), outline="red", width=4)
draw.line((x_p_min-25, y_p_min, x_p_min+25, y_p_min), fill="red", width=3)
draw.line((x_p_min, y_p_min-25, x_p_min, y_p_min+25), fill="red", width=3)

st.sidebar.image(img_miniatura, caption="Mira de enfoque", use_container_width=True)

# 4. PROBAR TEXTO Y DESCARGA
st.sidebar.markdown("---")
angulo_prueba = st.sidebar.selectbox("Giro del Texto", [270, 90, 0, 180], index=0)
texto_prueba = st.sidebar.text_input("Texto de test", "30-12345678-9")

if st.sidebar.button("⚙️ COMPROBAR CASILLERO EN PDF", type="primary", use_container_width=True):
    try:
        doc_test = fitz.open(PDF_PATH)
        page_test = doc_test[0]
        
        page_test.insert_text(
            (st.session_state.x_real, st.session_state.y_real),
            texto_prueba,
            fontsize=10,
            color=(1, 0, 0),
            rotate=angulo_prueba
        )
        
        output = io.BytesIO()
        doc_test.save(output)
        doc_test.close()
        output.seek(0)
        
        st.sidebar.download_button(
            label="📥 BAJAR Y COMPROBAR ALINEACIÓN",
            data=output,
            file_name="test_clic_osecac.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
