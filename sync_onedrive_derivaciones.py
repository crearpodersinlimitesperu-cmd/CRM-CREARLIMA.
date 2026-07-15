import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
import pandas as pd
import os
import re

# RUTAS ONEDRIVE
BASE_ONEDRIVE = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA"
FILE_DIANA = os.path.join(BASE_ONEDRIVE, "DERIVACIONES_DIANA_30ABR.xlsx")
FILE_JOYCE = os.path.join(BASE_ONEDRIVE, "DERIVACIONES_JOYCE_30ABR.xlsx")

def sync():
    print("Iniciando Sincronizacion OneDrive <-> Google Sheets...")
    
    # 1. CONECTAR A GOOGLE SHEETS
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = SAC.from_json_keyfile_name('credenciales.json', scope)
    client = gspread.authorize(creds)
    
    # Abrir el sheet maestro
    sh = client.open_by_key('1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y')
    ws_log = sh.worksheet("LOG_DERIVACIONES")
    data_log = ws_log.get_all_records()
    df_cloud = pd.DataFrame(data_log)
    
    if df_cloud.empty:
        print("Aviso: No hay datos en LOG_DERIVACIONES de la nube.")
        return

    # Key unica: Participante + Telefono + Fecha + Hora
    df_cloud['Key'] = df_cloud['Participante'].astype(str) + df_cloud['Telefono'].astype(str) + df_cloud['Fecha'].astype(str) + df_cloud['Hora'].astype(str)

    # 2. PROCESAR CADA COORDINADORA
    for name, path in [("Diana Moscoso", FILE_DIANA), ("Joyce Marin", FILE_JOYCE)]:
        print(f"Procesando {name}...")
        
        # Filtrar datos de la nube para esta CC
        df_cc_cloud = df_cloud[df_cloud['Coordinadora'].str.contains(name.split()[0], case=False, na=False)].copy()
        
        if os.path.exists(path):
            try:
                df_local = pd.read_excel(path)
                
                # Normalizar columnas locales si vienen del script anterior
                if 'Fecha/Hora' in df_local.columns:
                    df_local['Fecha'] = df_local['Fecha/Hora'].astype(str).str.split().str[0]
                    df_local['Hora'] = df_local['Fecha/Hora'].astype(str).str.split().str[1]
                if 'Respuesta' in df_local.columns:
                    df_local['Motivo'] = df_local['Respuesta']
                
                # Asegurar columnas de gestion
                if 'GESTIONADO' not in df_local.columns: df_local['GESTIONADO'] = 'NO'
                if 'COMENTARIOS' not in df_local.columns: df_local['COMENTARIOS'] = ''
                
                # Crear Key local para comparar
                df_local['Key'] = df_local['Participante'].astype(str) + df_local['Telefono'].astype(str) + df_local['Fecha'].astype(str) + df_local['Hora'].astype(str)
                
                # Identificar nuevos casos
                nuevos = df_cc_cloud[~df_cc_cloud['Key'].isin(df_local['Key'])]
                
                if not nuevos.empty:
                    print(f"Se encontraron {len(nuevos)} casos nuevos para {name}.")
                    nuevos_to_add = nuevos.drop(columns=['Key', 'Coordinadora']).copy()
                    nuevos_to_add['GESTIONADO'] = 'NO'
                    nuevos_to_add['COMENTARIOS'] = ''
                    
                    # Mantener solo columnas relevantes
                    cols_final = ['Fecha', 'Hora', 'Participante', 'Telefono', 'Motivo', 'Estado', 'GESTIONADO', 'COMENTARIOS']
                    df_local_clean = df_local[[c for c in cols_final if c in df_local.columns]]
                    
                    df_final = pd.concat([df_local_clean, nuevos_to_add], ignore_index=True)
                    df_final.to_excel(path, index=False)
                    print(f"Archivo actualizado con {len(nuevos)} nuevos casos.")
                else:
                    print(f"Sin casos nuevos para {name}.")
                    
            except Exception as e:
                print(f"Error en {name}: {e}")
        else:
            print(f"Creando nuevo archivo Excel para {name}...")
            df_final = df_cc_cloud.drop(columns=['Key', 'Coordinadora']).copy()
            df_final['GESTIONADO'] = 'NO'
            df_final['COMENTARIOS'] = ''
            df_final.to_excel(path, index=False)
            print(f"Archivo creado.")

    print("Sincronizacion completada con exito.")

if __name__ == "__main__":
    sync()
