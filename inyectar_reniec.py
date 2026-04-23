import pandas as pd
import os
import unicodedata

def normalize(text):
    if not text or pd.isna(text): return ""
    s = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def inyectar_datos():
    print("--- Iniciando Inyeccion Quirurgica de Datos RENIEC ---")
    
    file_master = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    file_mineria = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\Mineria_DNIs.xlsx"
    
    if not os.path.exists(file_mineria):
        print("ERROR: No se encuentra cache de minado.")
        return

    # 1. Cargar Master y Mineria
    df_m = pd.read_excel(file_master, dtype=str).fillna("")
    df_mini = pd.read_excel(file_mineria, dtype=str).fillna("")
    
    # Filtrar validos
    df_validos = df_mini[df_mini['Estatus'].str.contains('VERIFICADO', na=False)]
    
    # Mapeo DNI -> Datos
    dni_map = {}
    name_map = {}
    for _, row in df_validos.iterrows():
        dni = str(row['DNI']).split('.')[0].strip()
        data = {
            "n": str(row['RENIEC_Nombres']).title(),
            "a": f"{row['RENIEC_Paterno']} {row['RENIEC_Materno']}".title(),
            "full": normalize(f"{row['RENIEC_Nombres']} {row['RENIEC_Paterno']} {row['RENIEC_Materno']}")
        }
        if dni: dni_map[dni] = data
        n_orig = normalize(row.get('Nombre_Original', ''))
        if n_orig: name_map[n_orig] = data

    # 2. Inyectar en Master
    cambios = 0
    for idx, row in df_m.iterrows():
        dni = str(row.get('DNI', '')).split('.')[0].strip()
        crm_full = normalize(f"{row['Nombres']} {row['Apellidos']}")
        
        # Buscar por DNI (prioridad) o por nombre
        target = dni_map.get(dni) or name_map.get(crm_full)
        
        if target:
            # Respaldar original si no existe backup (opcional, pero el usuario dijo 'usaremos oficiales')
            df_m.at[idx, 'Nombres'] = target['n']
            df_m.at[idx, 'Apellidos'] = target['a']
            df_m.at[idx, 'Verificado_RENIEC'] = 'SI'
            cambios += 1

    # 3. Guardar
    df_m.to_excel(file_master, index=False)
    print(f"DONE: Se han purificado {cambios} registros con nombres oficiales de RENIEC.")

if __name__ == "__main__":
    try:
        inyectar_datos()
    except Exception as e:
        print(f"ERROR: {e}")
