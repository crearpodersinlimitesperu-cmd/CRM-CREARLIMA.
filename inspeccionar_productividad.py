import pandas as pd
import os

files = [
    r"C:\Users\josem\Downloads\productividad_coordinador.xlsx",
    r"C:\Users\josem\Downloads\productividad_coordinador (1).xlsx",
    r"C:\Users\josem\Downloads\productividad_coordinador (2).xlsx"
]

report = []
for f in files:
    if os.path.exists(f):
        try:
            df = pd.read_excel(f)
            report.append({
                "File": os.path.basename(f),
                "Columns": df.columns.tolist(),
                "Rows": len(df),
                "Sample": df.head(3).to_dict('records')
            })
        except Exception as e:
            report.append({"File": os.path.basename(f), "Error": str(e)})
    else:
        report.append({"File": os.path.basename(f), "Error": "Not found"})

for r in report:
    print(f"\n--- {r['File']} ---")
    if "Error" in r:
        print(f"Error: {r['Error']}")
    else:
        print(f"Columns: {r['Columns']}")
        print(f"Rows: {r['Rows']}")
        print("Sample Data:")
        for row in r['Sample']:
            print(row)
