import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

# CONFIGURACIÓN MAESTRA
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"

def conectar_sheets():
    """Establece conexión segura con Google Sheets API."""
    # Intentamos cargar la llave desde una variable de entorno (para Render)
    # o desde un archivo local 'credenciales.json'
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if os.path.exists("credenciales.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
            return gspread.authorize(creds)
        else:
            print("⚠️ No se encontró 'credenciales.json'. El sistema solo funcionará en modo LECTURA.")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def sincronizar_mineria_a_cloud(archivo_excel="Mineria_DNIs.xlsx"):
    """Sube los datos minados de RENIEC a la pestaña 'MINERIA' del Sheets."""
    client = conectar_sheets()
    if not client: return
    
    try:
        sh = client.open_by_key(SHEET_ID)
        # Intentar abrir la pestaña, si no existe, crearla
        try:
            ws = sh.worksheet("MINERIA")
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet(title="MINERIA", rows="1000", cols="20")
            print("✅ Pestaña 'MINERIA' creada con éxito.")

        # Cargar data local
        if os.path.exists(archivo_excel):
            df = pd.read_excel(archivo_excel).fillna("")
            # Limpiar pestaña y subir data nueva
            ws.clear()
            ws.update([df.columns.values.tolist()] + df.values.tolist())
            print(f"🚀 {len(df)} registros minados sincronizados con la nube.")
    except Exception as e:
        print(f"❌ Error sincronizando minería: {e}")

def actualizar_dato_maestro(dni, columna, nuevo_valor):
    """Edita una celda específica en el Master de Google Sheets."""
    client = conectar_sheets()
    if not client: return
    
    try:
        sh = client.open_by_key(SHEET_ID)
        ws = sh.get_worksheet(0) # Asumimos que el Master es la primera pestaña
        
        # Buscar la fila por DNI
        celda = ws.find(str(dni))
        if celda:
            # Buscar la columna por nombre
            headers = ws.row_values(1)
            if columna in headers:
                col_idx = headers.index(columna) + 1
                ws.update_cell(celda.row, col_idx, nuevo_valor)
                print(f"✅ {columna} actualizado para DNI {dni}.")
        else:
            print(f"⚠️ DNI {dni} no encontrado en el Master.")
    except Exception as e:
        print(f"❌ Error actualizando Sheets: {e}")
