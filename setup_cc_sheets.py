import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
import pandas as pd

def setup():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = SAC.from_json_keyfile_name('credenciales.json', scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key('1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y')

    # 1. Pestaña LOG_DERIVACIONES
    try:
        ws_log = sh.worksheet("LOG_DERIVACIONES")
    except gspread.exceptions.WorksheetNotFound:
        ws_log = sh.add_worksheet(title="LOG_DERIVACIONES", rows="5000", cols="10")
        ws_log.update('A1:G1', [["Fecha", "Hora", "Coordinadora", "Participante", "Telefono", "Motivo", "Estado"]])

    # 2. Pestaña RESUMEN_DERIVACIONES (Formato solicitado)
    try:
        ws_res = sh.worksheet("RESUMEN_DERIVACIONES")
    except gspread.exceptions.WorksheetNotFound:
        ws_res = sh.add_worksheet(title="RESUMEN_DERIVACIONES", rows="100", cols="10")
        headers = ["COORDINADORA", "CASOS TOTALES", "URGENTES", "CONFIRMACIONES (LOG)", "OPCIN 4 / INFO", "CIERRES"]
        ws_res.update('A1:F1', [headers])
        # Filas iniciales para las coordinadoras activas
        ws_res.update('A2:F3', [
            ["Diana Moscoso", 0, 0, 0, 0, 0],
            ["Joyce Marin", 0, 0, 0, 0, 0]
        ])

    print("✅ Pestañas de derivación creadas/verificadas en Google Sheets.")

if __name__ == "__main__":
    setup()
