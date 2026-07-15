import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
df_h2 = pd.read_excel(cal_path, sheet_name='Hoja2')
print(df_h2.iloc[38:52])
