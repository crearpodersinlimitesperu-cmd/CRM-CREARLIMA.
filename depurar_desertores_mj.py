import pandas as pd
import os
import unicodedata

def normalize(text):
    if not text or pd.isna(text): return ""
    s = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def depurar_desertores():
    print("--- Iniciando Depuracion de Desertores y Rezagados ---")
    
    file_master = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    file_desertores = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\MAESTRIA DEL JUEGO GLOBAL\Equipos\Lima\DESERTORES Y REZAGADOS LIMA.xlsx"
    
    # 1. Cargar Master
    df_m = pd.read_excel(file_master, dtype=str).fillna("")
    
    # 2. Cargar Desertores (Ambas hojas)
    desertores_names = set()
    try:
        xl = pd.ExcelFile(file_desertores)
        for sheet in xl.sheet_names:
            df_temp = pd.read_excel(file_desertores, sheet_name=sheet).fillna("")
            # Buscar columna de nombre (Nombre del Participante o PARTICIPANTE)
            col_name = next((c for c in df_temp.columns if 'Nombre' in c or 'PARTICIPANTE' in c), None)
            if col_name:
                for n in df_temp[col_name]:
                    norm_n = normalize(n)
                    if norm_n: desertores_names.add(norm_n)
                print(f"   - {len(df_temp)} registros cargados desde hoja '{sheet}'.")
    except Exception as e:
        print(f"Error cargando desertores: {e}")
    
    print(f"Total de {len(desertores_names)} desertores/rezagados unificados.")

    # 3. Marcar en el Master
    procesados = 0
    for idx, row in df_m.iterrows():
        full_name = normalize(f"{row['Nombres']} {row['Apellidos']}")
        
        if full_name in desertores_names:
            # MARCAR COMO DESERTOR
            df_m.at[idx, 'Estatus MJ'] = "DESERTOR MJ"
            
            # LIMPIAR IDENTIDAD DE EQUIPO (Eliminar el nombre místico para desertores)
            current_oe = str(row.get('Origen/Equipo', '')).strip()
            if " — " in current_oe:
                num = current_oe.split("—")[0].replace("Equipo","").strip()
                df_m.at[idx, 'Origen/Equipo'] = num
            
            procesados += 1

    # 4. Guardar
    df_m.to_excel(file_master, index=False)
    print(f"DONE: Se han marcado {procesados} desertores y limpiado su identidad de equipo.")

if __name__ == "__main__":
    try:
        depurar_desertores()
    except Exception as e:
        print(f"ERROR: {e}")
