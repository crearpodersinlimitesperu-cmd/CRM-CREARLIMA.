import pandas as pd
import numpy as np
import os
import sys

# Configurar encoding
sys.stdout.reconfigure(encoding='utf-8')

def generar_cierre_final_220():
    print("🏆 REPORTE OFICIAL DE CIERRE C1E27 - 220 PARTICIPANTES")
    print("-" * 65)
    
    try:
        # 1. CARGA DE SENTADOS OFICIALES (Archivo 3 - Los 220)
        df_asis = pd.read_excel(r"C:\Users\josem\Downloads\participantes_asistencia (3).xlsx")
        # El conteo dio 220 con valor "CONFIRMADO"
        df_sentados = df_asis[df_asis.iloc[:, 1] == "CONFIRMADO"].copy()
        df_sentados['DNI'] = df_sentados.iloc[:, 4].astype(str).str.strip().str.replace('.0', '', regex=False)
        
        print(f"✅ Sentados Validados: {len(df_sentados)}")

        # 2. CARGA DE ASIGNACIONES (Pendientes/Universo)
        path_asig = r"C:\Users\josem\Downloads\Reportes y Gestión\Asignacion_C1.xlsx"
        df_asig = pd.read_excel(path_asig)
        df_asig.columns = [str(c).replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_asig.columns]
        df_asig['DNI'] = df_asig['Identificacion'].astype(str).str.strip().str.replace('.0', '', regex=False)

        # 3. MAPEADOR DE COORDINADORAS
        def mapear_coord(user):
            u = str(user).lower().strip()
            if 'dmoscoso' in u: return 'Diana Moscoso'
            if 'jmarin' in u: return 'Joyce Marin'
            if 'zurteaga' in u: return 'Zuley Urteaga'
            if 'lvalencia' in u: return 'Lvalencia'
            return u.title()

        # Ranking de los 220 sentados
        # El archivo (3) trae el "Usuario Segumiento" directo
        df_sentados['Coord'] = df_sentados['Usuario Segumiento'].apply(mapear_coord)
        ranking_sentados = df_sentados.groupby('Coord').size()

        # Ranking de los que quedaron pendientes (del archivo de asignación)
        df_asig['Coord'] = df_asig['Usuario Registro'].apply(mapear_coord)
        ranking_pendientes = df_asig.groupby('Coord').size()

        # Consolidar
        final_ranking = pd.DataFrame({
            'Sentados (Logro)': ranking_sentados,
            'Pendientes (No asistió)': ranking_pendientes
        }).fillna(0).astype(int)

        final_ranking['Universo_Total'] = final_ranking['Sentados (Logro)'] + final_ranking['Pendientes (No asistió)']
        final_ranking['Efectividad (%)'] = (final_ranking['Sentados (Logro)'] / final_ranking['Universo_Total'] * 100).round(1)
        final_ranking = final_ranking.sort_values('Sentados (Logro)', ascending=False)

        # 4. REPORTE FINAL
        print(f"📊 RESULTADOS FINALES IRREFUTABLES")
        print(f"✅ Total Sentados (Confirmados): {len(df_sentados)}")
        print(f"✅ Total Pendientes (Asignados): {len(df_asig)}")
        print(f"✅ Universo Gestionado:         {len(df_sentados) + len(df_asig)}")
        print("\n🏆 RANKING OFICIAL DE CIERRE:")
        print(final_ranking.to_string())

        # EXPORTAR EXCEL DE CIERRE IRREFUTABLE
        output_path = r"C:\Users\josem\Downloads\REPORTE_FINAL_220_SENTADOS_C1E27.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            final_ranking.to_excel(writer, sheet_name='Ranking Final')
            df_sentados[['Identificaci\u00f3n' if 'Identificaci\u00f3n' in df_sentados.columns else 'DNI', 'Nombre Completo', 'Apellido Completo', 'Coord', 'Nombre IMO']].to_excel(writer, sheet_name='Detalle 220 Sentados', index=False)

        print(f"\n📁 REPORTE FINAL GENERADO: {output_path}")
        print("-" * 65)

    except Exception as e:
        print(f"❌ Error en cierre 220: {e}")

if __name__ == "__main__":
    generar_cierre_final_220()
