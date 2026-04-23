import pandas as pd

def audit_353():
    master_p = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    df = pd.read_excel(master_p)
    
    graduates = df[df['Estatus MJ'].str.contains('GRADUADO', na=False, case=False)]
    
    print(f"Total Graduados en Master: {len(graduates)}")
    
    # 1. Cuántos tienen trayectoria (Vienen de la lista de 318)
    con_tray = graduates[graduates['Trayectoria'] != '—']
    sin_tray = graduates[graduates['Trayectoria'] == '—']
    
    print(f"\nDistribución:")
    print(f" - Graduados con Trayectoria (Oficiales 318): {len(con_tray)}")
    print(f" - Graduados SIN Trayectoria (Infiltrados/Legacy): {len(sin_tray)}")
    
    if not sin_tray.empty:
        print("\nPrimeros 10 graduados sin trayectoria vinculada (Legacy/Duplicados?):")
        print(sin_tray[['Nombres', 'Apellidos', 'DNI']].head(10).to_string())
        
    # 2. Verificar duplicados por nombre en los graduados
    dups = graduates[graduates.duplicated(subset=['Nombres', 'Apellidos'], keep=False)]
    if not dups.empty:
        print(f"\nALERT: Se encontraron {len(dups)} registros de graduados que parecen duplicados por nombre.")
        print(dups[['Nombres', 'Apellidos', 'DNI', 'Trayectoria']].sort_values('Nombres').head(10).to_string())

if __name__ == "__main__":
    audit_353()
