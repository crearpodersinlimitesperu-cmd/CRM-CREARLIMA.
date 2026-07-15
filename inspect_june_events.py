import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
xl = pd.ExcelFile(cal_path)

for name in ['LIM', 'Hoja2']:
    df = xl.parse(name)
    print(f"--- Sheet '{name}' ---")
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Find any date columns
    date_cols = [c for c in df.columns if 'INICIO' in c or 'FINAL' in c or 'FECHA' in c or c.startswith('EQUIPO')]
    if date_cols:
        for c in date_cols:
            df[c] = pd.to_datetime(df[c], errors='coerce')
        
        # Filter for June 2026
        # Let's find columns that are datetime
        time_col = date_cols[0]
        df_june = df[(df[time_col] >= '2026-06-01') & (df[time_col] <= '2026-06-30')]
        if not df_june.empty:
            print(df_june)
        else:
            print("No events in June 2026 found.")
    print("-" * 50)
