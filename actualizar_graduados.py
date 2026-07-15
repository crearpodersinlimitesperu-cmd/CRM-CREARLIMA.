import pandas as pd
import sys
import difflib

sys.stdout.reconfigure(encoding='utf-8')

def actualizar_graduados():
    print("🎓 INICIANDO ACTUALIZACIÓN DE GRADUADOS EN BASE MAESTRA")
    print("-" * 60)
    
    path_graduados = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\GRADUADOS LIMA.xlsx"
    path_master = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\Master_Participantes_Limpio.csv"
    
    try:
        # 1. Leer nombres de graduados
        print("📖 Leyendo la pestaña 'GRADUADOS '...")
        df_graduados = pd.read_excel(path_graduados, sheet_name="GRADUADOS ")
        
        # Filtrar valores nulos y normalizar textos
        nombres_graduados = df_graduados['CREAR CUANTICO'].dropna().astype(str).str.strip().str.upper().tolist()
        print(f"✅ Se detectaron {len(nombres_graduados)} graduados en el archivo de Excel.")
        
        # 2. Leer Master
        print("\n📖 Leyendo Base de Datos General (Master)...")
        df_master = pd.read_csv(path_master, dtype=str)
        
        # Crear columna de nombre completo en master para comparar
        if 'NombreCompletoFuzzy' not in df_master.columns:
            # Algunas veces las columnas son Nombre y Apellido, otras Nombre Completo.
            if 'Nombre' in df_master.columns and 'Apellido' in df_master.columns:
                df_master['NombreCompletoFuzzy'] = (df_master['Nombre'].fillna("") + " " + df_master['Apellido'].fillna("")).str.strip().str.upper()
            else:
                print("❌ No se encontraron columnas Nombre/Apellido en el Master.")
                return
                
        total_master = len(df_master)
        
        # 3. Cruzar datos (Búsqueda exacta primero, luego fuzzy si es necesario)
        print("🔍 Cruzando datos...")
        encontrados = 0
        no_encontrados = []
        
        nombres_master_list = df_master['NombreCompletoFuzzy'].tolist()
        
        for nombre_grad in nombres_graduados:
            if nombre_grad in nombres_master_list:
                # Coincidencia exacta
                idx = df_master[df_master['NombreCompletoFuzzy'] == nombre_grad].index
                df_master.loc[idx, 'Tipo'] = 'GRADUADO'
                encontrados += 1
            else:
                # Fuzzy matching leve para errores de tipeo
                coincidencias = difflib.get_close_matches(nombre_grad, nombres_master_list, n=1, cutoff=0.90)
                if coincidencias:
                    mejor_match = coincidencias[0]
                    idx = df_master[df_master['NombreCompletoFuzzy'] == mejor_match].index
                    df_master.loc[idx, 'Tipo'] = 'GRADUADO'
                    encontrados += 1
                else:
                    no_encontrados.append(nombre_grad)
                    
        # Limpiar columna temporal
        df_master = df_master.drop(columns=['NombreCompletoFuzzy'])
        
        # 4. Guardar
        df_master.to_csv(path_master, index=False)
        
        print("\n" + "-" * 60)
        print("🎯 ACTUALIZACIÓN COMPLETADA")
        print(f"✔️ Graduados mapeados exitosamente y marcados en CRM: {encontrados}")
        print(f"⚠️ Graduados no encontrados en la base maestra: {len(no_encontrados)}")
        
        if no_encontrados:
            with open("graduados_no_encontrados.txt", "w", encoding="utf-8") as f:
                f.write("--- Graduados no encontrados en la Base Maestra ---\n")
                for n in no_encontrados:
                    f.write(f"{n}\n")
            print("📁 Se generó 'graduados_no_encontrados.txt' para revisión manual.")

    except Exception as e:
        print(f"❌ Error en la actualización: {e}")

if __name__ == "__main__":
    actualizar_graduados()
