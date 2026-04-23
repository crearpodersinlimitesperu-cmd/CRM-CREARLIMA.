import pandas as pd
import unicodedata
import os

def normalize(text):
    if not text or pd.isna(text): return ""
    s = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def scan_all_leadership():
    file_p = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\GRADUADOS LIMA.xlsx"
    xl = pd.ExcelFile(file_p)
    
    all_names = {} # Name -> Set of Roles
    
    print(f"Escaneando {len(xl.sheet_names)} hojas de liderazgo...")
    
    for sheet in xl.sheet_names:
        # Determinar rol por nombre de hoja
        role = "APOYO"
        s_upper = sheet.upper()
        if "ALIADO" in s_upper: role = "ALIADO"
        elif "MANAGER" in s_upper: role = "MANAGER"
        elif "CAP" in s_upper or "CAPITAN" in s_upper: role = "CAPITÁN"
        elif "QT" in s_upper or "QUANTUM" in s_upper: role = "QUANTUM TEAM"
        elif "SOMBRA" in s_upper: role = "SOMBRA"
        
        try:
            # Leer sin headers y buscar nombres en la col 0
            df = pd.read_excel(file_p, sheet_name=sheet, header=None).fillna("")
            for _, row in df.iterrows():
                name_raw = str(row[0]).strip()
                if not name_raw or len(name_raw) < 5 or any(x in name_raw.upper() for x in ['CAPITAN', 'NOMBRES', 'CREAR']): continue
                
                norm = normalize(name_raw)
                if norm not in all_names:
                    all_names[norm] = {"Name": name_raw.title(), "Roles": set()}
                all_names[norm]["Roles"].add(role)
        except: pass
        
    print(f"\n--- RESULTADO DEL ESCANEO ---")
    print(f"Total de personas únicas encontradas: {len(all_names)}")
    
    # Ver si llegamos cerca a los 318
    # O tal vez hay una hoja específica que no he visto bien
    
    # Mostrar conteo por rol
    role_counts = {"ALIADO": 0, "MANAGER": 0, "CAPITÁN": 0, "QUANTUM TEAM": 0, "SOMBRA": 0, "APOYO": 0}
    for n, data in all_names.items():
        for r in data["Roles"]:
            role_counts[r] += 1
            
    for r, count in role_counts.items():
        print(f" - {r}: {count}")

if __name__ == "__main__":
    scan_all_leadership()
