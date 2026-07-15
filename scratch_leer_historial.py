import os
import pandas as pd
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

load_dotenv()
SHEET_ID = "1NqEgzCkixVhMn3VLhsy_GVWwYBfwLQ1rwdHVcKTRyjo"

def conectar_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_json:
        return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope))
    if os.path.exists("credenciales.json"):
        return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope))
    print("❌ No hay credenciales.")
    return None

def main():
    client = conectar_sheets()
    if not client:
        return
    try:
        sh = client.open_by_key(SHEET_ID)
        print("Pestañas disponibles:", [ws.title for ws in sh.worksheets()])
        ws = sh.worksheet("Historial Completo")
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        
        print("Columnas:", df.columns.tolist())
        print("Total de filas:", len(df))
        
        # Filtramos los que tengan alguna coordinadora
        # Ajustar si el nombre de la columna es diferente
        df.to_csv("historial_completo_sheet.csv", index=False, encoding='utf-8')
        print("Guardado en historial_completo_sheet.csv")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error leyendo hoja:", e)

if __name__ == "__main__":
    main()
