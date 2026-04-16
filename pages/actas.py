import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, date
import re
import io

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
/* Reset tamaños globales */
html, body, [class*="css"] { font-size: 13px !important; }

/* Header compacto */
.app-header { padding: 0.6rem 1rem; background: #1e293b; border-left: 3px solid #3b82f6;
              border-radius: 6px; margin-bottom: 0.8rem; }
.app-header h3 { color: #fff; margin: 0; font-size: 1rem; font-weight: 500; }
.app-header p  { color: #94a3b8; margin: 0; font-size: 0.75rem; }

/* Botones chicos y discretos — anulan el estilo gigante de Streamlit */
div[data-testid="stButton"] > button {
    padding: 0.25rem 0.75rem !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    background: #334155 !important;
    color: #e2e8f0 !important;
    border: 1px solid #475569 !important;
    border-radius: 4px !important;
    min-height: 0 !important;
    height: auto !important;
    line-height: 1.4 !important;
}
div[data-testid="stButton"] > button:hover { background: #475569 !important; }

/* Botón primario (confirmar / guardar) */
div[data-testid="stButton"] > button[kind="primary"] {
    background: #2563eb !important;
    border-color: #1d4ed8 !important;
    color: #fff !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover { background: #1d4ed8 !important; }

/* Botón rojo (eliminar) */
.btn-danger div[data-testid="stButton"] > button {
    background: #7f1d1d !important;
    border-color: #991b1b !important;
    color: #fca5a5 !important;
}

/* Ocultar elementos innecesarios */
#MainMenu, footer, header { display: none !important; }

/* Inputs y selects más compactos */
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div { font-size: 0.8rem !important; padding: 0.2rem 0.5rem !important; }

/* Caja info compacta */
.msg { padding: 0.5rem 0.75rem; border-radius: 4px; font-size: 0.78rem;
       border-left: 3px solid; margin: 0.4rem 0; line-height: 1.5; }
.msg-info    { background: #1e293b; border-color: #3b82f6; color: #cbd5e1; }
.msg-success { background: #064e3b; border-color: #10b981; color: #6ee7b7; }
.msg-warning { background: #451a03; border-color: #f59e0b; color: #fcd34d; }

/* Tabla más compacta */
.stDataFrame { font-size: 0.78rem !important; }
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

# ── Utilidades de limpieza ────────────────────────────────────────────────────
def limpiar_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = re.sub(r'\s+', ' ', str(v)).strip()
    return None if s.lower() in ('', 'nan', 'none', 'null', 'nat') else s

def limpiar_cuit(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    if 'E' in s.upper():
        try:
            return str(int(float(s)))
        except Exception:
            pass
    return re.sub(r'[\.\-,\s]', '', s)

def excel_serial_fecha(n):
    try:
        return (datetime(1899, 12, 30) + pd.Timedelta(days=int(n))).strftime("%Y-%m-%d")
    except Exception:
        return None

def norm_fecha(v):
    """Cualquier formato → YYYY-MM-DD para Supabase."""
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
    if s.isdigit():
        return excel_serial_fecha(s)
    try:
        return pd.to_datetime(s, dayfirst=True).strftime('%Y-%m-%d')
    except Exception:
        return None

def fmt_fecha(v):
    """YYYY-MM-DD → DD/MM/YYYY para mostrar."""
    if not v:
        return None
    try:
        if pd.isna(v):
            return None
    except TypeError:
        pass
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

# ── Datos cacheados ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_localidades(_sb):
    r = _sb.table("padron_deuda_presunta").select("localidad").execute()
    locs = sorted({x['localidad'] for x in r.data if x.get('localidad')})
    if 'MAR DEL PLATA' in locs:
        locs.remove('MAR DEL PLATA')
        locs = ['MAR DEL PLATA'] + locs
    return locs

@st.cache_data(ttl=60)
def get_pares_existentes(_sb):
    """Trae solo CUIT + ultima_acta para deduplicar — mucho más rápido que traer todo."""
    todos, offset = [], 0
    while True:
        batch = _sb.table("padron_deuda_presunta") \
                   .select("cuit, ultima_acta") \
                   .range(offset, offset + 999).execute()
        if not batch.data:
            break
        todos.extend(batch.data)
        offset += 1000
        if len(batch.data) < 1000:
            break
    return {(str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) for r in todos if r.get('cuit')}

# ── Mapeo columnas Excel ──────────────────────────────────────────────────────
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
                v = excel_serial_fecha(v) if v.isdigit() else norm_fecha(v)
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

# ── Pestañas ──────────────────────────────────────────────────────────────────
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
    st.markdown("""<div class="msg msg-info">
    Seleccioná el Excel del padrón. El sistema filtra duplicados por <strong>CUIT + ULTIMA ACTA</strong>
    y solo inserta registros nuevos.
    </div>""", unsafe_allow_html=True)

    archivo = st.file_uploader("Archivo Excel", type=["xls","xlsx"], key="upload_padron")

    if archivo:
        st.caption(f"Archivo: **{archivo.name}**")
        try:
            registros = procesar_excel(archivo)
            hoy = date.today().isoformat()
            for r in registros:
                r.update({'leg':None,'vto':None,'mail_enviado':'NO','acta':None,
                           'fecha_carga':hoy,'estado_gestion':'PENDIENTE'})

            pares = get_pares_existentes(supabase)
            nuevos = [r for r in registros
                      if (str(r.get('cuit') or ''), str(r.get('ultima_acta') or '*')) not in pares]
            dupl   = len(registros) - len(nuevos)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total", len(registros))
            c2.metric("Nuevos", len(nuevos))
            c3.metric("Duplicados", dupl)

            if nuevos:
                with st.expander("Vista previa (10 primeros)"):
                    df_prev = pd.DataFrame(nuevos[:10])
                    for col in ['fechareldependencia','desde','hasta','fecha_pago_obl','vto','fecha_carga']:
                        if col in df_prev.columns:
                            df_prev[col] = df_prev[col].apply(fmt_fecha)
                    st.dataframe(df_prev, use_container_width=True, height=250)

                if st.button("✅ Confirmar carga", type="primary"):
                    with st.spinner("Insertando..."):
                        n = 0
                        for i in range(0, len(nuevos), 100):
                            res = supabase.table("padron_deuda_presunta").insert(nuevos[i:i+100]).execute()
                            n += len(res.data)
                    st.markdown(f'<div class="msg msg-success">✅ {n} registros insertados.</div>', unsafe_allow_html=True)
                    get_pares_existentes.clear()
                    get_localidades.clear()
            else:
                st.markdown('<div class="msg msg-warning">⚠️ No hay registros nuevos.</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(str(e))

# ══════════════════════════════════════════════════════════════════
# TAB 2 — Editar Legajos y Vtos
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Editar Legajos y Fechas de Vencimiento")

    # ── Barra de acciones compacta ────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑 Eliminar seleccionados", key="btn_del_sel"):
            ids = st.session_state.get('ids_a_eliminar', [])
            if ids:
                supabase.table("padron_deuda_presunta").delete().in_("id", ids).execute()
                st.session_state.ids_a_eliminar = []
                st.rerun()
            else:
                st.warning("Nada seleccionado.")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑 Eliminar TODO", key="btn_del_todo"):
            st.session_state.confirmar_del_todo = True
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        if st.button("↺ Resetear filtros", key="btn_reset"):
            for k in ['input_filtro_cuit','input_filtro_razon','filtro_localidad',
                      'filtro_mail','pagina_actual']:
                st.session_state.pop(k, None)
            st.rerun()
    with c4:
        if st.button("⟳ Recargar", key="btn_reload"):
            st.rerun()

    # Confirmación eliminar todo
    if st.session_state.get('confirmar_del_todo'):
        st.warning("⚠️ Esta acción eliminará **TODOS** los registros. ¿Confirmar?")
        ca, cb = st.columns(2)
        with ca:
            if st.button("Sí, eliminar todo", type="primary"):
                supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                st.session_state.confirmar_del_todo = False
                st.session_state.ids_a_eliminar = []
                st.rerun()
        with cb:
            if st.button("Cancelar"):
                st.session_state.confirmar_del_todo = False
                st.rerun()

    st.markdown("---")

    # ── Filtros en una sola fila ──────────────────────────────────
    f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
    with f1:
        filtro_cuit = st.text_input("CUIT", key="input_filtro_cuit", placeholder="Ej: 30707685243", label_visibility="collapsed")
    with f2:
        filtro_razon = st.text_input("Razón social", key="input_filtro_razon", placeholder="Razón social", label_visibility="collapsed")
    with f3:
        locs = get_localidades(supabase)
        localidad = st.selectbox("Localidad", ["TODAS"] + locs, key="filtro_localidad", label_visibility="collapsed")
    with f4:
        filtro_mail = st.selectbox("Mail", ["AMBOS","NO","SI"], key="filtro_mail", label_visibility="collapsed")

    # ── Consulta Supabase ─────────────────────────────────────────
    q = supabase.table("padron_deuda_presunta").select("*")
    if localidad != "TODAS":
        q = q.eq("localidad", localidad)
    if filtro_mail == "SI":
        q = q.eq("mail_enviado","SI")
    elif filtro_mail == "NO":
        q = q.eq("mail_enviado","NO")

    datos = q.execute()

    if not datos.data:
        st.info("Sin datos.")
    else:
        df = pd.DataFrame(datos.data)

        if filtro_cuit:
            df = df[df['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
        if filtro_razon:
            df = df[df['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]

        total = len(df)
        RPP   = 300
        pages = max(1, (total + RPP - 1) // RPP)

        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 1
        st.session_state.pagina_actual = max(1, min(st.session_state.pagina_actual, pages))

        # Paginación compacta
        pa, pn, ps = st.columns([1, 3, 1])
        with pa:
            if st.button("◀", key="btn_prev") and st.session_state.pagina_actual > 1:
                st.session_state.pagina_actual -= 1
                st.rerun()
        with pn:
            st.caption(f"Página {st.session_state.pagina_actual} / {pages}  |  {total} registros")
        with ps:
            if st.button("▶", key="btn_next") and st.session_state.pagina_actual < pages:
                st.session_state.pagina_actual += 1
                st.rerun()

        off = (st.session_state.pagina_actual - 1) * RPP
        df_p = df.iloc[off:off+RPP].reset_index(drop=True).copy()

        # Formatear para mostrar
        for col in ['empl_10_2025','emp_11_2025','empl_12_2025']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(limpiar_entero)
        for col in ['fechareldependencia','desde','hasta','fecha_pago_obl','vto','fecha_carga']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(fmt_fecha)

        df_orig = df_p.copy()
        df_ed   = df_p.drop(columns=['fecha_carga'], errors='ignore').rename(columns=TITULOS)
        df_ed.insert(0, "🗑️", False)

        sel_todos = st.checkbox("Seleccionar todos (página actual)", key="sel_todos")
        if sel_todos:
            df_ed["🗑️"] = True

        edited = st.data_editor(
            df_ed, use_container_width=True, height=550,
            column_config={"🗑️": st.column_config.CheckboxColumn("Elim.", help="Marcar para eliminar")},
            disabled=COLS_DISABLED,
            key=f"editor_{st.session_state.pagina_actual}",
        )

        ids_sel = edited[edited["🗑️"]]["ID"].tolist() if "ID" in edited.columns else []
        st.session_state.ids_a_eliminar = ids_sel
        if ids_sel:
            st.caption(f"📌 {len(ids_sel)} seleccionado(s) para eliminar.")

        st.markdown("---")

        if st.button("💾 Guardar cambios", type="primary", key="btn_save"):
            inverso = {v: k for k, v in TITULOS.items()}
            mods = 0
            with st.spinner("Guardando..."):
                for idx, row in edited.iterrows():
                    if idx >= len(df_orig):
                        continue
                    orig = df_orig.iloc[idx]
                    upd  = {}

                    # LEG
                    nv = row.get('LEG'); ov = orig.get('leg')
                    nv = None if pd.isna(nv) or nv == '' else nv
                    ov = None if pd.isna(ov) or ov == '' else ov
                    if nv != ov: upd['leg'] = nv

                    # VTO
                    nv = row.get('VTO'); ov = orig.get('vto')
                    nv = None if pd.isna(nv) or nv == '' else norm_fecha(nv)
                    ov = None if pd.isna(ov) or ov == '' else ov
                    if nv != ov: upd['vto'] = nv

                    # MAIL ENVIADO
                    nv = row.get('MAIL ENVIADO') or 'NO'
                    if nv not in ('SI','NO'): nv = 'NO'
                    if nv != orig.get('mail_enviado'): upd['mail_enviado'] = nv

                    # ACTA
                    nv = row.get('ACTA'); ov = orig.get('acta')
                    nv = None if pd.isna(nv) or nv == '' else nv
                    ov = None if pd.isna(ov) or ov == '' else ov
                    if nv != ov: upd['acta'] = nv

                    # ESTADO GESTION
                    nv = row.get('ESTADO GESTION') or 'PENDIENTE'
                    if nv != orig.get('estado_gestion'): upd['estado_gestion'] = nv

                    if upd:
                        supabase.table("padron_deuda_presunta").update(upd).eq("id", row['ID']).execute()
                        mods += 1

            if mods:
                st.markdown(f'<div class="msg msg-success">✅ {mods} registros actualizados.</div>', unsafe_allow_html=True)
                st.rerun()
            else:
                st.info("Sin cambios detectados.")

# ══════════════════════════════════════════════════════════════════
# TAB 3 — Solicitar Actas
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### Solicitar Actas a Central")
    st.markdown("""<div class="msg msg-info">
    Muestra empresas con <strong>LEG + VTO asignados</strong> y <strong>MAIL ENVIADO = NO</strong>.
    Al confirmar se registra la solicitud.
    </div>""", unsafe_allow_html=True)

    try:
        datos3 = (supabase.table("padron_deuda_presunta")
                  .select("id,cuit,razon_social,leg,vto,mail_enviado,estado_gestion")
                  .eq("mail_enviado","NO")
                  .not_.is_("leg","null")
                  .not_.is_("vto","null")
                  .execute())

        if datos3.data:
            df3 = pd.DataFrame(datos3.data)
            st.caption(f"📧 {len(df3)} empresas listas para solicitar actas.")
            dm = df3[['cuit','razon_social','leg','vto']].copy()
            dm['vto'] = dm['vto'].apply(fmt_fecha)
            st.dataframe(dm, use_container_width=True, height=400)

            if st.button("📧 Confirmar solicitud", type="primary"):
                with st.spinner("Actualizando..."):
                    for _, r in df3.iterrows():
                        supabase.table("padron_deuda_presunta") \
                            .update({"mail_enviado":"SI","estado_gestion":"ACTA_SOLICITADA"}) \
                            .eq("id", r['id']).execute()
                st.markdown(f'<div class="msg msg-success">✅ Solicitud registrada para {len(df3)} empresas.</div>', unsafe_allow_html=True)
        else:
            st.info("No hay registros listos.")
    except Exception as e:
        st.error(str(e))

# ══════════════════════════════════════════════════════════════════
# TAB 4 — Subir Actas
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### Subir Archivo de Actas (CSV)")
    st.markdown("""<div class="msg msg-info">
    El sistema busca coincidencias por <strong>CUIT + LEGAJO + FECHA VTO</strong>
    en registros con <strong>MAIL ENVIADO = SI</strong> y actualiza el estado.
    </div>""", unsafe_allow_html=True)

    csv_file = st.file_uploader("Archivo CSV", type=["csv"], key="upload_actas")

    if csv_file:
        st.caption(f"Archivo: **{csv_file.name}**")

        # Vista previa
        try:
            df_prev4 = pd.read_csv(io.BytesIO(csv_file.getvalue()), sep=';', dtype=str, encoding='utf-8-sig')
            with st.expander("Vista previa (5 primeras filas)"):
                st.dataframe(df_prev4.head(5), use_container_width=True, height=200)
        except Exception:
            pass

        if st.button("📋 Procesar y actualizar actas", type="primary"):
            with st.spinner("Procesando..."):
                try:
                    df4 = pd.read_csv(io.BytesIO(csv_file.getvalue()), sep=';', dtype=str, encoding='utf-8-sig')
                except Exception:
                    df4 = pd.read_csv(io.BytesIO(csv_file.getvalue()), sep=';', dtype=str, encoding='latin-1')

                df4.columns = [str(c).strip().upper() for c in df4.columns]

                # Detectar columnas flexiblemente
                col_cuit = col_leg = col_vto = col_acta = None
                for c in df4.columns:
                    cu = c.upper()
                    if 'CUIT' in cu and not col_cuit:         col_cuit = c
                    if ('LEG' in cu or 'LEGAJO' in cu) and not col_leg: col_leg = c
                    if ('VTO' in cu or 'FECHA_VTO' in cu) and not col_vto: col_vto = c
                    if ('NRO_ACTA' in cu or cu == 'ACTA') and not col_acta: col_acta = c

                if not all([col_cuit, col_leg, col_vto]):
                    st.error(f"Columnas no detectadas — CUIT: {col_cuit}, LEG: {col_leg}, VTO: {col_vto}")
                else:
                    st.caption(f"Columnas: CUIT=`{col_cuit}` · LEG=`{col_leg}` · VTO=`{col_vto}`")
                    actualizados = no_enc = 0
                    bar = st.progress(0)

                    for i, row in df4.iterrows():
                        cuit = limpiar_cuit(row[col_cuit])
                        leg  = limpiar_str(row[col_leg])
                        vto  = norm_fecha(row[col_vto])
                        acta = str(row[col_acta]) if col_acta and pd.notna(row.get(col_acta)) else "ACTUALIZADO"

                        if cuit and leg and vto:
                            try:
                                res = (supabase.table("padron_deuda_presunta")
                                       .select("id")
                                       .eq("cuit", cuit)
                                       .eq("leg",  leg)
                                       .eq("vto",  vto)
                                       .eq("mail_enviado","SI")
                                       .execute())
                                if res.data:
                                    for reg in res.data:
                                        supabase.table("padron_deuda_presunta") \
                                            .update({"acta": acta, "estado_gestion":"FINALIZADO"}) \
                                            .eq("id", reg['id']).execute()
                                    actualizados += len(res.data)
                                else:
                                    no_enc += 1
                            except Exception as e:
                                st.error(f"Error fila {i}: {e}")

                        bar.progress((i + 1) / len(df4))

                    bar.empty()
                    ca4, cb4 = st.columns(2)
                    ca4.metric("✅ Actualizados", actualizados)
                    cb4.metric("❌ No encontrados", no_enc)

                    if no_enc:
                        st.markdown(f'<div class="msg msg-warning">⚠️ {no_enc} filas sin coincidencia. '
                                     'Verificá que CUIT/LEG/VTO coincidan exactamente con lo guardado.</div>',
                                     unsafe_allow_html=True)
