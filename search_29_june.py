import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
xl = pd.ExcelFile(cal_path)

for name in xl.sheet_names:
    df = xl.parse(name)
    df_str = df.astype(str)
    mask = df_str.apply(lambda x: x.str.contains('29', case=False, na=False))
    if mask.any().any():
        print(f"Sheet '{name}' contains '29' matches!")
        rows = df[mask.any(axis=1)]
        # Filter for rows that mention junio or june or 06
        for col in rows.columns:
            matches = rows[rows[col].astype(str).str.contains('junio|june|06|jun', case=False, na=False)]
            if not matches.empty:
                print(matches)
                print("=" * 50)
