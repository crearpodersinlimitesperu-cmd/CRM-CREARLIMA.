import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials as SAC
import time

def main():
    c = gspread.authorize(SAC.from_json_keyfile_name('C:/Users/josem/Downloads/CONTROL_SISTEMA_CREARLIMA/credenciales.json', ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']))
    sh = c.open_by_key('1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y')
    
    df = pd.read_csv('C:/Users/josem/Downloads/CONTROL_SISTEMA_CREARLIMA/casos_cierre.csv').fillna("")
    
    hoja_nombre = 'CASOS'
    try:
        ws = sh.worksheet(hoja_nombre)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=hoja_nombre, rows="1000", cols="20")
        
    try:
        ws.clear()
        ws.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"OK: Subida exitosamente a {hoja_nombre} ({len(df)} filas).")
    except Exception as e:
        print(f"ERROR en {hoja_nombre}: {e}")

if __name__ == "__main__":
    main()
