import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
xl = pd.ExcelFile(cal_path)
df_h2 = xl.parse('Hoja2')
print(df_h2[df_h2.astype(str).apply(lambda x: x.str.contains('CAPITULO UNO', case=False, na=False)).any(axis=1)])
