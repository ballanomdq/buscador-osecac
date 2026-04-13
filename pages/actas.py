import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Sistema de Carga - Fiscalización OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión a Supabase usando TUS mismas variables de secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Estilo profesional
st.markdown("""
<style>
    .main-header {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border-left: 4px solid #3b82f6;
    }
    .success-box {
        background-color: #064e3b;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #451a03;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    div[data-testid="stButton"] button {
        background-color: #3b82f6;
        color: white;
        font-weight: 500;
        border: none;
        padding: 0.5rem 2rem;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if 'carga_realizada' not in st.session_state:
    st.session_state.carga_realizada = False
if 'registros_insertados' not in st.session_state:
    st.session_state.registros_insertados = 0

# Header
st.markdown("""
<div class="main-header">
    <h2 style="color: #ffffff; margin: 0; font-weight: 500;">Sistema de Carga de Padrón</h2>
    <p style="color: #94a3b8; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Fiscalización - Deuda Presunta</p>
</div>
""", unsafe_allow_html=True)

# Subir archivo
uploaded_file = st.file_uploader(
    "Seleccionar archivo Excel (.xls o .xlsx)",
    type=["xls", "xlsx"],
    help="Formatos aceptados: .xls (Excel 97-2003) o .xlsx (Excel 2007+)"
)

if uploaded_file is not None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Archivo", uploaded_file.name[:40] + "..." if len(uploaded_file.name) > 40 else uploaded_file.name)
    with col2:
        st.metric("Tamaño", f"{uploaded_file.size / 1024:.1f} KB")
    with col3:
        st.metric("Formato", "XLS" if uploaded_file.name.endswith('.xls') else "XLSX")
    
    try:
        # Leer archivo según extensión
        if uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, engine='xlrd')
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        if df.empty:
            st.markdown("""
            <div class="warning-box">
                <strong>Archivo vacío</strong><br>
                El archivo no contiene datos para procesar.
            </div>
            """, unsafe_allow_html=True)
        else:
            # Limpiar datos
            df = df.replace({pd.NA: None, float('nan'): None})
            
            # Mostrar resumen
            st.markdown(f"""
            <div class="info-box">
                <strong>Resumen del archivo</strong><br>
                Registros detectados: {len(df):,}
            </div>
            """, unsafe_allow_html=True)
            
            # Vista previa
            with st.expander("Ver vista previa (primeras 10 filas)"):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Botón de carga
            if not st.session_state.carga_realizada:
                if st.button("Confirmar carga de datos", type="primary", use_container_width=True):
                    with st.spinner("Procesando registros..."):
                        registros = df.to_dict(orient='records')
                        
                        # Agregar metadata
                        for registro in registros:
                            registro['fecha_carga'] = datetime.now().isoformat()
                            registro['archivo_origen'] = uploaded_file.name
                        
                        try:
                            # Insertar todos los registros
                            resultado = supabase.table("padron_deuda").insert(registros).execute()
                            
                            st.session_state.registros_insertados = len(resultado.data)
                            st.session_state.carga_realizada = True
                            
                            st.markdown(f"""
                            <div class="success-box">
                                <strong>CARGA COMPLETADA</strong><br>
                                Se insertaron {len(resultado.data):,} registros en la base de datos.
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("Nueva carga", use_container_width=True):
                                st.session_state.carga_realizada = False
                                st.session_state.registros_insertados = 0
                                st.rerun()
                                
                        except Exception as e:
                            st.markdown(f"""
                            <div class="warning-box">
                                <strong>ERROR EN LA CARGA</strong><br>
                                {str(e)}
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-box">
                    <strong>CARGA PREVIAMENTE COMPLETADA</strong><br>
                    {st.session_state.registros_insertados:,} registros fueron insertados.
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Iniciar nueva carga", use_container_width=True):
                    st.session_state.carga_realizada = False
                    st.session_state.registros_insertados = 0
                    st.rerun()
                    
    except Exception as e:
        st.markdown(f"""
        <div class="warning-box">
            <strong>ERROR AL LEER EL ARCHIVO</strong><br>
            {str(e)}<br><br>
            <strong>Soluciones:</strong><br>
            - Verificar que el archivo no esté abierto<br>
            - Guardar el archivo como .xlsx<br>
            - Verificar la estructura del archivo
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="info-box">
        <strong>Instrucciones</strong><br>
        1. Seleccione un archivo Excel (.xls o .xlsx) con el padrón de deuda presunta.<br>
        2. El sistema validará la estructura y mostrará un resumen.<br>
        3. Confirme la carga para insertar los datos en la base.<br>
        4. Los datos quedarán disponibles para consulta en fiscalización.
    </div>
    """, unsafe_allow_html=True)
