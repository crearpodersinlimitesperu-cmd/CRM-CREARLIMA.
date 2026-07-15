import pandas as pd

path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\GERENCIA LIMA\LIMA -PRESUPUESTO 2026.xlsx"
df = pd.read_excel(path, sheet_name='Hoja1')
print(df.dropna(how='all').head(30))
