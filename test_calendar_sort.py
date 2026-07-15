import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
df_cal = pd.read_excel(cal_path, sheet_name='LIM', dtype=str).fillna("—")
valid_cols = ['INICIO', 'FINAL', 'ENTRENAMIENTO', 'EQUIPO', 'ENTRENADOR', 'LUGAR']
available_cols = [c for c in valid_cols if c in df_cal.columns]
df_cal_clean = df_cal[available_cols].dropna(subset=['ENTRENAMIENTO'] if 'ENTRENAMIENTO' in df_cal.columns else []).copy()

for date_col in ['INICIO', 'FINAL']:
    if date_col in df_cal_clean.columns:
        df_cal_clean[date_col] = df_cal_clean[date_col].astype(str).str.slice(0, 10)

# Sort by date descending
df_cal_clean['temp_date'] = pd.to_datetime(df_cal_clean['INICIO'], errors='coerce')
df_cal_clean = df_cal_clean.sort_values(by='temp_date', ascending=False).drop(columns=['temp_date'])

print("Top 10 sorted events:")
print(df_cal_clean.head(10))
