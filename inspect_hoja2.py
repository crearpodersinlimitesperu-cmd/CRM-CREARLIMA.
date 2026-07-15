import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
df_h2 = pd.read_excel(cal_path, sheet_name='Hoja2')
print("Hoja2 shape:", df_h2.shape)
print("Hoja2 columns:", list(df_h2.columns))
print("Hoja2 data:")
print(df_h2.head(20))
