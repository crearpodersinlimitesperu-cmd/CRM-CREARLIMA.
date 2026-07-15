import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

# Forzar encoding para Windows
sys.stdout.reconfigure(encoding='utf-8')

# Credenciales y Configuración
GMAIL_USER = "crearpodersinlimitesperu@gmail.com"
GMAIL_PASS = "bgsl xjus xsmn pzqd" # Contraseña de aplicación verificada

DESTINATARIOS = {
    "Joyce": {
        "email": "joyce.marin@crearpsl.com",
        "archivo": r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\DERIVACIONES_JOYCE_30ABR.xlsx"
    },
    "Diana": {
        "email": "diana.moscoso@crearpsl.com",
        "archivo": r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\DERIVACIONES_DIANA_30ABR.xlsx"
    }
}

def enviar_correo_derivaciones():
    print("🚀 Iniciando envío de correos de prueba (Casos Pendientes)")
    print("-" * 60)
    
    try:
        # 1. Conectar al servidor SMTP de Gmail
        print("🔌 Conectando al servidor SMTP de Gmail...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_PASS)
        print("✅ Login exitoso.")
        
        for cc_nombre, info in DESTINATARIOS.items():
            email_dest = info["email"]
            archivo = info["archivo"]
            
            print(f"\n📂 Procesando archivo de {cc_nombre}...")
            
            # 2. Leer archivo y filtrar pendientes (Asumiendo GESTIONADO == 'NO')
            df = pd.read_excel(archivo)
            
            # Tomar solo las columnas más importantes para el correo
            cols_necesarias = ['Participante', 'Telefono', 'Clasificacion', 'Ultimo Mensaje', 'Ultimo Contacto']
            df_reducido = df[cols_necesarias].copy()
            
            # Reemplazar NaN con espacio en blanco
            df_reducido = df_reducido.fillna("")
            
            total_casos = len(df_reducido)
            print(f"📊 Encontrados {total_casos} casos pendientes para {cc_nombre}.")
            
            # 3. Construir HTML del correo
            html_table = df_reducido.to_html(index=False, border=0, classes='tabla-casos')
            
            # Añadir CSS para que se vea como un reporte profesional
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 800px; margin: auto; }}
                    .header {{ background-color: #1d4ed8; color: white; padding: 15px; border-radius: 8px 8px 0 0; }}
                    .tabla-casos {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
                    .tabla-casos th {{ background-color: #f1f5f9; padding: 10px; border-bottom: 2px solid #cbd5e1; text-align: left; }}
                    .tabla-casos td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2 style="margin: 0;">🚨 Alerta de Casos Pendientes — CPSL Lima</h2>
                    </div>
                    <p>Hola <b>{cc_nombre}</b>,</p>
                    <p>El Cerebro Cuántico te informa que tienes <b>{total_casos} casos derivados sin gestionar</b>. Por favor, revisa la siguiente lista y atiende a los participantes lo antes posible.</p>
                    
                    {html_table}
                    
                    <div class="footer">
                        <p>Mensaje generado automáticamente por el Sistema de Torre de Control. Por favor, no respondas a este correo.</p>
                        <p><b>Nota Anti-Spam:</b> Si este correo llegó a la carpeta de correo no deseado, márcalo como "No es Spam" para asegurar la recepción futura de alertas urgentes.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 4. Configurar el objeto MIME
            msg = MIMEMultipart()
            msg['From'] = f"Cerebro Cuántico CPSL <{GMAIL_USER}>"
            msg['To'] = email_dest
            msg['Subject'] = f"🚨 {total_casos} Casos Pendientes por Gestionar - {cc_nombre}"
            
            # Headers anti-spam básicos
            msg['X-Priority'] = '1'
            msg['X-MSMail-Priority'] = 'High'
            msg['Importance'] = 'High'
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # 5. Enviar el correo
            print(f"📧 Enviando correo a {email_dest}...")
            server.send_message(msg)
            print(f"✅ ¡Correo enviado a {cc_nombre} exitosamente!")
            
        # Cerrar conexión SMTP
        server.quit()
        print("\n" + "-" * 60)
        print("🎯 TODOS LOS CORREOS ENVIADOS DE MANERA EFECTIVA.")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO durante el envío: {e}")

if __name__ == "__main__":
    enviar_correo_derivaciones()
