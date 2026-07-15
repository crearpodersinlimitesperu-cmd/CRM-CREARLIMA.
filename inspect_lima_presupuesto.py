import pandas as pd
import os

path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\GERENCIA LIMA\LIMA -PRESUPUESTO 2026.xlsx"
print(f"File exists: {os.path.exists(path)}")
if os.path.exists(path):
    xl = pd.ExcelFile(path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        print(f"Sheet '{sheet}': shape={df.shape}, columns={list(df.columns)}")
        if not df.empty:
            print(df.head(2))
            print("-" * 50)
