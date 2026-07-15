import pandas as pd
import numpy as np
import os
import sys

# Configurar encoding
sys.stdout.reconfigure(encoding='utf-8')

def auditoria_verdad_absoluta():
    print("📋 AUDITORÍA TÉCNICA DE CIERRE - C1E27")
    print("-" * 50)
    
    try:
        # 1. BASE REAL DE ASIGNACIÓN (Fuente de Verdad de a quién le toca qué)
        df_asig = pd.read_excel(r"C:\Users\josem\Downloads\Asignacion_C1.xlsx")
        df_asig.columns = [str(c).replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_asig.columns]
        df_asig['DNI'] = df_asig['Identificacion'].astype(str).str.strip().str.replace('.0', '', regex=False)
        total_universo = len(df_asig)
        
        # 2. BASE REAL DE ASISTENCIA (Quién llegó al salón)
        df_asis = pd.read_excel(r"C:\Users\josem\Downloads\participantes_asistencia (2).xlsx")
        df_asis.columns = [str(c).replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_asis.columns]
        df_asis['DNI'] = df_asis['Identificacion'].astype(str).str.strip().str.replace('.0', '', regex=False)
        sentados_reales_dni = df_asis['DNI'].unique()
        total_sentados = len(sentados_reales_dni)

        # 3. CRUCE DIRECTO POR DNI (Sin Nombres, Sin IA, Solo números de identidad)
        df_asig['Llego_al_Salon'] = df_asig['DNI'].isin(sentados_reales_dni)
        
        # 4. CÁLCULO POR COORDINADORA
        def mapear_coord(user):
            u = str(user).lower().strip()
            if 'dmoscoso' in u: return 'Diana Moscoso'
            if 'jmarin' in u: return 'Joyce Marin'
            if 'zurteaga' in u: return 'Zuley Urteaga'
            return u.title()

        df_asig['Coordinadora_Final'] = df_asig['Usuario Registro'].apply(mapear_coord)
        
        # Generar Tabla de Verdad
        resumen = df_asig.groupby('Coordinadora_Final').agg(
            Asignados=('DNI', 'count'),
            Sentados=('Llego_al_Salon', 'sum')
        ).reset_index()
        
        resumen['Efectividad (%)'] = (resumen['Sentados'] / resumen['Asignados'] * 100).round(1)
        resumen = resumen.sort_values('Sentados', ascending=False)

        # 5. RESULTADOS EN CONSOLA
        print(f"✅ UNIVERSO TOTAL ASIGNADO: {total_universo}")
        print(f"✅ TOTAL SENTADOS EN SALÓN: {total_sentados}")
        print(f"✅ CRUCE EXITOSO (DNI EN ASIGNACIÓN): {df_asig['Llego_al_Salon'].sum()}")
        print("\n🏆 RANKING REAL DE COORDINADORAS (C1E27):")
        print(resumen.to_string(index=False))
        
        # 6. EXPORTAR EXCEL DE VERDAD (Para que lo revises DNI por DNI)
        output_path = r"C:\Users\josem\Downloads\AUDITORIA_CIERRE_FINAL_C1.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            resumen.to_excel(writer, sheet_name='Ranking Real', index=False)
            # Detalle de quién llegó y quién no de los asignados
            df_asig[['DNI', 'NombreCompleto', 'ApellidoCompleto', 'Coordinadora_Final', 'Llego_al_Salon']].to_excel(writer, sheet_name='Detalle Cruce DNI', index=False)
            # Aquellos que llegaron al salón pero NO estaban en tu lista de asignación
            fuera_de_lista = df_asis[~df_asis['DNI'].isin(df_asig['DNI'])]
            fuera_de_lista[['DNI', 'Nombre Completo', 'Apellido Completo', 'Usuario Segumiento']].to_excel(writer, sheet_name='Sentados Fuera de Asignacion', index=False)

        print(f"\n📁 ARCHIVO DE AUDITORÍA GENERADO: {output_path}")
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error en auditoría: {e}")

if __name__ == "__main__":
    auditoria_verdad_absoluta()
