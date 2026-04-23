import pandas as pd
import os

def audit():
    master_p = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    cache_p = "Mineria_DNIs.xlsx"
    
    print("--- AUDITORIA DE CONGRUENCIA LÓGICA ---")
    
    if os.path.exists(master_p):
        df = pd.read_excel(master_p)
        print(f"Total Registros (Unificado): {len(df)}")
        print(f"Verificados en Master: {len(df[df['Verificado_RENIEC'] == 'SI'])}")
        print(f"Pendientes en Master: {len(df[df['Verificado_RENIEC'] != 'SI'])}")
    
    if os.path.exists(cache_p):
        cache = pd.read_excel(cache_p)
        print(f"\nTotal Cache Robot: {len(cache)}")
        print(f"Encontrados en Cache: {len(cache[cache['Estatus'].str.contains('VERIFICADO', na=False)])}")
        print(f"No Encontrados/Error: {len(cache[~cache['Estatus'].str.contains('VERIFICADO', na=False)])}")
        
        # Últimas 5 acciones del robot
        print("\nÚltimas 5 acciones del Robot:")
        print(cache.tail(5)[['DNI', 'Estatus']].to_string())

if __name__ == "__main__":
    audit()
