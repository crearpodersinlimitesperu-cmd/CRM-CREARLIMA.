import pandas as pd

path = r"c:\Users\josem\Downloads\presupuesto_maestro.xlsx"
df_mov = pd.read_excel(path, sheet_name="Movimientos")
print("Rows with Categoria == 'Ingreso':", len(df_mov[df_mov['Categoria'] == 'Ingreso']))
if not df_mov[df_mov['Categoria'] == 'Ingreso'].empty:
    print(df_mov[df_mov['Categoria'] == 'Ingreso'].head(5))
