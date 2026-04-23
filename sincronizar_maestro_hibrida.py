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

def sincronizar_maestra_hibrida():
    print("--- Iniciando Reconciliacion Historica (Hibrida) ---")
    
    file_purgado = r"C:\Users\josem\Downloads\Hojas de Cálculo\participantes_2026-04-20.csv"
    file_master = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    file_backup = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database_BACKUP_PRE_PURGA.xlsx"
    file_graduados = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\GRADUADOS_TEMP.xlsx"
    output_file = file_master
    
    # 1. Cargar todas las fuentes
    print("1. Cargando fuentes (Campaña, Backup, Graduados)...")
    df_p = pd.read_csv(file_purgado, on_bad_lines='skip', sep=None, engine='python', encoding='utf-8')
    df_p.columns = [normalize(c) for c in df_p.columns]
    p_dni_col = next((c for c in df_p.columns if 'IDENTI' in c), 'IDENTIFICACION')
    
    df_m_old = pd.read_excel(file_backup, dtype=str).fillna("")
    
    df_g = pd.read_excel(file_graduados, sheet_name='GRADUADOS ')
    nombres_graduados_oficiales = [normalize(n) for n in df_g['CREAR CUANTICO'] if n]
    
    # 2. Paso 1: Procesar la base de campaña (3,035)
    print(f"2. Procesando base de campaña ({len(df_p)} registros)...")
    
    # Mapeo por DNI del backup
    m_map = {str(row.get('DNI', '')).strip(): row.to_dict() for _, row in df_m_old.iterrows()}
    # Mapeo por Nombre del backup (para huerfanos sin DNI)
    m_name_map = {normalize(f"{row['Nombres']} {row['Apellidos']}"): row.to_dict() for _, row in df_m_old.iterrows()}

    final_rows = []
    names_in_campaign = set() # Para identificar huerfanos despues

    def map_status(val):
        v = str(val).strip().upper()
        if v == 'SI' or 'SENTADO' in v: return 'Sentado'
        if v == 'NO': return '—'
        return val if val and val != 'nan' else '—'

    for _, row_p in df_p.iterrows():
        dni_p = str(row_p.get(p_dni_col, '')).strip()
        nom_p = str(row_p.get('NOMBRE', '')).strip()
        ape_p = str(row_p.get('APELLIDO', '')).strip()
        name_p = normalize(f"{nom_p} {ape_p}")
        names_in_campaign.add(name_p)
        
        hist = m_map.get(dni_p, m_name_map.get(name_p, {}))
        
        # Mapping base row
        final_rows.append({
            "Nombres": nom_p.title(),
            "Apellidos": ape_p.title(),
            "Teléfono": str(row_p.get('TELEFONO', '')).strip() or hist.get('Teléfono', ''),
            "Participación": str(row_p.get('TIPO', '')).strip() or hist.get('Participación', ''),
            "IMO Enrolador": str(row_p.get('IMO', '')).strip() or hist.get('IMO Enrolador', ''),
            "Aliado C1": hist.get('Aliado C1', '—'),
            "Aliado C2": hist.get('Aliado C2', '—'),
            "Estatus C1": map_status(row_p.get('C1')),
            "Estatus C2": map_status(row_p.get('C2')),
            "Estatus MJ": hist.get('Estatus MJ', '—'),
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

    # 3. Paso 2: Identificar y Recoverar Graduados Huérfanos
    print("3. Ejecutando motor de reconciliacion de graduados (Fuzzy Check)...")
    orphans_identified = 0
    graduados_marked = 0
    final_names_set = [normalize(f"{r['Nombres']} {r['Apellidos']}") for r in final_rows]
    
    # Pre-identificar graduados que ya están en la base actual
    graduados_en_base_indices = set()
    for g_name in nombres_graduados_oficiales:
        match_idx = -1
        # Intentar coincidencia exacta en lo ya procesado
        if g_name in final_names_set:
            match_idx = final_names_set.index(g_name)
        else:
            # Intento difuso
            for idx, p_name in enumerate(final_names_set):
                if similar(g_name, p_name) > 0.92:
                    match_idx = idx
                    break
        
        if match_idx != -1:
            final_rows[match_idx]['Estatus MJ'] = "Graduado ★"
            graduados_marked += 1
        else:
            # ES UN HUÉRFANO: Reincorporar
            orphans_identified += 1
            # Intentar rescatar del backup
            hist = m_name_map.get(g_name, {})
            # Si no hay backup exacto, probar fuzzy backup
            if not hist:
                for b_name, b_data in m_name_map.items():
                    if similar(g_name, b_name) > 0.92:
                        hist = b_data
                        break
            
            # Crear entrada histórica
            n_parts = g_name.split() # Intento de separar nombres/apellidos
            nom_h = " ".join(n_parts[:2]).title() if len(n_parts) > 2 else n_parts[0].title()
            ape_h = " ".join(n_parts[2:]).title() if len(n_parts) > 2 else (n_parts[1].title() if len(n_parts) > 1 else "")
            
            final_rows.append({
                "Nombres": hist.get('Nombres', nom_h),
                "Apellidos": hist.get('Apellidos', ape_h),
                "Teléfono": hist.get('Teléfono', '—'),
                "Participación": "GRADUADO HISTORICO",
                "IMO Enrolador": hist.get('IMO Enrolador', '—'),
                "Aliado C1": hist.get('Aliado C1', '—'),
                "Aliado C2": hist.get('Aliado C2', '—'),
                "Estatus C1": hist.get('Estatus C1', '—'),
                "Estatus C2": hist.get('Estatus C1', '—'),
                "Estatus MJ": "Graduado ★",
                "DNI": hist.get('DNI', ''),
                "RENIEC_Nombres": hist.get('RENIEC_Nombres', ''),
                "RENIEC_Paterno": hist.get('RENIEC_Paterno', ''),
                "RENIEC_Materno": hist.get('RENIEC_Materno', ''),
                "Verificado_RENIEC": hist.get('Verificado_RENIEC', 'NO'),
                "Coordinador": hist.get('Coordinador', ''),
                "Resultado Gestión": hist.get('Resultado Gestión', ''),
                "Fecha Gestión": hist.get('Fecha Gestión', ''),
                "Origen/Equipo": "REINCORPORADO (GRADUADO LIMA)"
            })
            graduados_marked += 1

    df_final = pd.DataFrame(final_rows)
    print(f"4. Guardando Master Hibrido (Final: {len(df_final)} filas)...")
    df_final.to_excel(output_file, index=False)
    
    print("\nDONE: RECONCILIACIÓN COMPLETADA.")
    print(f"   - Registros Activos (Campaña): {len(df_p)}")
    print(f"   - Graduados Re-incorporados (Huérfanos): {orphans_identified}")
    print(f"   - TOTAL GRADUADOS ★ EN BASE: {graduados_marked}")
    print(f"   - Universo Total Resultante: {len(df_final)}")

    # Generar Reporte Auditoria (Opcional pero recomendado para confianza)
    with open("C:\\Users\\josem\\Downloads\\CONTROL_SISTEMA_CREARLIMA\\REPORTE_AUDITORIA_GRADUADOS.md", "w", encoding='utf-8') as f:
        f.write("# Reporte de Auditoría: Graduados 🔱\n\n")
        f.write(f"Este documento detalla la reconciliación del conteo de graduados solicitado.\n\n")
        f.write(f"- **Meta Inicial:** 318 graduados.\n")
        f.write(f"- **Graduados identificados en campaña:** {graduados_marked - orphans_identified}\n")
        f.write(f"- **Graduados históricos recuperados:** {orphans_identified}\n")
        f.write(f"- **TOTAL FINAL:** {graduados_marked}\n\n")
        f.write("## Nota de Integridad\n")
        f.write("Los graduados históricos han sido re-insertados en la base maestra incluso si no estaban en el archivo CSV de campaña, respetando la veracidad de los datos oficiales.\n")

if __name__ == "__main__":
    try:
        sincronizar_maestra_hibrida()
    except Exception as e:
        print(f"ERROR: {e}")
