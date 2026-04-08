import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ========== CONFIGURACIÓN ==========
# Ruta al archivo JSON de credenciales
CREDENTIALS_FILE = 'credenciales.json'
# ID de tu hoja de cálculo (lo sacas de la URL)
SPREADSHEET_ID = '1eaujMJahDPn7YBpHeGKG_pSIvxjosnD6f2MHXLfngbI'
# Nombre de la solapa
SHEET_NAME = 'Respuestas de formulario 1'

# Parámetros del informe (cámbialos según necesites)
MES = 3          # Marzo (1=Enero, 2=Febrero, etc.)
DIA_INICIO = 1   # Desde el día 1
DIA_FIN = 15     # Hasta el día 15
AGENCIAS_FILTRO = None   # Si quieres una agencia específica: ['MIRAMAR'] o varias; None para todas

# ========== 1. CONEXIÓN A GOOGLE SHEETS ==========
def conectar_google_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    return sheet

# ========== 2. LEER DATOS ==========
def leer_datos(sheet):
    # Obtener todos los registros como lista de diccionarios
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    # Limpiar nombres de columnas (quitar espacios y saltos de línea)
    df.columns = df.columns.str.replace('\n', ' ').str.strip()
    return df

# ========== 3. PROCESAR Y FILTRAR ==========
def procesar_y_filtrar(df, mes, dia_inicio, dia_fin, agencias_filtro):
    # Convertir la columna de fecha (puede ser "Marca temporal" o "FECHA")
    # Primero intentamos con "FECHA", si no con "Marca temporal"
    fecha_col = None
    if 'FECHA' in df.columns:
        fecha_col = 'FECHA'
    elif 'Marca temporal' in df.columns:
        fecha_col = 'Marca temporal'
    else:
        raise ValueError("No se encontró columna de fecha")
    
    # Convertir a datetime (el formato puede variar, probamos varios)
    df['fecha_dt'] = pd.to_datetime(df[fecha_col], errors='coerce', dayfirst=True)
    # Si falla, intentar con dayfirst=False
    if df['fecha_dt'].isna().all():
        df['fecha_dt'] = pd.to_datetime(df[fecha_col], errors='coerce', dayfirst=False)
    
    # Eliminar filas sin fecha válida
    df = df.dropna(subset=['fecha_dt'])
    
    # Filtrar por mes y rango de días
    df = df[(df['fecha_dt'].dt.month == mes) & 
            (df['fecha_dt'].dt.day >= dia_inicio) & 
            (df['fecha_dt'].dt.day <= dia_fin)]
    
    # Filtrar por agencias (si se especificó)
    if agencias_filtro is not None:
        if isinstance(agencias_filtro, list):
            df = df[df['AGENCIA'].isin(agencias_filtro)]
        else:
            df = df[df['AGENCIA'] == agencias_filtro]
    
    return df

# ========== 4. SELECCIONAR ÍTEMS (excluir columnas que no son productos) ==========
def obtener_items(df):
    # Lista de columnas que NO son productos (metadata)
    no_items = ['Marca temporal', 'FECHA', '¿A dónde pertenece?', 'AGENCIA', 'SECTOR',
                'fecha_dt', 'MODELO_SOPORTE', 'OTROS PEDIDOS ARREGLADO', 'OTROS PEDIDOS', 
                'MODELO DE IMPRESORA', 'TONER CANTIDAD']  # Ajusta si hay más
    # También excluimos cualquier columna que comience con "OTROS" o "MODELO"
    items = [col for col in df.columns if col not in no_items and not col.startswith('OTROS') 
             and not col.startswith('MODELO') and col != 'fecha_dt']
    return items

# ========== 5. GENERAR TABLA PIVOTE ==========
def generar_informe(df, items):
    # Agrupar por AGENCIA y cada ítem, sumando las cantidades
    # Primero nos quedamos solo con las columnas necesarias
    df_informe = df[['AGENCIA'] + items].copy()
    # Rellenar NaN con 0 (casillas vacías del formulario)
    df_informe[items] = df_informe[items].fillna(0)
    
    # Agrupar y sumar
    agrupado = df_informe.groupby('AGENCIA')[items].sum().reset_index()
    
    # Transponer para que las agencias sean columnas y los items filas
    # Pero primero convertimos a formato largo para luego pivotar
    # Es más fácil: hacemos que agrupado tenga filas=agencia, columnas=items
    # Luego transponemos
    agrupado = agrupado.set_index('AGENCIA')
    # Eliminar columnas (agencias) que suman cero (opcional)
    agrupado = agrupado.loc[:, (agrupado.sum(axis=0) != 0)]
    # Transponer: ahora filas = items, columnas = agencias
    pivot = agrupado.T
    return pivot

# ========== 6. AGREGAR TOTALES ==========
def agregar_totales(pivot):
    # Total por fila (cada ítem)
    pivot['TOTAL ÍTEM'] = pivot.sum(axis=1)
    # Añadir una fila de total por columna (total por agencia)
    total_por_agencia = pivot.sum(axis=0)
    # Concatenar como una nueva fila al final
    pivot.loc['TOTAL AGENCIA'] = total_por_agencia
    return pivot

# ========== 7. EXPORTAR A PDF ==========
def exportar_pdf(df_informe, nombre_archivo='informe_pedidos.pdf'):
    # Crear el documento en orientación horizontal (más ancho)
    doc = SimpleDocTemplate(nombre_archivo, pagesize=landscape(A4), 
                            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    # Convertir DataFrame a lista de listas para la tabla
    # Encabezados: primera fila
    encabezados = ['Ítem'] + list(df_informe.columns)
    data = [encabezados]
    
    # Agregar filas (cada ítem con sus valores)
    for idx, row in df_informe.iterrows():
        fila = [idx] + [row[col] for col in df_informe.columns]
        data.append(fila)
    
    # Crear tabla
    tabla = Table(data)
    
    # Estilo de la tabla
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ])
    tabla.setStyle(estilo)
    
    # Construir el PDF
    elementos = []
    # Título
    styles = getSampleStyleSheet()
    titulo = Paragraph(f"Informe de Pedidos - Mes {MES} (Días {DIA_INICIO} al {DIA_FIN})", styles['Title'])
    elementos.append(titulo)
    elementos.append(Paragraph("<br/><br/>", styles['Normal']))
    elementos.append(tabla)
    
    doc.build(elementos)
    print(f"✅ PDF guardado como {nombre_archivo}")

# ========== 8. EJECUCIÓN PRINCIPAL ==========
if __name__ == '__main__':
    print("Conectando a Google Sheets...")
    sheet = conectar_google_sheets()
    print("Leyendo datos...")
    df_raw = leer_datos(sheet)
    print(f"Total de registros leídos: {len(df_raw)}")
    
    print("Filtrando por fecha y agencias...")
    df_filtrado = procesar_y_filtrar(df_raw, MES, DIA_INICIO, DIA_FIN, AGENCIAS_FILTRO)
    print(f"Registros después del filtro: {len(df_filtrado)}")
    
    if df_filtrado.empty:
        print("⚠️ No hay datos para los criterios seleccionados.")
        exit()
    
    items = obtener_items(df_filtrado)
    print(f"Ítems encontrados: {len(items)}")
    
    pivot = generar_informe(df_filtrado, items)
    pivot_con_totales = agregar_totales(pivot)
    
    print("\n--- INFORME GENERADO (vista previa) ---")
    print(pivot_con_totales)
    
    # Exportar a CSV (opcional)
    pivot_con_totales.to_csv('informe_pedidos.csv')
    print("✅ También se guardó una copia en CSV: informe_pedidos.csv")
    
    # Exportar a PDF
    exportar_pdf(pivot_con_totales, 'informe_pedidos.pdf')
