import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
df_cal = pd.read_excel(cal_path, sheet_name='LIM', dtype=str).fillna("—")
valid_cols = ['INICIO', 'FINAL', 'ENTRENAMIENTO', 'EQUIPO', 'ENTRENADOR', 'LUGAR']
available_cols = [c for c in valid_cols if c in df_cal.columns]
df_cal_clean = df_cal[available_cols].dropna(subset=['ENTRENAMIENTO'] if 'ENTRENAMIENTO' in df_cal.columns else []).copy()

# Parse date
df_cal_clean['temp_date'] = pd.to_datetime(df_cal_clean['INICIO'], errors='coerce')

# Filter to 2026 onwards
df_cal_clean = df_cal_clean[df_cal_clean['temp_date'] >= '2026-01-01']

# Sort ascending
df_cal_clean = df_cal_clean.sort_values(by='temp_date', ascending=True)

# Format date cols
for date_col in ['INICIO', 'FINAL']:
    if date_col in df_cal_clean.columns:
        df_cal_clean[date_col] = df_cal_clean[date_col].astype(str).str.slice(0, 10)

df_cal_clean = df_cal_clean.drop(columns=['temp_date'])

print("Top 15 sorted 2026 events:")
print(df_cal_clean.head(15))
