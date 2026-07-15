import os
from dotenv import load_dotenv
load_dotenv()
from sync_cloud import load_productividad_cloud, conectar_sheets
import pandas as pd

df = load_productividad_cloud()
print("PROD COLUMNS:", df.columns.tolist())

client = conectar_sheets()
if client:
    sh = client.open_by_key("1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y")
    try:
        ws = sh.worksheet("GESTION_LLAMADAS")
        df_g = pd.DataFrame(ws.get_all_records())
        print("GESTION COLUMNS:", df_g.columns.tolist())
    except Exception as e:
        print("Error GESTION:", e)
