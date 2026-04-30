import os
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Si modificas estos scopes, borra el archivo token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Obtiene el servicio de la API de Gmail, autenticando al usuario si es necesario."""
    creds = None
    # El archivo token.json almacena los tokens de acceso y de actualización del usuario.
    # Se crea automáticamente cuando el flujo de autorización se completa por primera vez.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no hay credenciales válidas, permite que el usuario inicie sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('client_secret.json'):
                raise FileNotFoundError("No se encontró el archivo client_secret.json. Requerido para OAuth.")
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guarda las credenciales para la próxima vez
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'Ocurrió un error al construir el servicio de Gmail: {error}')
        return None

def enviar_correo_api(destinatario, asunto, contenido_html):
    """
    Envía un correo electrónico usando la API de Gmail.
    Retorna True si fue exitoso, False en caso contrario.
    """
    service = get_gmail_service()
    if not service:
        return False
        
    try:
        message = EmailMessage()
        message.set_content("Tu cliente de correo no soporta HTML. Por favor revisa desde una versión más moderna.")
        message.add_alternative(contenido_html, subtype='html')
        
        message['To'] = destinatario
        message['From'] = 'me' # 'me' indica el usuario autenticado
        message['Subject'] = asunto

        # Codificar en base64 para la API de Gmail
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }

        # Ejecutar el envío
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(f"Correo enviado exitosamente vía API. Message Id: {send_message['id']}")
        return True
        
    except HttpError as error:
        print(f'Un error HTTP ocurrió al enviar el correo: {error}')
        return False
    except Exception as e:
        print(f'Ocurrió un error inesperado al enviar correo API: {e}')
        return False

if __name__ == '__main__':
    # Al ejecutar este archivo directamente, se forzará la creación del token.json
    print("Iniciando flujo de autorización de Gmail API...")
    get_gmail_service()
    print("¡Autorización completada! El archivo token.json ha sido generado exitosamente.")
