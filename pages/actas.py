import streamlit as st
import pandas as pd
from supabase import create_client
import io
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Sistema de Carga - Fiscalización OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    div[data-testid="stButton"] button:disabled {
        background-color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# Conexión a Supabase
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["anon_key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    # Mostrar info del archivo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Archivo", uploaded_file.name[:30] + "..." if len(uploaded_file.name) > 30 else uploaded_file.name)
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
        
        # Validar que no esté vacío
        if df.empty:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Archivo vacío</strong><br>
                El archivo no contiene datos para procesar.
            </div>
            """, unsafe_allow_html=True)
        else:
            # Limpiar datos
            df = df.replace({pd.NA: None, float('nan'): None})
            
            # Mostrar resumen
            st.markdown(f"""
            <div class="info-box">
                <strong>📊 Resumen del archivo</strong><br>
                Registros detectados: {len(df):,}
            </div>
            """, unsafe_allow_html=True)
            
            # Vista previa
            with st.expander("Ver vista previa de datos (primeras 10 filas)"):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Botón de carga (solo si no se realizó la carga)
            if not st.session_state.carga_realizada:
                if st.button("Confirmar carga de datos", type="primary", use_container_width=True):
                    with st.spinner("Procesando y validando registros..."):
                        # Convertir a lista de diccionarios
                        registros = df.to_dict(orient='records')
                        
                        # Agregar metadata
                        for registro in registros:
                            registro['fecha_carga'] = datetime.now().isoformat()
                            registro['archivo_origen'] = uploaded_file.name
                        
                        # Verificar duplicados por combinación de campos clave
                        # (ajustá estos campos según tu tabla real)
                        campos_clave = ['cuit', 'periodo', 'numero_acta']  # MODIFICAR SEGÚN TU TABLA
                        
                        # Obtener registros existentes
                        st.info("Verificando registros existentes...")
                        existentes = supabase.table("padron_deuda").select(",".join(campos_clave)).execute()
                        existentes_set = set()
                        
                        if existentes.data:
                            for reg in existentes.data:
                                clave = tuple(str(reg.get(campo, '')) for campo in campos_clave)
                                existentes_set.add(clave)
                        
                        # Filtrar nuevos registros
                        nuevos_registros = []
                        duplicados_encontrados = 0
                        
                        for reg in registros:
                            clave = tuple(str(reg.get(campo, '')) for campo in campos_clave)
                            if clave not in existentes_set:
                                nuevos_registros.append(reg)
                            else:
                                duplicados_encontrados += 1
                        
                        # Mostrar resultados de validación
                        if duplicados_encontrados > 0:
                            st.markdown(f"""
                            <div class="warning-box">
                                <strong>⚠️ Duplicados detectados</strong><br>
                                Se encontraron {duplicados_encontrados:,} registros que ya existen en la base de datos.<br>
                                Solo se cargarán los {len(nuevos_registros):,} registros nuevos.
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Insertar nuevos registros
                        if nuevos_registros:
                            try:
                                # Insertar en lotes de 500 para mejor rendimiento
                                lote_size = 500
                                total_insertados = 0
                                
                                for i in range(0, len(nuevos_registros), lote_size):
                                    lote = nuevos_registros[i:i+lote_size]
                                    resultado = supabase.table("padron_deuda").insert(lote).execute()
                                    total_insertados += len(resultado.data)
                                
                                st.session_state.registros_insertados = total_insertados
                                st.session_state.carga_realizada = True
                                
                                st.markdown(f"""
                                <div class="success-box">
                                    <strong>✓ CARGA COMPLETADA</strong><br>
                                    Se procesaron e insertaron {total_insertados:,} registros en la base de datos.
                                    {f'({duplicados_encontrados:,} registros duplicados omitidos)' if duplicados_encontrados > 0 else ''}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Mostrar botón para resetear (si quieren cargar otro archivo)
                                if st.button("Nueva carga", use_container_width=True):
                                    st.session_state.carga_realizada = False
                                    st.session_state.registros_insertados = 0
                                    st.rerun()
                                    
                            except Exception as e:
                                st.markdown(f"""
                                <div class="warning-box">
                                    <strong>✗ ERROR EN LA CARGA</strong><br>
                                    {str(e)}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="warning-box">
                                <strong>⚠️ SIN REGISTROS NUEVOS</strong><br>
                                Todos los registros del archivo ya existen en la base de datos.
                                No se realizó ninguna inserción.
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("Reintentar con otro archivo", use_container_width=True):
                                st.rerun()
            else:
                # Estado después de carga exitosa
                st.markdown(f"""
                <div class="success-box">
                    <strong>✓ CARGA PREVIAMENTE COMPLETADA</strong><br>
                    {st.session_state.registros_insertados:,} registros fueron insertados en la sesión actual.
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Iniciar nueva carga", use_container_width=True):
                    st.session_state.carga_realizada = False
                    st.session_state.registros_insertados = 0
                    st.rerun()
                    
    except Exception as e:
        st.markdown(f"""
        <div class="warning-box">
            <strong>✗ ERROR AL LEER EL ARCHIVO</strong><br>
            {str(e)}<br><br>
            <strong>Posibles soluciones:</strong><br>
            - Verificar que el archivo no esté abierto en otro programa<br>
            - Guardar el archivo como .xlsx (formato más reciente)<br>
            - Verificar que la estructura del archivo sea correcta
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="info-box">
        <strong>📌 Instrucciones</strong><br>
        1. Seleccione un archivo Excel (.xls o .xlsx) con el padrón de deuda presunta.<br>
        2. El sistema validará la estructura y detectará duplicados.<br>
        3. Confirme la carga para insertar solo los registros nuevos.<br>
        4. Los datos quedarán disponibles para consulta en el sistema de fiscalización.
    </div>
    """, unsafe_allow_html=True)
