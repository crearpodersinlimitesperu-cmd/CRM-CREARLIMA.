"""
DISPARADOR DE PLANTILLA emergencia_enrolamiento
Lee CONFIRMACIONES Y CIERRES.xlsx y envia los contactos al bot en Render.
El bot se encarga de enviar la plantilla aprobada de WhatsApp.
"""
import pandas as pd
import requests
import time
import json
import sys

BOT_URL = "https://bot-cpsl.onrender.com"
EXCEL_PATH = r"C:\Users\josem\Downloads\Reportes y Gestión\CONFIRMACIONES Y CIERRES.xlsx"
PLANTILLA = "emergencia_enrolamiento"
PAUSA_ENTRE_MENSAJES = 15  # segundos entre cada mensaje (seguridad Meta)

def main():
    # 1. Leer Excel
    df = pd.read_excel(EXCEL_PATH)
    print(f"Registros en Excel: {len(df)}")
    print(f"Columnas: {df.columns.tolist()}")

    # 2. Preparar contactos
    contactos = []
    for _, row in df.iterrows():
        tel = str(row.get("TeléfonoMovil", "")).strip()
        nombre = str(row.get("NombrePreferido", "")).strip()
        if not nombre or nombre == "nan":
            nombre = str(row.get("NombreCompleto", "Amigo")).split()[0]
        if not tel or tel == "nan" or len(tel) < 10:
            continue
        # Limpiar telefono
        tel = tel.replace(" ", "").replace("-", "").replace("+", "")
        contactos.append({"tel": tel, "nombre": nombre.title()})

    # Deduplicar por telefono
    seen = set()
    unicos = []
    for c in contactos:
        if c["tel"] not in seen:
            seen.add(c["tel"])
            unicos.append(c)
    contactos = unicos

    print(f"Contactos validos (unicos): {len(contactos)}")
    if not contactos:
        print("No hay contactos para enviar.")
        return

    # 3. Mostrar preview
    print("\n--- PREVIEW (primeros 10) ---")
    for c in contactos[:10]:
        print(f"  {c['nombre']} -> {c['tel']}")
    print(f"  ... y {max(0, len(contactos)-10)} mas\n")

    # 4. Confirmar
    resp = input(f"Enviar {len(contactos)} mensajes con plantilla '{PLANTILLA}'? (si/no): ").strip().lower()
    if resp not in ("si", "s", "yes", "y"):
        print("Cancelado.")
        return

    # 5. Disparar al bot (Render)
    print(f"\nEnviando lote al bot en {BOT_URL}...")
    try:
        r = requests.post(
            f"{BOT_URL}/api/plantilla/enviar_lote",
            json={
                "contactos": contactos,
                "plantilla": PLANTILLA,
                "pausa": PAUSA_ENTRE_MENSAJES
            },
            timeout=30
        )
        print(f"Respuesta del bot: {r.status_code}")
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error conectando con el bot: {e}")
        return

    # 6. Monitorear progreso
    print("\n--- MONITOREANDO PROGRESO ---")
    print("(Ctrl+C para dejar de monitorear, el envio continua en el bot)\n")
    try:
        while True:
            time.sleep(10)
            try:
                r = requests.get(f"{BOT_URL}/api/plantilla/estado", timeout=10)
                estado = r.json()
                total = estado.get("total", 0)
                enviados = estado.get("enviados", 0)
                errores = estado.get("errores", 0)
                corriendo = estado.get("corriendo", False)
                pct = (enviados + errores) / total * 100 if total > 0 else 0
                print(f"  [{pct:.0f}%] Enviados: {enviados} | Errores: {errores} | Total: {total} | {'EN CURSO' if corriendo else 'FINALIZADO'}")
                if not corriendo:
                    print("\n=== ENVIO FINALIZADO ===")
                    log = estado.get("log", [])
                    if log:
                        print(f"Ultimas entradas del log:")
                        for entry in log[-10:]:
                            print(f"  {entry}")
                    break
            except Exception as e:
                print(f"  (Error consultando estado: {e})")
    except KeyboardInterrupt:
        print("\nMonitoreo detenido. El envio continua en el bot.")
        print(f"Consulta estado manualmente: {BOT_URL}/api/plantilla/estado")

if __name__ == "__main__":
    main()
