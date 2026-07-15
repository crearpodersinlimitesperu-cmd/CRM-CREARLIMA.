import sys
import os

sys.path.append(r"c:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA")
sys.path.append(r"c:\Users\josem\Downloads\bot-cpsl-review")

try:
    from sync_cloud import conectar_sheets
    c = conectar_sheets()
    if c:
        print("Connected to Google Sheets successfully!")
        sh = c.open_by_key("1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y")
        print("Document Title:", sh.title)
        worksheets = sh.worksheets()
        print("Worksheets:")
        for ws in worksheets:
            print(f"- {ws.title} (rows={ws.row_count}, cols={ws.col_count})")
    else:
        print("Failed to get sheet client (conectar_sheets returned None).")
except Exception as e:
    import traceback
    traceback.print_exc()
