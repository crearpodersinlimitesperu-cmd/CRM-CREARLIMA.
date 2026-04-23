import pandas as pd
import os
import unicodedata
from difflib import SequenceMatcher

def normalize(text):
    if not text or pd.isna(text): return ""
    s = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def sincronizar_maestra():
    print("--- Iniciando Sincronizacion de ALTA PRECISION ---")
    
    # Rutas
    file_purgado = r"C:\Users\josem\Downloads\Hojas de Cálculo\participantes_2026-04-20.csv"
    file_master = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    file_graduados = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\GRADUADOS_TEMP.xlsx"
    output_file = file_master
    
    # 1. Cargar Base Purgada
    print("1. Cargando base purgada oficial...")
    df_p = pd.read_csv(file_purgado, on_bad_lines='skip', sep=None, engine='python', encoding='utf-8')
    df_p.columns = [normalize(c) for c in df_p.columns]
    p_dni_col = next((c for c in df_p.columns if 'IDENTI' in c), 'IDENTIFICACION')
    
    # 2. Cargar Master Actual
    print("2. Rescatando historicos del Master...")
    df_m = pd.read_excel(file_master, dtype=str).fillna("")
    
    # 3. Cargar Graduados (318)
    print("3. Preparando lista de 318 graduados con FUZZY MATCH...")
    df_g = pd.read_excel(file_graduados, sheet_name='GRADUADOS ')
    nombres_graduados_oficiales = [normalize(n) for n in df_g['CREAR CUANTICO'] if n]
    
    # Pre-calcular nombres normalizados en la base purgada para el fuzzy match
    p_entries = []
    for _, row_p in df_p.iterrows():
        nom = str(row_p.get('NOMBRE', '')).strip()
        ape = str(row_p.get('APELLIDO', '')).strip()
        p_entries.append(normalize(f"{nom} {ape}"))
    
    # Identificar graduados mediante fuzzy matching (más lento pero preciso)
    # Si el nombre normalizado NO es igual, probamos similitud > 0.9
    graduados_ids = set()
    print("   - Ejecutando motor de similitud de nombres...")
    for idx, p_name in enumerate(p_entries):
        # 1. Coincidencia exacta (rápida)
        if p_name in nombres_graduados_oficiales:
            graduados_ids.add(idx)
            continue
        # 2. Coincidencia difusa (si es lo suficientemente parecido)
        # Solo lo hacemos si el nombre oficial tiene longitud razonable
        for g_name in nombres_graduados_oficiales:
            if similar(p_name, g_name) > 0.92:
                graduados_ids.add(idx)
                break
                
    # 4. CONSTRUCCIÓN DE LA NUEVA BASE
    print(f"4. Reconstruyendo base sobre {len(df_p)} registros...")
    
    m_map = {str(row.get('DNI', '')).strip(): row.to_dict() for _, row in df_m.iterrows()}
            
    final_rows = []
    for idx, row_p in df_p.iterrows():
        dni_p = str(row_p.get(p_dni_col, '')).strip()
        
        # Mapeo de estatus (Normalizando SI -> Sentado)
        def map_status(val):
            v = str(val).strip().upper()
            if v == 'SI': return 'Sentado'
            if v == 'NO': return '—'
            return val if val and val != 'nan' else '—'

        hist = m_map.get(dni_p, {})
        estatus_mj = hist.get('Estatus MJ', '—')
        if idx in graduados_ids:
            estatus_mj = "Graduado ★"
            
        final_rows.append({
            "Nombres": str(row_p.get('NOMBRE', '')).strip().title(),
            "Apellidos": str(row_p.get('APELLIDO', '')).strip().title(),
            "Teléfono": str(row_p.get('TELEFONO', '')).strip() or hist.get('Teléfono', ''),
            "Participación": str(row_p.get('TIPO', '')).strip() or hist.get('Participación', ''),
            "IMO Enrolador": str(row_p.get('IMO', '')).strip() or hist.get('IMO Enrolador', ''),
            "Aliado C1": hist.get('Aliado C1', '—'),
            "Aliado C2": hist.get('Aliado C2', '—'),
            "Estatus C1": map_status(row_p.get('C1')),
            "Estatus C2": map_status(row_p.get('C2')),
            "Estatus MJ": estatus_mj,
            "DNI": dni_p,
            "RENIEC_Nombres": hist.get('RENIEC_Nombres', ''),
            "RENIEC_Paterno": hist.get('RENIEC_Paterno', ''),
            "RENIEC_Materno": hist.get('RENIEC_Materno', ''),
            "Verificado_RENIEC": hist.get('Verificado_RENIEC', 'NO'),
            "Coordinador": hist.get('Coordinador', ''),
            "Resultado Gestión": hist.get('Resultado Gestión', ''),
            "Fecha Gestión": hist.get('Fecha Gestión', ''),
            "Origen/Equipo": str(row_p.get('EQUIPO', '—')).strip()
        })
        
    df_new = pd.DataFrame(final_rows)
    print(f"5. Guardando Master Purgado (Final: {len(df_new)} filas)...")
    df_new.to_excel(output_file, index=False)
    
    print("\nDONE: PROCESO COMPLETADO CON EXITO.")
    print(f"   - Registros Purgados: {len(df_new)}")
    print(f"   - Graduados identificados: {len(graduados_ids)}")

if __name__ == "__main__":
    try:
        sincronizar_maestra()
    except Exception as e:
        print(f"ERROR: {e}")
