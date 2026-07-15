import pandas as pd
import unicodedata
import os
import sys

# Configurar encoding para salida en Windows
sys.stdout.reconfigure(encoding='utf-8')

def norm(text):
    if not text or pd.isna(text): return ""
    s = str(text).upper().strip()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def exportar_kpis_excel():
    print("🚀 Generando Excel de KPIs Estratégicos - C1E27")
    
    try:
        # 1. CARGA DE DATOS
        df_asis = pd.read_excel(r"C:\Users\josem\Downloads\participantes_asistencia (2).xlsx")
        df_asis['_key'] = (df_asis['Nombre Completo'].astype(str) + " " + df_asis['Apellido Completo'].astype(str)).apply(norm)
        sentados_keys = df_asis['_key'].unique()

        prod_files = [
            r"C:\Users\josem\Downloads\productividad_coordinador.xlsx",
            r"C:\Users\josem\Downloads\productividad_coordinador (1).xlsx",
            r"C:\Users\josem\Downloads\productividad_coordinador (2).xlsx"
        ]
        df_prod = pd.concat([pd.read_excel(f) for f in prod_files if os.path.exists(f)]).drop_duplicates(subset=['ClienteId'], keep='last')
        df_prod['_key'] = (df_prod['NombreCompleto'].astype(str) + " " + df_prod['ApellidoCompleto'].astype(str)).apply(norm)

        df_master = pd.read_csv(r"C:\Users\josem\Downloads\participantes_2026-05-01.csv", sep=',', on_bad_lines='skip', low_memory=False)
        df_master.columns = [c.replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_master.columns]
        df_master['_key'] = (df_master['Nombre'].astype(str) + " " + df_master['Apellido'].astype(str)).apply(norm)

        # 2. CÁLCULO DE MÉTRICAS
        total_asignados = len(df_prod)
        total_sentados = len(sentados_keys)
        
        res_gest_col = 'Resultado Gestión' if 'Resultado Gestión' in df_prod.columns else 'Resultado Gestion'
        confirmados_mask = df_prod[res_gest_col].astype(str).str.upper().str.contains('CONFIRMA|SENTADO', na=False)
        total_confirmados = confirmados_mask.sum()
        
        # Resumen Global
        resumen_data = {
            'Métrica': [
                'Total Asignados', 
                'Total Confirmados (Sistema)', 
                'Total Sentados (Oficial)',
                'Efectividad Global (%)',
                'Efectividad de Confirmación (%)'
            ],
            'Valor': [
                total_asignados,
                total_confirmados,
                total_sentados,
                round((total_sentados / total_asignados * 100), 1),
                round((df_prod[confirmados_mask]['_key'].isin(sentados_keys).sum() / total_confirmados * 100), 1) if total_confirmados > 0 else 0
            ]
        }
        df_resumen = pd.DataFrame(resumen_data)

        # Efectividad por Coordinadora
        coord_col = 'Coordinador'
        if coord_col in df_prod.columns:
            df_prod['EsSentado'] = df_prod['_key'].isin(sentados_keys)
            ranking = df_prod[df_prod[coord_col] != '—'].groupby(coord_col).agg(
                Asignados=('ClienteId', 'count'),
                Sentados=('EsSentado', 'sum')
            ).reset_index()
            ranking['Efectividad (%)'] = (ranking['Sentados'] / ranking['Asignados'] * 100).round(1)
            ranking = ranking.sort_values('Sentados', ascending=False)
        else:
            ranking = pd.DataFrame({'Info': ['No se encontró columna de Coordinador']})

        # 3. EXPORTACIÓN A EXCEL
        output_path = r"C:\Users\josem\Downloads\KPI_CIERRE_C1E27.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_resumen.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
            ranking.to_excel(writer, sheet_name='Ranking Coordinadoras', index=False)
            # Detalle de Sentados
            df_asis[['Identificación' if 'Identificación' in df_asis.columns else 'Identificacion', 'Nombre Completo', 'Apellido Completo', 'Nombre IMO']].to_excel(writer, sheet_name='Detalle Sentados', index=False)

        print(f"✅ Excel generado exitosamente en: {output_path}")

    except Exception as e:
        print(f"❌ Error generando Excel: {e}")

if __name__ == "__main__":
    exportar_kpis_excel()
