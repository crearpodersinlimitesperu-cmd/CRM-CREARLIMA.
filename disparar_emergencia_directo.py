"""
DISPARADOR DIRECTO - emergencia_enrolamiento
Lee Excel y envia al bot de Render SIN confirmacion interactiva.
"""
import pandas as pd
import requests
import time
import json

BOT_URL = "https://bot-cpsl.onrender.com"
EXCEL_PATH = r"C:\Users\josem\Downloads\Reportes y Gestión\CONFIRMACIONES Y CIERRES.xlsx"
PLANTILLA = "emergencia_enrolamiento_c1e27"
PAUSA = 15

df = pd.read_excel(EXCEL_PATH)
print(f"Registros: {len(df)}")

contactos = []
seen = set()
for _, row in df.iterrows():
    tel = str(row.get("TeléfonoMovil", "")).strip().replace(" ","").replace("-","").replace("+","")
    nombre = str(row.get("NombrePreferido", "")).strip()
    if not nombre or nombre == "nan":
        nombre = str(row.get("NombreCompleto", "Amigo")).split()[0]
    if not tel or tel == "nan" or len(tel) < 10 or tel in seen:
        continue
    seen.add(tel)
    contactos.append({"tel": tel, "nombre": nombre.title()})

print(f"Contactos unicos: {len(contactos)}")

# DISPARAR
print(f"Enviando {len(contactos)} contactos al bot con plantilla '{PLANTILLA}'...")
r = requests.post(
    f"{BOT_URL}/api/plantilla/enviar_lote",
    json={"contactos": contactos, "plantilla": PLANTILLA, "pausa": PAUSA},
    timeout=30
)
print(f"Bot responde: {r.status_code}")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))

# MONITOREAR
print("\n--- MONITOREANDO ---")
while True:
    time.sleep(12)
    try:
        r2 = requests.get(f"{BOT_URL}/api/plantilla/estado", timeout=10)
        e = r2.json()
        t, ok, err, run = e.get("total",0), e.get("enviados",0), e.get("errores",0), e.get("corriendo",False)
        pct = (ok+err)/t*100 if t>0 else 0
        print(f"  [{pct:.0f}%] Enviados: {ok} | Errores: {err} | Total: {t} | {'CORRIENDO' if run else 'FIN'}")
        if not run:
            print("\n=== ENVIO FINALIZADO ===")
            for entry in e.get("log",[])[-15:]:
                print(f"  {entry}")
            break
    except Exception as ex:
        print(f"  (Error: {ex})")
