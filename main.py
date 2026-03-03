# --- SECCIÓN 7: NOVEDADES Y CHAT ---
with st.expander("📢 7. NOVEDADES Y COMUNICADOS", expanded=True):
    
    st.markdown("### ✍️ Publicar Novedad")
    with st.form("form_novedades", clear_on_submit=True):
        mensaje = st.text_area("Escribí tu comunicado aquí:", placeholder="Ej: Nueva resolución disponible...")
        adjuntos = st.file_uploader("Adjuntar archivos (Podés elegir varios):", accept_multiple_files=True)
        enviar = st.form_submit_button("🚀 PUBLICAR AHORA")

        if enviar:
            if mensaje:
                try:
                    client_sheets, service_drive = conectar_robot()
                    links = []

                    if adjuntos:
                        for arc in adjuntos:
                            meta = {'name': arc.name, 'parents': [ID_CARPETA_DRIVE]}
                            media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
                            
                            # Subida
                            f = service_drive.files().create(body=meta, media_body=media, fields='id, webViewLink').execute()
                            
                            # Permiso público (Evita el error 403 de cuota)
                            service_drive.permissions().create(fileId=f['id'], body={'type': 'anyone', 'role': 'viewer'}).execute()
                            
                            links.append(f.get('webViewLink'))

                    # Guardar en Excel
                    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                    links_str = " | ".join(links) if links else "Sin adjuntos"
                    hoja = client_sheets.open_by_key(ID_EXCEL_CHAT).sheet1
                    hoja.append_row([fecha, mensaje, links_str])
                    
                    st.success("¡Publicado correctamente!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al publicar: {e}")
            else:
                st.warning("Escribí un mensaje primero.")

    st.divider()

    st.markdown("### 📬 Últimos Comunicados")
    try:
        df = pd.read_csv(URL_LECTURA_CHAT)
        if not df.empty:
            for i, fila in df.iloc[::-1].iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"📅 {fila.iloc[0]}")
                        st.markdown(f"**{fila.iloc[1]}**")
                    with col2:
                        links_raw = str(fila.iloc[2])
                        if "http" in links_raw:
                            lista_links = links_raw.split(" | ")
                            for idx, l in enumerate(lista_links):
                                st.link_button(f"📄 Ver Adjunto {idx+1 if len(lista_links)>1 else ''}", l)
        else:
            st.info("No hay comunicados guardados.")
    except:
        st.error("Todavía no hay datos o el archivo está vacío.")
