import pandas as pd
import os

path = r"c:\Users\josem\Downloads\presupuesto_maestro.xlsx"
print(f"File exists: {os.path.exists(path)}")
if os.path.exists(path):
    xl = pd.ExcelFile(path)
    print("Sheets in budget master:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        print(f"Sheet '{sheet}': shape={df.shape}, columns={list(df.columns)}")
        if not df.empty:
            print(f"Sample data from '{sheet}':")
            print(df.head(2))
            print("-" * 50)
