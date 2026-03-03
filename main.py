from flask import Flask, request, render_template
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os
import pickle

app = Flask(__name__)

# === CONFIGURACIÓN (esto lo hacés VOS una vez) ===
SCOPES = ['https://www.googleapis.com/auth/drive']
CARPETA_ID = 'ID_DE_LA_CARPETA_EN_TU_DRIVE'  # Ej: "1a2b3c4d5e"

# === AUTENTICACIÓN (esto corre UNA VEZ y se guarda) ===
def get_drive_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_localServer(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

# === RUTA PARA EL FORMULARIO DE TU JEFE ===
@app.route('/', methods=['GET', 'POST'])
def portal():
    if request.method == 'POST':
        texto = request.form.get('texto', '')
        archivo = request.files.get('archivo')
        
        service = get_drive_service()
        
        # 1. Guardar el texto en un archivo temporal
        archivo_texto = io.BytesIO(texto.encode('utf-8'))
        
        # 2. Subir el texto a Drive
        texto_metadata = {
            'name': 'texto_del_jefe.txt',
            'parents': [CARPETA_ID]
        }
        texto_media = MediaIoBaseUpload(archivo_texto, mimetype='text/plain')
        service.files().create(
            body=texto_metadata,
            media_body=texto_media
        ).execute()
        
        # 3. Subir el archivo si existe
        if archivo and archivo.filename:
            archivo_metadata = {
                'name': archivo.filename,
                'parents': [CARPETA_ID]
            }
            archivo_media = MediaIoBaseUpload(
                io.BytesIO(archivo.read()), 
                mimetype=archivo.content_type
            )
            service.files().create(
                body=archivo_metadata,
                media_body=archivo_media
            ).execute()
        
        return "✅ ¡Archivo y texto guardados en Drive!"
    
    return '''
        <form method="post" enctype="multipart/form-data">
            <textarea name="texto" placeholder="Escribí algo..."></textarea><br>
            <input type="file" name="archivo"><br>
            <button type="submit">Enviar</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
