import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
xl = pd.ExcelFile(cal_path)
df_lim = xl.parse('LIM')
cols = ['INICIO', 'FINAL', 'ENTRENAMIENTO', 'EQUIPO', 'ENTRENADOR']
avail_cols = [c for c in cols if c in df_lim.columns]
print(df_lim[avail_cols].iloc[280:290])
