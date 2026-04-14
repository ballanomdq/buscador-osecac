# ==================== TAB 2: EDITAR LEGAJOS Y VTOS ====================
with tab2:
    st.markdown("### Editar Legajos y Fechas de Vencimiento")
    
    try:
        datos = supabase.table("padron_deuda_presunta").select("*").execute()
        
        if datos.data:
            df_datos = pd.DataFrame(datos.data)
            st.write(f"**Total de registros:** {len(df_datos)}")
            
            # Mostrar SOLO las primeras 100 filas para no saturar
            st.info("Mostrando primeros 100 registros. Podés editar fila por fila.")
            df_mostrar = df_datos.head(100).copy()
            
            # Columnas a mostrar
            columnas_editor = ['id', 'cuit', 'razon_social', 'leg', 'vto', 'mail_enviado', 'acta', 'estado_gestion']
            columnas_existentes = [col for col in columnas_editor if col in df_mostrar.columns]
            df_editable = df_mostrar[columnas_existentes].copy()
            
            # Convertir fechas a string para mostrar
            if 'vto' in df_editable.columns:
                df_editable['vto'] = pd.to_datetime(df_editable['vto']).dt.strftime('%Y-%m-%d')
            
            # Editor de datos (sin SelectColumn, usando texto normal)
            edited_df = st.data_editor(
                df_editable,
                use_container_width=True,
                column_config={
                    "leg": st.column_config.TextColumn("LEG", help="Número de legajo del inspector"),
                    "vto": st.column_config.TextColumn("VTO", help="Fecha de vencimiento (YYYY-MM-DD)"),
                    "mail_enviado": st.column_config.TextColumn("MAIL ENVIADO", help="NO o SI"),
                    "acta": st.column_config.TextColumn("ACTA", help="Número de acta"),
                    "estado_gestion": st.column_config.TextColumn("Estado", help="PENDIENTE, ACTA_SOLICITADA, ACTA_RECIBIDA, CERRADO"),
                },
                disabled=['id', 'cuit', 'razon_social'],
                key="editor"
            )
            
            if st.button("Guardar Cambios", type="primary"):
                with st.spinner("Guardando..."):
                    for _, row in edited_df.iterrows():
                        datos_update = {}
                        
                        if 'leg' in edited_df.columns:
                            val = row['leg']
                            datos_update['leg'] = val if pd.notna(val) and val != '' else None
                        
                        if 'vto' in edited_df.columns:
                            val = row['vto']
                            if pd.notna(val) and val != '':
                                datos_update['vto'] = str(val)
                            else:
                                datos_update['vto'] = None
                        
                        if 'mail_enviado' in edited_df.columns:
                            val = row['mail_enviado']
                            if pd.notna(val) and val != '':
                                datos_update['mail_enviado'] = str(val).upper()
                            else:
                                datos_update['mail_enviado'] = 'NO'
                        
                        if 'acta' in edited_df.columns:
                            val = row['acta']
                            datos_update['acta'] = val if pd.notna(val) and val != '' else None
                        
                        if 'estado_gestion' in edited_df.columns:
                            val = row['estado_gestion']
                            if pd.notna(val) and val != '':
                                datos_update['estado_gestion'] = str(val).upper()
                            else:
                                datos_update['estado_gestion'] = 'PENDIENTE'
                        
                        if datos_update:
                            supabase.table("padron_deuda_presunta").update(datos_update).eq("id", row['id']).execute()
                    
                    st.success("✅ Cambios guardados correctamente")
                    st.rerun()
        else:
            st.info("No hay datos cargados")
    except Exception as e:
        st.error(f"Error: {str(e)}")
