import pandas as pd
import os
import unicodedata

def normalize(text):
    if not text or pd.isna(text): return ""
    s = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def sincronizar_identidad():
    print("--- Iniciando Integracion de Identidad de Equipos ---")
    
    file_master = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    file_seguimiento = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\MAESTRIA DEL JUEGO GLOBAL\Equipos\Lima\SEGUIMIENTO EQUIPOS LIMA.xlsx"
    dir_equipos = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\MAESTRIA DEL JUEGO GLOBAL\Equipos\Lima"
    
    # 1. Cargar Master
    df_m = pd.read_excel(file_master, dtype=str).fillna("")
    
    # 2. Cargar Seguimiento
    df_s = pd.read_excel(file_seguimiento).fillna("")
    # Crear mapa Nombre -> Nombre Equipo
    team_name_map = {}
    team_num_map = {}
    for _, row in df_s.iterrows():
        n = normalize(row.get('NOMBRE', ''))
        if n:
            team_name_map[n] = str(row.get('NOMBRE  EQUIPO', '')).strip().upper()
            team_num_map[n] = str(row.get('EQUIPO', '')).strip()

    # 3. Mapeo de Carpetas Físicas (para validación)
    folder_map = {}
    if os.path.exists(dir_equipos):
        for folder in os.listdir(dir_equipos):
            if folder.startswith("EQUIPO"):
                # Extraer numero
                parts = folder.split()
                if len(parts) > 1:
                    num = parts[1]
                    folder_map[num] = folder

    # 4. Actualizar Master
    print(f"Actualizando identidad para {len(df_m)} registros...")
    for idx, row in df_m.iterrows():
        full_name = normalize(f"{row['Nombres']} {row['Apellidos']}")
        
        t_name = team_name_map.get(full_name)
        t_num = team_num_map.get(full_name)
        
        # Si no está en el seguimiento, intentar ver si ya tenía un número en Origen/Equipo
        if not t_num:
            current_oe = str(row.get('Origen/Equipo', '')).strip()
            if current_oe.isdigit():
                t_num = current_oe
        
        if t_num:
            # Reconstruir identidad "Equipo X — NOMBRE"
            # Buscar el nombre oficial de la carpeta si es posible
            official_folder = folder_map.get(t_num, "")
            if official_folder and " — " not in official_folder:
                # Si la carpeta es "EQUIPO 10 DAVIDS...", intentar limpiar
                tag = official_folder.replace(f"EQUIPO {t_num}", "").strip()
                if tag and not t_name: t_name = tag
            
            final_tag = f"Equipo {t_num}"
            if t_name and t_name != "0" and t_name != "NAN":
                final_tag += f" — {t_name}"
            
            df_m.at[idx, 'Origen/Equipo'] = final_tag

    # 5. Guardar
    df_m.to_excel(file_master, index=False)
    print(f"DONE: Identidad de equipos integrada exitosamente.")

if __name__ == "__main__":
    try:
        sincronizar_identidad()
    except Exception as e:
        print(f"ERROR: {e}")
