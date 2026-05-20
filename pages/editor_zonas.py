def generar_lluvia_de_numeros():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"No se encuentra {PDF_PATH}")
    
    doc = fitz.open(PDF_PATH)
    page = doc[0]
    
    # Dejamos la página quieta tal como viene
    rot_original = page.rotation
    
    # Tomamos las dimensiones reales de la hoja Legal (612 x 1008 aprox)
    ancho = int(page.rect.width)
    alto = int(page.rect.height)
    
    fontsize = 6
    color = (1, 0, 0)  # Rojo
    
    contador = 1
    mapa_referencia = {}
    
    # Barremos la matriz a lo largo de la hoja Legal
    for y in range(20, alto - 20, 20):
        for x in range(20, ancho - 20, 40):
            
            # CORRECCIÓN DE CABEZA:
            # Si antes con la rotación base te salieron invertidos, 
            # le sumamos 180 grados al giro del texto para darlos vuelta.
            angulo_texto = (360 - rot_original + 180) % 360 if rot_original != 0 else 0
            
            page.insert_text(
                (x, y), 
                str(contador), 
                fontsize=fontsize, 
                color=color, 
                rotate=angulo_texto
            )
            
            mapa_referencia[contador] = (x, y)
            contador += 1
            
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    
    return output, mapa_referencia
