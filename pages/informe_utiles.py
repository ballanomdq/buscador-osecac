def procesar_informe(df, mes, anio, dia_inicio, dia_fin, agencias_seleccionadas):
    # Convertir fecha
    fecha_col = 'FECHA' if 'FECHA' in df.columns else 'Marca temporal'
    df['fecha'] = pd.to_datetime(df[fecha_col], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['fecha'])
    
    # Filtrar por año, mes y rango de días
    df = df[(df['fecha'].dt.year == anio) & 
            (df['fecha'].dt.month == mes) &
            (df['fecha'].dt.day >= dia_inicio) &
            (df['fecha'].dt.day <= dia_fin)]
    
    # Filtrar por agencias seleccionadas
    if agencias_seleccionadas:
        df = df[df['AGENCIA'].isin(agencias_seleccionadas)]
    
    if df.empty:
        return None
    
    # Definir columnas de productos
    excluir = ['Marca temporal', 'FECHA', '¿A dónde pertenece?', 'AGENCIA', 'SECTOR',
               'MODELO_SOPORTE', 'OTROS PEDIDOS ARREGLADO', 'OTROS PEDIDOS',
               'MODELO DE IMPRESORA', 'TONER CANTIDAD', 'fecha']
    items = [col for col in df.columns if col not in excluir and not col.startswith('OTROS')]
    
    # 🔥 CLAVE: convertir todas las columnas de items a números (forzando errores a 0)
    for item in items:
        df[item] = pd.to_numeric(df[item], errors='coerce').fillna(0)
    
    # Agrupar por agencia y sumar
    df_agrupado = df.groupby('AGENCIA')[items].sum().reset_index()
    
    # Pivot: items como filas, agencias como columnas
    df_pivot = df_agrupado.set_index('AGENCIA').T
    
    # Agregar total por ítem (suma horizontal)
    df_pivot['TOTAL ÍTEM'] = df_pivot.sum(axis=1)
    
    # Agregar fila de total por agencia (suma vertical)
    total_por_agencia = df_pivot.sum(axis=0)
    df_pivot.loc['TOTAL AGENCIA'] = total_por_agencia
    
    return df_pivot
