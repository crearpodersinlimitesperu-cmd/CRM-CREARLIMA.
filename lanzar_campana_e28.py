import pandas as pd
import requests
import time
import os
import sys

# Forzar encoding para Windows
sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------
# CONFIGURACIÓN DE META / WHATSAPP API
# ---------------------------------------------------------
# NOTA: Lee el TOKEN y PHONE_ID desde las variables de entorno 
# del sistema. Debes asegurarte de tenerlas configuradas, 
# o pegarlas temporalmente aquí si lo prefieres.
from dotenv import load_dotenv
load_dotenv(r"C:\Users\josem\Downloads\bot-cpsl-review\.env")

TOKEN = os.environ.get("WA_TOKEN", "")
PHONE_ID = os.environ.get("WA_PHONE_ID", "")

# Plantilla aprobada
TEMPLATE_NAME = "reactivacion_c1_e28"
LANGUAGE_CODE = "es"

def enviar_plantilla(telefono, primer_nombre):
    """Envía la plantilla de WhatsApp aprobada."""
    if not TOKEN or not PHONE_ID:
        print("❌ ERROR: Faltan credenciales (WA_TOKEN o WA_PHONE_ID).")
        return False
        
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": str(telefono),
        "type": "template",
        "template": {
            "name": TEMPLATE_NAME,
            "language": {
                "code": LANGUAGE_CODE
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": str(primer_nombre)
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"\n⚠️ Error enviando a {telefono}: {response.text}")
            return False
    except Exception as e:
        print(f"\n⚠️ Error de conexión al enviar a {telefono}: {e}")
        return False

def lanzar_campana(modo_prueba=True):
    print("🚀 SISTEMA DE LANZAMIENTO - CAMPAÑA C1 E28")
    print("-" * 60)
    
    path_csv = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\campana_e28_diana_joyce.csv"
    
    if not os.path.exists(path_csv):
        print("❌ ERROR: No se encontró el archivo de la campaña.")
        print(f"Ruta esperada: {path_csv}")
        return
        
    df = pd.read_csv(path_csv)
    total = len(df)
    
    print(f"📊 Prospectos listos en base: {total}")
    
    if modo_prueba:
        print("\n🧪 MODO PRUEBA ACTIVADO (No se enviarán mensajes masivos)")
        print("Se enviará únicamente a los 2 primeros registros para validar el formato.")
        df = df.head(2)
    else:
        print("\n🔥 MODO REAL ACTIVADO (Se enviarán mensajes a TODA la base)")
        confirmacion = input('Escribe "LANZAR" para confirmar el envío masivo: ')
        if confirmacion.strip().upper() != 'LANZAR':
            print("🚫 Operación cancelada por el usuario.")
            return

    exitos = 0
    errores = 0
    
    print("\nIniciando envío...")
    
    for index, row in df.iterrows():
        telefono = str(row['wa_id']).strip()
        nombre = str(row['primer_nombre']).strip()
        
        # Eliminar ".0" si el archivo lo importó como float en algún caso extremo
        if telefono.endswith(".0"):
            telefono = telefono[:-2]
            
        sys.stdout.write(f"\rEnviando: [{index + 1}/{len(df)}] -> {nombre} ({telefono}) ... ")
        sys.stdout.flush()
        
        if enviar_plantilla(telefono, nombre):
            exitos += 1
        else:
            errores += 1
            
        # Delay de seguridad anti-ban (Meta recomienda no enviar ráfagas muy altas de golpe)
        time.sleep(1.5)
        
    print("\n\n✅ LANZAMIENTO FINALIZADO")
    print("-" * 60)
    print(f"✔️ Entregados al API de Meta: {exitos}")
    print(f"❌ Fallos de envío: {errores}")
    
    if modo_prueba:
        print("\nSi los mensajes llegaron bien, cambia modo_prueba=False en el código y lanza el masivo.")

if __name__ == "__main__":
    # Para ejecutar de verdad, cambiar a: lanzar_campana(modo_prueba=False)
    lanzar_campana(modo_prueba=True)
