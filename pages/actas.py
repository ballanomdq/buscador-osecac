# Dentro de TAB 2, después del botón "🤖 Asignar Legajos", agregá:

with col4:  # o donde quieras ubicarlo
    if st.button("🔍 Buscar calles sin asociar", key="btn_buscar_sinonimos"):
        st.session_state.buscar_sinonimos = True

# Y luego, después de la asignación automática, agregá este bloque:

# ── Buscar calles sin asociar (solo para Mar del Plata) ────────────────────
if st.session_state.get('buscar_sinonimos'):
    with st.spinner("Analizando calles de Mar del Plata..."):
        # 1. Obtener todas las calles oficiales y sus sinónimos
        calles_oficiales = supabase.table("zonas_inspectores").select("calle").execute()
        calles_oficiales_set = set([c['calle'].upper().strip() for c in calles_oficiales.data]) if calles_oficiales.data else set()
        
        # 2. Obtener sinónimos ya existentes
        sinonimos_existentes = supabase.table("sinonimos_calles").select("sinonimo").execute()
        sinonimos_set = set([s['sinonimo'].upper().strip() for s in sinonimos_existentes.data]) if sinonimos_existentes.data else set()
        
        # 3. Obtener todas las calles ÚNICAS de Mar del Plata del padrón
        registros_mdq = supabase.table("padron_deuda_presunta")\
            .select("calle")\
            .eq("localidad", "MAR DEL PLATA")\
            .execute()
        
        calles_en_padron = set()
        for r in registros_mdq.data:
            calle_norm = normalizar_calle(r.get('calle', ''))
            if calle_norm:
                calles_en_padron.add(calle_norm)
        
        # 4. Filtrar las que NO están en oficiales NI en sinónimos
        calles_sin_asociar = []
        for calle in calles_en_padron:
            if calle not in calles_oficiales_set and calle not in sinonimos_set:
                calles_sin_asociar.append(calle)
        
        if not calles_sin_asociar:
            st.success("✅ Todas las calles de Mar del Plata están correctamente asociadas")
            st.session_state.buscar_sinonimos = False
        else:
            st.warning(f"🔍 Se encontraron {len(calles_sin_asociar)} calles únicas sin asociar")
            
            # 5. Mostrar cada una con sugerencias
            for calle_problema in sorted(calles_sin_asociar):
                with st.container():
                    st.markdown(f"**Calle en el padrón:** `{calle_problema}`")
                    
                    # Buscar posibles coincidencias con calles oficiales
                    coincidencias = []
                    for oficial in calles_oficiales_set:
                        # Similitud simple
                        ratio = difflib.SequenceMatcher(None, calle_problema, oficial).ratio()
                        if ratio > 0.6:  # Umbral de similitud
                            coincidencias.append((oficial, ratio))
                    
                    coincidencias.sort(key=lambda x: x[1], reverse=True)
                    
                    if coincidencias:
                        st.markdown("**Posibles coincidencias:**")
                        cols = st.columns(len(coincidencias) + 1)
                        for i, (oficial, ratio) in enumerate(coincidencias[:3]):
                            porcentaje = int(ratio * 100)
                            if cols[i].button(f"✅ Asociar a '{oficial}' ({porcentaje}%)", key=f"asoc_{calle_problema}_{i}"):
                                # Guardar sinónimo
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
                        
                        # Opción manual
                        with cols[len(coincidencias[:3])]:
                            if st.button("✏️ Asociar manualmente", key=f"manual_{calle_problema}"):
                                st.session_state.asociar_manual = calle_problema
                    else:
                        st.info("No se encontraron coincidencias automáticas")
                        if st.button("✏️ Asociar manualmente", key=f"manual2_{calle_problema}"):
                            st.session_state.asociar_manual = calle_problema
                    
                    # Asociación manual expandida
                    if st.session_state.get('asociar_manual') == calle_problema:
                        with st.form(key=f"form_manual_{calle_problema}"):
                            oficial_manual = st.selectbox("Seleccionar calle oficial", options=sorted(calles_oficiales_set))
                            if st.form_submit_button("Guardar asociación"):
                                supabase.table("sinonimos_calles").insert({
                                    "calle_oficial": oficial_manual,
                                    "sinonimo": calle_problema,
                                    "creado_por": "usuario"
                                }).execute()
                                st.success(f"Sinónimo guardado manualmente")
                                del st.session_state.asociar_manual
                                st.rerun()
                    
                    st.markdown("---")
            
            if st.button("Cerrar búsqueda", key="cerrar_busqueda"):
                st.session_state.buscar_sinonimos = False
                st.rerun()
