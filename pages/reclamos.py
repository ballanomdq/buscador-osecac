def subir_a_drive(file_path, file_name):
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build('drive', 'v3', credentials=creds)
        
        # 1. Verificar que la carpeta existe y es accesible (debug)
        try:
            folder_check = service.files().get(
                fileId=FOLDER_ID_RECLAMOS, 
                fields='id, name, mimeType, driveId',
                supportsAllDrives=True
            ).execute()
            st.write(f"✅ Carpeta verificada: {folder_check.get('name')} (ID: {folder_check.get('driveId')})")
        except Exception as e:
            st.error(f"❌ No se puede acceder a la carpeta. Verificá permisos: {str(e)}")
            return None

        # 2. Subir archivo con todos los parámetros para Shared Drive
        file_metadata = {
            'name': file_name,
            'parents': [FOLDER_ID_RECLAMOS]
        }
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink',
            supportsAllDrives=True,          # Obligatorio para Shared Drive
            enforceSingleParent=True          # Evita conflictos de carpetas
        ).execute()
        
        # 3. Hacer público (opcional, pero útil)
        try:
            service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'},
                supportsAllDrives=True
            ).execute()
        except Exception as e:
            st.warning(f"Archivo subido pero no se pudo hacer público: {str(e)}")
        
        return file.get('webViewLink')
        
    except Exception as e:
        st.error(f"Error detallado al subir archivo: {str(e)}")
        # Mostrar más información si es un error 403
        if "403" in str(e):
            st.info("🔑 Posible solución: Verificá que la cuenta de servicio sea 'Editor' en el Drive compartido y en la carpeta.")
        return None
