import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
import plotly.express as px
import base64

st.set_page_config(layout="wide", page_title="Informe de Útiles")

st.title("📊 INFORME DE PEDIDOS DE ÚTILES")
st.markdown("---")

# ========== CONFIGURACIÓN ==========
SPREADSHEET_ID = "1eaujMJahDPn7YBpHeGKG_pSIvxjosnD6f2MHXLfngbI"
SHEET_NAME = "Respuestas de formulario 1"

AGENCIAS_TODAS = [
    "MIRAMAR", "M CHIQUITA", "MECHONGUE", "GESELL", "DOLORES", "MONOLITO",
    "PINAMAR", "S CLEMENTE", "MAR DE AJO", "MAIPU", "S TERESITA", "MADARIAGA",
    "PIRAN", "VIDAL"
]

# ========== FUNCIÓN PARA CARGAR DATOS ==========
@st.cache_data(ttl=300)
def cargar_datos_utiles():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        df.columns = df.columns.str.replace('\n', ' ').str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

# ========== FUNCIÓN PROCESAR INFORME (CORREGIDA) ==========
def procesar_informe(df, mes, anio, dia_inicio, dia_fin, agencias_seleccionadas):
    # Detectar columna de fecha
    fecha_col = 'FECHA' if 'FECHA' in df.columns else 'Marca temporal'
    df['fecha'] = pd.to_datetime(df[fecha_col], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['fecha'])
    
    # Filtrar por fecha
    df = df[(df['fecha'].dt.year == anio) & 
            (df['fecha'].dt.month == mes) &
            (df['fecha'].dt.day >= dia_inicio) &
            (df['fecha'].dt.day <= dia_fin)]
    
    if agencias_seleccionadas:
        df = df[df['AGENCIA'].isin(agencias_seleccionadas)]
    
    if df.empty:
        return None
    
    # Excluir columnas que no son productos (incluyendo las columnas "parche")
    excluir = [
        'Marca temporal', 'FECHA', '¿A dónde pertenece?', 'AGENCIA', 'SECTOR',
        'MODELO_SOPORTE', 'OTROS PEDIDOS ARREGLADO', 'OTROS PEDIDOS',
        'MODELO DE IMPRESORA', 'TONER CANTIDAD', 'fecha'
    ]
    # También excluir cualquier columna que contenga "OTROS" o "MODELO" (por si acaso)
    items = [
        col for col in df.columns 
        if col not in excluir 
        and not col.startswith('OTROS') 
        and not col.startswith('MODELO')
        and col != 'fecha'
    ]
    
    # Convertir TODAS las columnas de items a números (forzando errores a 0)
    for item in items:
        df[item] = pd.to_numeric(df[item], errors='coerce').fillna(0)
    
    # Agrupar por agencia y sumar
    df_agrupado = df.groupby('AGENCIA')[items].sum().reset_index()
    
    # Pivot: items como filas, agencias como columnas
    df_pivot = df_agrupado.set_index('AGENCIA').T
    
    # Totales
    df_pivot['TOTAL ÍTEM'] = df_pivot.sum(axis=1)
    total_por_agencia = df_pivot.sum(axis=0)
    df_pivot.loc['TOTAL AGENCIA'] = total_por_agencia
    
    return df_pivot

# ========== FILTROS EN LA PÁGINA PRINCIPAL ==========
st.subheader("🔍 Filtros de búsqueda")

col1, col2, col3, col4 = st.columns(4)
with col1:
    año = st.number_input("📅 Año", min_value=2020, max_value=2030, value=2026, step=1)
with col2:
    mes = st.selectbox("📆 Mes", options=list(range(1,13)), 
                       format_func=lambda x: datetime(2000, x, 1).strftime('%B'), 
                       index=datetime.today().month-1)
with col3:
    dia_inicio = st.number_input("📅 Día desde", min_value=1, max_value=31, value=1)
with col4:
    dia_fin = st.number_input("📅 Día hasta", min_value=1, max_value=31, value=15)

agencias_seleccionadas = st.multiselect("🏢 Agencias (vacío = todas)", options=AGENCIAS_TODAS)

generar = st.button("📊 GENERAR INFORME", type="primary", use_container_width=True)

# ========== CARGA Y GENERACIÓN ==========
df_raw = cargar_datos_utiles()

if generar:
    if df_raw.empty:
        st.warning("No se pudieron cargar los datos. Revisá la conexión a Google Sheets.")
    else:
        with st.spinner("Procesando pedidos, por favor espera..."):
            informe = procesar_informe(df_raw, mes, año, dia_inicio, dia_fin, agencias_seleccionadas)
        
        if informe is None:
            st.info("📭 No hay pedidos para los filtros seleccionados.")
        else:
            st.success(f"✅ Informe generado para {datetime(año, mes, 1).strftime('%B %Y')} (días {dia_inicio} al {dia_fin})")
            
            # Mostrar tabla
            st.dataframe(informe.style.format("{:.0f}").background_gradient(cmap='Blues', axis=None), 
                         use_container_width=True, height=600)
            
            # Descargar CSV
            csv = informe.to_csv()
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="informe_utiles.csv" style="text-decoration: none;">📥 Descargar informe en CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            # Gráfico top 10
            st.subheader("📈 Top 10 ítems más solicitados")
            top_items = informe[:-1].copy()
            top_items['Total General'] = top_items.sum(axis=1)
            top_items = top_items.sort_values('Total General', ascending=False).head(10)
            fig = px.bar(top_items, x=top_items.index, y='Total General', 
                         title="Cantidad total por ítem",
                         labels={'index': 'Ítem', 'Total General': 'Cantidad pedida'},
                         color='Total General', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
