import os
import glob
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

def encontrar_dnis():
    print("Mapeando archivos Excel y CSV para encontrar DNIs...")
    dirs = [
        r"C:\Users\josem\OneDrive\Documentos\campana-cpsl",
        r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\MAESTRIA DEL JUEGO GLOBAL"
    ]
    patterns = ["**/*.xlsx", "**/*.csv"]
    all_files = []
    for d in dirs:
        for p in patterns:
            all_files.extend(glob.glob(os.path.join(d, p), recursive=True))

    dni_list = {}
    for fpath in all_files:
        if "~$" in fpath: continue
        try:
            if fpath.endswith('.csv'):
                try: df = pd.read_csv(fpath, dtype=str, encoding='latin-1', on_bad_lines='skip')
                except: df = pd.read_csv(fpath, dtype=str, encoding='utf-8', on_bad_lines='skip')
            else:
                df = pd.read_excel(fpath, dtype=str)
            
            dni_col = next((c for c in df.columns if any(x in str(c).upper() for x in ['DNI', 'DOCUMENTO', 'IDENTIF'])), None)
            name_col = next((c for c in df.columns if any(x in str(c).upper() for x in ['NOMB', 'APELL', 'PARTICIPANTE'])), None)
            
            if dni_col:
                for idx, row in df.iterrows():
                    v = str(row[dni_col]).strip().split('.')[0]
                    v = ''.join(filter(str.isdigit, v))
                    if len(v) == 8:
                        dni_list[v] = str(row.get(name_col, '')).strip()
        except: pass
    return [{"DNI": k, "Nombre_Original": v} for k, v in dni_list.items()]

def procesar_un_dni(browser_context, item):
    dni = item['DNI']
    page = browser_context.new_page()
    try:
        page.goto("https://eldni.com/pe/buscar-datos-por-dni", wait_until="domcontentloaded", timeout=25000)
        page.locator("input#dni").fill(dni)
        page.locator("button#btn-buscar-datos-por-dni").click()
        try:
            page.wait_for_selector("input#nombres", timeout=7000)
            res_nom = page.locator("input#nombres").input_value()
            res_pat = page.locator("input#apellidop").input_value()
            res_mat = page.locator("input#apellidom").input_value()
            if res_nom:
                print(f"✅ {dni}: {res_nom}")
                page.close()
                return {"DNI": dni, "Nombre_Original": item['Nombre_Original'], "RENIEC_Nombres": res_nom.upper(), "RENIEC_Paterno": res_pat.upper(), "RENIEC_Materno": res_mat.upper(), "Estatus": "VERIFICADO"}
        except: pass
        page.close()
        return {"DNI": dni, "Nombre_Original": item['Nombre_Original'], "Estatus": "NO_ENCONTRADO"}
    except:
        page.close()
        return {"DNI": dni, "Nombre_Original": item['Nombre_Original'], "Estatus": "ERROR"}

def ejecutar_bot_multihilo(dnis_dicts):
    if not dnis_dicts: return
    output_path = "Mineria_DNIs.xlsx"
    resultados = []
    if os.path.exists(output_path):
        try:
            df_old = pd.read_excel(output_path)
            procesados = set(df_old['DNI'].astype(str))
            resultados = df_old.to_dict('records')
            dnis_dicts = [d for d in dnis_dicts if str(d['DNI']) not in procesados]
        except: pass
    
    if not dnis_dicts:
        print("¡Sincronización Completa!")
        return

    print(f"⚡ Minería Sónica Activada: {len(dnis_dicts)} pendientes con 3 hilos...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        batch_size = 15
        for i in range(0, len(dnis_dicts), batch_size):
            batch = dnis_dicts[i:i+batch_size]
            with ThreadPoolExecutor(max_workers=3) as executor:
                batch_results = list(executor.map(lambda x: procesar_un_dni(context, x), batch))
            resultados.extend(batch_results)
            pd.DataFrame(resultados).to_excel(output_path, index=False)
            print(f"📦 Lote {i//batch_size + 1} blindado. Total: {len(resultados)}")
        browser.close()

if __name__ == '__main__':
    dnis = encontrar_dnis()
    ejecutar_bot_multihilo(dnis)
