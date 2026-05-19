with tab2:
    st.markdown("#### Editar Legajos y Fechas de Vencimiento")

    total_general = supabase.table("padron_deuda_presunta").select("id", count="exact").execute().count
    con_legajo    = supabase.table("padron_deuda_presunta").select("id", count="exact").not_.is_("leg", "null").execute().count
    sin_legajo_total = total_general - con_legajo

    # Tarjetas con texto a tope
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown(f"""
        <div class="big-number">
            <h1>{total_general:,}</h1>
            <p>TOTAL REGISTROS</p>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"""
        <div class="big-number">
            <h1>{con_legajo:,}</h1>
            <p>CON LEGAJO</p>
        </div>
        """, unsafe_allow_html=True)
    with col_t3:
        st.markdown(f"""
        <div class="big-number">
            <h1>{sin_legajo_total:,}</h1>
            <p>SIN LEGAJO</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Tarjetas de inspectores con texto a tope
    inspectores = supabase.table("inspectores").select("*").order("legajo").execute()
    if inspectores.data:
        cols_inspectores = st.columns(len(inspectores.data))
        for idx, ins in enumerate(inspectores.data):
            count = supabase.table("padron_deuda_presunta").select("id", count="exact").eq("leg", ins['legajo']).execute().count
            nombre_corto = ins['nombre'].split(',')[0]
            with cols_inspectores[idx]:
                st.markdown(f"""
                <div class="inspector-card">
                    <h3>{nombre_corto}</h3>
                    <h1>{count}</h1>
                    <p>Legajo: {ins['legajo']}</p>
                </div>
                """, unsafe_allow_html=True)
    st.markdown("---")

    col_guardar, col_elim_sel, col_elim_todo, col_asignar, col_preparar_mails, col_inf_no, col_inf_si, col_inf_insp, col_reset, col_recargar = st.columns(10)
    
    with col_guardar:
        guardar_click = st.button("💾 GUARDAR CAMBIOS", type="secondary", use_container_width=True)
    with col_elim_sel:
        if st.button("🗑 Eliminar sel.", use_container_width=True):
            ids = st.session_state.get('ids_a_eliminar', [])
            if ids:
                supabase.table("padron_deuda_presunta").delete().in_("id", ids).execute()
                st.session_state.ids_a_eliminar = []
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
            for k in ['input_filtro_cuit','input_filtro_razon','filtro_localidad',
                      'filtro_mail','filtro_leg','filtro_calle_aproximacion','pagina_actual']:
                st.session_state.pop(k, None)
            st.rerun()
    with col_recargar:
        # BOTÓN RECARGAR MEJORADO: fuerza actualización completa
        if st.button("⟳ Recargar", use_container_width=True):
            # Forzar recreación completa
            st.session_state.ultima_recarga = datetime.now()
            st.session_state.pop('pagina_actual', None)
            # Limpiar cualquier caché de consultas
            st.cache_data.clear()
            st.rerun()

    if st.session_state.get('confirmar_del_todo'):
        st.warning("⚠️ Esta acción eliminará **TODOS** los registros.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("Sí, eliminar todo"):
                supabase.table("padron_deuda_presunta").delete().neq("id", 0).execute()
                st.session_state.confirmar_del_todo = False
                st.rerun()
        with col_no:
            if st.button("Cancelar"):
                st.session_state.confirmar_del_todo = False
                st.rerun()

    # ── DIÁLOGO FLOTANTE DE PREPARAR MAILS ─────────────────────────────────
    if st.session_state.get('preparar_mails'):
        @st.dialog("📧 PREPARAR MAILS")
        def mostrar_dialogo_preparar_mails():
            query = supabase.table("padron_deuda_presunta")\
                .select("*")\
                .not_.is_("leg", "null")\
                .eq("mail_enviado", "NO")\
                .is_("vto", "null")\
                .execute()
            
            df_candidatos = pd.DataFrame(query.data) if query.data else pd.DataFrame()
            
            if df_candidatos.empty:
                st.warning("No hay registros disponibles")
                if st.button("Finalizar"):
                    st.session_state.preparar_mails = False
                    st.rerun()
                return
            
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                localidades = ["TODAS"] + sorted(df_candidatos['localidad'].unique().tolist())
                localidad_filtro = st.selectbox("Localidad", localidades, key="dialog_localidad")
                usar_todos = st.checkbox("Seleccionar TODOS", value=True, key="dialog_usar_todos")
                cantidad_personalizada = None
                if not usar_todos:
                    cantidad_personalizada = st.number_input("Cantidad", min_value=1, max_value=len(df_candidatos), value=100, step=1, key="dialog_cantidad")
            
            with col_f2:
                nueva_fecha_vto = st.date_input("Fecha VTO", value=date.today(), key="dialog_fecha")
                ordenar_deuda = st.checkbox("Ordenar por DEUDA (mayor a menor)", value=True, key="dialog_deuda")
                ordenar_hasta = st.checkbox("Ordenar por HASTA (más antiguo)", value=False, key="dialog_hasta")
            
            df_filtrado = df_candidatos.copy()
            if localidad_filtro != "TODAS":
                df_filtrado = df_filtrado[df_filtrado['localidad'] == localidad_filtro]
            
            if ordenar_deuda or ordenar_hasta:
                def parse_deuda(val):
                    if val is None:
                        return 0
                    try:
                        if isinstance(val, str):
                            val = val.replace('$', '').replace('.', '').replace(',', '.').strip()
                        return float(val)
                    except:
                        return 0
                
                def parse_hasta(val):
                    if val is None:
                        return datetime.max
                    try:
                        if isinstance(val, str):
                            if '/' in val:
                                return datetime.strptime(val, '%d/%m/%Y')
                            if '-' in val:
                                return datetime.strptime(val, '%Y-%m-%d')
                        return val
                    except:
                        return datetime.max
                
                if ordenar_deuda:
                    df_filtrado['_deuda_num'] = df_filtrado['deuda_presunta'].apply(parse_deuda)
                    df_filtrado = df_filtrado.sort_values('_deuda_num', ascending=False)
                if ordenar_hasta:
                    df_filtrado['_hasta_date'] = df_filtrado['hasta'].apply(parse_hasta)
                    df_filtrado = df_filtrado.sort_values('_hasta_date', ascending=True)
                df_filtrado = df_filtrado.drop(columns=[c for c in ['_deuda_num', '_hasta_date'] if c in df_filtrado.columns])
            
            if usar_todos:
                df_seleccionado = df_filtrado.copy()
            else:
                df_seleccionado = df_filtrado.head(int(cantidad_personalizada))
            
            if st.button("✅ PROCESAR Y DESCARGAR", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                
                fecha_str = nueva_fecha_vto.strftime('%Y-%m-%d')
                fecha_mostrar = nueva_fecha_vto.strftime('%d/%m/%Y')
                total_registros = len(df_seleccionado)
                
                batch_size = 50
                for i in range(0, total_registros, batch_size):
                    batch = df_seleccionado.iloc[i:i+batch_size]
                    for _, row in batch.iterrows():
                        supabase.table("padron_deuda_presunta").update({
                            "vto": fecha_str,
                            "mail_enviado": "SI"
                        }).eq("id", row['id']).execute()
                    
                    progress_bar.progress(min((i + batch_size) / total_registros, 1.0))
                    time.sleep(0.05)
                
                progress_bar.progress(1.0)
                
                excel_data = generar_excel_para_mailing(df_seleccionado, fecha_mostrar)
                st.session_state.excel_descarga = excel_data
                st.session_state.nombre_excel = f"MAILING_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                st.session_state.preparar_mails = False
                st.rerun()
            
            if st.button("✅ Finalizar", use_container_width=True):
                st.session_state.preparar_mails = False
                st.rerun()
        
        mostrar_dialogo_preparar_mails()

    # ── DESCARGA FUERA DEL MODAL ─────────────────────────────────────────────
    if st.session_state.get("excel_descarga"):
        st.success("🎉 ¡Mailing generado exitosamente! Descargue el archivo:")
        
        col_desc1, col_desc2, col_desc3 = st.columns([1, 2, 1])
        with col_desc2:
            st.download_button(
                label="📥 DESCARGAR EXCEL",
                data=st.session_state.excel_descarga,
                file_name=st.session_state.nombre_excel,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )
            
            if st.button("✅ FINALIZAR", use_container_width=True):
                del st.session_state["excel_descarga"]
                del st.session_state["nombre_excel"]
                st.rerun()

    # ── GENERAR INFORMES ─────────────────────────────────────────────────────
    if st.session_state.get('generar_informe'):
        with st.spinner("Generando informe..."):
            registros_sin_legajo = traer_registros_sin_legajo()
            if registros_sin_legajo:
                contenido_txt = generar_informe_txt(registros_sin_legajo)
                st.download_button(
                    label="📥 DESCARGAR TXT",
                    data=contenido_txt.encode('utf-8'),
                    file_name=f"INFORME_NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                st.info(f"📊 {len(registros_sin_legajo)} registros sin legajo")
            else:
                st.success("✅ No hay registros sin legajo")
        st.session_state.generar_informe = False

    if st.session_state.get('generar_informe_asignados'):
        with st.spinner("Generando informe..."):
            registros_con_legajo = traer_registros_con_legajo()
            if registros_con_legajo:
                excel_data = generar_excel_asignados(registros_con_legajo)
                st.download_button(
                    label="📥 DESCARGAR EXCEL (TODOS)",
                    data=excel_data,
                    file_name=f"INFORME_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.info(f"📊 {len(registros_con_legajo)} registros con legajo")
            else:
                st.success("✅ No hay registros con legajo")
        st.session_state.generar_informe_asignados = False

    if st.session_state.get('generar_informe_por_inspector'):
        with st.spinner("Generando informe por inspector..."):
            excel_data = generar_excel_por_inspector()
            st.download_button(
                label="📥 DESCARGAR EXCEL (POR INSPECTOR)",
                data=excel_data,
                file_name=f"INFORME_POR_INSPECTOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("✅ Informe generado - Una hoja por inspector")
        st.session_state.generar_informe_por_inspector = False

    # ── ASIGNACIÓN AUTOMÁTICA DE LEGAJOS ─────────────────────────────────────
    if st.session_state.get('asignar_legajos'):
        st.info("⏳ Asignando legajos...")
        
        with st.spinner("Cargando configuración..."):
            insp_loc   = cargar_inspectores_localidad()
            insp_zonas = cargar_zonas_inspectores()
            sinonimos  = cargar_sinonimos()
            palabras_ancla = cargar_palabras_ancla()
            lkp_loc    = construir_lookup_localidades(insp_loc)
            lkp_zonas  = construir_lookup_zonas(insp_zonas)
            lkp_sin    = construir_lookup_sinonimos(sinonimos)
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
                
                legajo = asignar_legajo(
                    reg.get('localidad', '') or '',
                    reg.get('calle', '') or '',
                    reg.get('numero', '') or '',
                    lkp_loc, lkp_zonas, lkp_sin, lkp_palabras
                )
                
                if legajo:
                    asig.append({'id': reg['id'], 'legajo': legajo})
                else:
                    no_asig.append({
                        'id': reg['id'],
                        'localidad': reg.get('localidad', ''),
                        'calle': reg.get('calle', ''),
                        'numero': reg.get('numero', ''),
                        'razon_social': reg.get('razon_social', ''),
                        'cuit': reg.get('cuit', ''),
                        'tel_dom_legal': reg.get('tel_dom_legal', ''),
                        'tel_dom_real': reg.get('tel_dom_real', ''),
                    })
                
                time.sleep(0.01)

            progress_bar.empty()
            status_text.empty()

            with st.spinner("Guardando..."):
                guardados = guardar_legajos_en_batch(asig)

            st.session_state.asignar_legajos = False
            st.session_state.ultima_asignacion = {
                "asignados": guardados,
                "no_asignados": len(no_asig),
                "detalle": no_asig,
            }
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
            st.download_button(
                label="📥 DESCARGAR INFORME",
                data=contenido_informe.encode('utf-8'),
                file_name=f"NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            with st.expander(f"📋 Ver {res['no_asignados']} registros"):
                st.dataframe(pd.DataFrame(res['detalle']), use_container_width=True)
        
        if st.button("Cerrar resultado"):
            del st.session_state.ultima_asignacion
            st.rerun()

    # ============================================================
    # SECCIÓN DE FILTROS Y TABLA - VERSIÓN ROBUSTA
    # ============================================================
    st.markdown("### 📋 Filtros")
    
    # Inicializar timestamp para forzar recarga
    if 'ultima_recarga' not in st.session_state:
        st.session_state.ultima_recarga = datetime.now()
    
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    with f1:
        st.markdown('<p class="filtro-titulo">CUIT</p>', unsafe_allow_html=True)
        filtro_cuit = st.text_input("CUIT", key="input_filtro_cuit", placeholder="Ej: 30707685243", label_visibility="collapsed")
    with f2:
        st.markdown('<p class="filtro-titulo">RAZÓN SOCIAL</p>', unsafe_allow_html=True)
        filtro_razon = st.text_input("Razón", key="input_filtro_razon", placeholder="Razón social", label_visibility="collapsed")
    with f3:
        st.markdown('<p class="filtro-titulo">LOCALIDAD</p>', unsafe_allow_html=True)
        locs = get_localidades()
        localidad = st.selectbox("Localidad", ["TODAS"] + locs, key="filtro_localidad", label_visibility="collapsed")
    with f4:
        st.markdown('<p class="filtro-titulo">MAIL</p>', unsafe_allow_html=True)
        filtro_mail = st.selectbox("Mail", ["AMBOS", "NO", "SI"], key="filtro_mail", label_visibility="collapsed")
    with f5:
        st.markdown('<p class="filtro-titulo">LEGAJO</p>', unsafe_allow_html=True)
        filtro_leg = st.selectbox("Legajo", ["TODOS", "CON LEGAJO", "SIN LEGAJO"], key="filtro_leg", label_visibility="collapsed")
    with f6:
        st.markdown('<p class="filtro-titulo">CALLE</p>', unsafe_allow_html=True)
        filtro_calle_aprox = st.text_input("Calle", key="filtro_calle_aproximacion", placeholder="Ej: Yrigoyen", label_visibility="collapsed")

    # ── CONSTRUIR CONSULTA CON TODOS LOS FILTROS EN SUPABASE ──
    q = supabase.table("padron_deuda_presunta").select("*")
    
    # Filtro LOCALIDAD
    if localidad != "TODAS":
        q = q.eq("localidad", localidad)
    
    # Filtro MAIL
    if filtro_mail == "SI":
        q = q.eq("mail_enviado", "SI")
    elif filtro_mail == "NO":
        q = q.eq("mail_enviado", "NO")
    
    # Filtro LEGAJO (en Supabase, NO en Pandas)
    if filtro_leg == "CON LEGAJO":
        q = q.not_.is_("leg", "null")
    elif filtro_leg == "SIN LEGAJO":
        q = q.is_("leg", "null")
    
    # IMPORTANTE: Forzar límite alto para traer todos (evita paginación de Supabase)
    q = q.range(0, 100000)
    
    # EJECUTAR CONSULTA (siempre nueva, sin caché)
    with st.spinner("Consultando base de datos..."):
        datos = q.execute()
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos.data) if datos.data else pd.DataFrame()
    
    # Filtros CUIT y RAZON SOCIAL (en Pandas por ser búsqueda textual)
    if not df.empty and filtro_cuit:
        df = df[df['cuit'].astype(str).str.contains(filtro_cuit, case=False, na=False)]
    if not df.empty and filtro_razon:
        df = df[df['razon_social'].astype(str).str.contains(filtro_razon, case=False, na=False)]
    
    # Filtro CALLE por similitud (en Pandas)
    if not df.empty and filtro_calle_aprox:
        filtro_norm = normalizar_calle(filtro_calle_aprox)
        if filtro_norm:
            df['calle_norm'] = df['calle'].apply(lambda x: normalizar_calle(str(x)) if x else "")
            df['similitud'] = df['calle_norm'].apply(lambda x: difflib.SequenceMatcher(None, filtro_norm, x).ratio() if x else 0)
            df = df[df['similitud'] > 0.4].sort_values('similitud', ascending=False)
            df = df.drop(columns=['calle_norm', 'similitud'])

    # ── CONTADOR REAL (sobre el df actual) ──
    total_en_tabla = len(df)
    RPP = 300
    pages = max(1, (total_en_tabla + RPP - 1) // RPP)

    # Inicializar o validar página actual
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 1
    st.session_state.pagina_actual = max(1, min(st.session_state.pagina_actual, pages))

    # Paginación
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

    # Si no hay datos, mostrar mensaje
    if df.empty:
        st.info("No hay registros que coincidan con los filtros seleccionados.")
    else:
        off = (st.session_state.pagina_actual - 1) * RPP
        df_p = df.iloc[off:off+RPP].reset_index(drop=True).copy()

        # Formatear celdas
        for col in df_p.columns:
            df_p[col] = df_p[col].apply(lambda x: "" if pd.isna(x) else str(x))
        
        for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(lambda x: fmt_fecha(x) if x and x != "" else "")

        df_orig = df_p.copy()
        df_ed = df_p.rename(columns={
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
        })
        df_ed.insert(0, "🗑️", False)

        if st.checkbox("Seleccionar todos los de esta página"):
            df_ed["🗑️"] = True

        # key ÚNICA que cambia con la página y la recarga
        editor_key = f"editor_{st.session_state.pagina_actual}_{st.session_state.ultima_recarga.timestamp()}"
        
        edited = st.data_editor(
            df_ed, use_container_width=True, height=500,
            column_config={"🗑️": st.column_config.CheckboxColumn("Eliminar")},
            key=editor_key,
        )

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
                    
                    nv = row.get('LEG')
                    if nv != orig.get('leg'):
                        if nv and str(nv).strip():
                            try:
                                upd['leg'] = int(float(str(nv)))
                            except:
                                upd['leg'] = None
                        else:
                            upd['leg'] = None
                    
                    nv = row.get('VTO')
                    if nv != orig.get('vto'):
                        if nv and str(nv).strip():
                            fecha_ok = norm_fecha(str(nv))
                            if fecha_ok:
                                upd['vto'] = fecha_ok
                            else:
                                errores_fecha += 1
                        else:
                            upd['vto'] = None
                    
                    nv = row.get('MAIL ENVIADO') or 'NO'
                    if nv not in ('SI', 'NO'):
                        nv = 'NO'
                    if nv != orig.get('mail_enviado'):
                        upd['mail_enviado'] = nv
                    
                    nv = row.get('ACTA')
                    if nv != orig.get('acta'):
                        upd['acta'] = nv if nv and str(nv).strip() else None
                    
                    nv = row.get('ESTADO GESTION') or 'PENDIENTE'
                    if nv != orig.get('estado_gestion'):
                        upd['estado_gestion'] = nv
                    
                    if upd:
                        supabase.table("padron_deuda_presunta").update(upd).eq("id", row['ID']).execute()
                        mods += 1

            if mods > 0:
                st.success(f"✅ {mods} registros actualizados correctamente.")
                if errores_fecha > 0:
                    st.warning(f"⚠️ {errores_fecha} fecha(s) no se pudieron guardar (formato incorrecto). Usá DD/MM/YYYY.")
                # FORZAR RECARGA COMPLETA DESPUÉS DE GUARDAR
                st.session_state.ultima_recarga = datetime.now()
                st.rerun()
            elif errores_fecha > 0:
                st.warning(f"No se guardaron cambios. {errores_fecha} fecha(s) con formato incorrecto.")
            else:
                st.info("No se detectaron cambios para guardar.")
