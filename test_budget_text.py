import pandas as pd
import os

path = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\GERENCIA LIMA\LIMA -PRESUPUESTO 2026.xlsx"
if os.path.exists(path):
    df = pd.read_excel(path, sheet_name='Hoja1')
    lines = []
    for idx, row in df.iterrows():
        # Represent only non-empty rows
        vals = [str(v).strip() for v in row.values]
        # Keep if not all are nan/empty
        non_empty = [v for v in vals if v != 'nan' and v != '—' and v != '']
        if len(non_empty) > 1:
            lines.append(" | ".join([f"{df.columns[i]}: {vals[i]}" for i in range(len(vals)) if vals[i] != 'nan']))
    print("Formatted sample:")
    for line in lines[:20]:
        print(line)
