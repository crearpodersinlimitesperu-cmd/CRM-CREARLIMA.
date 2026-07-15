import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
import pandas as pd
import json
import re
from datetime import datetime

def generate():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = SAC.from_json_keyfile_name('credenciales.json', scope)
    client = gspread.authorize(creds)
    
    CC_POR_EQUIPO = {
        "EQUIPO 26": "DIANA", "EQUIPO 25": "JOYCE", "EQUIPO 24": "DIANA",
        "EQUIPO 23": "JOYCE", "EQUIPO 22": "JOYCE", "EQUIPO 21": "JOYCE",
        "EQUIPO 20": "JOYCE", "EQUIPO 19": "DIANA", "EQUIPO 18": "DIANA",
        "EQUIPO 17": "DIANA", "EQUIPO 16": "DIANA", "EQUIPO 15": "DIANA",
        "EQUIPO 14": "DIANA",
    }

    # 1. CARGAR HISTORIAL
    sh_hist = client.open_by_key('1NqEgzCkixVhMn3VLhsy_GVWwYBfwLQ1rwdHVcKTRyjo')
    ws_hist = sh_hist.worksheet("Historial Completo")
    data_h = ws_hist.get_all_values()
    headers_h = data_h[0]
    df = pd.DataFrame(data_h[1:], columns=headers_h)
    
    col_fecha = [c for c in headers_h if 'FECHA' in c.upper()][0]
    col_tel_h = [c for c in headers_h if 'TEL' in c.upper()][0]
    col_tipo = [c for c in headers_h if 'TIPO' in c.upper()][0]
    col_msg = [c for c in headers_h if 'MENSAJE' in c.upper()][0]

    hoy = "30/04"
    df_hoy = df[df[col_fecha].astype(str).str.contains(hoy)].copy()
    
    # 2. CARGAR BASE MAESTRA
    try:
        sh_master = client.open_by_key('1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y')
        ws_p = sh_master.worksheet("Hoja 1")
        data_p = ws_p.get_all_values()
        headers_p = data_p[0]
        df_p = pd.DataFrame(data_p[1:], columns=headers_p)
        
        c_p_nom = [c for c in headers_p if 'NOMBRE' in c.upper()][0]
        c_p_ape = [c for c in headers_p if 'APELLIDO' in c.upper()][0]
        c_p_tel = [c for c in headers_p if 'TEL' in c.upper() and 'IMO' not in c.upper()][0]
        c_p_eq = [c for c in headers_p if 'EQUIPO' in c.upper()][0]
        
        def clean_tel(t):
            t = re.sub(r'[^\d]', '', str(t))
            if len(t) == 9: t = "51" + t
            return t
        
        df_p['tel_clean'] = df_p[c_p_tel].apply(clean_tel)
        p_info_map = {}
        for _, row in df_p.iterrows():
            t = row['tel_clean']
            p_info_map[t] = {
                "nombre": f"{row[c_p_nom]} {row[c_p_ape]}",
                "equipo": str(row[c_p_eq]).upper().strip()
            }
    except Exception as e:
        print(f"Error base maestra: {e}")
        p_info_map = {}

    casos_diana = []
    casos_joyce = []
    
    # 3. PROCESAR
    for tel, group in df_hoy.groupby(col_tel_h):
        tel_str = str(tel)
        tel_clean = re.sub(r'[^\d]', '', tel_str)
        if len(tel_clean) == 9: tel_clean = "51" + tel_clean
        
        p_data = p_info_map.get(tel_clean, {"nombre": "Participante Desconocido", "equipo": "DESCONOCIDO"})
        nombre = p_data["nombre"]
        equipo = p_data["equipo"]
        cc_asignada = CC_POR_EQUIPO.get(equipo, "SIN ASIGNAR")
        
        respuestas = group[group[col_tipo].astype(str).str.contains('CLIENTE', case=False)][col_msg].tolist()
        if not respuestas: continue
        
        msg_concatenado = " | ".join(respuestas)
        if "[button]" in msg_concatenado and len(msg_concatenado) < 15: continue
        
        es_confirmacion = any(x in msg_concatenado.upper() for x in ["SI", "CONFIRMO", "ASISTIR", "VOY"])
        
        caso = {
            "Fecha/Hora": group[col_fecha].iloc[-1],
            "Participante": nombre,
            "Telefono": f"wa.me/{tel_clean}",
            "Respuesta": msg_concatenado,
            "Tipo": "CONFIRMACION" if es_confirmacion else "DERIVACION"
        }
        
        if cc_asignada == "DIANA": casos_diana.append(caso)
        elif cc_asignada == "JOYCE": casos_joyce.append(caso)
        else:
            bot_msgs = group[group[col_tipo].astype(str).str.contains('BOT', case=False)][col_msg].tolist()
            if any("Diana" in m for m in bot_msgs): casos_diana.append(caso)
            elif any("Joyce" in m for m in bot_msgs): casos_joyce.append(caso)

    # 4. SALIDA
    def clean_txt(t): return str(t).encode('ascii', 'ignore').decode()

    with open("REPORTE_CORREO_CC.txt", "w", encoding="utf-8") as f:
        f.write("=== BORRADOR DE CORREO - DIANA MOSCOSO ===\n")
        f.write(f"Asunto: URGENTE - {len(casos_diana)} Casos por gestionar hoy 30/04 - C1E27\n\n")
        f.write("Hola Diana,\n\n")
        f.write("Te adjunto el reporte de las nuevas derivaciones y confirmaciones recibidas hoy.\n")
        f.write("Por favor, confirma cada caso en el CRM o en PRODUCTIVIDAD.\n\n")
        for c in casos_diana:
            f.write(f"👤 {c['Participante']} ({c['Telefono']})\n")
            f.write(f"💬 {c['Respuesta']}\n")
            f.write(f"👉 Tipo: {c['Tipo']}\n\n")
        
        f.write("\n\n" + "="*50 + "\n\n")
        
        f.write("=== BORRADOR DE CORREO - JOYCE MARIN ===\n")
        f.write(f"Asunto: URGENTE - {len(casos_joyce)} Casos por gestionar hoy 30/04 - C1E27\n\n")
        f.write("Hola Joyce,\n\n")
        f.write("Te adjunto el reporte de las nuevas derivaciones y confirmaciones recibidas hoy.\n")
        f.write("Por favor, confirma cada caso en el CRM o en PRODUCTIVIDAD.\n\n")
        for c in casos_joyce:
            f.write(f"👤 {c['Participante']} ({c['Telefono']})\n")
            f.write(f"💬 {c['Respuesta']}\n")
            f.write(f"👉 Tipo: {c['Tipo']}\n\n")

    if casos_diana:
        pd.DataFrame(casos_diana).to_excel("DERIVACIONES_DIANA_30ABR.xlsx", index=False)
        print("Excel generado: DERIVACIONES_DIANA_30ABR.xlsx")
    if casos_joyce:
        pd.DataFrame(casos_joyce).to_excel("DERIVACIONES_JOYCE_30ABR.xlsx", index=False)
        print("Excel generado: DERIVACIONES_JOYCE_30ABR.xlsx")
    
    print("Reporte de correo guardado en REPORTE_CORREO_CC.txt")

if __name__ == "__main__":
    generate()
