import pandas as pd
import unicodedata
from difflib import SequenceMatcher

def normalize(text):
    if not text or pd.isna(text): return ""
    s = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def fuzzy_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

def audit_fuzzy_matches():
    master_p = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    grads_p = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\GRADUADOS LIMA.xlsx"
    
    master = pd.read_excel(master_p)
    grads = pd.read_excel(grads_p)
    
    master['Norm'] = master.apply(lambda x: normalize(f"{x.get('Nombres','')} {x.get('Apellidos','')}"), axis=1)
    col_name = 'CREAR CUANTICO' if 'CREAR CUANTICO' in grads.columns else grads.columns[0]
    
    missing_grads = grads[~grads[col_name].apply(normalize).isin(master['Norm'])]
    
    print(f"Buscando coincidencias para {len(missing_grads)} graduados faltantes...")
    
    matches = []
    for _, g_row in missing_grads.iterrows():
        g_name = normalize(g_row[col_name])
        best_match = None
        best_ratio = 0
        
        # Comparar con todo el universo del Master
        for _, m_row in master.iterrows():
            m_name = m_row['Norm']
            ratio = fuzzy_ratio(g_name, m_name)
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = f"{m_row.get('Nombres','')} {m_row.get('Apellidos','')}"
        
        if best_ratio > 0.8: # Umbral de confianza
            matches.append({
                "Graduado Faltante": g_row[col_name],
                "Sugerencia en Master": best_match,
                "Confianza": f"{best_ratio:.1%}"
            })
            
    if matches:
        print("\nCOINCIDENCIAS ENCONTRADAS (Para unificación automática):")
        print(pd.DataFrame(matches).to_string())
    else:
        print("\nNo se encontraron coincidencias automáticas claras.")

if __name__ == "__main__":
    audit_fuzzy_matches()
