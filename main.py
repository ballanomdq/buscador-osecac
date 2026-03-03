import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# --- CONFIGURACIÓN DE IDs ---
ID_CARPETA_DRIVE = "1IGtmxHWB3cWKzyCgx9hlvIGfKN2N136w"
ID_EXCEL_CHAT = "15jcmrXXI9UrqSKDOgaryiW_n_35ZjTpYWpAAHAQ2NCg"
URL_LECTURA_CHAT = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL_CHAT}/export?format=csv&gid=0"

# --- FUNCIÓN PARA CONECTAR AL ROBOT ---
def conectar_robot():
    info = dict(st.secrets["gcp_service_account"])
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    # Alcance (Scopes) para Sheets y Drive
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds), build('drive', 'v3', credentials=creds)
