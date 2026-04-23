import pandas as pd
import unicodedata

def normalize(text):
    if not text or pd.isna(text): return ""
    s = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def audit_grads():
    master_p = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    grads_p = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\GRADUADOS LIMA.xlsx"
    
    master = pd.read_excel(master_p)
    grads = pd.read_excel(grads_p)
    
    master['Norm'] = master.apply(lambda x: normalize(f"{x.get('Nombres','')} {x.get('Apellidos','')}"), axis=1)
    # Suponiendo que el excel de graduados tiene el nombre en una columna como 'CREAR CUANTICO' o 'NOMBRES'
    col_name = 'CREAR CUANTICO' if 'CREAR CUANTICO' in grads.columns else grads.columns[0]
    grads['Norm'] = grads[col_name].apply(normalize)
    
    missing = grads[~grads['Norm'].isin(master['Norm'])]
    
    print(f"Total Graduados en Excel: {len(grads)}")
    print(f"Graduados FALTANTES en Master: {len(missing)}")
    if not missing.empty:
        print("\nPrimeros 20 graduados faltantes (por qué no se encuentran?):")
        print(missing[col_name].head(20).to_string())

if __name__ == "__main__":
    audit_grads()
