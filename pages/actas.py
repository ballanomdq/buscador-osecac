import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, date
import re

# ── Conexión ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL_ACTAS"],
        st.secrets["SUPABASE_KEY_ACTAS"]
    )

supabase = get_supabase()

st.set_page_config(page_title="Fiscalización - OSECAC", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
html, body, [class*="css"] { font-size: 13px !important; }
.app-header { padding: 0.6rem 1rem; background: #1e293b; border-left: 3px solid #3b82f6;
              border-radius: 6px; margin-bottom: 0.8rem; }
.app-header h3 { color: #fff; margin: 0; font-size: 1rem; font-weight: 500; }
.app-header p  { color: #94a3b8; margin: 0; font-size: 0.75rem; }
div[data-testid="stButton"] > button {
    padding: 0.25rem 0.75rem !important;
    font-size: 0.78rem !important;
    background: #334155 !important;
    color: #e2e8f0 !important;
    border: 1px solid #475569 !important;
    border-radius: 4px !important;
}
div[data-testid="stButton"] > button:hover { background: #475569 !important; }
div[data-testid="stButton"] > button[kind="primary"] {
    background: #2563eb !important;
    border-color: #1d4ed8 !important;
}
#MainMenu, footer, header { display: none !important; }
.big-number {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 12px;
    padding: 0.5rem 1rem;
    text-align: center;
    border: 1px solid #3b82f6;
}
.big-number h1 { margin: 0; font-size: 1.8rem; color: #3b82f6; }
.big-number p { margin: 0; font-size: 0.7rem; color: #94a3b8; }
.msg { padding: 0.5rem 0.75rem; border-radius: 4px; font-size: 0.78rem;
       border-left: 3px solid; margin: 0.4rem 0; }
.msg-success { background: #064e3b; border-color: #10b981; color: #6ee7b7; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
  <h3>Fiscalización — Deuda Presunta</h3>
  <p>Sistema de gestión y seguimiento</p>
</div>
""", unsafe_allow_html=True)

col_back, _ = st.columns([1, 11])
with col_back:
    if st.button("← Volver"):
        st.switch_page("main.py")

# ── Utilidades generales ──────────────────────────────────────────────────────
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
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y', '%m/%d/%Y'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    try:
        return pd.to_datetime(s, dayfirst=True).strftime('%Y-%m-%d')
    except Exception:
        return None

def fmt_fecha(v):
    if not v:
        return None
    try:
        if isinstance(v, (pd.Timestamp, datetime)):
            return v.strftime('%d/%m/%Y')
        s = str(v).strip()
        if re.match(r'\d{4}-\d{2}-\d{2}', s):
            return datetime.strptime(s[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
        return s
    except Exception:
        return str(v) if v else None

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

def limpiar_entero(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        n = float(v)
        return int(n) if n == int(n) else None
    except Exception:
        return None

def limpiar_para_comparar(texto):
    if not texto:
        return ""
    return re.sub(r'\s+', ' ', str(texto).upper()).strip()

def normalizar_calle(calle):
    if not calle:
        return ""
    calle = calle.upper().strip()
    parentesis = re.search(r'\(([^)]+)\)', calle)
    if parentesis:
        calle = parentesis.group(1)
    for prefijo in ['AV ', 'AV.', 'AVENIDA ', 'CALLE ', 'C/', 'RUTA ', 'RP ']:
        if calle.startswith(prefijo):
            calle = calle[len(prefijo):]
    calle = re.sub(r'^\d+\s+', '', calle)
    calle = calle.replace("SETIEMBRE", "SEPTIEMBRE")
    return calle.strip()

# ── Asignación de legajo ─────────────────────────────────────────────────────
def asignar_legajo(localidad, calle, numero, lookup_localidades, lookup_zonas):
    localidad_cmp = limpiar_para_comparar(localidad)

    if localidad_cmp not in ("MAR DEL PLATA", ""):
        return lookup_localidades.get(localidad_cmp)

    calle_norm = normalizar_calle(calle)
    if not calle_norm:
        return None

    try:
        num = int(re.sub(r'\D', '', str(numero)))
    except Exception:
        return None

    lado_actual = "PAR" if num % 2 == 0 else "IMPAR"

    for zona in lookup_zonas.get(calle_norm, []):
        lado_db = str(zona['lado']).upper().strip()
        es_mismo_lado = (
            lado_db in ("AMBOS", "A")
            or (lado_actual == "PAR"   and lado_db in ("PAR",   "P"))
            or (lado_actual == "IMPAR" and lado_db in ("IMPAR", "I"))
        )
        try:
            desde = int(zona['desde'])
            hasta = int(zona['hasta'])
        except (TypeError, ValueError):
            continue
        if es_mismo_lado and desde <= num <= hasta:
            return zona['legajo']
    return None

# ── Carga de datos ────────────────────────────────────────────────────────────
def cargar_inspectores_localidad():
    r = supabase.table("inspectores_localidad").select("*").execute()
    return r.data if r.data else []

def cargar_zonas_inspectores():
    r = supabase.table("zonas_inspectores").select("*").execute()
    return r.data if r.data else []

def construir_lookup_localidades(inspectores_localidad):
    lookup = {}
    for item in inspectores_localidad:
        clave = limpiar_para_comparar(item['localidad'])
        if clave:
            lookup[clave] = item['legajo']
    return lookup

def construir_lookup_zonas(zonas_inspectores):
    lookup = {}
    for zona in zonas_inspectores:
        clave = normalizar_calle(zona.get('calle', ''))
        if not clave:
            continue
        lookup.setdefault(clave, []).append({
            'legajo': zona['legajo'],
            'lado':   zona['lado'],
            'desde':  zona['altura_desde'],
            'hasta':  zona['altura_hasta'],
        })
    return lookup

def traer_registros_sin_legajo():
    registros, offset = [], 0
    while True:
        r = supabase.table("padron_deuda_presunta") \
            .select("id, localidad, calle, numero, razon_social") \
            .is_("leg", "null") \
            .range(offset, offset + 999).execute()
        if not r.data:
            break
        registros.extend(r.data)
        offset += 1000
        if len(r.data) < 1000:
            break
    return registros

def guardar_legajos_en_batch(asignaciones, batch_size=100):
    if not asignaciones:
        return 0
    por_legajo = {}
    for a in asignaciones:
        por_legajo.setdefault(a['legajo'], []).append(a['id'])
    total = 0
    for legajo, ids in por_legajo.items():
        for i in range(0, len(ids), batch_size):
            chunk = ids[i:i + batch_size]
            supabase.table("padron_deuda_presunta").update({"leg": legajo}).in_("id", chunk).execute()
            total += len(chunk)
    return total

def get_localidades():
    r = supabase.table("padron_deuda_presunta").select("localidad").execute()
    locs = sorted({x['localidad'] for x in r.data if x.get('localidad')})
    if 'MAR DEL PLATA' in locs:
        locs.remove('MAR DEL PLATA')
        locs = ['MAR DEL PLATA'] + locs
    return locs

def get_pares_existentes():
    todos, offset = [], 0
    while True:
        batch = supabase.table("padron_deuda_presunta") \
                   .select("cuit, ultima_acta") \
                   .range(offset, offset + 999).execute()
        if not batch.data:
            break
        todos.extend(batch.data)
        offset += 1000
        if len(batch.data) < 1000:
            break
    return {(str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) for r in todos if r.get('cuit')}

# ── Mapeo Excel ───────────────────────────────────────────────────────────────
COLS_EXCEL = [
    "DELEGACION","LOCALIDAD","CUIT","RAZON SOCIAL","DEUDA PRESUNTA",
    "CP","CALLE","NUMERO","PISO","DPTO","FECHARELDEPENDENCIA",
    "EMAIL","TEL_DOM_LEGAL","TEL_DOM_REAL","ULTIMA ACTA","DESDE",
    "HASTA","DETECTADO","ESTADO","FECHA_PAGO_OBL",
    "EMPL 10-2025","EMP 11-2025","EMPL 12-2025","ACTIVIDAD","SITUACION",
]
MAPA = {
    "DELEGACION":"delegacion","LOCALIDAD":"localidad","CUIT":"cuit",
    "RAZON SOCIAL":"razon_social","DEUDA PRESUNTA":"deuda_presunta",
    "CP":"cp","CALLE":"calle","NUMERO":"numero","PISO":"piso","DPTO":"dpto",
    "FECHARELDEPENDENCIA":"fechareldependencia","EMAIL":"email",
    "TEL_DOM_LEGAL":"tel_dom_legal","TEL_DOM_REAL":"tel_dom_real",
    "ULTIMA ACTA":"ultima_acta","DESDE":"desde","HASTA":"hasta",
    "DETECTADO":"detectado","ESTADO":"estado","FECHA_PAGO_OBL":"fecha_pago_obl",
    "EMPL 10-2025":"empl_10_2025","EMP 11-2025":"emp_11_2025","EMPL 12-2025":"empl_12_2025",
    "ACTIVIDAD":"actividad","SITUACION":"situacion",
}
COLS_FECHA  = {"fechareldependencia","desde","hasta","fecha_pago_obl"}
COLS_MONEDA = {"deuda_presunta","detectado"}
TITULOS = {
    'id':'ID','delegacion':'DELEGACION','localidad':'LOCALIDAD','cuit':'CUIT',
    'razon_social':'RAZON SOCIAL','deuda_presunta':'DEUDA PRESUNTA','cp':'CP',
    'calle':'CALLE','numero':'NUMERO','piso':'PISO','dpto':'DPTO',
    'fechareldependencia':'FECHARELDEPENDENCIA','email':'EMAIL',
    'tel_dom_legal':'TEL_DOM_LEGAL','tel_dom_real':'TEL_DOM_REAL',
    'ultima_acta':'ULTIMA ACTA','desde':'DESDE','hasta':'HASTA',
    'detectado':'DETECTADO','estado':'ESTADO','fecha_pago_obl':'FECHA PAGO OBL',
    'empl_10_2025':'EMPL 10-2025','emp_11_2025':'EMP 11-2025','empl_12_2025':'EMPL 12-2025',
    'actividad':'ACTIVIDAD','situacion':'SITUACION',
    'leg':'LEG','vto':'VTO','mail_enviado':'MAIL ENVIADO',
    'acta':'ACTA','estado_gestion':'ESTADO GESTION',
}
COLS_DISABLED = [
    'ID','CUIT','RAZON SOCIAL','DEUDA PRESUNTA','CP','CALLE','NUMERO','PISO','DPTO',
    'FECHARELDEPENDENCIA','EMAIL','TEL_DOM_LEGAL','TEL_DOM_REAL','ULTIMA ACTA',
    'DESDE','HASTA','DETECTADO','ESTADO','FECHA PAGO OBL',
    'EMPL 10-2025','EMP 11-2025','EMPL 12-2025','ACTIVIDAD','SITUACION',
]

def procesar_excel(archivo):
    engine = 'xlrd' if archivo.name.endswith('.xls') else 'openpyxl'
    df = pd.read_excel(archivo, engine=engine, dtype=str)
    df.columns = [str(c).strip().upper() for c in df.columns]
    faltantes = [c for c in COLS_EXCEL if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes: {faltantes}")
    df = df[COLS_EXCEL].rename(columns=MAPA)
    out = []
    for _, fila in df.iterrows():
        r = {}
        for col in MAPA.values():
            v = fila.get(col)
            v = None if pd.isna(v) else limpiar_str(v)
            if col in COLS_FECHA and v:
                v = norm_fecha(v)
            if col in COLS_MONEDA and v:
                try:
                    v = fmt_moneda(float(v))
                except Exception:
                    pass
            if col == "ultima_acta" and not v:
                v = "*"
            r[col] = v
        out.append(r)
    return out

# ==================== PESTAÑAS ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Cargar Padrón",
    "✏️ Editar Legajos y Vtos",
    "📧 Solicitar Actas",
    "📋 Subir Actas",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — Cargar Padrón
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### Cargar Padrón de Deuda Presunta")
    archivo = st.file_uploader("Archivo Excel", type=["xls","xlsx"], key="upload_padron")

    if archivo:
        st.caption(f"Archivo: **{archivo.name}**")
        try:
            registros = procesar_excel(archivo)
            hoy = date.today().isoformat()
            for r in registros:
                r.update({'leg':None,'vto':None,'mail_enviado':'NO','acta':None,
                           'fecha_carga':hoy,'estado_gestion':'PENDIENTE'})

            pares = get_pares_existentes()
            nuevos = [r for r in registros
                      if (str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) not in pares]
            dupl = len(registros) - len(nuevos)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total", len(registros))
            c2.metric("Nuevos", len(nuevos))
            c3.metric("Duplicados", dupl)

            if nuevos:
                if st.button("✅ Confirmar carga", type="primary"):
                    with st.spinner("Insertando..."):
                        n = 0
                        for i in range(0, len(nuevos), 100):
                            res = supabase.table("padron_deuda_presunta").insert(nuevos[i:i+100]).execute()
                            n += len(res.data)
                    st.success(f"✅ {n} registros insertados.")
            else:
                st.warning("⚠️ No hay registros nuevos.")
        except Exception as e:
            st.error(str(e))

# ══════════════════════════════════════════════════════════════════
# TAB 2 — Editar Legajos y Vtos
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Editar Legajos y Fechas de Vencimiento")

    total_general = supabase.table("padron_deuda_presunta").select("id", count="exact").execute().count
    con_legajo    = supabase.table("padron_deuda_presunta").select("id", count="exact").not_.is_("leg", "null").execute().count
    sin_legajo_total = total_general - con_legajo

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown(f'<div class="big-number"><h1>{total_general}</h1><p>TOTAL</p></div>', unsafe_allow_html=True)
    with col_t2:
        st.markdown(f'<div class="big-number"><h1>{con_legajo}</h1><p>CON LEGAJO</p></div>', unsafe_allow_html=True)
    with col_t3:
        st.markdown(f'<div class="big-number"><h1>{sin_legajo_total}</h1><p>SIN LEGAJO</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🗑 Eliminar seleccionados"):
            ids = st.session_state.get('ids_a_eliminar', [])
            if ids:
                supabase.table("padron_deuda_presunta").delete().in_("id", ids).execute()
                st.session_state.ids_a_eliminar = []
                st.rerun()
    with col2:
        if st.button("🗑 Eliminar TODO"):
            st.session_state.confirmar_del_todo = True
    with col3:
        if st.button("🤖 Asignar Legajos"):
            st.session_state.asignar_legajos = True
    with col4:
        if st.button("↺ Resetear filtros"):
            for k in ['input_filtro_cuit','input_filtro_razon','filtro_localidad',
                      'filtro_mail','filtro_leg','pagina_actual']:
                st.session_state.pop(k, None)
            st.rerun()
    with col5:
        if st.button("⟳ Recargar"):
            st.rerun()

    if st.session_state.get('confirmar_del_todo'):
        st.warning("⚠️ Esta acción eliminará **TODOS** los registros.")
        if st.button("Sí, eliminar todo"):
            supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
            st.session_state.confirmar_del_todo = False
            st.rerun()
        if st.button("Cancelar"):
            st.session_state.confirmar_del_todo = False
            st.rerun()

    # ── Asignación automática de legajos ─────────────────────────────────
    if st.session_state.get('asignar_legajos'):
        with st.spinner("Cargando tablas de inspectores..."):
            insp_loc   = cargar_inspectores_localidad()
            insp_zonas = cargar_zonas_inspectores()
            lkp_loc    = construir_lookup_localidades(insp_loc)
            lkp_zonas  = construir_lookup_zonas(insp_zonas)

        with st.spinner("Cargando registros sin legajo..."):
            registros = traer_registros_sin_legajo()

        if not registros:
            st.info("No hay registros sin legajo.")
            st.session_state.asignar_legajos = False
        else:
            total    = len(registros)
            bar      = st.progress(0)
            status   = st.empty()
            asig     = []
            no_asig  = []

            for i, reg in enumerate(registros):
                bar.progress((i + 1) / total)
                status.text(f"Procesando {i+1} de {total}…")

                legajo = asignar_legajo(
                    reg.get('localidad', '') or '',
                    reg.get('calle',     '') or '',
                    reg.get('numero',    '') or '',
                    lkp_loc, lkp_zonas
                )
                if legajo:
                    asig.append({'id': reg['id'], 'legajo': legajo})
                else:
                    no_asig.append({
                        'id':          reg['id'],
                        'localidad':   reg.get('localidad', ''),
                        'calle':       reg.get('calle', ''),
                        'numero':      reg.get('numero', ''),
                        'razon_social': reg.get('razon_social', ''),
                    })

            bar.empty()
            status.empty()

            with st.spinner("Guardando legajos…"):
                guardados = guardar_legajos_en_batch(asig)

            st.session_state.asignar_legajos   = False
            st.session_state.ultima_asignacion = {
                "asignados":    guardados,
                "no_asignados": len(no_asig),
                "detalle":      no_asig,
            }
            st.rerun()

    if st.session_state.get('ultima_asignacion'):
        res = st.session_state.ultima_asignacion
        st.success(f"✅ {res['asignados']} legajos asignados · {res['no_asignados']} sin coincidencia.")
        if res['no_asignados'] > 0:
            with st.expander(f"📋 Ver {res['no_asignados']} registros sin legajo"):
                st.dataframe(pd.DataFrame(res['detalle']), use_container_width=True)
        if st.button("Cerrar resultado"):
            del st.session_state.ultima_asignacion
            st.rerun()

    st.markdown("---")

    # ── Filtros ───────────────────────────────────────────────────────────
    f1, f2, f3, f4, f5 = st.columns([1.5, 1.5, 1.5, 1, 1])
    with f1:
        filtro_cuit  = st.text_input("CUIT",  key="input_filtro_cuit",  placeholder="Ej: 30707685243", label_visibility="collapsed")
    with f2:
        filtro_razon = st.text_input("Razón", key="input_filtro_razon", placeholder="Razón social",    label_visibility="collapsed")
    with f3:
        locs     = get_localidades()
        localidad = st.selectbox("Localidad", ["TODAS"] + locs, key="filtro_localidad", label_visibility="collapsed")
    with f4:
        filtro_mail = st.selectbox("Mail",   ["AMBOS","NO","SI"],                       key="filtro_mail", label_visibility="collapsed")
    with f5:
        filtro_leg  = st.selectbox("Legajo", ["TODOS","CON LEGAJO","SIN LEGAJO"],       key="filtro_leg",  label_visibility="collapsed")

    q = supabase.table("padron_deuda_presunta").select("*")
    if localidad != "TODAS":
        q = q.eq("localidad", localidad)
    if filtro_mail == "SI":
        q = q.eq("mail_enviado", "SI")
    elif filtro_mail == "NO":
        q = q.eq("mail_enviado", "NO")

    datos = q.execute()

    if not datos.data:
        st.info("Sin datos.")
    else:
        df = pd.DataFrame(datos.data)
        if filtro_cuit:
            df = df[df['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
        if filtro_razon:
            df = df[df['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
        if filtro_leg == "CON LEGAJO":
            df = df[df['leg'].notna()]
        elif filtro_leg == "SIN LEGAJO":
            df = df[df['leg'].isna()]

        total = len(df)
        RPP   = 300
        pages = max(1, (total + RPP - 1) // RPP)

        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 1
        st.session_state.pagina_actual = max(1, min(st.session_state.pagina_actual, pages))

        pa, pn, ps = st.columns([1, 3, 1])
        with pa:
            if st.button("◀") and st.session_state.pagina_actual > 1:
                st.session_state.pagina_actual -= 1
                st.rerun()
        with pn:
            st.caption(f"Página {st.session_state.pagina_actual} / {pages} | {total} registros")
        with ps:
            if st.button("▶") and st.session_state.pagina_actual < pages:
                st.session_state.pagina_actual += 1
                st.rerun()

        off  = (st.session_state.pagina_actual - 1) * RPP
        df_p = df.iloc[off:off+RPP].reset_index(drop=True).copy()

        for col in ['empl_10_2025','emp_11_2025','empl_12_2025']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(limpiar_entero)
        for col in ['fechareldependencia','desde','hasta','fecha_pago_obl','vto','fecha_carga']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(fmt_fecha)

        df_orig = df_p.copy()
        df_ed   = df_p.drop(columns=['fecha_carga'], errors='ignore').rename(columns=TITULOS)
        df_ed.insert(0, "🗑️", False)

        if st.checkbox("Seleccionar todos (página actual)"):
            df_ed["🗑️"] = True

        edited = st.data_editor(
            df_ed, use_container_width=True, height=550,
            column_config={"🗑️": st.column_config.CheckboxColumn("Elim.")},
            disabled=COLS_DISABLED,
            key=f"editor_{st.session_state.pagina_actual}",
        )

        ids_sel = edited[edited["🗑️"]]["ID"].tolist() if "ID" in edited.columns else []
        st.session_state.ids_a_eliminar = ids_sel

        if st.button("💾 Guardar cambios", type="primary"):
            mods = 0
            with st.spinner("Guardando..."):
                for idx, row in edited.iterrows():
                    if idx >= len(df_orig):
                        continue
                    orig = df_orig.iloc[idx]
                    upd  = {}

                    nv = row.get('LEG')
                    if nv != orig.get('leg'):
                        upd['leg'] = nv if nv and nv != '' else None

                    nv = row.get('VTO')
                    if nv != orig.get('vto'):
                        upd['vto'] = norm_fecha(nv) if nv else None

                    nv = row.get('MAIL ENVIADO') or 'NO'
                    if nv != orig.get('mail_enviado'):
                        upd['mail_enviado'] = nv

                    nv = row.get('ACTA')
                    if nv != orig.get('acta'):
                        upd['acta'] = nv if nv and nv != '' else None

                    nv = row.get('ESTADO GESTION') or 'PENDIENTE'
                    if nv != orig.get('estado_gestion'):
                        upd['estado_gestion'] = nv

                    if upd:
                        supabase.table("padron_deuda_presunta").update(upd).eq("id", row['ID']).execute()
                        mods += 1

            if mods:
                st.success(f"✅ {mods} registros actualizados.")
                st.rerun()

# ══════════════════════════════════════════════════════════════════
# TAB 3 — Solicitar Actas
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.info("📧 Solicitar Actas — en construcción")

# ══════════════════════════════════════════════════════════════════
# TAB 4 — Subir Actas
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.info("📋 Subir Actas — en construcción")
