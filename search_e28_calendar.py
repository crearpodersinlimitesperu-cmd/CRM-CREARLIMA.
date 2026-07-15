import pandas as pd
import os

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
xl = pd.ExcelFile(cal_path)
for name in xl.sheet_names:
    df = xl.parse(name)
    df_str = df.astype(str)
    mask = df_str.apply(lambda x: x.str.contains('E28|EQUIPO 28', case=False, na=False))
    if mask.any().any():
        print(f"Sheet '{name}' contains E28 matches!")
        rows = df[mask.any(axis=1)]
        print(rows)
        print("-" * 50)
