import sys
import os
import pandas as pd

sys.path.append(r"c:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA")
sys.path.append(r"c:\Users\josem\Downloads\bot-cpsl-review")

try:
    from sync_cloud import conectar_sheets
    c = conectar_sheets()
    if c:
        sh = c.open_by_key("1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y")
        for name in ["PRODUCTIVIDAD", "ASIGNACIONES", "HISTORIAL"]:
            try:
                ws = sh.worksheet(name)
                df = pd.DataFrame(ws.get_all_records())
                print(f"Worksheet '{name}': shape={df.shape}, columns={list(df.columns)}")
                if not df.empty:
                    print("Sample data:")
                    print(df.head(2))
                print("-" * 50)
            except Exception as e:
                print(f"Error reading '{name}': {e}")
except Exception as e:
    import traceback
    traceback.print_exc()
