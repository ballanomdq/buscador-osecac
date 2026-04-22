import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def generar_infografia_osecac():
    # Creamos un lienzo oscuro profesional (Full HD)
    img = Image.new('RGB', (1200, 800), color='#1E1E1E')
    draw = ImageDraw.Draw(img)
    
    # Intentamos cargar una fuente clara, si no, usamos la de sistema
    try:
        font_title = ImageFont.truetype("arial.ttf", 45)
        font_inspector = ImageFont.truetype("arial.ttf", 30)
        font_calle = ImageFont.truetype("arial.ttf", 18)
    except:
        font_title = font_inspector = font_calle = ImageFont.load_default()

    # TÍTULO
    draw.text((50, 30), "MAPA TÉCNICO DE JURISDICCIONES - OSECAC MDP", fill="white", font=font_title)
    draw.line((50, 85, 1150, 85), fill="#444444", width=2)

    # DEFINICIÓN DE ZONAS (Coordenadas de dibujo, no geográficas)
    # ZONA NORTE - RODRÍGUEZ (Celeste)
    draw.rectangle([100, 150, 550, 350], fill="#00BFFF33", outline="#00BFFF", width=3)
    draw.text((120, 160), "INSPECTOR: RODRÍGUEZ (NORTE)", fill="#00BFFF", font=font_inspector)
    draw.text((120, 200), "LÍMITES PERIMETRALES:", fill="white", font=font_calle)
    draw.text((120, 230), "• NORTE: Límite Partido Gral. Pueyrredón\n• SUR: Av. Pedro Luro\n• ESTE: Costa Atlántica\n• OESTE: Av. Champagnat", fill="#AAAAAA", font=font_calle)

    # ZONA CENTRO - CARBAYO (Rosa)
    draw.rectangle([600, 150, 1100, 350], fill="#DC143C33", outline="#DC143C", width=3)
    draw.text((620, 160), "INSPECTOR: CARBAYO (CENTRO)", fill="#DC143C", font=font_inspector)
    draw.text((620, 200), "LÍMITES PERIMETRALES:", fill="white", font=font_calle)
    draw.text((620, 230), "• NORTE: Av. Pedro Luro\n• SUR: Av. Juan B. Justo\n• ESTE: Costa Atlántica (Varese/P. Grande)\n• OESTE: Av. Champagnat", fill="#AAAAAA", font=font_calle)

    # ZONA OESTE - LÓPEZ (Amarillo)
    draw.rectangle([100, 400, 550, 650], fill="#FFD70033", outline="#FFD700", width=3)
    draw.text((120, 410), "INSPECTOR: LÓPEZ (OESTE / BATÁN)", fill="#FFD700", font=font_inspector)
    draw.text((120, 450), "LÍMITES PERIMETRALES:", fill="white", font=font_calle)
    draw.text((120, 480), "• NORTE: Límite Rural\n• SUR: Av. Juan B. Justo (prolongación)\n• ESTE: Av. Champagnat\n• OESTE: Batán / Parque Industrial", fill="#AAAAAA", font=font_calle)

    # ZONA SUR - GARCÍA (Naranja)
    draw.rectangle([600, 400, 1100, 650], fill="#FF8C0033", outline="#FF8C00", width=3)
    draw.text((620, 410), "INSPECTOR: GARCÍA (SUR / MIRAMAR)", fill="#FF8C00", font=font_inspector)
    draw.text((620, 450), "LÍMITES PERIMETRALES:", fill="white", font=font_calle)
    draw.text((620, 480), "• NORTE: Av. Juan B. Justo\n• SUR: Ciudad de MIRAMAR\n• ESTE: Costa (Faro / Chapadmalal)\n• OESTE: Ruta 88 / Campo", fill="#AAAAAA", font=font_calle)

    # PIE DE PÁGINA
    draw.text((50, 720), "Nota: Los límites coinciden con el Mapa de Jurisdicción Interna de la Agencia.", fill="#666666", font=font_calle)
    
    return img

# Ejecución en Streamlit
st.subheader("Esquema Técnico para Validación de Inspectores")
imagen_final = generar_infografia_osecac()
st.image(imagen_final, use_container_width=True)
