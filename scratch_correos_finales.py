import pandas as pd
import json

def main():
    # Cargar respuestas
    with open("reporte_derivaciones_cc.txt", "r", encoding="utf-8") as f:
        lineas = f.readlines()
        
    # Cargar base de datos
    try:
        db = pd.read_csv("E27_participantes_limpio.csv", encoding="utf-8-sig")
    except:
        db = pd.DataFrame()
        
    casos = []
    caso_actual = {}
    for linea in lineas:
        if linea.startswith("[30/04"):
            # Parse header
            parts = linea.split("-")
            header = parts[0].strip()
            persona = "-".join(parts[1:]).strip()
            # Extraer telefono (xxxx)
            import re
            m = re.search(r'\((\d+)\)', persona)
            tel = m.group(1) if m else ""
            nom = persona.replace(f"({tel})", "").strip()
            caso_actual = {"tel": tel, "nom": nom, "msg": []}
        elif linea.startswith("Mensaje:"):
            if "msg" in caso_actual:
                caso_actual["msg"].append(linea.replace("Mensaje:", "").strip())
        elif linea.startswith("----"):
            if caso_actual and caso_actual["msg"]:
                # Es un autoresponder o robot si tiene "[button]" o "Gracias por comunicarte"
                txt = " ".join(caso_actual["msg"])
                if "[button]" not in txt and "Gracias por comunicarte" not in txt and "¡Hola! Gracias por escribir" not in txt:
                    casos.append(caso_actual)
            caso_actual = {}

    # Agrupar por CC
    # Buscar el CC del tel
    cc_map = {}
    if not db.empty:
        for _, row in db.iterrows():
            tel = str(row.get("Telefono", "")).strip()
            # Clean tel
            import re
            tel = re.sub(r'[^\d]', '', tel)
            if len(tel) == 9: tel = "51" + tel
            cc = str(row.get("CC_Asignada", "SIN ASIGNAR")).upper()
            cc_map[tel] = cc

    correos = {"DIANA": [], "JOYCE": [], "ZULEY": [], "SIN ASIGNAR": []}
    
    for c in casos:
        tel = c["tel"]
        cc = cc_map.get(tel)
        if not cc:
            # Buscar sin el 51
            tel2 = tel[2:] if tel.startswith("51") else tel
            cc = cc_map.get(tel2, "SIN ASIGNAR")
            
        # Normalizar cc
        cc_norm = "SIN ASIGNAR"
        if "DIANA" in cc: cc_norm = "DIANA"
        elif "JOYCE" in cc: cc_norm = "JOYCE"
        elif "ZULEY" in cc: cc_norm = "ZULEY"
        
        correos[cc_norm].append(c)

    with open("correos_cc_finales.txt", "w", encoding="utf-8") as out:
        for cc, lista in correos.items():
            if not lista: continue
            out.write(f"=== CORREO PARA {cc} ===\n")
            out.write(f"Asunto: URGENTE - Acciones requeridas C1E27 - Casos derivados bot WhatsApp\n\n")
            out.write(f"Hola {cc.title()},\n\n")
            out.write("El sistema automático de WhatsApp (Bot) ha finalizado el envío de emergencia y hemos recibido las siguientes respuestas de tus participantes que requieren gestión inmediata (SLA 12 horas).\n\n")
            out.write("IMPORTANTE: Para que el bot DEJE de enviarles mensajes de seguimiento, DEBES actualizar la pestaña PRODUCTIVIDAD en Google Sheets. Cambia su 'Asistencia' a 'SI' o su 'Resultado Gestión' a algo distinto de 'NO CONTESTA'.\n\n")
            out.write("Detalle de respuestas entrantes:\n\n")
            for c in lista:
                out.write(f"👤 {c['nom']} (Tel: {c['tel']})\n")
                out.write(f"💬 Respondió: \"{' '.join(c['msg'])}\"\n")
                out.write(f"👉 Acción sugerida: Contactar y actualizar estado en Google Sheets.\n\n")
            out.write("---------------------------------------------------\n\n")

if __name__ == "__main__":
    main()
