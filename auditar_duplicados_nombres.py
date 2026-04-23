import pandas as pd
import unicodedata
import os

def normalize(text):
    if not text or pd.isna(text): return ""
    s = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def auditar():
    p = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    if not os.path.exists(p): return
    
    df = pd.read_excel(p)
    df['Norm_Name'] = df.apply(lambda x: normalize(f"{x['Nombres']} {x['Apellidos']}"), axis=1)
    
    # Buscar duplicados por nombre normalizado
    dups = df[df.duplicated('Norm_Name', keep=False)].copy()
    dups = dups.sort_values('Norm_Name')
    
    print(f"Total registros con nombres duplicados: {len(dups)}")
    if not dups.empty:
        print("\nEjemplos de Duplicados por Nombre:")
        print(dups[['Nombres', 'Apellidos', 'DNI', 'Participación', 'Origen/Equipo', 'Coordinador']].head(30).to_string())
        
        # Guardar auditoria para analisis
        dups.to_csv("auditoria_duplicados.csv", index=False)

if __name__ == "__main__":
    auditar()
