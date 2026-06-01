import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, date
import re
import io

# ── CONFIGURACIÓN INICIAL ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Subir Actas - OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📋"
)

# ── ESTILOS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #f8fafc; }
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.35rem; font-weight: 600; }
    .main-header p { color: #94a3b8; margin: 0; font-size: 0.78rem; }
    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; }
    .stButton > button[kind="primary"] { background: #3b82f6 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📋 Subir Actas</h1>
    <p>Carga de archivos CSV para actualizar actas y finalizar gestión</p>
</div>
""", unsafe_allow_html=True)

# ── Conexión Supabase ───────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

# ── Utilidades ──────────────────────────────────────────────────────────────
def limpiar_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = re.sub(r'\s+', ' ', str(v)).strip()
    return None if s.lower() in ('', 'nan', 'none', 'null', 'nat') else s

def norm_fecha(v):
    if not v:
        return None
    s = limpiar_str(v)
    if not s:
        return None
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return s
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m/%y'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    try:
        return pd.to_datetime(s, dayfirst=True).strftime('%Y-%m-%d')
    except Exception:
        return None

def fmt_moneda(v):
    if not v or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        n = float(v)
        if n.is_integer():
            return "${:,.0f}".format(n).replace(",", ".")
        e, d = int(n), int(round((n - int(n)) * 100))
        return "${},{:02d}".format("{:,}".format(e).replace(",", "."), d)
    except Exception:
        return str(v)

def parsear_periodo(valor):
    if not valor or pd.isna(valor):
        return None
    try:
        s = str(valor).strip()
        match = re.match(r'(\d{4})[/](\d{1,2})', s)
        if match:
            anio = int(match.group(1))
            mes = int(match.group(2))
            if 1 <= mes <= 12:
                return datetime(anio, mes, 1).strftime('%Y-%m-%d')
        return None
    except:
        return None

# ══════════════════════════════════════════════════════════════════
# SUBIR ACTAS
# ══════════════════════════════════════════════════════════════════
st.markdown("#### 📋 Subir Actas (CSV)")
st.markdown("""
<div style="background: #f1f5f9; padding: 0.5rem 1rem; border-radius: 10px; border-left: 4px solid #3b82f6; margin-bottom: 1rem;">
El sistema busca coincidencias por <strong>CUIT + LEGAJO + FECHA VTO</strong>
en registros con <strong>MAIL ENVIADO = SI</strong> y actualiza:
<ul>
    <li>ACTA y ESTADO GESTIÓN a FINALIZADO</li>
    <li>DEUDA PRESUNTA (si la columna existe)</li>
    <li>PERÍODO DESDE y PERÍODO HASTA (si las columnas existen, formato AAAA/MM → se completa con día 1)</li>
</ul>
</div>
""", unsafe_allow_html=True)

csv_file = st.file_uploader("Archivo CSV", type=["csv"], key="upload_actas_csv")

if csv_file:
    st.caption(f"Archivo: **{csv_file.name}**")
    
    try:
        # LEER CSV DE FORMA ROBUSTA - IGNORANDO FILAS CON ERRORES
        contenido = csv_file.getvalue().decode('utf-8-sig')
        lineas = contenido.split('\n')
        
        # Detectar separador ( , o ; )
        separador = ',' if ',' in lineas[0] else ';'
        
        # Determinar número de columnas esperado (de la primera línea no vacía)
        num_columnas_esperado = None
        for linea in lineas:
            if linea.strip():
                num_columnas_esperado = len(linea.split(separador))
                break
        
        if num_columnas_esperado is None:
            num_columnas_esperado = 1
        
        # Corregir líneas con distinto número de columnas
        lineas_corregidas = []
        lineas_error = 0
        
        for linea in lineas:
            if not linea.strip():
                continue
            
            partes = linea.split(separador)
            
            if len(partes) == num_columnas_esperado:
                lineas_corregidas.append(linea)
            elif len(partes) > num_columnas_esperado:
                # Tiene columnas de más: unir las extras a la última columna
                nuevas_partes = partes[:num_columnas_esperado-1]
                nuevas_partes.append(''.join(partes[num_columnas_esperado-1:]))
                lineas_corregidas.append(separador.join(nuevas_partes))
                lineas_error += 1
            else:
                # Tiene menos columnas: rellenar con vacías
                nuevas_partes = partes + [''] * (num_columnas_esperado - len(partes))
                lineas_corregidas.append(separador.join(nuevas_partes))
                lineas_error += 1
        
        if lineas_error > 0:
            st.warning(f"⚠️ Se corrigieron {lineas_error} línea(s) con formato incorrecto automáticamente.")
        
        # Leer CSV corregido
        from io import StringIO
        df_completo = pd.read_csv(StringIO('\n'.join(lineas_corregidas)), sep=separador, dtype=str, encoding='utf-8-sig')
        
        st.success(f"✅ Archivo cargado correctamente. {len(df_completo)} filas procesadas.")
        
        # Vista previa
        with st.expander("📄 Vista previa del archivo"):
            st.dataframe(df_completo.head(5), use_container_width=True, height=150)
            st.caption(f"Columnas detectadas: {', '.join(df_completo.columns.tolist())}")
        
        # Detectar columnas necesarias
        col_cuit = col_leg = col_vto = col_acta = col_deuda = col_desde = col_hasta = None
        for c in df_completo.columns:
            cu = c.upper()
            if 'CUIT' in cu and not col_cuit: 
                col_cuit = c
            if ('LEG' in cu or 'LEGAJO' in cu) and not col_leg: 
                col_leg = c
            if ('VTO' in cu or 'FECHA_VTO' in cu or 'FECHA VTO' in cu) and not col_vto: 
                col_vto = c
            if ('NRO_ACTA' in cu or cu == 'ACTA' or 'NUMERO ACTA' in cu) and not col_acta: 
                col_acta = c
            if ('DEUDA' in cu or 'MONTO' in cu) and not col_deuda: 
                col_deuda = c
            if 'PERIODO_DESDE' in cu and not col_desde: 
                col_desde = c
            if 'PERIODO_HASTA' in cu and not col_hasta: 
                col_hasta = c
        
        if not all([col_cuit, col_leg, col_vto]):
            st.warning(f"⚠️ No se detectaron todas las columnas necesarias. Buscamos: CUIT, LEG, VTO")
            st.info(f"Columnas encontradas: CUIT={col_cuit}, LEG={col_leg}, VTO={col_vto}, ACTA={col_acta}, DEUDA={col_deuda}")
        else:
            st.success(f"✅ Columnas detectadas: CUIT=`{col_cuit}` · LEG=`{col_leg}` · VTO=`{col_vto}`" + 
                      (f" · DEUDA=`{col_deuda}`" if col_deuda else "") +
                      (f" · PERIODO_DESDE=`{col_desde}`" if col_desde else "") +
                      (f" · PERIODO_HASTA=`{col_hasta}`" if col_hasta else ""))
            
            if st.button("📋 Procesar y actualizar actas", type="primary"):
                with st.spinner("Procesando..."):
                    actualizados = 0
                    no_encontrados = 0
                    errores_fila = 0
                    bar = st.progress(0)
                    errores = []
                    
                    for i, row in df_completo.iterrows():
                        try:
                            # Extraer CUIT
                            cuit_raw = str(row[col_cuit]) if pd.notna(row[col_cuit]) else ""
                            cuit = re.sub(r'[\.\-,\s]', '', cuit_raw).strip()
                            
                            # Extraer LEGAJO
                            leg_raw = str(row[col_leg]) if pd.notna(row[col_leg]) else ""
                            leg = re.sub(r'\D', '', leg_raw).strip() if leg_raw else None
                            
                            # Extraer FECHA VTO
                            vto_raw = str(row[col_vto]) if pd.notna(row[col_vto]) else ""
                            vto = norm_fecha(vto_raw)
                            
                            # Extraer ACTA (opcional)
                            acta = "ACTUALIZADO"
                            if col_acta and pd.notna(row.get(col_acta)):
                                acta_raw = str(row[col_acta]).strip()
                                if acta_raw:
                                    acta = acta_raw
                            
                            # Extraer DEUDA (opcional) - PISA EL IMPORTE SI EXISTE
                            deuda_nueva = None
                            if col_deuda and pd.notna(row.get(col_deuda)):
                                deuda_raw = str(row[col_deuda]).replace(',', '.').strip()
                                try:
                                    deuda_valor = float(deuda_raw)
                                    deuda_nueva = fmt_moneda(deuda_valor)
                                except:
                                    deuda_nueva = deuda_raw
                            
                            # Extraer períodos (opcional)
                            desde_nuevo = None
                            if col_desde and pd.notna(row.get(col_desde)):
                                desde_nuevo = parsear_periodo(row[col_desde])
                            
                            hasta_nuevo = None
                            if col_hasta and pd.notna(row.get(col_hasta)):
                                hasta_nuevo = parsear_periodo(row[col_hasta])
                            
                            # Buscar coincidencia y actualizar
                            if cuit and leg and vto:
                                resultado = supabase.table("padron_deuda_presunta").select("id").eq("cuit", cuit).eq("leg", leg).eq("vto", vto).eq("mail_enviado", "SI").execute()
                                
                                if resultado.data:
                                    for reg in resultado.data:
                                        update_data = {
                                            "acta": acta, 
                                            "estado_gestion": "FINALIZADO"
                                        }
                                        if deuda_nueva:
                                            update_data["deuda_presunta"] = deuda_nueva
                                        if desde_nuevo:
                                            update_data["desde"] = desde_nuevo
                                        if hasta_nuevo:
                                            update_data["hasta"] = hasta_nuevo
                                        
                                        supabase.table("padron_deuda_presunta").update(update_data).eq("id", reg['id']).execute()
                                        actualizados += 1
                                else:
                                    no_encontrados += 1
                            else:
                                no_encontrados += 1
                                
                        except Exception as e:
                            errores_fila += 1
                            if len(errores) < 20:
                                errores.append(f"Fila {i+1}: {str(e)[:100]}")
                        
                        bar.progress((i + 1) / len(df_completo))
                    
                    bar.empty()
                    
                    # Mostrar resultados
                    col1, col2, col3 = st.columns(3)
                    col1.metric("✅ ACTUALIZADOS", actualizados)
                    col2.metric("❌ NO ENCONTRADOS", no_encontrados)
                    col3.metric("⚠️ ERRORES", errores_fila)
                    
                    if errores:
                        with st.expander(f"📋 Ver detalles de {len(errores)} error(es)"):
                            for err in errores[:10]:
                                st.caption(f"• {err}")
                    
                    if actualizados > 0:
                        st.success(f"✅ ¡Proceso completado! {actualizados} actas actualizadas correctamente.")
                    else:
                        st.warning("⚠️ No se pudo actualizar ningún registro. Verificá que los CUIT, LEGAJO y FECHAS VTO coincidan exactamente con registros que tengan MAIL ENVIADO = SI.")
                    
                    if no_encontrados > 0:
                        st.info(f"ℹ️ {no_encontrados} filas no encontraron coincidencia en la base de datos.")
    
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.info("💡 Asegurate de que el archivo CSV tenga al menos las columnas: CUIT, LEGAJO y FECHA VTO")
