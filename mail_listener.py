import imaplib
import email
from email.header import decode_header
import re
import time
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import sys

# Forzar encoding para Windows
sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno del bot (donde están SHEET_ID y SHEDS)
from dotenv import load_dotenv
load_dotenv(r"C:\Users\josem\Downloads\bot-cpsl-review\.env")

# --- CONFIGURACIÓN DE CORREO ---
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "crearpodersinlimitesperu@gmail.com"
EMAIL_PASSWORD = "bgsl xjus xsmn pzqd"

# --- CONFIGURACIÓN DE SHEETS ---
SHEET_ID = os.environ.get("SHEET_ID", "")
SHEDS = os.environ.get("GOOGLE_CREDENTIALS", "")

def decodificar_asunto(asunto_raw):
    """Decodifica el asunto del correo que puede venir en formatos especiales."""
    decoded_list = decode_header(asunto_raw)
    asunto_final = ""
    for texto, encoding in decoded_list:
        if isinstance(texto, bytes):
            asunto_final += texto.decode(encoding if encoding else "utf-8", errors='ignore')
        else:
            asunto_final += texto
    return asunto_final

def extraer_cuerpo_correo(msg):
    """Extrae la respuesta limpia ignorando el historial previo."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode()
                except:
                    body = part.get_payload()
                break # Tomar solo la primera parte de texto
    else:
        try:
            body = msg.get_payload(decode=True).decode()
        except:
            body = msg.get_payload()
            
    # Limpiar el historial del correo (todo lo que está debajo de "El ... escribió:")
    lineas = body.split('\n')
    respuesta_limpia = []
    for linea in lineas:
        if linea.startswith(">") or "escribió:" in linea or "wrote:" in linea or "crearpodersinlimitesperu@gmail.com" in linea:
            break
        respuesta_limpia.append(linea)
        
    return "\n".join(respuesta_limpia).strip()

def conectar_sheets():
    """Conecta a Google Sheets y devuelve la hoja de derivaciones."""
    if not SHEDS:
        print("⚠️ Advertencia: No se encontraron credenciales de Google Sheets (SHEDS).")
        return None
        
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(SHEDS), scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet("LOG_DERIVACIONES")

def procesar_correos_no_leidos():
    print(f"\n[{time.strftime('%H:%M:%S')}] 📡 Revisando bandeja de entrada...")
    
    try:
        # Conectar a IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        
        # Buscar correos NO LEÍDOS
        status, messages = mail.search(None, "UNSEEN")
        
        if status != "OK":
            print("❌ Error al buscar correos.")
            return
            
        email_ids = messages[0].split()
        if not email_ids:
            print("📭 No hay respuestas nuevas.")
            mail.logout()
            return
            
        print(f"📬 Encontrados {len(email_ids)} correos no leídos.")
        
        # Conectar a Sheets solo si hay correos
        ws = conectar_sheets()
        
        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    asunto = decodificar_asunto(msg.get("Subject", ""))
                    remitente = msg.get("From", "")
                    
                    print(f"\n📩 Procesando correo de: {remitente}")
                    print(f"📌 Asunto: {asunto}")
                    
                    # 1. Verificar si es una respuesta a una Derivación
                    # El asunto original era: 🚨 DERIVACIÓN: Pedro Perez (Motivo)
                    # La respuesta suele ser: Re: 🚨 DERIVACIÓN: Pedro Perez (Motivo)
                    match = re.search(r"DERIVACI[OÓ]N:\s*(.*?)\s*\(", asunto, re.IGNORECASE)
                    
                    if match:
                        nombre_px = match.group(1).strip()
                        cuerpo = extraer_cuerpo_correo(msg)
                        
                        print(f"🎯 Participante detectado: {nombre_px}")
                        print(f"💬 Comentario CC: {cuerpo[:50]}...")
                        
                        # 2. Actualizar Google Sheets
                        if ws:
                            # Buscar al participante en la hoja
                            registros = ws.get_all_values()
                            fila_encontrada = None
                            
                            # Buscar desde abajo hacia arriba (para agarrar el caso más reciente)
                            for i in range(len(registros)-1, -1, -1):
                                # La columna D (índice 3) tiene el Nombre del PX
                                if len(registros[i]) >= 4 and registros[i][3].strip().lower() == nombre_px.lower():
                                    fila_encontrada = i + 1 # +1 porque gspread usa índice 1-based
                                    break
                                    
                            if fila_encontrada:
                                print(f"✅ Registro encontrado en fila {fila_encontrada}. Cerrando caso...")
                                # Actualizar ESTADO a CERRADO (Columna 7 / G)
                                ws.update_cell(fila_encontrada, 7, "CERRADO")
                                
                                # Anotar el comentario en la Columna 8 (H)
                                # Prevenir reemplazar si ya hay algo
                                actual_comment = ""
                                if len(registros[fila_encontrada-1]) >= 8:
                                    actual_comment = registros[fila_encontrada-1][7]
                                
                                nuevo_comentario = f"[Vía Correo]: {cuerpo}" if not actual_comment else f"{actual_comment} | [Vía Correo]: {cuerpo}"
                                ws.update_cell(fila_encontrada, 8, nuevo_comentario)
                                
                                print("💾 Sheets actualizado con éxito.")
                            else:
                                print(f"⚠️ No se encontró al participante '{nombre_px}' en LOG_DERIVACIONES.")
                    else:
                        print("⏭️ El correo no es una respuesta de derivación estructurada. Ignorando.")
            
            # Marcar como leído (IMAP ya lo hace al hacer fetch de RFC822, pero confirmamos)
            mail.store(e_id, '+FLAGS', '\Seen')
            
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error en el Listener: {e}")

def iniciar_demonio():
    print("==================================================")
    print("🤖 LISTENER IMAP - CEREBRO CUÁNTICO INICIADO")
    print("Escuchando respuestas de las CCs para cerrar casos.")
    print("Presiona Ctrl+C para detener.")
    print("==================================================")
    
    while True:
        procesar_correos_no_leidos()
        time.sleep(60) # Esperar 60 segundos antes de volver a revisar

if __name__ == "__main__":
    iniciar_demonio()
