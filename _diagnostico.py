import pandas as pd
import os

master = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
mineria = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\Mineria_DNIs.xlsx"

print("=" * 60)
print("DIAGNOSTICO DE INTEGRIDAD DE DATOS - CREAR LIMA")
print("=" * 60)

if os.path.exists(master):
    df = pd.read_excel(master, dtype=str).fillna("")
    print(f"\nMAESTER: {len(df)} registros totales")
    print(f"  -> DNIs duplicados: {df.duplicated(subset=['DNI']).sum()}")

    # Carnet de extranjeria: documentos no numericos o > 8 digitos
    def es_ce(x):
        s = str(x).strip()
        return len(s) >= 7 and not s.isdigit()
    
    ce = df[df['DNI'].apply(es_ce)]
    print(f"  -> Con Carnet Extranjeria / CE: {len(ce)}")
    if not ce.empty:
        print(ce[['Nombres','Apellidos','DNI']].head(10).to_string(index=False))

    # Duplicados por nombre normalizado
    import unicodedata, re
    def norm(t):
        s = str(t).strip().upper()
        s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        return re.sub(r'\s+', ' ', s).strip()

    df['_full'] = (df['Nombres'] + " " + df['Apellidos']).apply(norm)
    dups_nom = df[df.duplicated(subset=['_full'], keep=False) & (df['_full'] != "")]
    print(f"  -> Duplicados por nombre: {len(dups_nom)}")
    if not dups_nom.empty:
        print(dups_nom[['Nombres','Apellidos','DNI','_full']].head(20).to_string(index=False))
else:
    print("  [!] Master NO encontrado en la ruta especificada")

print("\n" + "=" * 60)

if os.path.exists(mineria):
    dm = pd.read_excel(mineria, dtype=str).fillna("")
    print(f"MINERIA: {len(dm)} DNIs procesados")
    for estado in ['VERIFICADO', 'VERIFICADO_TABLA', 'NO_ENCONTRADO', 'ERROR']:
        count = len(dm[dm['Estatus'] == estado])
        print(f"  -> {estado}: {count}")
else:
    print("Mineria_DNIs.xlsx aun no existe (bot no ha corrido).")

print("\n[OK] Diagnostico completado.")
