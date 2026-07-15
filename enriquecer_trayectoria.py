import pandas as pd
import difflib
import sys

# Forzar encoding para consola Windows
sys.stdout.reconfigure(encoding='utf-8')

# Definir jerarquía de rangos (Mayor número = Rango más alto)
JERARQUIA_RANGOS = {
    'C': (4, 'Capitán'),
    'M': (3, 'Manager'),
    'Q': (2, 'Quantum Team'),
    'A': (1, 'Aliado')
}

def enriquecer_trayectoria():
    print("🚀 INICIANDO EXTRACCIÓN DE TRAYECTORIA Y RANGOS")
    print("-" * 60)
    
    path_graduados = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\temp_graduados.xlsx"
    path_master = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\Master_Participantes_Limpio.csv"
    
    try:
        # 1. Leer archivo de graduados
        print("📖 Leyendo la matriz de trayectoria desde Excel...")
        df_graduados = pd.read_excel(path_graduados, sheet_name="GRADUADOS ")
        
        # 2. Leer Master de CRM
        print("📖 Leyendo Base de Datos General (CRM)...")
        df_master = pd.read_csv(path_master, dtype=str)
        
        # Asegurar que existan las columnas destino en el master
        if 'Max Rango Historico' not in df_master.columns:
            df_master['Max Rango Historico'] = ""
        if 'Historial Trayectoria' not in df_master.columns:
            df_master['Historial Trayectoria'] = ""
            
        # Crear columna temporal para búsqueda si no existe
        if 'NombreCompletoFuzzy' not in df_master.columns:
            df_master['NombreCompletoFuzzy'] = (df_master['Nombre'].fillna("") + " " + df_master['Apellido'].fillna("")).str.strip().str.upper()
            
        nombres_master_list = df_master['NombreCompletoFuzzy'].tolist()
        
        # Extraer nombres de las columnas de eventos (E5, E6... E28)
        columnas_eventos = [c for c in df_graduados.columns if str(c).startswith('E') and str(c)[1:].isdigit()]
        
        encontrados = 0
        actualizados = 0
        
        print("🔍 Procesando historial por participante...")
        for index, row in df_graduados.iterrows():
            nombre_raw = str(row.get('CREAR CUANTICO', '')).strip().upper()
            if nombre_raw == 'NAN' or not nombre_raw:
                continue
                
            # Procesar el historial de esta persona
            historial = []
            max_score = 0
            max_rango = ""
            
            for col_evt in columnas_eventos:
                val = str(row.get(col_evt, '')).strip().upper()
                if val in JERARQUIA_RANGOS:
                    # Guardar en el historial (ej: E15:C)
                    historial.append(f"{col_evt}:{val}")
                    
                    # Calcular si es el rango más alto
                    score, nombre_rango = JERARQUIA_RANGOS[val]
                    if score > max_score:
                        max_score = score
                        max_rango = nombre_rango
            
            # Solo actualizar si tiene algo en el historial
            if max_rango:
                str_historial = " | ".join(historial)
                
                # Buscar en el master
                # Intento 1: Exacto o muy similar
                coincidencias = difflib.get_close_matches(nombre_raw, nombres_master_list, n=1, cutoff=0.90)
                mejor_match = coincidencias[0] if coincidencias else None
                
                # Intento 2: Intersección de palabras (para nombres incompletos)
                if not mejor_match:
                    grad_words = set(nombre_raw.split())
                    best_score = 0
                    for mn in nombres_master_list:
                        mn_words = set(mn.split())
                        if mn_words and grad_words:
                            intersect = len(mn_words.intersection(grad_words))
                            if intersect >= 2: # Al menos 2 palabras coinciden (Nombre y Apellido)
                                score = intersect / max(len(mn_words), len(grad_words))
                                if score > best_score:
                                    best_score = score
                                    mejor_match = mn
                    if best_score <= 0.4:
                        mejor_match = None

                if mejor_match:
                    idx = df_master[df_master['NombreCompletoFuzzy'] == mejor_match].index
                    
                    # Actualizar las celdas
                    df_master.loc[idx, 'Max Rango Historico'] = max_rango
                    df_master.loc[idx, 'Historial Trayectoria'] = str_historial
                    
                    actualizados += 1
                    
        # Limpieza
        df_master = df_master.drop(columns=['NombreCompletoFuzzy'])
        
        # Guardar archivo maestro
        df_master.to_csv(path_master, index=False)
        
        print("\n" + "-" * 60)
        print("🎯 EXTRACCIÓN Y CRUCE COMPLETADO")
        print(f"✔️ Graduados con trayectoria inyectada en el CRM: {actualizados}")
        print("Ahora la base maestra cuenta con los campos 'Max Rango Historico' y 'Historial Trayectoria'.")

    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")

if __name__ == "__main__":
    enriquecer_trayectoria()
