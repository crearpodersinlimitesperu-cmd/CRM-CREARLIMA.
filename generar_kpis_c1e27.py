import pandas as pd
import numpy as np
import os
import sys
import unicodedata

# Configurar encoding para salida en Windows
sys.stdout.reconfigure(encoding='utf-8')

def norm(text):
    if not text or pd.isna(text): return ""
    s = str(text).upper().strip()
    # Eliminar acentos y caracteres especiales
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def generar_kpis_c1e27():
    print("🚀 Iniciando Motor de KPIs Cuánticos (Cruce por Nombre) - C1E27")
    
    # --- 1. CARGA DE DATOS ---
    try:
        # Asistencia Real (Sentados)
        df_asis = pd.read_excel(r"C:\Users\josem\Downloads\participantes_asistencia (2).xlsx")
        df_asis.columns = [c.replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_asis.columns]
        
        # Crear llave de cruce por nombre completo en Asistencia
        df_asis['_key'] = (df_asis['Nombre Completo'].astype(str) + " " + df_asis['Apellido Completo'].astype(str)).apply(norm)
        sentados_keys = df_asis['_key'].unique()
        print(f"✅ Sentados Oficiales: {len(sentados_keys)}")

        # Productividad (Confirmados y Asignados)
        prod_files = [
            r"C:\Users\josem\Downloads\productividad_coordinador.xlsx",
            r"C:\Users\josem\Downloads\productividad_coordinador (1).xlsx",
            r"C:\Users\josem\Downloads\productividad_coordinador (2).xlsx"
        ]
        df_prod_list = []
        for f in prod_files:
            if os.path.exists(f):
                df_prod_list.append(pd.read_excel(f))
        df_prod = pd.concat(df_prod_list).drop_duplicates(subset=['ClienteId'], keep='last')
        
        # Crear llave de cruce por nombre completo en Productividad
        df_prod['_key'] = (df_prod['NombreCompleto'].astype(str) + " " + df_prod['ApellidoCompleto'].astype(str)).apply(norm)
        print(f"✅ Total Universo Productividad: {len(df_prod)}")

        # Master CSV (Enrolados de FDS anteriores)
        df_master = pd.read_csv(r"C:\Users\josem\Downloads\participantes_2026-05-01.csv", sep=',', on_bad_lines='skip', low_memory=False)
        df_master.columns = [c.replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u') for c in df_master.columns]
        # Crear llave de cruce por nombre completo en Master
        df_master['_key'] = (df_master['Nombre'].astype(str) + " " + df_master['Apellido'].astype(str)).apply(norm)
        print(f"✅ Master CSV cargado. Total: {len(df_master)}")

    except Exception as e:
        print(f"❌ Error cargando archivos: {e}")
        return

    # --- 2. CÁLCULO DE KPIs ---
    
    # A. Confirmados vs Sentados
    res_gest_col = 'Resultado Gestión' if 'Resultado Gestión' in df_prod.columns else 'Resultado Gestion'
    confirmados_mask = df_prod[res_gest_col].astype(str).str.upper().str.contains('CONFIRMA|SENTADO', na=False)
    df_conf = df_prod[confirmados_mask]
    total_confirmados = len(df_conf)
    
    n_conf_sentados = df_conf['_key'].isin(sentados_keys).sum()
    efectividad_conf = (n_conf_sentados / total_confirmados * 100) if total_confirmados > 0 else 0

    # B. Asignados vs Sentados (Global)
    total_asignados = len(df_prod)
    total_sentados_final = len(sentados_keys)
    efectividad_total = (total_sentados_final / total_asignados * 100) if total_asignados > 0 else 0

    # C. Asignados Equipo 27 vs Sentados
    df_e27 = df_prod[df_prod['Equipo'].astype(str).str.contains('27', na=False)]
    total_e27 = len(df_e27)
    n_sentados_e27 = df_e27['_key'].isin(sentados_keys).sum()
    efectividad_e27 = (n_sentados_e27 / total_e27 * 100) if total_e27 > 0 else 0

    # D. Enrolados por FDS (E26, E25, E24)
    def get_enrolados_stats(equipo_grad):
        mask_fds = df_master['Equipo'].astype(str).str.contains(f"EQUIPO {equipo_grad}", na=False)
        pax_fds_keys = df_master[mask_fds]['_key'].unique()
        total_pax_fds = len(pax_fds_keys)
        n_sentados_fds = sum(1 for k in pax_fds_keys if k in sentados_keys)
        return total_pax_fds, n_sentados_fds

    e26_total, e26_sent = get_enrolados_stats(26)
    e25_total, e25_sent = get_enrolados_stats(25)
    e24_total, e24_sent = get_enrolados_stats(24)

    # --- 3. REPORTE FINAL ---
    print("\n" + "="*50)
    print("📊 REPORTE DE KPIs ESTRATÉGICOS - CAMPAÑA C1E27")
    print("="*50)
    
    print(f"\n✅ 1. EFECTIVIDAD DE CONFIRMACIÓN")
    print(f"   - Confirmados en Sistema: {total_confirmados}")
    print(f"   - Sentados Reales:        {n_conf_sentados}")
    print(f"   - Ratio de Cumplimiento:  {efectividad_conf:.1f}%")

    print(f"\n👥 2. PENETRACIÓN DE BASE (GLOBAL)")
    print(f"   - Asignados Totales:      {total_asignados}")
    print(f"   - Sentados Totales:       {total_sentados_final}")
    print(f"   - Efectividad Total:      {efectividad_total:.1f}%")

    print(f"\n🎯 3. RENDIMIENTO EQUIPO 27 (FOCO)")
    print(f"   - Asignados E27:          {total_e27}")
    print(f"   - Sentados E27:           {n_sentados_e27}")
    print(f"   - Efectividad E27:        {efectividad_e27:.1f}%")

    print(f"\n🎓 4. RETENCIÓN POR PROMOCIÓN (FDS)")
    print(f"   - Enrolados E26 -> Sentados C1: {e26_sent} de {e26_total} ({(e26_sent/e26_total*100 if e26_total>0 else 0):.1f}%)")
    print(f"   - Enrolados E25 -> Sentados C1: {e25_sent} de {e25_total} ({(e25_sent/e25_total*100 if e25_total>0 else 0):.1f}%)")
    print(f"   - Enrolados E24 -> Sentados C1: {e24_sent} de {e24_total} ({(e24_sent/e24_total*100 if e24_total>0 else 0):.1f}%)")

    print(f"\n🤝 5. ALIADOS ESTRATÉGICOS")
    aliados_activos = df_prod[df_prod['_key'].isin(sentados_keys)]['Nombre IMO'].nunique()
    print(f"   - Aliados (Graduados) con Sentados: {aliados_activos}")
    print("="*50)

if __name__ == "__main__":
    generar_kpis_c1e27()
