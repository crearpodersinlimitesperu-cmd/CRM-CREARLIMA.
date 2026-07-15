import os
import glob
import pandas as pd
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

load_dotenv()
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"

def conectar_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_json:
        return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope))
    if os.path.exists("credenciales.json"):
        return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope))
    print("❌ No hay credenciales.")
    return None

def find_files(patterns):
    files = []
    base_dirs = [r"C:\Users\josem\Downloads", r"C:\Users\josem\Downloads\Reportes y Gestión"]
    for bd in base_dirs:
        for pat in patterns:
            files.extend(glob.glob(os.path.join(bd, pat)))
    return list(set(files)) # unique

def safe_read_excel(f):
    try:
        return pd.read_excel(f)
    except Exception as e:
        print(f"Error leyendo {f}: {e}")
        return pd.DataFrame()

def process_and_upload():
    print("Iniciando consolidación y subida...")
    
    # 1. PRODUCTIVIDAD
    prod_files = find_files(["productividad_coordinador*.xlsx"])
    print(f"Archivos de Productividad encontrados: {len(prod_files)}")
    if prod_files:
        df_prod = pd.concat([safe_read_excel(f) for f in prod_files], ignore_index=True)
        if not df_prod.empty:
            df_prod = df_prod.fillna("—").astype(str)
            # Deduplicar
            if 'ClienteId' in df_prod.columns:
                df_prod = df_prod.drop_duplicates(subset=['ClienteId'], keep='last')
            elif 'NombreCompleto' in df_prod.columns and 'ApellidoCompleto' in df_prod.columns:
                df_prod['_key'] = df_prod['NombreCompleto'] + df_prod['ApellidoCompleto']
                df_prod = df_prod.drop_duplicates(subset=['_key'], keep='last').drop(columns=['_key'])
            
            print(f"Productividad: {len(df_prod)} registros únicos.")
            
            # Subir a sheets
            client = conectar_sheets()
            if client:
                sh = client.open_by_key(SHEET_ID)
                try: ws = sh.worksheet("PRODUCTIVIDAD")
                except: ws = sh.add_worksheet("PRODUCTIVIDAD", 1000, 20)
                ws.clear()
                ws.update([df_prod.columns.values.tolist()] + df_prod.values.tolist())
                print("OK PRODUCTIVIDAD actualizada en Google Sheets.")

    # 2. GESTION_LLAMADAS
    gest_files = find_files(["gestion_llamadas*.xlsx"])
    print(f"\nArchivos de Gestion encontrados: {len(gest_files)}")
    if gest_files:
        df_gest = pd.concat([safe_read_excel(f) for f in gest_files], ignore_index=True)
        if not df_gest.empty:
            df_gest = df_gest.fillna("—").astype(str)
            if 'Nombres' in df_gest.columns and 'Apellidos' in df_gest.columns:
                df_gest['_key'] = df_gest['Nombres'] + df_gest['Apellidos']
                # Si hay 'Ultima_Gestion', la podemos usar para ordenar, sino keep='last'
                if 'Ultima_Gestion' in df_gest.columns:
                    df_gest = df_gest.sort_values('Ultima_Gestion').drop_duplicates(subset=['_key'], keep='last')
                else:
                    df_gest = df_gest.drop_duplicates(subset=['_key'], keep='last')
                df_gest = df_gest.drop(columns=['_key'])
            else:
                df_gest = df_gest.drop_duplicates(keep='last')
                
            print(f"Gestion LLamadas: {len(df_gest)} registros únicos.")
            
            # Subir a sheets
            client = conectar_sheets()
            if client:
                sh = client.open_by_key(SHEET_ID)
                try: ws = sh.worksheet("GESTION_LLAMADAS")
                except: ws = sh.add_worksheet("GESTION_LLAMADAS", 1000, 20)
                ws.clear()
                ws.update([df_gest.columns.values.tolist()] + df_gest.values.tolist())
                print("OK GESTION_LLAMADAS actualizada en Google Sheets.")

if __name__ == "__main__":
    process_and_upload()
