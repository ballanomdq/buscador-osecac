def asignar_legajo_por_direccion(localidad, calle, numero):
    localidad_upper = localidad.upper().strip() if localidad else ""
    calle_norm = normalizar_calle(calle)
    
    if localidad_upper != "MAR DEL PLATA" and localidad_upper != "":
        inspectores_localidad = cargar_inspectores_localidad()
        for item in inspectores_localidad:
            if item['localidad'].upper().strip() == localidad_upper:
                return item['legajo']
        return None
    
    if not calle_norm or not numero:
        return None
    
    try:
        numero_limpio = int(re.sub(r'\D', '', str(numero)))
    except:
        return None
    
    lado = "PAR" if numero_limpio % 2 == 0 else "IMPAR"
    
    zonas = cargar_zonas_inspectores()
    for zona in zonas:
        if normalizar_calle(zona['calle']) == calle_norm:
            if zona['lado'] == "AMBOS" or zona['lado'] == lado:
                if zona['altura_desde'] <= numero_limpio <= zona['altura_hasta']:
                    return zona['legajo']
    return None
