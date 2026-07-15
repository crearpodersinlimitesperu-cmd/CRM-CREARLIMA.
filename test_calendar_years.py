import pandas as pd

cal_path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\PROGRAMACION 2026 CREAR LIMA.xlsx"
df_cal = pd.read_excel(cal_path, sheet_name='LIM', dtype=str).fillna("—")
df_cal['AÑO'] = df_cal['INICIO'].astype(str).str.slice(0, 4)
print("Year distribution:")
print(df_cal['AÑO'].value_counts())
print("-" * 50)
print("Let's look at 2026 events:")
df_2026 = df_cal[df_cal['AÑO'] == '2026']
print("Number of 2026 events:", len(df_2026))
if not df_2026.empty:
    print(df_2026.head(10))
