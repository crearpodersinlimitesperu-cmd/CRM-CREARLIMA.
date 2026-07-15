import pandas as pd
import os

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
xl = pd.ExcelFile(cal_path)

def clean_sheet(df, name):
    df_clean = df.copy()
    # Normalize column names
    rename_map = {}
    cols = list(df_clean.columns)
    
    # If it's Hoja2 or similar unnamed style
    if len(cols) >= 3 and ('EQUIPO' in str(cols[0]).upper() or 'INICIO' in str(cols[0]).upper()):
        rename_map[cols[0]] = 'INICIO'
        rename_map[cols[1]] = 'FINAL'
        rename_map[cols[2]] = 'ENTRENAMIENTO'
        if len(cols) >= 4:
            rename_map[cols[3]] = 'DETALLES'
    else:
        # Standard cleaning
        for col in cols:
            c_clean = str(col).strip().upper()
            if 'INICIO' in c_clean:
                rename_map[col] = 'INICIO'
            elif 'FINAL' in c_clean or c_clean == 'FIN':
                rename_map[col] = 'FINAL'
            elif 'ENTRENAMIENTO' in c_clean or 'EVENTO' in c_clean:
                rename_map[col] = 'ENTRENAMIENTO'
            elif 'ENTRENADOR' in c_clean:
                rename_map[col] = 'ENTRENADOR'
            elif 'LUGAR' in c_clean:
                rename_map[col] = 'LUGAR'
            elif 'EQUIPO' in c_clean:
                rename_map[col] = 'EQUIPO'
                
    df_clean = df_clean.rename(columns=rename_map)
    valid_cols = ['INICIO', 'FINAL', 'ENTRENAMIENTO', 'EQUIPO', 'ENTRENADOR', 'LUGAR', 'DETALLES']
    available_cols = [c for c in valid_cols if c in df_clean.columns]
    df_disp = df_clean[available_cols].copy()
    
    # Drop rows where ENTRENAMIENTO is null/empty
    if 'ENTRENAMIENTO' in df_disp.columns:
        df_disp = df_disp.dropna(subset=['ENTRENAMIENTO'])
        df_disp = df_disp[df_disp['ENTRENAMIENTO'].astype(str).str.strip() != '']
    
    # Filter dates
    if 'INICIO' in df_disp.columns:
        df_disp['temp_date'] = pd.to_datetime(df_disp['INICIO'], errors='coerce')
        df_disp = df_disp[df_disp['temp_date'].notna()]
        df_disp = df_disp.sort_values(by='temp_date', ascending=True)
        # Format dates
        for date_col in ['INICIO', 'FINAL']:
            if date_col in df_disp.columns:
                df_disp[date_col] = df_disp[date_col].astype(str).str.slice(0, 10)
        df_disp = df_disp.drop(columns=['temp_date'])
        
    return df_disp

for name in ['LIM', 'Hoja2']:
    df = xl.parse(name)
    df_clean = clean_sheet(df, name)
    print(f"Sheet '{name}' cleaned shape:", df_clean.shape)
    print(df_clean.head(5))
    print("-" * 50)
