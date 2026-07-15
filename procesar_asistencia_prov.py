import pandas as pd
import os
import sys
from sync_cloud import sincronizar_productividad_a_cloud

# Forzar encoding para evitar errores de consola Windows
sys.stdout.reconfigure(encoding='utf-8')

def procesar_asistencia_provisional():
    path_prov = r"C:\Users\josem\Downloads\participantes_asistencia (1).xlsx"
    path_web = "Productividad_Web.xlsx"
    
    if not os.path.exists(path_prov):
        print(f"ERROR: No se encontró el archivo: {path_prov}")
        return

    print("Leyendo archivo provisional de asistencia...")
    # Cargar intentando detectar nombres de columnas con caracteres especiales
    df_prov = pd.read_excel(path_prov)
    
    # Mapeo robusto por posición si los nombres fallan, pero probaremos nombres normalizados
    # ['Ficha', 'Asistencia', 'Equipo', 'Usuario Segumiento', 'Identificaci\u00f3n', 'Apellido Completo', ...]
    
    cols = df_prov.columns.tolist()
    col_dni = next((c for c in cols if 'Ident' in c), None)
    col_nom = next((c for c in cols if 'Nombre Completo' in c), None)
    col_ape = next((c for c in cols if 'Apellido Completo' in c), None)
    col_asis = next((c for c in cols if 'Asistencia' in c), None)
    col_cc = next((c for c in cols if 'Usuario' in c), None)

    if not col_dni or not col_asis:
        print(f"ERROR: No se encontraron columnas críticas. Columnas detectadas: {cols}")
        return

    # Renombrar para compatibilidad con Productividad_Web.xlsx
    df_crm = pd.DataFrame()
    df_crm['ClienteId'] = df_prov[col_dni].astype(str).str.strip().str.replace('.0', '', regex=False)
    df_crm['NombreCompleto'] = df_prov[col_nom].astype(str).str.strip() if col_nom else ""
    df_crm['ApellidoCompleto'] = df_prov[col_ape].astype(str).str.strip() if col_ape else ""
    df_crm['Asistencia'] = df_prov[col_asis].astype(str).str.strip()
    
    def traducir_estatus(val):
        v = str(val).upper()
        # En el Excel provisional, lo que NO sea "Actualizar Asistencia" suele ser ya una marca
        if any(x in v for x in ["CONFIRMADO", "ASISTIO", "SI", "SENTADO", "CHECK"]):
            return "SENTADO"
        return "PENDIENTE"

    df_crm['Resultado Gestión'] = df_crm['Asistencia'].apply(traducir_estatus)
    df_crm['Fecha Gestión'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    df_crm['CC_Reportada'] = df_prov[col_cc].astype(str).str.strip() if col_cc else "SISTEMA"
    
    # Guardar localmente
    df_crm.to_excel(path_web, index=False)
    print(f"Archivo local {path_web} generado con {len(df_crm)} registros.")
    
    # Sincronizar a la nube
    print("Sincronizando a la nube...")
    try:
        sincronizar_productividad_a_cloud(path_web)
        print("Proceso completado exitosamente.")
    except Exception as e:
        print(f"Error en sincronización: {e}")

if __name__ == "__main__":
    procesar_asistencia_provisional()
