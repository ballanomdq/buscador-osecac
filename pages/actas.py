# ══════════════════════════════════════════════════════════════════
# TAB 2 — Editar Legajos y Vtos (VERSIÓN MEJORADA)
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

    # Botones principales
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
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
        if st.button("🔍 Buscar calles sin asociar"):
            st.session_state.buscar_sinonimos = True
    with col5:
        if st.button("📄 INFORME NO ASIGNADOS"):
            st.session_state.generar_informe = True
    with col6:
        if st.button("↺ Resetear filtros"):
            for k in ['input_filtro_cuit','input_filtro_razon','filtro_localidad',
                      'filtro_mail','filtro_leg','filtro_calle_aproximacion','pagina_actual']:
                st.session_state.pop(k, None)
            st.rerun()
    with col7:
        if st.button("⟳ Recargar"):
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

    # ── Generar informe TXT ─────────────────────────────────────────────────
    if st.session_state.get('generar_informe'):
        with st.spinner("Generando informe de no asignados..."):
            registros_sin_legajo = traer_registros_sin_legajo()
            if registros_sin_legajo:
                contenido_txt = generar_informe_txt(registros_sin_legajo)
                st.download_button(
                    label="📥 DESCARGAR INFORME (TXT)",
                    data=contenido_txt.encode('utf-8'),
                    file_name=f"INFORME_NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_informe"
                )
                st.info(f"📊 Se encontraron {len(registros_sin_legajo)} registros sin legajo")
            else:
                st.success("✅ No hay registros sin legajo para exportar")
        st.session_state.generar_informe = False

    # ── Asignación automática de legajos (CON BARRA DE PROGRESO VISIBLE) ────
    if st.session_state.get('asignar_legajos'):
        st.info("⏳ INICIANDO ASIGNACIÓN DE LEGAJOS... Esto puede tomar unos minutos según la cantidad de registros.")
        
        with st.spinner("Cargando tablas de inspectores..."):
            insp_loc   = cargar_inspectores_localidad()
            insp_zonas = cargar_zonas_inspectores()
            sinonimos  = cargar_sinonimos()
            lkp_loc    = construir_lookup_localidades(insp_loc)
            lkp_zonas  = construir_lookup_zonas(insp_zonas)
            lkp_sin    = construir_lookup_sinonimos(sinonimos)

        with st.spinner("Cargando registros sin legajo..."):
            registros = traer_registros_sin_legajo()

        if not registros:
            st.info("No hay registros sin legajo.")
            st.session_state.asignar_legajos = False
        else:
            total = len(registros)
            
            progress_bar = st.progress(0, text="Procesando registros...")
            status_text = st.empty()
            
            asig = []
            no_asig = []

            for i, reg in enumerate(registros):
                percent = (i + 1) / total
                progress_bar.progress(percent, text=f"Procesando registro {i+1} de {total}...")
                status_text.markdown(f"🔄 **Progreso:** {int(percent * 100)}% completado - Procesando: {reg.get('razon_social', 'Sin nombre')[:50]}...")
                
                legajo = asignar_legajo(
                    reg.get('localidad', '') or '',
                    reg.get('calle',     '') or '',
                    reg.get('numero',    '') or '',
                    lkp_loc, lkp_zonas, lkp_sin
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
                        'cuit':        reg.get('cuit', ''),
                        'tel_dom_legal': reg.get('tel_dom_legal', ''),
                        'tel_dom_real': reg.get('tel_dom_real', ''),
                    })
                
                time.sleep(0.01)

            progress_bar.empty()
            status_text.empty()

            with st.spinner("Guardando legajos en la base de datos..."):
                guardados = guardar_legajos_en_batch(asig)

            st.session_state.asignar_legajos = False
            st.session_state.ultima_asignacion = {
                "asignados": guardados,
                "no_asignados": len(no_asig),
                "detalle": no_asig,
            }
            st.success(f"✅ ASIGNACIÓN COMPLETADA: {guardados} legajos asignados, {len(no_asig)} sin coincidencia.")
            st.rerun()

    # ── Buscar calles sin asociar ──────────────────────────────────────────
    if st.session_state.get('buscar_sinonimos'):
        with st.spinner("Analizando calles de Mar del Plata..."):
            calles_oficiales = supabase.table("zonas_inspectores").select("calle").execute()
            calles_oficiales_set = set([normalizar_calle(c['calle']) for c in calles_oficiales.data]) if calles_oficiales.data else set()
            
            sinonimos_existentes = supabase.table("sinonimos_calles").select("sinonimo").execute()
            sinonimos_set = set([normalizar_calle(s['sinonimo']) for s in sinonimos_existentes.data]) if sinonimos_existentes.data else set()
            
            registros_mdq = supabase.table("padron_deuda_presunta")\
                .select("calle")\
                .eq("localidad", "MAR DEL PLATA")\
                .execute()
            
            calles_en_padron = set()
            for r in registros_mdq.data:
                calle_norm = normalizar_calle(r.get('calle', ''))
                if calle_norm:
                    calles_en_padron.add(calle_norm)
            
            calles_sin_asociar = []
            for calle in calles_en_padron:
                if calle not in calles_oficiales_set and calle not in sinonimos_set:
                    calles_sin_asociar.append(calle)
            
            if not calles_sin_asociar:
                st.success("✅ Todas las calles de Mar del Plata están correctamente asociadas")
                st.session_state.buscar_sinonimos = False
            else:
                st.warning(f"🔍 Se encontraron {len(calles_sin_asociar)} calles únicas sin asociar")
                
                for calle_problema in sorted(calles_sin_asociar):
                    key_segura = generar_key_segura(calle_problema)
                    
                    with st.container():
                        st.markdown(f"**Calle en el padrón:** `{calle_problema}`")
                        
                        coincidencias = []
                        for oficial in calles_oficiales_set:
                            ratio = difflib.SequenceMatcher(None, calle_problema, oficial).ratio()
                            if ratio > 0.6:
                                coincidencias.append((oficial, ratio))
                        
                        coincidencias.sort(key=lambda x: x[1], reverse=True)
                        
                        if coincidencias:
                            st.markdown("**Posibles coincidencias:**")
                            cols = st.columns(min(len(coincidencias) + 1, 4))
                            for i, (oficial, ratio) in enumerate(coincidencias[:3]):
                                porcentaje = int(ratio * 100)
                                if cols[i].button(f"✅ Asociar a '{oficial}' ({porcentaje}%)", key=f"asoc_{key_segura}_{i}"):
                                    try:
                                        supabase.table("sinonimos_calles").insert({
                                            "calle_oficial": oficial,
                                            "sinonimo": calle_problema,
                                            "creado_por": "auto_detectado"
                                        }).execute()
                                        st.success(f"Sinónimo guardado: {calle_problema} → {oficial}")
                                        st.rerun()
                                    except Exception as e:
                                        if "duplicate" in str(e).lower():
                                            st.warning("Este sinónimo ya existe")
                                        else:
                                            st.error(f"Error: {e}")
                            
                            idx_manual = min(len(coincidencias), 3)
                            if cols[idx_manual].button("✏️ Asociar manualmente", key=f"manual_{key_segura}"):
                                st.session_state[f"manual_{key_segura}"] = calle_problema
                        else:
                            st.info("No se encontraron coincidencias automáticas")
                            if st.button("✏️ Asociar manualmente", key=f"manual2_{key_segura}"):
                                st.session_state[f"manual_{key_segura}"] = calle_problema
                        
                        if st.session_state.get(f"manual_{key_segura}"):
                            with st.form(key=f"form_manual_{key_segura}"):
                                oficial_manual = st.selectbox("Seleccionar calle oficial", options=sorted(calles_oficiales_set))
                                if st.form_submit_button("Guardar asociación"):
                                    try:
                                        supabase.table("sinonimos_calles").insert({
                                            "calle_oficial": oficial_manual,
                                            "sinonimo": calle_problema,
                                            "creado_por": "usuario"
                                        }).execute()
                                        st.success(f"Sinónimo guardado manualmente")
                                        del st.session_state[f"manual_{key_segura}"]
                                        st.rerun()
                                    except Exception as e:
                                        if "duplicate" in str(e).lower():
                                            st.warning("Este sinónimo ya existe")
                                        else:
                                            st.error(f"Error: {e}")
                            
                            if st.button("Cancelar", key=f"cancel_{key_segura}"):
                                del st.session_state[f"manual_{key_segura}"]
                                st.rerun()
                        
                        st.markdown("---")
                
                if st.button("Cerrar búsqueda", key="cerrar_busqueda"):
                    st.session_state.buscar_sinonimos = False
                    st.rerun()

    if st.session_state.get('ultima_asignacion'):
        res = st.session_state.ultima_asignacion
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.success(f"✅ {res['asignados']} legajos asignados")
        with col_res2:
            st.warning(f"⚠️ {res['no_asignados']} registros sin coincidencia")
        
        if res['no_asignados'] > 0:
            contenido_informe = generar_informe_txt(res['detalle'])
            st.download_button(
                label="📥 DESCARGAR INFORME DE NO ASIGNADOS",
                data=contenido_informe.encode('utf-8'),
                file_name=f"NO_ASIGNADOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="download_no_asignados"
            )
            
            with st.expander(f"📋 Ver detalle de {res['no_asignados']} registros sin legajo"):
                st.dataframe(pd.DataFrame(res['detalle']), use_container_width=True)
        
        if st.button("Cerrar resultado"):
            del st.session_state.ultima_asignacion
            st.rerun()

    st.markdown("---")

    # ── Filtros (con mini títulos) ──────────────────────────────────────────
    st.markdown("### 📋 Filtros de búsqueda")
    
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
        st.markdown('<p class="filtro-titulo">MAIL ENVIADO</p>', unsafe_allow_html=True)
        filtro_mail = st.selectbox("Mail", ["AMBOS", "NO", "SI"], key="filtro_mail", label_visibility="collapsed")
    with f5:
        st.markdown('<p class="filtro-titulo">LEGAJO</p>', unsafe_allow_html=True)
        filtro_leg = st.selectbox("Legajo", ["TODOS", "CON LEGAJO", "SIN LEGAJO"], key="filtro_leg", label_visibility="collapsed")
    with f6:
        st.markdown('<p class="filtro-titulo">CALLE (APROXIMACIÓN)</p>', unsafe_allow_html=True)
        filtro_calle_aprox = st.text_input("Calle", key="filtro_calle_aproximacion", placeholder="Ej: Yrigoyen, Colon...", label_visibility="collapsed")

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
        
        if filtro_calle_aprox:
            filtro_norm = normalizar_calle(filtro_calle_aprox)
            if filtro_norm:
                df['calle_norm'] = df['calle'].apply(lambda x: normalizar_calle(str(x)) if x else "")
                df['similitud'] = df['calle_norm'].apply(lambda x: difflib.SequenceMatcher(None, filtro_norm, x).ratio() if x else 0)
                df = df[df['similitud'] > 0.4].sort_values('similitud', ascending=False)
                df = df.drop(columns=['calle_norm', 'similitud'])

        total = len(df)
        RPP = 300
        pages = max(1, (total + RPP - 1) // RPP)

        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 1
        st.session_state.pagina_actual = max(1, min(st.session_state.pagina_actual, pages))

        pa, pn, ps = st.columns([1, 3, 1])
        with pa:
            if st.button("◀ ANTERIOR") and st.session_state.pagina_actual > 1:
                st.session_state.pagina_actual -= 1
                st.rerun()
        with pn:
            st.caption(f"📄 Página {st.session_state.pagina_actual} / {pages} | {total} registros totales")
        with ps:
            if st.button("SIGUIENTE ▶") and st.session_state.pagina_actual < pages:
                st.session_state.pagina_actual += 1
                st.rerun()

        off = (st.session_state.pagina_actual - 1) * RPP
        df_p = df.iloc[off:off+RPP].reset_index(drop=True).copy()

        # Formatear fechas
        for col in ['empl_10_2025', 'emp_11_2025', 'empl_12_2025']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(limpiar_entero)
        for col in ['fechareldependencia', 'desde', 'hasta', 'fecha_pago_obl', 'vto', 'fecha_carga']:
            if col in df_p.columns:
                df_p[col] = df_p[col].apply(fmt_fecha)

        # Mostrar tabla SOLO PARA SELECCIONAR (sin edición inline)
        df_mostrar = df_p.drop(columns=['fecha_carga'], errors='ignore').rename(columns=TITULOS)
        
        # Agregar columna de selección y botón de edición
        df_mostrar.insert(0, "📝", False)  # Columna para seleccionar para editar
        df_mostrar.insert(1, "🔍", "")     # Columna para botón de edición (placeholder)
        
        st.info("💡 **Para editar un registro:** Click en el botón ✏️ de la fila correspondiente")
        
        # Mostrar tabla con botones de edición
        for idx, row in df_mostrar.iterrows():
            cols = st.columns([0.3, 0.3, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2])
            
            # Checkbox para seleccionar (para eliminar)
            seleccionado = cols[0].checkbox("", key=f"sel_{idx}_{row['ID']}")
            
            # Botón de edición
            if cols[1].button("✏️", key=f"edit_{row['ID']}"):
                st.session_state[f"editando_{row['ID']}"] = True
            
            # Mostrar datos
            col_idx = 2
            for campo in ['LEG', 'VTO', 'MAIL ENVIADO', 'ACTA', 'ESTADO GESTION', 
                          'LOCALIDAD', 'CUIT', 'RAZON SOCIAL', 'CALLE', 'NUMERO',
                          'PISO', 'DPTO', 'TELEFONO LEGAL', 'TELEFONO REAL', 'ULTIMA ACTA']:
                if campo in row.index:
                    cols[col_idx].write(str(row[campo]) if pd.notna(row[campo]) else "-")
                col_idx += 1
            
            # Formulario de edición (se muestra solo si se clickeó el botón)
            if st.session_state.get(f"editando_{row['ID']}"):
                with st.expander(f"✏️ EDITANDO REGISTRO ID {row['ID']} - {row.get('RAZON SOCIAL', 'Sin nombre')[:50]}", expanded=True):
                    # Obtener datos originales
                    orig_data = df_p[df_p['id'] == row['ID']].iloc[0] if len(df_p[df_p['id'] == row['ID']]) > 0 else None
                    
                    if orig_data is not None:
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            nuevo_legajo = st.text_input("Legajo", value=str(orig_data.get('leg', '') or ''), key=f"leg_{row['ID']}")
                            nuevo_vto = st.text_input("Vencimiento (DD/MM/YYYY)", value=fmt_fecha(orig_data.get('vto', '')) or '', key=f"vto_{row['ID']}")
                            nuevo_mail = st.selectbox("Mail Enviado", ["NO", "SI"], index=0 if orig_data.get('mail_enviado') != 'SI' else 1, key=f"mail_{row['ID']}")
                            nuevo_acta = st.text_input("Acta", value=str(orig_data.get('acta', '') or ''), key=f"acta_{row['ID']}")
                            nuevo_estado = st.selectbox("Estado Gestión", ["PENDIENTE", "EN PROCESO", "COMPLETADO", "RECHAZADO"], 
                                                        index=["PENDIENTE", "EN PROCESO", "COMPLETADO", "RECHAZADO"].index(orig_data.get('estado_gestion', 'PENDIENTE')), 
                                                        key=f"estado_{row['ID']}")
                        with col_b:
                            nueva_localidad = st.text_input("Localidad", value=str(orig_data.get('localidad', '') or ''), key=f"loc_{row['ID']}")
                            nuevo_cuit = st.text_input("CUIT", value=str(orig_data.get('cuit', '') or ''), key=f"cuit_{row['ID']}")
                            nueva_razon = st.text_input("Razón Social", value=str(orig_data.get('razon_social', '') or ''), key=f"razon_{row['ID']}")
                            nueva_calle = st.text_input("Calle", value=str(orig_data.get('calle', '') or ''), key=f"calle_{row['ID']}")
                            nuevo_numero = st.text_input("Número", value=str(orig_data.get('numero', '') or ''), key=f"num_{row['ID']}")
                        with col_c:
                            nuevo_piso = st.text_input("Piso", value=str(orig_data.get('piso', '') or ''), key=f"piso_{row['ID']}")
                            nuevo_dpto = st.text_input("Dpto", value=str(orig_data.get('dpto', '') or ''), key=f"dpto_{row['ID']}")
                            nuevo_tel_legal = st.text_input("Teléfono Legal", value=str(orig_data.get('tel_dom_legal', '') or ''), key=f"tel_legal_{row['ID']}")
                            nuevo_tel_real = st.text_input("Teléfono Real", value=str(orig_data.get('tel_dom_real', '') or ''), key=f"tel_real_{row['ID']}")
                            nueva_ultima_acta = st.text_input("Última Acta", value=str(orig_data.get('ultima_acta', '') or ''), key=f"acta_num_{row['ID']}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("💾 GUARDAR CAMBIOS", key=f"save_{row['ID']}"):
                                # Preparar datos a actualizar
                                updates = {}
                                if nuevo_legajo and nuevo_legajo != str(orig_data.get('leg', '')):
                                    updates['leg'] = int(nuevo_legajo) if nuevo_legajo.isdigit() else None
                                if nuevo_vto != fmt_fecha(orig_data.get('vto', '')):
                                    updates['vto'] = norm_fecha(nuevo_vto) if nuevo_vto else None
                                if nuevo_mail != orig_data.get('mail_enviado', 'NO'):
                                    updates['mail_enviado'] = nuevo_mail
                                if nuevo_acta != str(orig_data.get('acta', '')):
                                    updates['acta'] = nuevo_acta if nuevo_acta else None
                                if nuevo_estado != orig_data.get('estado_gestion', 'PENDIENTE'):
                                    updates['estado_gestion'] = nuevo_estado
                                if nueva_localidad != str(orig_data.get('localidad', '')):
                                    updates['localidad'] = nueva_localidad
                                if nuevo_cuit != str(orig_data.get('cuit', '')):
                                    updates['cuit'] = nuevo_cuit
                                if nueva_razon != str(orig_data.get('razon_social', '')):
                                    updates['razon_social'] = nueva_razon
                                if nueva_calle != str(orig_data.get('calle', '')):
                                    updates['calle'] = nueva_calle
                                if nuevo_numero != str(orig_data.get('numero', '')):
                                    updates['numero'] = nuevo_numero
                                if nuevo_piso != str(orig_data.get('piso', '')):
                                    updates['piso'] = nuevo_piso
                                if nuevo_dpto != str(orig_data.get('dpto', '')):
                                    updates['dpto'] = nuevo_dpto
                                if nuevo_tel_legal != str(orig_data.get('tel_dom_legal', '')):
                                    updates['tel_dom_legal'] = nuevo_tel_legal
                                if nuevo_tel_real != str(orig_data.get('tel_dom_real', '')):
                                    updates['tel_dom_real'] = nuevo_tel_real
                                if nueva_ultima_acta != str(orig_data.get('ultima_acta', '')):
                                    updates['ultima_acta'] = nueva_ultima_acta
                                
                                if updates:
                                    supabase.table("padron_deuda_presunta").update(updates).eq("id", int(row['ID'])).execute()
                                    st.success("✅ Cambios guardados correctamente")
                                    del st.session_state[f"editando_{row['ID']}"]
                                    st.rerun()
                                else:
                                    st.info("No se detectaron cambios")
                        with col_btn2:
                            if st.button("❌ Cancelar", key=f"cancel_{row['ID']}"):
                                del st.session_state[f"editando_{row['ID']}"]
                                st.rerun()
        
        # Botón para eliminar los registros seleccionados
        ids_seleccionados = []
        for idx, row in df_mostrar.iterrows():
            if st.session_state.get(f"sel_{idx}_{row['ID']}", False):
                ids_seleccionados.append(row['ID'])
        
        st.session_state.ids_a_eliminar = ids_seleccionados
        
        if ids_seleccionados:
            st.warning(f"⚠️ {len(ids_seleccionados)} registros seleccionados para eliminar")
            if st.button("🗑️ ELIMINAR SELECCIONADOS", type="secondary"):
                supabase.table("padron_deuda_presunta").delete().in_("id", ids_seleccionados).execute()
                for idx, row in df_mostrar.iterrows():
                    st.session_state.pop(f"sel_{idx}_{row['ID']}", None)
                st.session_state.ids_a_eliminar = []
                st.rerun()
