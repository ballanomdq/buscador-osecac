def generar_lluvia_de_numeros():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"No se encuentra {PDF_PATH}")
    
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    # 1. ESTO ARREGLA EL DESFASE DE COSTADO:
    # Si la página está rotada internamente (ej. 90 o 270 grados),
    # forzamos a PyMuPDF a trabajar con la vista real de pantalla.
    rotacion_original = page.rotation
    
    # Conseguimos el ancho y alto corregidos según cómo lo ves en pantalla
    rect_vista = page.rect
    if rotacion_original in (90, 270):
        ancho = int(rect_vista.height)
        alto = int(rect_vista.width)
    else:
        ancho = int(rect_vista.width)
        alto = int(rect_vista.height)
    
    fontsize = 6
    color = (1, 0, 0)
    
    contador = 1
    mapa_referencia = {}
    
    # Barremos la cuadrícula usando las dimensiones reales de tu visualización
    for y in range(30, alto - 30, 20):
        for x in range(20, ancho - 20, 45):
            
            # Mandamos el texto usando 'rotate=rotacion_original' para que 
            # las letras giren y queden perfectamente horizontales para tus ojos
            page.insert_text(
                (x, y), 
                str(contador), 
                fontsize=fontsize, 
                color=color, 
                rotate=rotacion_original
            )
            
            mapa_referencia[contador] = (x, y)
            contador += 1
            
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    return output, mapa_referencia
