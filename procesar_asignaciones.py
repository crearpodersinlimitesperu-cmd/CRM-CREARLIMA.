import pandas as pd
import os
import sys
from sync_cloud import sincronizar_asignaciones_a_cloud

# Forzar encoding
sys.stdout.reconfigure(encoding='utf-8')

def procesar_asignaciones():
    path_asig = r"C:\Users\josem\Downloads\Asignacion_C1.xlsx"
    path_web = "Asignaciones_Web.xlsx"
    
    if not os.path.exists(path_asig):
        print(f"ERROR: No se encontró el archivo: {path_asig}")
        return

    print("Leyendo archivo de asignaciones...")
    df_asig = pd.read_excel(path_asig)
    
    # Mapeo de columnas para compatibilidad CRM
    # Columnas: ['Check', 'Usuario Registro', 'NombreEquipo', 'Identificacin', 'NombreCompleto', 'ApellidoCompleto', 'TelefonoMovil', 'Correo', 'IdentificacionIMO']
    
    df_crm = pd.DataFrame()
    
    # Normalizar Identificación (DNI)
    col_dni = next((c for c in df_asig.columns if 'Ident' in c), None)
    if col_dni:
        df_crm['ClienteId'] = df_asig[col_dni].astype(str).str.strip().str.replace('.0', '', regex=False)
    
    df_crm['NombreCompleto'] = df_asig['NombreCompleto'].astype(str).str.strip()
    df_crm['ApellidoCompleto'] = df_asig['ApellidoCompleto'].astype(str).str.strip()
    df_crm['Telefono'] = df_asig['TelefonoMovil'].astype(str).str.strip()
    df_crm['Email'] = df_asig['Correo'].astype(str).str.strip()
    
    # Mapear Coordinador desde Usuario Registro
    # dmoscoso -> Diana Moscoso, jmarin -> Joyce Marin, zurteaga -> (Reasignada equitativamente)
    def mapear_coord(user, dni_val):
        u = str(user).lower().strip()
        if 'dmoscoso' in u: return 'Diana Moscoso'
        if 'jmarin' in u: return 'Joyce Marin'
        if 'zurteaga' in u:
            # Reasignación equitativa y determinista basada en el DNI
            try:
                if int(hash(str(dni_val))) % 2 == 0: return 'Diana Moscoso'
                else: return 'Joyce Marin'
            except:
                return 'Diana Moscoso'
        return u.title()

    df_crm['Coordinador'] = df_asig.apply(lambda row: mapear_coord(row['Usuario Registro'], row.get(col_dni, '0')), axis=1)
    df_crm['Equipo'] = df_asig['NombreEquipo'].astype(str).str.strip()
    df_crm['IMO_DNI'] = df_asig['IdentificacionIMO'].astype(str).str.strip().str.replace('.0', '', regex=False)
    
    # Guardar localmente
    df_crm.to_excel(path_web, index=False)
    print(f"Archivo local {path_web} generado con {len(df_crm)} registros.")
    
    # Sincronizar a la nube
    print("Sincronizando a la nube (Pestaña ASIGNACIONES)...")
    try:
        sincronizar_asignaciones_a_cloud(path_web)
        print("Proceso de asignaciones completado exitosamente.")
    except Exception as e:
        print(f"Error en sincronización: {e}")

if __name__ == "__main__":
    procesar_asignaciones()
