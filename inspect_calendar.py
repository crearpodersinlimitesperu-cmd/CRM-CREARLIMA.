import pandas as pd
import os

path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
print(f"File exists: {os.path.exists(path)}")
if os.path.exists(path):
    xl = pd.ExcelFile(path)
    print("Sheets in Calendar:", xl.sheet_names)
    for sheet in xl.sheet_names:
        try:
            df = xl.parse(sheet)
            print(f"Sheet '{sheet}': shape={df.shape}, columns={list(df.columns)}")
            if not df.empty:
                print(f"Sample data from '{sheet}':")
                print(df.head(2))
                print("-" * 50)
        except Exception as e:
            print(f"Error parsing sheet '{sheet}': {e}")
