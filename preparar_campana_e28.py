import pandas as pd
import sys
import re

# Forzar encoding para Windows
sys.stdout.reconfigure(encoding='utf-8')

def preparar_datos_campana_e28():
    print("⚙️ INICIANDO FASE 2: PREPARACIÓN DE DATOS (C1 E28)")
    print("-" * 60)
    
    # Ruta del archivo de asignaciones proporcionado
    path_asignaciones = r"C:\Users\josem\Downloads\Asignacion_C1 (2).xlsx"
    path_salida = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\campana_e28_diana_joyce.csv"
    
    try:
        # 1. Cargar archivo
        print("📖 Leyendo archivo de asignaciones...")
        df = pd.read_excel(path_asignaciones)
        
        # Limpiar nombres de columnas (quitar caracteres raros)
        df.columns = [str(c).replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u').strip() for c in df.columns]
        
        total_inicial = len(df)
        print(f"📊 Total de registros en archivo: {total_inicial}")

        # 2. Filtrar solo Diana (dmoscoso) y Joyce (jmarin)
        mask_cc = df['Usuario Registro'].astype(str).str.lower().str.contains('dmoscoso|jmarin', na=False)
        df_filtrado = df[mask_cc].copy()
        print(f"🎯 Registros asignados a Diana y Joyce: {len(df_filtrado)}")
        
        # 3. Formatear y Validar Datos Críticos (Teléfono y Nombre)
        print("🛠️ Limpiando y formateando datos para WhatsApp...")
        
        def formato_telefono(tel):
            tel_str = re.sub(r'\D', '', str(tel))
            if not tel_str: return ""
            # Asumimos Perú (+51) si tiene 9 dígitos
            if len(tel_str) == 9 and tel_str.startswith('9'):
                return f"51{tel_str}"
            return tel_str
            
        def formato_nombre(nom):
            n = str(nom).strip()
            if n == 'nan' or not n: return "amigo/a"
            # Tomar el primer nombre y capitalizarlo
            return n.split()[0].title()

        df_filtrado['wa_id'] = df_filtrado['TelefonoMovil'].apply(formato_telefono)
        df_filtrado['primer_nombre'] = df_filtrado['NombreCompleto'].apply(formato_nombre)
        
        # 4. Filtrar inválidos (sin teléfono válido)
        validos = df_filtrado[df_filtrado['wa_id'].str.len() >= 11] # 51 + 9 digitos
        invalidos = len(df_filtrado) - len(validos)
        
        if invalidos > 0:
            print(f"⚠️ Se descartaron {invalidos} registros por teléfono inválido o vacío.")
            
        # 5. Exportar CSV Final
        # Seleccionamos solo las columnas necesarias para el motor de envíos
        columnas_export = ['wa_id', 'primer_nombre', 'Identificacion', 'Usuario Registro']
        df_final = validos[columnas_export]
        
        df_final.to_csv(path_salida, index=False, encoding='utf-8-sig')
        
        print("\n✅ PREPARACIÓN COMPLETADA")
        print(f"📁 Archivo de campaña generado: {path_salida}")
        print(f"🚀 Total de prospectos listos para envío: {len(df_final)}")
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error en la preparación de datos: {e}")

if __name__ == "__main__":
    preparar_datos_campana_e28()
