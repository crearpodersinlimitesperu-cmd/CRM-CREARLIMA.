import pandas as pd
import numpy as np
import os
import sys

# Configurar encoding
sys.stdout.reconfigure(encoding='utf-8')

def generar_kpis_finales_c1e27():
    print("🏆 GENERANDO RANKING FINAL DE CIERRE - CAMPAÑA C1E27")
    print("-" * 60)
    
    try:
        # 1. CARGA DE SENTADOS (Oficial)
        df_asis = pd.read_excel(r"C:\Users\josem\Downloads\participantes_asistencia (2).xlsx")
        df_asis.columns = [str(c).replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_asis.columns]
        df_asis['DNI'] = df_asis['Identificacion'].astype(str).str.strip().str.replace('.0', '', regex=False)
        total_sentados = len(df_asis)

        # 2. CARGA DE PENDIENTES (Asignación actual filtrada)
        path_asig = r"C:\Users\josem\Downloads\Reportes y Gestión\Asignacion_C1.xlsx"
        df_asig_pend = pd.read_excel(path_asig)
        df_asig_pend.columns = [str(c).replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_asig_pend.columns]
        df_asig_pend['DNI'] = df_asig_pend['Identificacion'].astype(str).str.strip().str.replace('.0', '', regex=False)
        total_pendientes = len(df_asig_pend)

        # 3. MAPEADOR DE COORDINADORAS
        def mapear_coord(user):
            u = str(user).lower().strip()
            if 'dmoscoso' in u: return 'Diana Moscoso'
            if 'jmarin' in u: return 'Joyce Marin'
            if 'zurteaga' in u: return 'Zuley Urteaga'
            if 'lvalencia' in u: return 'Lvalencia'
            return u.title()

        # 4. DETERMINAR COORDINADORA DE SENTADOS (Buscando en históricos)
        prod_files = [
            r"C:\Users\josem\Downloads\productividad_coordinador.xlsx",
            r"C:\Users\josem\Downloads\productividad_coordinador (1).xlsx",
            r"C:\Users\josem\Downloads\productividad_coordinador (2).xlsx"
        ]
        df_hist = pd.concat([pd.read_excel(f) for f in prod_files if os.path.exists(f)]).drop_duplicates(subset=['ClienteId'], keep='last')
        df_hist['DNI'] = df_hist['ClienteId'].astype(str).str.strip().str.replace('.0', '', regex=False)
        
        # Mapeo DNI -> Coordinadora (desde historial o desde el mismo archivo de asistencia si trae el dato)
        mapping_hist = df_hist.set_index('DNI')['Usuario Seguimiento'].to_dict()
        
        def identificar_coord_sentado(row):
            dni = str(row['DNI'])
            # Prioridad 1: Columna del archivo de asistencia (Usuario Segumiento)
            if 'Usuario Segumiento' in row and str(row['Usuario Segumiento']) != 'nan' and row['Usuario Segumiento'] != '':
                return mapear_coord(row['Usuario Segumiento'])
            # Prioridad 2: Buscar en historial de productividad por DNI
            if dni in mapping_hist:
                return mapear_coord(mapping_hist[dni])
            return "Desconocido"

        df_asis['Coordinadora_Final'] = df_asis.apply(identificar_coord_sentado, axis=1)
        df_asig_pend['Coordinadora_Final'] = df_asig_pend['Usuario Registro'].apply(mapear_coord)

        # 5. CONSOLIDACIÓN DE UNIVERSO (Sentados + Pendientes)
        res_sentados = df_asis.groupby('Coordinadora_Final').size()
        res_pendientes = df_asig_pend.groupby('Coordinadora_Final').size()

        ranking = pd.DataFrame({
            'Sentados': res_sentados,
            'Pendientes': res_pendientes
        }).fillna(0).astype(int)

        ranking['Total_Universo'] = ranking['Sentados'] + ranking['Pendientes']
        ranking['Efectividad (%)'] = (ranking['Sentados'] / ranking['Total_Universo'] * 100).round(1)
        ranking = ranking.sort_values('Sentados', ascending=False)

        # 6. REPORTE FINAL
        print(f"📊 RESUMEN GLOBAL DE CIERRE")
        print(f"✅ Total Sentados (En Salón): {total_sentados}")
        print(f"✅ Total Pendientes (No llegaron): {total_pendientes}")
        print(f"✅ Universo Inicial Gestionado: {total_sentados + total_pendientes}")
        print("\n🏆 RANKING DE CIERRE POR COORDINADORA:")
        print(ranking.to_string())

        # EXPORTAR EXCEL DE CIERRE OFICIAL
        output_path = r"C:\Users\josem\Downloads\KPI_CIERRE_OFICIAL_RECONSTRUIDO.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            ranking.to_excel(writer, sheet_name='Ranking Final')
            df_asis[['DNI', 'Nombre Completo', 'Apellido Completo', 'Coordinadora_Final']].to_excel(writer, sheet_name='Detalle Sentados', index=False)
            df_asig_pend[['DNI', 'NombreCompleto', 'ApellidoCompleto', 'Coordinadora_Final']].to_excel(writer, sheet_name='Detalle Pendientes', index=False)

        print(f"\n📁 EXCEL DE CIERRE OFICIAL GENERADO: {output_path}")
        print("-" * 60)

    except Exception as e:
        print(f"❌ Error reconstruyendo KPIs: {e}")

if __name__ == "__main__":
    generar_kpis_finales_c1e27()
