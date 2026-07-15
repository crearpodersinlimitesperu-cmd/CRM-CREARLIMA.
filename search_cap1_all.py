import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
xl = pd.ExcelFile(cal_path)

for name in xl.sheet_names:
    df = xl.parse(name)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df_str = df.astype(str)
    mask = df_str.apply(lambda x: x.str.contains('CAPITULO UNO', case=False, na=False))
    if mask.any().any():
        print(f"Sheet '{name}' has CAPITULO UNO:")
        print(df[mask.any(axis=1)])
        print("-" * 50)
