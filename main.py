# --- BLOQUE CORREGIDO DE SUBIDA ---
                    for arc in adjuntos:
                        meta = {
                            'name': arc.name, 
                            'parents': [ID_CARPETA_DRIVE]
                        }
                        media = MediaIoBaseUpload(io.BytesIO(arc.read()), mimetype=arc.type)
                        
                        # Creamos el archivo
                        f = service_drive.files().create(
                            body=meta, 
                            media_body=media, 
                            fields='id, webViewLink'
                        ).execute()

                        # --- LA SOLUCIÓN AL ERROR 403 ---
                        # Le decimos al robot que NO sea el dueño, sino que te dé el permiso a vos o a cualquiera
                        service_drive.permissions().create(
                            fileId=f['id'], 
                            body={'type': 'anyone', 'role': 'viewer'}
                        ).execute()
                        
                        links.append(f.get('webViewLink'))
                    # ----------------------------------
