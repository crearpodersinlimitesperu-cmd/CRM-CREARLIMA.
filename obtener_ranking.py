import pandas as pd
import os

def procesar_productividad():
    folder = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(folder, "Fuentes_Productividad")
    
    files = [
        os.path.join(source_dir, "productividad_coordinador.xlsx"),
        os.path.join(source_dir, "productividad_coordinador (1).xlsx"),
        os.path.join(source_dir, "productividad_coordinador (2).xlsx")
    ]
    
    dfs = []
    for f in files:
        if os.path.exists(f):
            try:
                dfs.append(pd.read_excel(f))
            except: pass
            
    if not dfs:
        return None
        
    # Unificar y Deduplicar por ClienteId
    df_full = pd.concat(dfs, ignore_index=True)
    df_full = df_full.drop_duplicates(subset=['ClienteId'])
    
    # Limpieza robusta de nombres de columnas
    def clean_col(c):
        import unicodedata
        s = str(c).strip()
        # Eliminar tildes y normalizar a mayúsculas para comparación estable
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').upper()
        return s

    # Mapear columnas originales a sus versiones limpias
    col_map = {clean_col(c): c for c in df_full.columns}
    
    # Identificar columnas críticas
    target_coord = col_map.get('COORDINADOR')
    target_res = col_map.get('RESULTADO GESTION')
    target_asist = col_map.get('ASISTENCIA')
    target_id = col_map.get('CLIENTEID')
    
    if not target_coord or not target_res:
        # Intento secundario si los nombres varían un poco
        target_coord = next((c for c in df_full.columns if 'COORD' in clean_col(c)), None)
        target_res = next((c for c in df_full.columns if 'GESTION' in clean_col(c)), None)
    
    if not target_coord or not target_res:
        return None

    # Agrupar usando las columnas detectadas
    ranking = df_full.groupby(target_coord).agg(
        Gestiones=(target_id, 'count'),
        Confirmados_Llamada=(target_res, lambda x: (x.astype(str).str.upper() == 'CONFIRMADO').sum()),
        Asistentes_Reales=(target_asist, lambda x: (x.astype(str).str.upper() == 'CONFIRMADO').sum()) if target_asist else ('Gestiones', lambda x: 0)
    ).reset_index()
    
    # Renombrar para consistencia interna
    ranking.columns = ['Coordinador', 'Gestiones', 'Confirmados_Llamada', 'Asistentes_Reales']
    
    # Calcular Efectividad
    ranking['% Efectividad Llamada'] = (ranking['Confirmados_Llamada'] / ranking['Gestiones'] * 100).round(1)
    ranking['% Efectividad Final (C1)'] = (ranking['Asistentes_Reales'] / ranking['Gestiones'] * 100).round(1)
    
    return ranking.sort_values(by='Asistentes_Reales', ascending=False)

if __name__ == "__main__":
    r = procesar_productividad()
    if r is not None:
        print(r.to_string())
