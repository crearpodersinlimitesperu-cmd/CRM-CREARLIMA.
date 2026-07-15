import pandas as pd
import os

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
df_cal = pd.read_excel(cal_path, sheet_name='LIM', dtype=str).fillna("—")
print("Original shape:", df_cal.shape)
valid_cols = ['INICIO', 'FINAL', 'ENTRENAMIENTO', 'EQUIPO', 'ENTRENADOR', 'LUGAR']
available_cols = [c for c in valid_cols if c in df_cal.columns]
print("Available columns:", available_cols)
df_cal_clean = df_cal[available_cols].dropna(subset=['ENTRENAMIENTO'] if 'ENTRENAMIENTO' in df_cal.columns else []).copy()
print("Cleaned shape:", df_cal_clean.shape)
if not df_cal_clean.empty:
    print("First 5 rows:")
    print(df_cal_clean.head(5))
