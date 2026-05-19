import streamlit as st
import pandas as pd
from supabase import create_client
import re
from datetime import datetime

st.set_page_config(page_title="Zonas de Inspectores - OSECAC", layout="wide", initial_sidebar_state="collapsed")

SUPABASE_URL_ACTAS = st.secrets["SUPABASE_URL_ACTAS"]
SUPABASE_KEY_ACTAS = st.secrets["SUPABASE_KEY_ACTAS"]
supabase = create_client(SUPABASE_URL_ACTAS, SUPABASE_KEY_ACTAS)

st.markdown("""
<style>
.main-header { background-color: #1e293b; padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #3b82f6; }
.main-header h2 { color: #ffffff; margin: 0; font-size: 1.2rem; }
.main-header p { color: #94a3b8; margin: 0; font-size: 0.75rem; }
div[data-testid="stButton"] button { background-color: #3b82f6; color: white; border: none; padding: 0.2rem 0.5rem; font-size: 0.75rem; border-radius: 4px; }
div[data-testid="stButton"] button:hover { background-color: #2563eb; }
div[data-testid="stButton"] button[kind="secondary"] { background-color: #dc2626; }
div[data-testid="stButton"] button[kind="secondary"]:hover { background-color: #b91c1c; }
.stDataFrame { font-size: 0.75rem; }
hr { margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h2>🗺️ Zonas de Inspectores - Gestión Completa</h2>
    <p>Administración de inspectores, localidades, calles y palabras ancla (Mar del Plata)</p>
</div>
""", unsafe_allow_html=True)

# ── FILA DE BOTONES: Volver, Actas, Mapa, Editor Zonas, Informe ───────────────
col_back, col_actas, col_mapa, col_editor, col_informe = st.columns([1, 1, 1, 1, 1.5])

with col_back:
    if st.button("← Volver", key="btn_volver_zonas"):
        st.switch_page("main.py")

with col_actas:
    url_actas = "https://buscador-osecac-6jztx7xjhgkvcaubfinn5y.streamlit.app/actas"
    st.markdown(f'<a href="{url_actas}" target="_blank" style="text-decoration: none;"><button style="background-color: #3b82f6; color: white; border: none; padding: 0.2rem 0.5rem; font-size: 0.75rem; border-radius: 4px; cursor: pointer; width: 100%;">📋 ACTAS</button></a>', unsafe_allow_html=True)

with col_mapa:
    if st.button("🗺️ MAPA", key="btn_mapa"):
        st.switch_page("pages/mapazona.py")

with col_editor:
    if st.button("🎨 EDITAR ZONAS", key="btn_editor_zonas"):
        st.switch_page("pages/editor_zonas.py")

with col_informe:
    if st.button("📄 INFORME ZONAS POR INSPECTOR", key="btn_informe_completo"):
        st.session_state.generar_informe_completo = True

st.markdown("---")

# ── Generar informe completo de inspectores ──────────────────────────────────
def generar_informe_completo():
    """Genera un informe TXT detallado de todos los inspectores con sus localidades, calles y palabras ancla"""
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    
    contenido = []
    contenido.append("=" * 80)
    contenido.append("              INFORME COMPLETO DE INSPECTORES - ZONAS Y LOCALIDADES")
    contenido.append(f"                        Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    contenido.append("=" * 80)
    contenido.append("")
    
    for ins in inspectores.data:
        legajo = ins['legajo']
        nombre = ins['nombre']
        
        contenido.append("")
        contenido.append("█" * 80)
        contenido.append(f"  INSPECTOR: {nombre}")
        contenido.append(f"  LEGAJO: {legajo}")
        contenido.append("█" * 80)
        contenido.append("")
        
        # ── LOCALIDADES ASIGNADAS (fuera de Mar del Plata) ──
        localidades = supabase.table("inspectores_localidad").select("*").eq("legajo", legajo).order("localidad").execute()
        
        contenido.append("")
        contenido.append("┌" + "─" * 78 + "┐")
        contenido.append("│ 📍 LOCALIDADES ASIGNADAS (Fuera de Mar del Plata)")
        contenido.append("├" + "─" * 78 + "┤")
        
        if localidades.data:
            for loc in localidades.data:
                contenido.append(f"│   • {loc['localidad']}")
        else:
            contenido.append("│   • Sin localidades asignadas")
        contenido.append("└" + "─" * 78 + "┘")
        contenido.append("")
        
        # ── CALLES ASIGNADAS (Mar del Plata) ──
        calles = supabase.table("zonas_inspectores").select("*").eq("legajo", legajo).order("calle").execute()
        
        contenido.append("")
        contenido.append("┌" + "─" * 78 + "┐")
        contenido.append("│ 🏠 CALLES ASIGNADAS (Mar del Plata)")
        contenido.append("├" + "─" * 78 + "┤")
        
        if calles.data:
            calles_agrupadas = {}
            for calle in calles.data:
                clave = calle['calle']
                if clave not in calles_agrupadas:
                    calles_agrupadas[clave] = []
                calles_agrupadas[clave].append({
                    'lado': calle['lado'],
                    'desde': calle['altura_desde'],
                    'hasta': calle['altura_hasta']
                })
            
            for calle_nombre, rangos in sorted(calles_agrupadas.items()):
                contenido.append(f"│")
                contenido.append(f"│  📌 {calle_nombre}")
                for r in rangos:
                    contenido.append(f"│      Lado: {r['lado']} - Alturas: {r['desde']} a {r['hasta']}")
        else:
            contenido.append("│   • Sin calles asignadas")
        contenido.append("└" + "─" * 78 + "┘")
        contenido.append("")
        
        # ── PALABRAS ANCLA (Mar del Plata) ──
        palabras = supabase.table("palabras_ancla").select("*").eq("legajo", legajo).order("palabra").execute()
        
        contenido.append("")
        contenido.append("┌" + "─" * 78 + "┐")
        contenido.append("│ ⚓ PALABRAS ANCLA (Mar del Plata - Coincidencia parcial)")
        contenido.append("├" + "─" * 78 + "┤")
        
        if palabras.data:
            for pal in palabras.data:
                contenido.append(f"│   • {pal['palabra']}")
        else:
            contenido.append("│   • Sin palabras ancla asignadas")
        contenido.append("└" + "─" * 78 + "┘")
        contenido.append("")
    
    contenido.append("")
    contenido.append("=" * 80)
    contenido.append("                      FIN DEL INFORME")
    contenido.append("=" * 80)
    
    return "\n".join(contenido)

if st.session_state.get('generar_informe_completo'):
    with st.spinner("Generando informe completo..."):
        contenido_txt = generar_informe_completo()
        st.download_button(
            label="📥 DESCARGAR INFORME ZONAS POR INSPECTOR (TXT)",
            data=contenido_txt.encode('utf-8'),
            file_name=f"INFORME_ZONAS_POR_INSPECTOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            key="download_informe_completo"
        )
        st.success("✅ Informe generado correctamente")
        st.session_state.generar_informe_completo = False

def forzar_recarga_cache():
    try:
        import sys
        if 'actas' in sys.modules:
            import actas
            if hasattr(actas, 'cargar_inspectores_localidad'):
                actas.cargar_inspectores_localidad.clear()
            if hasattr(actas, 'cargar_zonas_inspectores'):
                actas.cargar_zonas_inspectores.clear()
            if hasattr(actas, 'cargar_palabras_ancla'):
                actas.cargar_palabras_ancla.clear()
    except:
        pass

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Inspectores", "📍 Localidades", "📍 Calles (MDQ)", "⚓ Palabras Ancla", "🔄 Sinónimos"])

# TAB 1: INSPECTORES
with tab1:
    st.markdown("### 👥 Inspectores")
    
    with st.expander("➕ Agregar inspector"):
        with st.form("form_inspector"):
            nombre = st.text_input("Nombre completo")
            legajo = st.text_input("Número de legajo")
            if st.form_submit_button("Guardar"):
                if nombre and legajo:
                    supabase.table("inspectores").insert({"nombre": nombre.upper(), "legajo": int(legajo)}).execute()
                    forzar_recarga_cache()
                    st.rerun()
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if inspectores.data:
        for ins in inspectores.data:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{ins['nombre']}**")
            col2.write(f"Legajo: {ins['legajo']}")
            if col3.button("🗑️", key=f"del_insp_{ins['id']}"):
                zonas_asig = supabase.table("zonas_inspectores").select("*").eq("legajo", ins['legajo']).execute()
                palabras_asig = supabase.table("palabras_ancla").select("*").eq("legajo", ins['legajo']).execute()
                if zonas_asig.data or palabras_asig.data:
                    st.warning(f"Elimine primero las {len(zonas_asig.data)} calles y {len(palabras_asig.data)} palabras ancla asignadas")
                else:
                    supabase.table("inspectores").delete().eq("id", ins['id']).execute()
                    forzar_recarga_cache()
                    st.rerun()
    else:
        st.info("No hay inspectores")

# TAB 2: LOCALIDADES
with tab2:
    st.markdown("### 📍 Localidades fuera de Mar del Plata")
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if not inspectores.data:
        st.warning("Primero cargá inspectores")
    else:
        opts = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        legajo_sel = st.selectbox("Seleccionar inspector", options=list(opts.values()), format_func=lambda x: [k for k, v in opts.items() if v == x][0], key="sel_localidad")
        
        with st.expander("➕ Agregar localidad"):
            with st.form("form_localidad"):
                localidad = st.text_input("Nombre de la localidad")
                if st.form_submit_button("Guardar"):
                    if localidad:
                        supabase.table("inspectores_localidad").insert({
                            "legajo": legajo_sel,
                            "localidad": localidad.upper().strip()
                        }).execute()
                        forzar_recarga_cache()
                        st.rerun()
        
        localidades = supabase.table("inspectores_localidad").select("*").eq("legajo", legajo_sel).order("localidad").execute()
        if localidades.data:
            for loc in localidades.data:
                col1, col2 = st.columns([4, 1])
                col1.write(loc['localidad'])
                if col2.button("🗑️", key=f"del_loc_{loc['id']}"):
                    supabase.table("inspectores_localidad").delete().eq("id", loc['id']).execute()
                    forzar_recarga_cache()
                    st.rerun()
        else:
            st.info("No hay localidades asignadas")

# TAB 3: CALLES - EDITOR CON FORMULARIOS POR FILA
with tab3:
    st.markdown("### 📍 Calles de Mar del Plata - Editor Completo")
    st.caption("📝 Usá los botones ✏️ para editar cada calle, 🗑️ para eliminar con confirmación.")
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if not inspectores.data:
        st.warning("Primero cargá inspectores")
    else:
        opts = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        
        # Filtro por inspector
        filtro_legajo = st.selectbox(
            "Filtrar por inspector", 
            options=["TODOS"] + list(opts.values()), 
            format_func=lambda x: "TODOS" if x == "TODOS" else [k for k, v in opts.items() if v == x][0], 
            key="filtro_legajo_calles"
        )
        
        # Obtener zonas
        query = supabase.table("zonas_inspectores").select("*")
        if filtro_legajo != "TODOS":
            query = query.eq("legajo", filtro_legajo)
        zonas = query.order("calle").execute()
        
        if zonas.data:
            # Mostrar cada calle con botones de editar y eliminar
            for zona in zonas.data:
                col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 0.8, 0.8, 1.2, 0.5, 0.5])
                
                # Buscar nombre del inspector
                inspector = next((i for i in inspectores.data if i['legajo'] == zona['legajo']), None)
                nombre_inspector = inspector['nombre'].split(',')[0] if inspector else str(zona['legajo'])
                
                col1.write(f"**{zona['calle']}**")
                col2.write(zona['lado'])
                col3.write(str(zona['altura_desde']))
                col4.write(str(zona['altura_hasta']))
                col5.write(nombre_inspector)
                
                # Botón Editar
                if col6.button("✏️", key=f"edit_{zona['id']}"):
                    st.session_state[f"editando_{zona['id']}"] = True
                
                # Botón Eliminar con confirmación
                if col7.button("🗑️", key=f"del_{zona['id']}"):
                    st.session_state[f"confirmar_del_{zona['id']}"] = True
                
                # Confirmación de eliminación
                if st.session_state.get(f"confirmar_del_{zona['id']}"):
                    st.warning(f"⚠️ ¿Eliminar '{zona['calle']}'?")
                    col_ok, col_cancel = st.columns(2)
                    with col_ok:
                        if st.button("✅ Sí, eliminar", key=f"confirm_ok_{zona['id']}"):
                            supabase.table("zonas_inspectores").delete().eq("id", zona['id']).execute()
                            forzar_recarga_cache()
                            del st.session_state[f"confirmar_del_{zona['id']}"]
                            st.rerun()
                    with col_cancel:
                        if st.button("❌ Cancelar", key=f"confirm_cancel_{zona['id']}"):
                            del st.session_state[f"confirmar_del_{zona['id']}"]
                            st.rerun()
                    st.markdown("---")
                
                # Formulario de edición
                if st.session_state.get(f"editando_{zona['id']}"):
                    with st.expander(f"✏️ Editando: {zona['calle']}", expanded=True):
                        with st.form(key=f"form_edit_{zona['id']}"):
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                nueva_calle = st.text_input("Calle", value=zona['calle'])
                            with col_b:
                                nuevo_lado = st.selectbox("Lado", ["PAR", "IMPAR", "AMBOS"], index=["PAR", "IMPAR", "AMBOS"].index(zona['lado']))
                            with col_c:
                                nuevo_legajo = st.selectbox(
                                    "Inspector", 
                                    options=list(opts.values()), 
                                    format_func=lambda x: [k for k, v in opts.items() if v == x][0],
                                    index=list(opts.values()).index(zona['legajo'])
                                )
                            
                            col_d, col_e = st.columns(2)
                            with col_d:
                                nueva_desde = st.number_input("Altura desde", value=int(zona['altura_desde']), min_value=1)
                            with col_e:
                                nueva_hasta = st.number_input("Altura hasta", value=int(zona['altura_hasta']), min_value=1)
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.form_submit_button("💾 GUARDAR"):
                                    supabase.table("zonas_inspectores").update({
                                        "calle": nueva_calle.upper().strip(),
                                        "lado": nuevo_lado,
                                        "legajo": nuevo_legajo,
                                        "altura_desde": int(nueva_desde),
                                        "altura_hasta": int(nueva_hasta)
                                    }).eq("id", zona['id']).execute()
                                    forzar_recarga_cache()
                                    del st.session_state[f"editando_{zona['id']}"]
                                    st.success("✅ Guardado")
                                    st.rerun()
                            with col_btn2:
                                if st.form_submit_button("❌ Cancelar"):
                                    del st.session_state[f"editando_{zona['id']}"]
                                    st.rerun()
                
                st.markdown("---")
            
            # Agregar nueva calle
            st.markdown("### ➕ Agregar nueva calle")
            with st.form("form_nueva_calle", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    nueva_calle = st.text_input("Nombre de la calle", placeholder="Ej: BELGRANO")
                with col2:
                    nuevo_legajo = st.selectbox(
                        "Inspector", 
                        options=list(opts.values()), 
                        format_func=lambda x: [k for k, v in opts.items() if v == x][0],
                        key="nuevo_legajo"
                    )
                with col3:
                    nuevo_lado = st.selectbox("Lado", ["PAR", "IMPAR", "AMBOS"], key="nuevo_lado")
                
                col4, col5 = st.columns(2)
                with col4:
                    nueva_desde = st.number_input("Altura desde", min_value=1, value=1, step=1)
                with col5:
                    nueva_hasta = st.number_input("Altura hasta", min_value=1, value=9999, step=1)
                
                if st.form_submit_button("➕ AGREGAR CALLE"):
                    if nueva_calle:
                        supabase.table("zonas_inspectores").insert({
                            "legajo": int(nuevo_legajo),
                            "calle": nueva_calle.upper().strip(),
                            "lado": nuevo_lado,
                            "altura_desde": int(nueva_desde),
                            "altura_hasta": int(nueva_hasta)
                        }).execute()
                        forzar_recarga_cache()
                        st.success(f"✅ Calle {nueva_calle.upper()} agregada")
                        st.rerun()
                    else:
                        st.error("El nombre de la calle es obligatorio")
        else:
            st.info("No hay calles cargadas")

# TAB 4: PALABRAS ANCLA (NUEVO)
with tab4:
    st.markdown("### ⚓ Palabras Ancla para Mar del Plata")
    st.caption("""
    **¿Qué son las palabras ancla?**  
    Son palabras clave que permiten asignar un inspector aunque la dirección tenga texto adicional.  
    Por ejemplo: si agregás `RUTA 88` para LOPEZ, cualquier empresa en Mar del Plata que tenga `RUTA 88` en su dirección  
    (aunque diga `RUTA 88 KM 12.5` o `RUTA 88 Y CALLE 45`) se asignará automáticamente a LOPEZ.
    
    ⚠️ **Importante:** Las palabras ancla SOLO se evalúan cuando la localidad es MAR DEL PLATA.
    """)
    
    # Verificar tabla
    try:
        supabase.table("palabras_ancla").select("id").limit(1).execute()
    except:
        st.error("La tabla 'palabras_ancla' no existe. Ejecutá este SQL en Supabase:")
        st.code("""
CREATE TABLE palabras_ancla (
  id SERIAL PRIMARY KEY,
  palabra TEXT NOT NULL UNIQUE,
  legajo INTEGER NOT NULL REFERENCES inspectores(legajo),
  creado_por TEXT DEFAULT 'usuario',
  fecha_creacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_palabras_ancla_palabra ON palabras_ancla(palabra);
        """)
    
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if not inspectores.data:
        st.warning("Primero cargá inspectores")
    else:
        opts = {f"{ins['nombre']} (Legajo {ins['legajo']})": ins['legajo'] for ins in inspectores.data}
        
        # Formulario para agregar palabra ancla
        with st.expander("➕ Agregar palabra ancla", expanded=True):
            with st.form("form_palabra_ancla"):
                col1, col2 = st.columns(2)
                with col1:
                    nueva_palabra = st.text_input("Palabra clave", placeholder="Ej: RUTA 88, RUTA 226, AV COSTANERA")
                    st.caption("La palabra puede aparecer en cualquier parte de la dirección")
                with col2:
                    legajo_sel = st.selectbox(
                        "Asignar a inspector", 
                        options=list(opts.values()), 
                        format_func=lambda x: [k for k, v in opts.items() if v == x][0],
                        key="palabra_legajo"
                    )
                
                if st.form_submit_button("⚓ AGREGAR PALABRA ANCLA"):
                    if nueva_palabra:
                        try:
                            supabase.table("palabras_ancla").insert({
                                "palabra": nueva_palabra.upper().strip(),
                                "legajo": int(legajo_sel),
                                "creado_por": "usuario"
                            }).execute()
                            forzar_recarga_cache()
                            st.success(f"✅ Palabra ancla '{nueva_palabra.upper()}' agregada correctamente")
                            st.rerun()
                        except Exception as e:
                            if "duplicate" in str(e).lower():
                                st.error("Esta palabra ancla ya existe")
                            else:
                                st.error(f"Error: {e}")
                    else:
                        st.error("La palabra ancla es obligatoria")
        
        # Lista de palabras ancla existentes
        palabras = supabase.table("palabras_ancla").select("*").order("palabra").execute()
        if palabras.data:
            st.markdown("#### 📋 Lista de palabras ancla actuales")
            for pal in palabras.data:
                # Buscar nombre del inspector
                inspector = next((i for i in inspectores.data if i['legajo'] == pal['legajo']), None)
                nombre_inspector = inspector['nombre'].split(',')[0] if inspector else str(pal['legajo'])
                
                col1, col2, col3, col4 = st.columns([2, 2, 1, 0.5])
                col1.write(f"**{pal['palabra']}**")
                col2.write(f"Asignado a: {nombre_inspector} (Legajo {pal['legajo']})")
                col3.write(pal.get('creado_por', 'sistema'))
                if col4.button("🗑️", key=f"del_ancla_{pal['id']}"):
                    supabase.table("palabras_ancla").delete().eq("id", pal['id']).execute()
                    forzar_recarga_cache()
                    st.rerun()
        else:
            st.info("No hay palabras ancla cargadas aún")

# TAB 5: SINÓNIMOS
with tab5:
    st.markdown("### 🔄 Sinónimos de Calles")
    st.caption("Acá podés agregar sinónimos para que el sistema reconozca formas alternativas de escribir las calles")
    
    # Verificar tabla
    try:
        supabase.table("sinonimos_calles").select("id").limit(1).execute()
    except:
        st.error("La tabla 'sinonimos_calles' no existe. Ejecutá este SQL en Supabase:")
        st.code("""
CREATE TABLE sinonimos_calles (
  id SERIAL PRIMARY KEY,
  calle_oficial TEXT NOT NULL,
  sinonimo TEXT NOT NULL UNIQUE,
  creado_por TEXT DEFAULT 'usuario',
  fecha_creacion TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_sinonimos_sinonimo ON sinonimos_calles(sinonimo);
        """)
    
    # Obtener calles oficiales
    calles_oficiales = supabase.table("zonas_inspectores").select("calle").execute()
    calles_unicas = sorted(list(set([c['calle'] for c in calles_oficiales.data]))) if calles_oficiales.data else []
    
    if calles_unicas:
        with st.expander("➕ Agregar nuevo sinónimo"):
            with st.form("form_sinonimo"):
                col1, col2 = st.columns(2)
                with col1:
                    calle_oficial = st.selectbox("Calle oficial", options=calles_unicas)
                with col2:
                    nuevo_sinonimo = st.text_input("Sinónimo (forma alternativa)", placeholder="Ej: H YRIGOREN, YRIGOYEN")
                if st.form_submit_button("Guardar sinónimo"):
                    if nuevo_sinonimo:
                        try:
                            supabase.table("sinonimos_calles").insert({
                                "calle_oficial": calle_oficial,
                                "sinonimo": nuevo_sinonimo.upper().strip(),
                                "creado_por": "usuario"
                            }).execute()
                            forzar_recarga_cache()
                            st.success("Sinónimo agregado")
                            st.rerun()
                        except Exception as e:
                            if "duplicate" in str(e).lower():
                                st.error("Este sinónimo ya existe")
                            else:
                                st.error(f"Error: {e}")
        
        sinonimos = supabase.table("sinonimos_calles").select("*").order("calle_oficial").execute()
        if sinonimos.data:
            st.markdown("#### Lista de sinónimos actuales")
            for sin in sinonimos.data:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 0.5])
                col1.write(f"**{sin['calle_oficial']}**")
                col2.write(sin['sinonimo'])
                col3.write(sin.get('creado_por', 'sistema'))
                if col4.button("🗑️", key=f"del_sin_{sin['id']}"):
                    supabase.table("sinonimos_calles").delete().eq("id", sin['id']).execute()
                    forzar_recarga_cache()
                    st.rerun()
        else:
            st.info("No hay sinónimos cargados aún")
    else:
        st.info("Primero cargá calles oficiales")
