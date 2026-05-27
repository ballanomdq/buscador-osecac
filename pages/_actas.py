with tab2:
    st.markdown("#### Gestionar Legajos y Fechas de Vencimiento")

    stats = get_dashboard_stats()

    total_general       = stats.get('total', 0) or 0
    con_legajo          = stats.get('con_legajo', 0) or 0
    sin_legajo_total    = total_general - con_legajo
    pendientes_sin_mail = stats.get('sin_mail', 0) or 0
    pendientes_con_mail = stats.get('con_mail', 0) or 0
    finalizados         = stats.get('finalizados', 0) or 0
    por_inspector       = stats.get('por_inspector') or {}

    with st.expander("📊 CONTEO DE REGISTROS", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="kpi-card kpi-total"><div class="kpi-icon">📊</div><h1>{total_general:,}</h1><p>TOTAL REGISTROS</p></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="kpi-card kpi-con-legajo"><div class="kpi-icon">✅</div><h1>{con_legajo:,}</h1><p>CON LEGAJO</p></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="kpi-card kpi-sin-legajo"><div class="kpi-icon">⚠️</div><h1>{sin_legajo_total:,}</h1><p>SIN LEGAJO</p></div>""", unsafe_allow_html=True)

    with st.expander("🔄 ESTADO DE REGISTROS", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="kpi-card kpi-pendiente"><div class="kpi-icon">📧</div><h1>{pendientes_sin_mail:,}</h1><p>PENDIENTES (sin mail)</p></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="kpi-card kpi-mail"><div class="kpi-icon">📨</div><h1>{pendientes_con_mail:,}</h1><p>MAIL ENVIADO</p></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="kpi-card kpi-finalizado"><div class="kpi-icon">🏁</div><h1>{finalizados:,}</h1><p>FINALIZADOS</p></div>""", unsafe_allow_html=True)

    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if inspectores.data:
        with st.expander("👥 EMPRESAS POR INSPECTOR", expanded=False):
            cols = st.columns(len(inspectores.data))
            for idx, ins in enumerate(inspectores.data):
                count = por_inspector.get(str(ins['legajo']), 0)
                nombre_corto = ins['nombre'].split(',')[0]
                with cols[idx]:
                    st.markdown(f"""<div class="inspector-card"><h3>{nombre_corto}</h3><h1>{count}</h1><p>Legajo: {ins['legajo']}</p></div>""", unsafe_allow_html=True)

    st.divider()

    col_guardar, col_elim_sel, col_elim_todo, col_asignar, col_preparar_mails, col_inf_no, col_inf_si, col_inf_insp, col_reset, col_recargar = st.columns(10)
    
    with col_guardar:
        guardar_click = st.button("💾 GUARDAR CAMBIOS", type="secondary", use_container_width=True)
    with col_elim_sel:
        if st.button("🗑 Eliminar sel.", use_container_width=True):
            ids = st.session_state.get('ids_a_eliminar', [])
            if ids:
                supabase.table("padron_deuda_presunta").delete().in_("id", ids).execute()
                st.session_state.ids_a_eliminar = []
                get_dashboard_stats.clear()
                st.rerun()
    with col_elim_todo:
        if st.button("🗑 Eliminar TODO", use_container_width=True):
            st.session_state.confirmar_del_todo = True
    with col_asignar:
        if st.button("🤖 Asignar Legajos", use_container_width=True):
            st.session_state.asignar_legajos = True
    with col_preparar_mails:
        if st.button("📧 PREPARAR MAILS", use_container_width=True):
            st.session_state.preparar_mails = True
    with col_inf_no:
        if st.button("📄 Inf. NO asig.", use_container_width=True):
            st.session_state.generar_informe = True
    with col_inf_si:
        if st.button("📊 Inf. ASIGNADOS", use_container_width=True):
            st.session_state.generar_informe_asignados = True
    with col_inf_insp:
        if st.button("📊 Inf. POR INSPECTOR", use_container_width=True):
            st.session_state.generar_informe_por_inspector = True
    with col_reset:
        if st.button("↺ Resetear filtros", use_container_width=True):
            for k in ['input_filtro_cuit','input_filtro_razon','filtro_localidad', 'filtro_mail','filtro_leg','filtro_calle_aproximacion','pagina_actual','filtro_estado']:
                st.session_state.pop(k, None)
            st.rerun()
    with col_recargar:
        if st.button("⟳ Recargar", use_container_width=True):
            st.session_state.ultima_recarga = datetime.now()
            st.session_state.pop('pagina_actual', None)
            get_dashboard_stats.clear()
            st.rerun()

    st.markdown("---")
    col_elim_cancel1, col_elim_cancel2, col_elim_cancel3 = st.columns([1, 2, 1])
    with col_elim_cancel2:
        if st.button("🗑️ EMPAQUETAR Y ELIMINAR REGISTROS CON DEUDA CANCELADA", type="primary", use_container_width=True):
            resultado = eliminar_registros_cancelados()
            if resultado:
                excel_data, cantidad = resultado
                st.success(f"✅ {cantidad} registros eliminados. Descargando backup...")
                st.download_button(
                    label="📥 DESCARGAR BACKUP (Excel)",
                    data=excel_data,
                    file_name=f"BACKUP_DEUDA_CANCELADA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                get_dashboard_stats.clear()
                time.sleep(1)
                st.rerun()

    if st.session_state.get('confirmar_del_todo'):
        st.warning("⚠️ Esta acción eliminará **TODOS** los registros.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("Sí, eliminar todo"):
                supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                st.session_state.confirmar_del_todo = False
                get_dashboard_stats.clear()
                st.rerun()
        with col_no:
            if st.button("Cancelar"):
                st.session_state.confirmar_del_todo = False
                st.rerun()

    # ── DIÁLOGO PREPARAR MAILS (sin cambios) ─────────────────────────────────
    if st.session_state.get('preparar_mails'):
        @st.dialog("📧 PREPARAR MAILS")
        def mostrar_dialogo_preparar_mails():
            # ... (todo el contenido del diálogo se mantiene igual, no lo copio para no alargar, pero va igual que antes)
            pass
        mostrar_dialogo_preparar_mails()

    if st.session_state.get("excel_descarga"):
        st.success("🎉 ¡Mailing generado exitosamente! Descargue el archivo:")
        col_desc1, col_desc2, col_desc3 = st.columns([1, 2, 1])
        with col_desc2:
            st.download_button(label="📥 DESCARGAR EXCEL", data=st.session_state.excel_descarga, file_name=st.session_state.nombre_excel, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
            if st.button("✅ FINALIZAR", use_container_width=True):
                del st.session_state["excel_descarga"]
                del st.session_state["nombre_excel"]
                st.rerun()

    if st.session_state.get('generar_informe'):
        with st.spinner("Generando informe..."):
            registros_sin_legajo = traer_registros_sin_legajo()
            if registros_sin_legajo:
                contenido_txt = generar_informe_txt(registros_sin_legajo)
                st.download_button(label="📥 DESCARGAR TXT", data=contenido_txt.encode('utf-8'), file_name=f"INFORME_NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain")
                st.info(f"📊 {len(registros_sin_legajo)} registros sin legajo")
            else:
                st.success("✅ No hay registros sin legajo")
        st.session_state.generar_informe = False

    if st.session_state.get('generar_informe_asignados'):
        with st.spinner("Generando informe..."):
            registros_con_legajo = traer_registros_con_legajo()
            if registros_con_legajo:
                excel_data = generar_excel_asignados(registros_con_legajo)
                st.download_button(label="📥 DESCARGAR EXCEL (TODOS)", data=excel_data, file_name=f"INFORME_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                st.info(f"📊 {len(registros_con_legajo)} registros con legajo")
            else:
                st.success("✅ No hay registros con legajo")
        st.session_state.generar_informe_asignados = False

    if st.session_state.get('generar_informe_por_inspector'):
        with st.spinner("Generando informe por inspector..."):
            excel_data = generar_excel_por_inspector()
            st.download_button(label="📥 DESCARGAR EXCEL (POR INSPECTOR)", data=excel_data, file_name=f"INFORME_POR_INSPECTOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.success("✅ Informe generado - Una hoja por inspector")
        st.session_state.generar_informe_por_inspector = False

    if st.session_state.get('asignar_legajos'):
        st.info("⏳ Asignando legajos...")
        with st.spinner("Cargando configuración..."):
            insp_loc = cargar_inspectores_localidad()
            insp_zonas = cargar_zonas_inspectores()
            sinonimos = cargar_sinonimos()
            palabras_ancla = cargar_palabras_ancla()
            lkp_loc = construir_lookup_localidades(insp_loc)
            lkp_zonas = construir_lookup_zonas(insp_zonas)
            lkp_sin = construir_lookup_sinonimos(sinonimos)
            lkp_palabras = construir_lookup_palabras_ancla(palabras_ancla)
        with st.spinner("Cargando registros..."):
            registros = traer_registros_sin_legajo()
        if not registros:
            st.info("No hay registros sin legajo.")
            st.session_state.asignar_legajos = False
        else:
            total = len(registros)
            progress_bar = st.progress(0)
            status_text = st.empty()
            asig = []
            no_asig = []
            for i, reg in enumerate(registros):
                percent = (i + 1) / total
                progress_bar.progress(percent)
                status_text.markdown(f"🔄 {int(percent * 100)}% - {reg.get('razon_social', 'Sin nombre')[:40]}...")
                legajo = asignar_legajo(reg.get('localidad', '') or '', reg.get('calle', '') or '', reg.get('numero', '') or '', lkp_loc, lkp_zonas, lkp_sin, lkp_palabras)
                if legajo:
                    asig.append({'id': reg['id'], 'legajo': legajo})
                else:
                    no_asig.append({'id': reg['id'], 'localidad': reg.get('localidad', ''), 'calle': reg.get('calle', ''), 'numero': reg.get('numero', ''), 'razon_social': reg.get('razon_social', ''), 'cuit': reg.get('cuit', ''), 'tel_dom_legal': reg.get('tel_dom_legal', ''), 'tel_dom_real': reg.get('tel_dom_real', '')})
                time.sleep(0.01)
            progress_bar.empty()
            status_text.empty()
            with st.spinner("Guardando..."):
                guardados = guardar_legajos_en_batch(asig)
            st.session_state.asignar_legajos = False
            st.session_state.ultima_asignacion = {"asignados": guardados, "no_asignados": len(no_asig), "detalle": no_asig}
            get_dashboard_stats.clear()
            st.success(f"✅ {guardados} legajos asignados, {len(no_asig)} sin coincidencia.")
            st.rerun()

    if st.session_state.get('ultima_asignacion'):
        res = st.session_state.ultima_asignacion
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.success(f"✅ {res['asignados']} legajos asignados")
        with col_res2:
            st.warning(f"⚠️ {res['no_asignados']} sin coincidencia")
        if res['no_asignados'] > 0:
            contenido_informe = generar_informe_txt(res['detalle'])
            st.download_button(label="📥 DESCARGAR INFORME", data=contenido_informe.encode('utf-8'), file_name=f"NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain")
            with st.expander(f"📋 Ver {res['no_asignados']} registros"):
                st.dataframe(pd.DataFrame(res['detalle']), use_container_width=True)
        if st.button("Cerrar resultado"):
            del st.session_state.ultima_asignacion
            st.rerun()

    # ── FILTROS Y TABLA EDITABLE (con el nuevo filtro de estado) ──
    st.markdown("### 🔎 Filtros de búsqueda")
    
    if 'ultima_recarga' not in st.session_state:
        st.session_state.ultima_recarga = datetime.now()
    
    # Inicializar filtro de estado si no existe
    if 'filtro_estado' not in st.session_state:
        st.session_state.filtro_estado = "AMBOS"
    
    col_f1, col_f2, col_f3, col_f4, col_f5, col_f6 = st.columns(6)
    with col_f1:
        st.markdown('<p class="filtro-titulo">📍 LOCALIDAD</p>', unsafe_allow_html=True)
        locs = get_localidades()
        localidad = st.selectbox("Localidad", ["TODAS"] + locs, key="filtro_localidad", label_visibility="collapsed")
    with col_f2:
        st.markdown('<p class="filtro-titulo">✉️ MAIL</p>', unsafe_allow_html=True)
        filtro_mail = st.selectbox("Mail", ["AMBOS", "NO", "SI"], key="filtro_mail", label_visibility="collapsed")
    with col_f3:
        st.markdown('<p class="filtro-titulo">🆔 LEGAJO</p>', unsafe_allow_html=True)
        filtro_leg = st.selectbox("Legajo", ["TODOS", "CON LEGAJO", "SIN LEGAJO"], key="filtro_leg", label_visibility="collapsed")
    with col_f4:
        st.markdown('<p class="filtro-titulo">🔢 CUIT</p>', unsafe_allow_html=True)
        filtro_cuit_temp = st.text_input("CUIT", key="filtro_cuit_temp", placeholder="Ej: 30707685243", label_visibility="collapsed")
    with col_f5:
        st.markdown('<p class="filtro-titulo">🏢 RAZÓN SOCIAL</p>', unsafe_allow_html=True)
        filtro_razon_temp = st.text_input("Razón Social", key="filtro_razon_temp", placeholder="Razón social", label_visibility="collapsed")
    with col_f6:
        st.markdown('<p class="filtro-titulo">📌 ESTADO GESTIÓN</p>', unsafe_allow_html=True)
        filtro_estado_temp = st.selectbox("Estado Gestión", ["AMBOS", "PENDIENTE", "FINALIZADO"], key="filtro_estado_temp", label_visibility="collapsed")
    
    col_f7, col_f8 = st.columns([3, 1])
    with col_f7:
        st.markdown('<p class="filtro-titulo">🏠 CALLE</p>', unsafe_allow_html=True)
        filtro_calle_temp = st.text_input("Calle", key="filtro_calle_temp", placeholder="Ej: Yrigoyen", label_visibility="collapsed")
    with col_f8:
        st.markdown('<div class="buscar-btn" style="margin-top: 18px;">', unsafe_allow_html=True)
        buscar_click = st.button("🔍 BUSCAR", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if 'filtro_cuit' not in st.session_state:
        st.session_state.filtro_cuit = ""
    if 'filtro_razon' not in st.session_state:
        st.session_state.filtro_razon = ""
    if 'filtro_calle' not in st.session_state:
        st.session_state.filtro_calle = ""
    
    if buscar_click:
        st.session_state.filtro_cuit = filtro_cuit_temp
        st.session_state.filtro_razon = filtro_razon_temp
        st.session_state.filtro_calle = filtro_calle_temp
        st.session_state.filtro_estado = filtro_estado_temp
        st.session_state.pagina_actual = 1
        st.rerun()
    
    filtro_cuit = st.session_state.filtro_cuit
    filtro_razon = st.session_state.filtro_razon
    filtro_calle_aprox = st.session_state.filtro_calle
    filtro_estado = st.session_state.filtro_estado
    
    if filtro_cuit or filtro_razon or filtro_calle_aprox or filtro_estado != "AMBOS":
        st.caption(f"🔍 Búsqueda activa - CUIT: {filtro_cuit or 'todo'} | Razón Social: {filtro_razon or 'todo'} | Calle: {filtro_calle_aprox or 'todo'} | Estado: {filtro_estado}")

    q = supabase.table("padron_deuda_presunta").select("*")
    if localidad != "TODAS":
        q = q.eq("localidad", localidad)
    if filtro_mail == "SI":
        q = q.eq("mail_enviado", "SI")
    elif filtro_mail == "NO":
        q = q.eq("mail_enviado", "NO")
    if filtro_leg == "CON LEGAJO":
        q = q.not_.is_("leg", "null")
    elif filtro_leg == "SIN LEGAJO":
        q = q.is_("leg", "null")
    if filtro_estado != "AMBOS":
        q = q.eq("estado_gestion", filtro_estado)
    
    with st.spinner("Consultando base de datos..."):
        datos = q.execute()
    
    df = pd.DataFrame(datos.data) if datos.data else pd.DataFrame()
    
    if not df.empty and filtro_cuit:
        df = df[df['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
    if not df.empty and filtro_razon:
        df = df[df['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
    if not df.empty and filtro_calle_aprox:
        filtro_norm = normalizar_calle(filtro_calle_aprox)
        if filtro_norm:
            df['calle_norm'] = df['calle'].apply(lambda x: normalizar_calle(str(x)) if x else "")
            df['similitud'] = df['calle_norm'].apply(lambda x: difflib.SequenceMatcher(None, filtro_norm, x).ratio() if x else 0)
            df = df[df['similitud'] > 0.4].sort_values('similitud', ascending=False)
            df = df.drop(columns=['calle_norm', 'similitud'])

    total_en_tabla = len(df)
    RPP = 200
    pages = max(1, (total_en_tabla + RPP - 1) // RPP)

    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 1
    st.session_state.pagina_actual = max(1, min(st.session_state.pagina_actual, pages))

    col_pag1, col_pag2, col_pag3 = st.columns([1, 3, 1])
    with col_pag1:
        if st.button("◀ Anterior", disabled=st.session_state.pagina_actual <= 1):
            st.session_state.pagina_actual -= 1
            st.rerun()
    with col_pag2:
        st.caption(f"Página {st.session_state.pagina_actual} de {pages} | Total en tabla: {total_en_tabla} registros")
    with col_pag3:
        if st.button("Siguiente ▶", disabled=st.session_state.pagina_actual >= pages):
            st.session_state.pagina_actual += 1
            st.rerun()

    if df.empty:
        st.info("No hay registros que coincidan con los filtros seleccionados.")
    else:
        off = (st.session_state.pagina_actual - 1) * RPP
        df_p = df.iloc[off:off+RPP].reset_index(drop=True).copy()
        for col in df_p.columns:
            df_p[col] = df_p[col].apply(lambda x: "" if pd.isna(x) else str(x))
        for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(lambda x: fmt_fecha(x) if x and x != "" else "")
        df_orig = df_p.copy()
        df_ed = df_p.rename(columns={
            'id':'ID', 'delegacion':'DELEGACION', 'localidad':'LOCALIDAD', 'cuit':'CUIT',
            'razon_social':'RAZON SOCIAL', 'deuda_presunta':'DEUDA PRESUNTA', 'cp':'CP',
            'calle':'CALLE', 'numero':'NUMERO', 'piso':'PISO', 'dpto':'DPTO',
            'fechareldependencia':'FECHARELDEPENDENCIA', 'email':'EMAIL',
            'tel_dom_legal':'TEL_DOM_LEGAL', 'tel_dom_real':'TEL_DOM_REAL',
            'ultima_acta':'ULTIMA ACTA', 'desde':'DESDE', 'hasta':'HASTA',
            'detectado':'DETECTADO', 'estado':'ESTADO', 'fecha_pago_obl':'FECHA PAGO OBL',
            'empl_10_2025':'EMPL 10-2025', 'emp_11_2025':'EMP 11-2025', 'empl_12_2025':'EMPL 12-2025',
            'actividad':'ACTIVIDAD', 'situacion':'SITUACION',
            'leg':'LEG', 'vto':'VTO', 'mail_enviado':'MAIL ENVIADO',
            'acta':'ACTA', 'estado_gestion':'ESTADO GESTION', 'deuda_cancelada':'CANCELAR',
        })
        df_ed.insert(0, "🗑️", False)
        if st.checkbox("Seleccionar todos los de esta página"):
            df_ed["🗑️"] = True
        editor_key = f"editor_{st.session_state.pagina_actual}_{st.session_state.ultima_recarga.timestamp()}"
        edited = st.data_editor(df_ed, use_container_width=True, height=500, column_config={"🗑️": st.column_config.CheckboxColumn("Eliminar"), "CANCELAR": st.column_config.CheckboxColumn("Cancelar Deuda")}, key=editor_key)
        ids_sel = edited[edited["🗑️"]]["ID"].tolist() if "ID" in edited.columns else []
        st.session_state.ids_a_eliminar = ids_sel
        if ids_sel:
            st.info(f"📌 {len(ids_sel)} registro(s) seleccionado(s) para eliminar")
        if guardar_click:
            mods = 0
            errores_fecha = 0
            with st.spinner("Guardando cambios en Supabase..."):
                for idx, row in edited.iterrows():
                    if idx >= len(df_orig):
                        continue
                    orig = df_orig.iloc[idx]
                    upd = {}
                    
                    id_valor = row.get('ID')
                    if pd.isna(id_valor) or id_valor is None or str(id_valor).strip() == '':
                        continue
                    
                    for col_edit, col_orig in [
                        ('LEG', 'leg'), ('VTO', 'vto'), ('MAIL ENVIADO', 'mail_enviado'),
                        ('ACTA', 'acta'), ('ESTADO GESTION', 'estado_gestion'),
                        ('LOCALIDAD', 'localidad'), ('RAZON SOCIAL', 'razon_social'),
                        ('CUIT', 'cuit'), ('CALLE', 'calle'), ('NUMERO', 'numero'),
                        ('DEUDA PRESUNTA', 'deuda_presunta'), ('DESDE', 'desde'), ('HASTA', 'hasta'),
                        ('CANCELAR', 'deuda_cancelada')
                    ]:
                        nv = row.get(col_edit)
                        if nv is None or (isinstance(nv, float) and pd.isna(nv)) or (isinstance(nv, str) and nv.strip() == ''):
                            nv = None
                        elif isinstance(nv, str):
                            nv = nv.strip()
                        
                        if nv != orig.get(col_orig):
                            if col_orig == 'vto' and nv:
                                fecha_ok = norm_fecha(str(nv))
                                if fecha_ok:
                                    upd[col_orig] = fecha_ok
                                else:
                                    errores_fecha += 1
                            elif col_orig == 'leg' and nv:
                                try:
                                    upd[col_orig] = int(float(str(nv)))
                                except:
                                    upd[col_orig] = None
                            else:
                                upd[col_orig] = nv
                    
                    if upd:
                        try:
                            supabase.table("padron_deuda_presunta").update(upd).eq("id", int(id_valor)).execute()
                            mods += 1
                        except Exception as e:
                            st.error(f"Error actualizando registro ID {id_valor}: {e}")
            if mods > 0:
                st.success(f"✅ ¡{mods} registros actualizados correctamente!")
                if errores_fecha > 0:
                    st.warning(f"⚠️ {errores_fecha} fecha(s) no se pudieron guardar (formato incorrecto). Usá DD/MM/YYYY.")
                get_dashboard_stats.clear()
                st.session_state.ultima_recarga = datetime.now()
                st.rerun()
            elif errores_fecha > 0:
                st.warning(f"No se guardaron cambios. {errores_fecha} fecha(s) con formato incorrecto.")
            else:
                st.info("No se detectaron cambios para guardar.")
