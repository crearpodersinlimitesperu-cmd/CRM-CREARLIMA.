import pandas as pd
from datetime import datetime

def main():
    try:
        df = pd.read_csv("historial_completo_sheet.csv")
    except Exception as e:
        print("Error leyendo CSV:", e)
        return

    # Normalizamos nombres de columnas por si hay espacios
    df.columns = [c.strip() for c in df.columns]

    # Vamos a buscar interacciones recientes (ej: últimos 500 registros) 
    # que sean derivados (TIPO contenga CONFIRMA, DERIVADO, NEGATIVA, etc)
    # y los agrupamos por coordinadora.
    # En el CRM local o bot se envia un correo a la CC. Aquí generaremos un reporte.

    if "MENSAJE" not in df.columns or "TIPO" not in df.columns:
        print("Columnas no esperadas:", df.columns.tolist())
        return

    # Filtrar solo registros del día de hoy o recientes
    # Asumimos que la fecha está en "FECHA Y HORA"
    hoy_str = datetime.now().strftime("%d/%m/%Y")
    
    casos = []
    for _, row in df.tail(1000).iterrows():
        tipo = str(row.get("TIPO", "")).upper()
        msg = str(row.get("MENSAJE", ""))
        fecha = str(row.get("FECHA Y HORA", ""))
        nombre = str(row.get("IDENTIDAD", ""))
        tel = str(row.get("TELÉFONO", ""))
        
        # Filtramos los eventos de cliente
        if "CLIENTE" in tipo:
            # Determinamos si el mensaje tiene pinta de ser relevante (más de 1-2 letras y no sea solo un emoji)
            if len(msg) > 2 and "[button]" not in msg.lower():
                casos.append({
                    "Fecha": fecha,
                    "PX": nombre,
                    "Telefono": tel,
                    "Tipo": tipo,
                    "Mensaje": msg
                })
            
    # Guardamos en un txt para leerlo tranquilo sin fallos de consola
    with open("reporte_derivaciones_cc.txt", "w", encoding="utf-8") as f:
        f.write("REPORTE DE CASOS DERIVADOS RECIENTES\n")
        f.write("====================================\n\n")
        for c in casos[-50:]:  # últimos 50
            f.write(f"[{c['Fecha']}] {c['Tipo']} - {c['PX']} ({c['Telefono']})\n")
            f.write(f"Mensaje: {c['Mensaje']}\n")
            f.write("-" * 40 + "\n")
            
    print("Reporte generado en reporte_derivaciones_cc.txt")

if __name__ == "__main__":
    main()
