import pandas as pd
import requests

SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

print("Downloading Google Sheet...")
res = requests.get(url)
print("Response size:", len(res.content))
if res.status_code == 200:
    xl = pd.ExcelFile(res.content)
    print("Sheets in Excel download:", xl.sheet_names)
    for name in xl.sheet_names:
        df = xl.parse(name)
        print(f"Sheet '{name}': shape={df.shape}")
else:
    print("Error downloading sheet:", res.status_code)
