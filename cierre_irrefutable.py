import pandas as pd
import numpy as np
import os
import sys

# Configurar encoding
sys.stdout.reconfigure(encoding='utf-8')

def cierre_definitivo_c1e27():
    print("💎 CIERRE OFICIAL DE CAMPAÑA C1E27 - VERDAD DEFINITIVA")
    print("-" * 65)
    
    try:
        # 1. CARGA DE SENTADOS OFICIALES (OneDrive)
        path_sent = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\KPIS C1E27.xlsx"
        df_sent = pd.read_excel(path_sent)
        df_sent.columns = [str(c).replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_sent.columns]
        
        # Filtramos solo los que efectivamente están marcados como CONFIRMADO/SENTADO
        df_sent_real = df_sent[df_sent['Asistencia'].astype(str).str.upper().str.contains("CONFIRMADO|SENTADO|SI|✓|✔", na=False)].copy()
        df_sent_real['DNI'] = df_sent_real['Identificacion'].astype(str).str.strip().str.replace('.0', '', regex=False)
        total_sentados = len(df_sent_real)

        # 2. CARGA DE ASIGNACIONES (Pendientes/Universo)
        path_asig = r"C:\Users\josem\Downloads\Reportes y Gestión\Asignacion_C1.xlsx"
        df_asig = pd.read_excel(path_asig)
        df_asig.columns = [str(c).replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_asig.columns]
        df_asig['DNI'] = df_asig['Identificacion'].astype(str).str.strip().str.replace('.0', '', regex=False)
        total_pendientes = len(df_asig)

        # 3. UNIFICACIÓN DE UNIVERSO
        def mapear_coord(user):
            u = str(user).lower().strip()
            if 'dmoscoso' in u: return 'Diana Moscoso'
            if 'jmarin' in u: return 'Joyce Marin'
            if 'zurteaga' in u: return 'Zuley Urteaga'
            if 'lvalencia' in u: return 'Lvalencia'
            return u.title()

        # Preparar data para el Ranking
        # De los sentados:
        df_sent_real['Coord'] = df_sent_real['usuarioSeguimiento'].apply(mapear_coord)
        ranking_sentados = df_sent_real.groupby('Coord').size()

        # De los pendientes:
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
        print(f"📊 RESULTADOS FINALES CONSOLIDADOS")
        print(f"✅ Total Sentados (Confirmados): {total_sentados}")
        print(f"✅ Total Pendientes (Asignados): {total_pendientes}")
        print(f"✅ Universo Inicial:           {total_sentados + total_pendientes}")
        print("\n🏆 RANKING OFICIAL DE CIERRE:")
        print(final_ranking.to_string())

        # EXPORTAR EXCEL DE CIERRE IRREFUTABLE
        output_path = r"C:\Users\josem\Downloads\REPORTE_CIERRE_IRREFUTABLE_C1E27.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            final_ranking.to_excel(writer, sheet_name='Ranking Final')
            df_sent_real[['DNI', 'NombreCompleto', 'ApellidoCompleto', 'Coord', 'NombreIMO']].to_excel(writer, sheet_name='Detalle Sentados', index=False)
            df_asig[['DNI', 'NombreCompleto', 'ApellidoCompleto', 'Coord', 'IdentificacionIMO']].to_excel(writer, sheet_name='Detalle Pendientes', index=False)

        print(f"\n📁 REPORTE GENERADO: {output_path}")
        print("-" * 65)

    except Exception as e:
        print(f"❌ Error en cierre definitivo: {e}")

if __name__ == "__main__":
    cierre_definitivo_c1e27()
