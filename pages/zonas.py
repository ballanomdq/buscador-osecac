import streamlit as st
import pandas as pd
from supabase import create_client
import re

# Configuración de página
st.set_page_config(
    page_title="Zonas de Inspectores - OSECAC",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Conexión a Supabase
SUPABASE_URL_ACTAS = st.secrets["SUPABASE_URL_ACTAS"]
SUPABASE_KEY_ACTAS = st.secrets["SUPABASE_KEY_ACTAS"]
supabase = create_client(SUPABASE_URL_ACTAS, SUPABASE_KEY_ACTAS)

# Estilo
st.markdown("""
<style>
    .main-header { background-color: #1e293b; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #3b82f6; }
    .success-box { background-color: #064e3b; padding: 1rem; border-radius: 6px; border-left: 4px solid #10b981; margin: 1rem 0; color: #ffffff; }
    .warning-box { background-color: #451a03; padding: 1rem; border-radius: 6px; border-left: 4px solid #f59e0b; margin: 1rem 0; color: #ffffff; }
    .info-box { background-color: #1e293b; padding: 1rem; border-radius: 6px; border-left: 4px solid #3b82f6; margin: 1rem 0; color: #ffffff; }
    div[data-testid="stButton"] button { background-color: #3b82f6; color: white; font-weight: 500; border: none; padding: 0.4rem 1.2rem; }
    div[data-testid="stButton"] button:hover { background-color: #2563eb; }
    .delete-btn button { background-color: #dc2626 !important; }
    .compact-table td, .compact-table th { padding: 2px 8px !important; font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h2 style="color: #ffffff; margin: 0; font-weight: 500;">🗺️ Zonas de Inspectores</h2>
    <p style="color: #94a3b8; margin: 0.3rem 0 0 0; font-size: 0.85rem;">Gestión de inspectores y asignación automática de legajos</p>
</div>
""", unsafe_allow_html=True)

# Botón volver
col_back, _ = st.columns([1, 5])
with col_back:
    if st.button("← Volver al inicio", key="btn_volver"):
        st.switch_page("main.py")

st.markdown("---")

# ==================== FUNCIÓN PARA PARSAR EL BLOQUE DE CALLES ====================
def parsear_bloque_calles(bloque_texto):
    resultados = []
    partes = bloque_texto.split(' / ')
    
    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue
        
        patron = r'^(.*?)\s*\(([PpIiEeY\s]+)\)\s*(\d+)-(\d+)$'
        match = re.match(patron, parte)
        
        if match:
            calle = match.group(1).strip().upper()
            lado_raw = match.group(2).strip().upper()
            desde = int(match.group(3))
            hasta = int(match.group(4))
            
            if 'P' in lado_raw and 'I' in lado_raw:
                lado = 'AMBOS'
            elif 'P' in lado_raw:
                lado = 'PAR'
            elif 'I' in lado_raw:
                lado = 'IMPAR'
            else:
                lado = 'AMBOS'
            
            resultados.append({
                'calle': calle,
                'lado': lado,
                'desde': desde,
                'hasta': hasta
            })
        else:
            st.warning(f"No se pudo parsear: {parte}")
    
    return resultados

# ==================== PESTAÑAS ====================
tab1, tab2, tab3 = st.tabs(["👥 Inspectores", "📍 Zonas por Inspector", "🔄 Asignar Legajos"])

# ==================== TAB 1: INSPECTORES ====================
with tab1:
    st.markdown("### 👥 Administrar Inspectores")
    
    with st.expander("➕ Agregar nuevo inspector", expanded=False):
        with st.form("form_nuevo_inspector"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo", placeholder="Ej: GARCIA JUAN PAULO")
            with col2:
                legajo = st.text_input("Número de legajo", placeholder="Ej: 7952")
            
            if st.form_submit_button("💾 Guardar Inspector", type="primary"):
                if nombre and legajo:
                    try:
                        supabase.table("inspectores").insert({"nombre": nombre, "legajo": legajo}).execute()
                        st.success(f"✅ Inspector {nombre} (Legajo {legajo}) agregado")
                        st.rerun()
                    except Exception as e:
                        if "duplicate" in str(e).lower():
                            st.error(f"❌ El legajo {legajo} ya existe")
                        else:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Completá nombre y legajo")
    
    st.markdown("### 📋 Listado de inspectores")
    
    try:
        inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
        
        if inspectores.data:
            for row in inspectores.data:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                with col1:
                    st.write(f"**{row['nombre']}**")
                with col2:
                    st.write(f"Legajo: {row['legajo']}")
                with col3:
                    if st.button("✏️", key=f"edit_insp_{row['id']}"):
                        st.session_state.editando_inspector = row
                with col4:
                    if st.button("🗑️", key=f"del_insp_{row['id']}"):
                        zonas = supabase.table("zonas_inspectores").select("id").eq("legajo", row['legajo']).execute()
                        if zonas.data:
                            st.warning(f"⚠️ No se puede eliminar. El inspector tiene {len(zonas.data)} zona(s) asignada(s).")
                        else:
                            supabase.table("inspectores").delete().eq("id", row['id']).execute()
                            st.success(f"✅ Inspector {row['nombre']} eliminado")
                            st.rerun()
                st.markdown("---")
            
            if st.session_state.get('editando_inspector'):
                st.markdown("### ✏️ Editar inspector")
                editando = st.session_state.editando_inspector
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_nombre = st.text_input("Nombre", value=editando['nombre'])
                with col2:
                    nuevo_legajo = st.text_input("Legajo", value=editando['legajo'])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Guardar cambios"):
                        supabase.table("inspectores").update({
                            "nombre": nuevo_nombre,
                            "legajo": nuevo_legajo
                        }).eq("id", editando['id']).execute()
                        del st.session_state.editando_inspector
                        st.success("✅ Inspector actualizado")
                        st.rerun()
                with col_btn2:
                    if st.button("❌ Cancelar"):
                        del st.session_state.editando_inspector
                        st.rerun()
        else:
            st.info("No hay inspectores cargados")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Ejecutá el SQL de creación de tablas en Supabase")

# ==================== TAB 2: ZONAS POR INSPECTOR ====================
with tab2:
    st.markdown("### 📍 Asignar calles a inspectores")
    
    try:
        inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
        
        if not inspectores.data:
            st.warning("⚠️ Primero debes cargar inspectores en la pestaña 'Inspectores'")
        else:
            opciones_inspectores = {f"{row['nombre']} (Legajo {row['legajo']})": row['legajo'] for row in inspectores.data}
            inspector_seleccionado = st.selectbox(
                "Seleccionar inspector",
                options=list(opciones_inspectores.keys()),
                key="select_inspector_zona"
            )
            legajo_seleccionado = opciones_inspectores[inspector_seleccionado]
            
            st.markdown(f"**Legajo:** {legajo_seleccionado}")
            
            # Área para pegar bloque de calles
            st.markdown("### 📋 Cargar nuevas calles desde bloque de texto")
            st.markdown("""
            <div class="info-box">
                <strong>📌 Formato aceptado:</strong><br>
                <code>Av. Colón (P) 2000-2500 / San Juan (P) 2100-5400 / Pehuajó (P) 2100-5400</code><br>
                <strong>Separador:</strong> espacio barra espacio: <code> / </code>
            </div>
            """, unsafe_allow_html=True)
            
            bloque_calles = st.text_area(
                "Pegá acá el bloque de calles:",
                height=150,
                placeholder='Ejemplo: Av. Colón (P) 2000-2500 / San Juan (P) 2100-5400'
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔍 Previsualizar y guardar", type="primary"):
                    if bloque_calles:
                        calles_parseadas = parsear_bloque_calles(bloque_calles)
                        if calles_parseadas:
                            st.markdown("### 📋 Calles a guardar:")
                            df_preview = pd.DataFrame(calles_parseadas)
                            st.dataframe(df_preview, use_container_width=True, hide_index=True)
                            
                            # Confirmar guardado
                            if st.button("✅ Confirmar guardado de estas calles"):
                                # Insertar nuevas calles (sin borrar las existentes)
                                insertados = 0
                                for calle_data in calles_parseadas:
                                    try:
                                        # Verificar si ya existe
                                        existe = supabase.table("zonas_inspectores").select("id").eq("legajo", legajo_seleccionado).eq("calle", calle_data['calle']).execute()
                                        if not existe.data:
                                            supabase.table("zonas_inspectores").insert({
                                                "legajo": legajo_seleccionado,
                                                "calle": calle_data['calle'],
                                                "lado": calle_data['lado'],
                                                "altura_desde": calle_data['desde'],
                                                "altura_hasta": calle_data['hasta']
                                            }).execute()
                                            insertados += 1
                                    except Exception as e:
                                        st.error(f"Error con calle {calle_data['calle']}: {str(e)}")
                                
                                st.success(f"✅ Se agregaron {insertados} nuevas calles")
                                st.rerun()
                        else:
                            st.error("No se pudo parsear ninguna calle. Verificá el formato.")
                    else:
                        st.warning("Pegá un bloque de calles primero")
            
            with col_btn2:
                if st.button("🗑️ Eliminar TODAS las calles de este inspector", key="delete_all"):
                    supabase.table("zonas_inspectores").delete().eq("legajo", legajo_seleccionado).execute()
                    st.success(f"✅ Se eliminaron todas las calles")
                    st.rerun()
            
            # Listado de zonas actuales (VERSIÓN COMPACTA)
            st.markdown(f"### 📋 Calles actuales de {inspector_seleccionado}")
            
            zonas = supabase.table("zonas_inspectores").select("*").eq("legajo", legajo_seleccionado).order("calle").execute()
            
            if zonas.data:
                # Mostrar como tabla compacta
                for row in zonas.data:
                    col1, col2, col3, col4, col5 = st.columns([2.5, 1, 1, 0.5, 0.5])
                    with col1:
                        st.write(f"**{row['calle']}**")
                    with col2:
                        st.write(row['lado'])
                    with col3:
                        st.write(f"{row['altura_desde']} - {row['altura_hasta']}")
                    with col4:
                        if st.button("✏️", key=f"edit_zona_{row['id']}"):
                            st.session_state.editando_zona = row
                    with col5:
                        if st.button("🗑️", key=f"del_zona_{row['id']}"):
                            supabase.table("zonas_inspectores").delete().eq("id", row['id']).execute()
                            st.success(f"✅ Zona {row['calle']} eliminada")
                            st.rerun()
                    st.markdown("---")
                
                if st.session_state.get('editando_zona'):
                    st.markdown("### ✏️ Editar zona")
                    editando = st.session_state.editando_zona
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        nueva_calle = st.text_input("Calle", value=editando['calle'])
                    with col2:
                        nuevo_lado = st.selectbox("Lado", options=["AMBOS", "PAR", "IMPAR"], index=["AMBOS", "PAR", "IMPAR"].index(editando['lado']))
                    with col3:
                        nueva_altura_desde = st.number_input("Desde", value=editando['altura_desde'])
                    with col4:
                        nueva_altura_hasta = st.number_input("Hasta", value=editando['altura_hasta'])
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("💾 Guardar cambios"):
                            supabase.table("zonas_inspectores").update({
                                "calle": nueva_calle.upper().strip(),
                                "lado": nuevo_lado,
                                "altura_desde": nueva_altura_desde,
                                "altura_hasta": nueva_altura_hasta
                            }).eq("id", editando['id']).execute()
                            del st.session_state.editando_zona
                            st.success("✅ Zona actualizada")
                            st.rerun()
                    with col_btn2:
                        if st.button("❌ Cancelar"):
                            del st.session_state.editando_zona
                            st.rerun()
            else:
                st.info("No hay calles asignadas. Usá el bloque de texto para cargarlas.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ==================== TAB 3: ASIGNAR LEGAJOS ====================
with tab3:
    st.markdown("### 🔄 Asignar Legajos Automáticamente")
    st.markdown("""
    <div class="info-box">
        <strong>📌 ¿Qué hace esta función?</strong><br>
        - Toma empresas con <strong>leg vacío</strong><br>
        - Lee su dirección (calle y número)<br>
        - Busca en las zonas qué inspector le corresponde<br>
        - Asigna el legajo automáticamente
    </div>
    """, unsafe_allow_html=True)
    
    try:
        inspectores = supabase.table("inspectores").select("legajo").execute()
        zonas = supabase.table("zonas_inspectores").select("id").limit(1).execute()
        
        if not inspectores.data:
            st.warning("⚠️ No hay inspectores cargados.")
        elif not zonas.data:
            st.warning("⚠️ No hay zonas cargadas.")
        else:
            sin_legajo = supabase.table("padron_deuda_presunta").select("id", count="exact").is_("leg", "null").execute()
            total_sin_legajo = sin_legajo.count
            
            st.metric("📊 Registros sin legajo", total_sin_legajo)
            
            if total_sin_legajo == 0:
                st.success("✅ Todos los registros ya tienen legajo.")
            else:
                todas_zonas = supabase.table("zonas_inspectores").select("*").execute()
                df_zonas = pd.DataFrame(todas_zonas.data)
                
                st.info(f"📌 Se asignarán legajos a {total_sin_legajo} registros")
                
                if st.button("🚀 Asignar Legajos Automáticamente", type="primary"):
                    with st.spinner("Procesando..."):
                        todos_registros = []
                        offset = 0
                        batch_size = 100
                        while True:
                            batch = supabase.table("padron_deuda_presunta").select("*").is_("leg", "null").range(offset, offset + batch_size - 1).execute()
                            if not batch.data:
                                break
                            todos_registros.extend(batch.data)
                            offset += batch_size
                            if len(batch.data) < batch_size:
                                break
                        
                        asignados = 0
                        no_asignados = 0
                        
                        for reg in todos_registros:
                            calle = reg.get('calle', '')
                            numero = reg.get('numero', '')
                            
                            if not calle or not numero:
                                no_asignados += 1
                                continue
                            
                            try:
                                numero_limpio = int(re.sub(r'\D', '', str(numero)))
                            except:
                                no_asignados += 1
                                continue
                            
                            lado = "PAR" if numero_limpio % 2 == 0 else "IMPAR"
                            legajo_asignado = None
                            
                            for _, zona in df_zonas.iterrows():
                                if zona['calle'].upper() == calle.upper():
                                    if zona['lado'] == "AMBOS" or zona['lado'] == lado:
                                        if zona['altura_desde'] <= numero_limpio <= zona['altura_hasta']:
                                            legajo_asignado = zona['legajo']
                                            break
                            
                            if legajo_asignado:
                                supabase.table("padron_deuda_presunta").update({
                                    "leg": legajo_asignado
                                }).eq("id", reg['id']).execute()
                                asignados += 1
                            else:
                                no_asignados += 1
                        
                        st.success(f"✅ {asignados} legajos asignados, {no_asignados} no encontrados")
                        st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")
