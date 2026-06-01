# ══════════════════════════════════════════════════════════════════
# TAB 3 — Subir Actas (con períodos DESDE/HASTA) - VERSIÓN CORREGIDA
# ══════════════════════════════════════════════════════════════════
with tab3:
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
        
        try:
            # LEER EL CSV DE FORMA ROBUSTA - IGNORANDO FILAS CON ERRORES
            contenido = csv_file.getvalue().decode('utf-8-sig')
            lineas = contenido.split('\n')
            
            # Detectar separador ( , o ; )
            separador = ',' if ',' in lineas[0] else ';'
            
            # Contar columnas en primeras líneas para determinar el número esperado
            num_columnas_esperado = None
            for linea in lineas[:10]:
                if linea.strip():
                    num_cols = len(linea.split(separador))
                    if num_columnas_esperado is None:
                        num_columnas_esperado = num_cols
                    elif num_cols != num_columnas_esperado:
                        # Si hay variación, tomamos el más común o el de la primera línea
                        pass
            
            if num_columnas_esperado is None:
                num_columnas_esperado = 1
            
            # Procesar línea por línea, corrigiendo automáticamente
            lineas_corregidas = []
            lineas_error = 0
            
            for i, linea in enumerate(lineas):
                if not linea.strip():
                    continue
                
                partes = linea.split(separador)
                
                if len(partes) == num_columnas_esperado:
                    lineas_corregidas.append(linea)
                elif len(partes) > num_columnas_esperado:
                    # Tiene columnas de más: unimos las extras a la última columna
                    nuevas_partes = partes[:num_columnas_esperado-1]
                    extras = ''.join(partes[num_columnas_esperado-1:])
                    nuevas_partes.append(extras)
                    lineas_corregidas.append(separador.join(nuevas_partes))
                    lineas_error += 1
                else:
                    # Tiene menos columnas: agregamos vacías al final
                    nuevas_partes = partes + [''] * (num_columnas_esperado - len(partes))
                    lineas_corregidas.append(separador.join(nuevas_partes))
                    lineas_error += 1
            
            # Reconstruir el CSV corregido
            contenido_corregido = '\n'.join(lineas_corregidas)
            
            if lineas_error > 0:
                st.warning(f"⚠️ Se encontraron {lineas_error} línea(s) con formato incorrecto. Se corrigieron automáticamente.")
            
            # Leer el CSV corregido
            from io import StringIO
            df_completo = pd.read_csv(StringIO(contenido_corregido), sep=separador, dtype=str, encoding='utf-8-sig')
            
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
            
            # Mostrar qué columnas se encontraron
            st.info(f"""
            **Columnas detectadas:**
            - CUIT: `{col_cuit or '❌ No encontrada'}`
            - LEGAJO: `{col_leg or '❌ No encontrada'}`
            - FECHA VTO: `{col_vto or '❌ No encontrada'}`
            - ACTA: `{col_acta or '⚠️ Opcional (se usará "ACTUALIZADO")'}`
            - DEUDA: `{col_deuda or '⚠️ Opcional'}`
            - PERÍODO DESDE: `{col_desde or '⚠️ Opcional'}`
            - PERÍODO HASTA: `{col_hasta or '⚠️ Opcional'}`
            """)
            
            if not all([col_cuit, col_leg, col_vto]):
                st.warning(f"⚠️ Faltan columnas obligatorias: CUIT, LEGAJO y/o FECHA VTO")
            else:
                if st.button("📋 Procesar y actualizar actas", type="primary"):
                    with st.spinner("Procesando..."):
                        actualizados = 0
                        no_encontrados = 0
                        errores_fila = 0
                        bar = st.progress(0)
                        errores = []
                        
                        for i, row in df_completo.iterrows():
                            try:
                                # Extraer CUIT (limpiando caracteres)
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
                                
                                # Extraer DEUDA (opcional)
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
                                
                                # Buscar coincidencia en la base de datos
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
                                if len(errores) < 20:  # Limitar cantidad de errores mostrados
                                    errores.append(f"Fila {i+1}: {str(e)[:100]}")
                            
                            # Actualizar barra de progreso
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
                            get_dashboard_stats.clear()
                        else:
                            st.warning("⚠️ No se pudo actualizar ningún registro. Verificá que los CUIT, LEGAJO y FECHAS VTO coincidan exactamente con registros que tengan MAIL ENVIADO = SI.")
                        
                        if no_encontrados > 0:
                            st.info(f"ℹ️ {no_encontrados} filas no encontraron coincidencia en la base de datos. Puede ser que esos registros no existan, no tengan legajo asignado, o no tengan mail enviado.")
                        
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")
            st.info("💡 Consejo: Asegurate de que el archivo CSV tenga al menos las columnas: CUIT, LEGAJO y FECHA VTO. El resto son opcionales.")
