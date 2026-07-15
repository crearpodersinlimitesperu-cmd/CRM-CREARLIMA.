import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials as SAC
import time

def main():
    print("Iniciando subida de base a Google Sheets...")
    c = gspread.authorize(SAC.from_json_keyfile_name('C:/Users/josem/Downloads/CONTROL_SISTEMA_CREARLIMA/credenciales.json', ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']))
    sh = c.open_by_key('1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y')
    
    df = pd.read_csv('C:/Users/josem/Downloads/bot-cpsl-review/E27_participantes_limpio.csv').fillna("")
    
    for hoja_nombre in ['Hoja 1', 'ASIGNACIONES']:
        try:
            ws = sh.worksheet(hoja_nombre)
            ws.clear()
            ws.update([df.columns.values.tolist()] + df.values.tolist())
            print(f"OK: Base subida exitosamente a {hoja_nombre} ({len(df)} filas).")
            time.sleep(2)
        except Exception as e:
            print(f"ERROR en {hoja_nombre}: {e}")

if __name__ == "__main__":
    main()
