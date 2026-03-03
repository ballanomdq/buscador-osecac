# --- BLOQUE CORREGIDO (SIN ERRORES DE ESPACIOS) ---
                    for arc in adjuntos:
                        meta = {
                            'name': arc.name, 
                            'parents': [ID_CARPETA_DRIVE]
                        }
                        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
                        
                        # El robot crea el archivo
                        f = service_drive.files().create(
                            body=meta, 
                            media_body=media, 
                            fields='id, webViewLink'
                        ).execute()

                        # Truco para que no te tire el error 403 de espacio:
                        # Le damos permiso a "cualquiera" para ver el archivo inmediatamente.
                        try:
                            service_drive.permissions().create(
                                fileId=f['id'], 
                                body={'type': 'anyone', 'role': 'viewer'}
                            ).execute()
                        except:
                            pass # Si ya tiene permiso, que siga
                        
                        links.append(f.get('webViewLink'))
                    # --------------------------------------------------
