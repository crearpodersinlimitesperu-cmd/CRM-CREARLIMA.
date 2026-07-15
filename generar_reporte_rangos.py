import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

def generar_reporte_rangos():
    print("📊 GENERANDO REPORTE DE GRADUADOS POR RANGO")
    print("-" * 60)
    
    path_master = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\Master_Participantes_Limpio.csv"
    output_excel = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\Reporte_Lideres_Graduados.xlsx"
    
    try:
        df = pd.read_csv(path_master, dtype=str)
        
        # Filtrar a los que tienen rango y a los que son solo graduados
        df_lideres = df[df['Max Rango Historico'].notna() & (df['Max Rango Historico'] != "")]
        df_solo_graduados = df[(df['Tipo'] == "GRADUADO") & ((df['Max Rango Historico'].isna()) | (df['Max Rango Historico'] == ""))]
        
        if df_lideres.empty and df_solo_graduados.empty:
            print("❌ No se encontraron graduados en la base maestra.")
            return
            
        # Seleccionar columnas de interés
        cols = ['Nombre', 'Apellido', 'Teléfono', 'Tipo', 'Max Rango Historico', 'Historial Trayectoria']
        cols_existentes = [c for c in cols if c in df_lideres.columns]
        
        df_export = df_lideres[cols_existentes].copy()
        
        # Ordenar por jerarquía: Capitán, Manager, Quantum, Aliado
        jerarquia = {'Capitán': 1, 'Manager': 2, 'Quantum Team': 3, 'Aliado': 4}
        df_export['Orden'] = df_export['Max Rango Historico'].map(jerarquia).fillna(99)
        df_export = df_export.sort_values(['Orden', 'Nombre']).drop(columns=['Orden'])
        
        # Guardar en Excel con múltiples pestañas
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            # Pestaña 1: Todos los que tienen rol
            df_export.to_excel(writer, sheet_name='Todos_los_Líderes', index=False)
            
            # Crear una pestaña por cada rango
            for rango in df_export['Max Rango Historico'].unique():
                df_rango = df_export[df_export['Max Rango Historico'] == rango]
                nombre_pestana = str(rango).replace('á', 'a').replace('í', 'i')
                df_rango.to_excel(writer, sheet_name=f'Solo_{nombre_pestana}s', index=False)
                
            # Pestaña extra: Graduados sin rol asignado
            if not df_solo_graduados.empty:
                cols_grad = ['Nombre', 'Apellido', 'Teléfono', 'Tipo']
                cols_grad_existentes = [c for c in cols_grad if c in df_solo_graduados.columns]
                df_solo_graduados[cols_grad_existentes].to_excel(writer, sheet_name='Graduados_Sin_Rol', index=False)
                
        print(f"✅ Excel generado exitosamente en: {output_excel}")
        print("\nResumen de Líderes Encontrados:")
        print(df_export['Max Rango Historico'].value_counts().to_string())
        print(f"\nGraduados Base (Sin roles de liderazgo registrados): {len(df_solo_graduados)}")

    except Exception as e:
        print(f"❌ Error al generar el reporte: {e}")

if __name__ == "__main__":
    generar_reporte_rangos()
