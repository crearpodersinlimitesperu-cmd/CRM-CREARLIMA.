import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
import pandas as pd
import re

def populate():
    # 1. CONECTAR
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = SAC.from_json_keyfile_name('credenciales.json', scope)
    client = gspread.authorize(creds)
    
    # Abrir el sheet de HISTORIAL
    sh_hist = client.open_by_key('1NqEgzCkixVhMn3VLhsy_GVWwYBfwLQ1rwdHVcKTRyjo')
    ws_hist = sh_hist.worksheet("Historial Completo")
    data_h = ws_hist.get_all_values()
    headers_h = data_h[0]
    df_h = pd.DataFrame(data_h[1:], columns=headers_h)
    
    col_fecha = [c for c in headers_h if 'FECHA' in c.upper()][0]
    col_tel_h = [c for c in headers_h if 'TEL' in c.upper()][0]
    col_tipo = [c for c in headers_h if 'TIPO' in c.upper()][0]
    col_msg = [c for c in headers_h if 'MENSAJE' in c.upper()][0]

    # Filtrar solo hoy 30/04
    df_hoy = df_h[df_h[col_fecha].astype(str).str.contains("30/04")].copy()

    # 2. MAPEO EQUIPOS (Cargar de Hoja 1)
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
    p_map = {}
    for _, row in df_p.iterrows():
        p_map[row['tel_clean']] = {
            "nombre": f"{row[c_p_nom]} {row[c_p_ape]}",
            "equipo": str(row[c_p_eq]).upper().strip()
        }

    CC_POR_EQUIPO = {
        "EQUIPO 26": "Diana Moscoso", "EQUIPO 25": "Joyce Marin", "EQUIPO 24": "Diana Moscoso",
        "EQUIPO 23": "Joyce Marin", "EQUIPO 22": "Joyce Marin", "EQUIPO 21": "Joyce Marin",
        "EQUIPO 20": "Joyce Marin", "EQUIPO 19": "Diana Moscoso", "EQUIPO 18": "Diana Moscoso",
        "EQUIPO 17": "Diana Moscoso", "EQUIPO 16": "Diana Moscoso", "EQUIPO 15": "Diana Moscoso",
        "EQUIPO 14": "Diana Moscoso",
    }

    rows_to_log = []
    # 3. PROCESAR HISTORIAL PARA LLENAR LOG
    for tel, group in df_hoy.groupby(col_tel_h):
        tel_clean = clean_tel(tel)
        p_data = p_map.get(tel_clean, {"nombre": "Participante Desconocido", "equipo": "DESCONOCIDO"})
        cc = CC_POR_EQUIPO.get(p_data["equipo"], "Diana Moscoso") # Default
        
        respuestas = group[group[col_tipo].astype(str).str.contains('CLIENTE', case=False)][col_msg].tolist()
        if not respuestas: continue
        
        msg = " | ".join(respuestas)
        if "[button]" in msg and len(msg) < 15: continue
        
        fecha_full = group[col_fecha].iloc[-1]
        fecha_p = fecha_full.split()[0] + "/2026"
        hora_p = fecha_full.split()[1] if len(fecha_full.split()) > 1 else ""
        
        rows_to_log.append([fecha_p, hora_p, cc, p_data["nombre"], tel_clean, msg, "DERIVADO"])

    # 4. SUBIR A LOG_DERIVACIONES
    ws_log = sh_master.worksheet("LOG_DERIVACIONES")
    if rows_to_log:
        ws_log.append_rows(rows_to_log)
        print(f"✅ Cargadas {len(rows_to_log)} filas a LOG_DERIVACIONES.")
    else:
        print("⚠️ No se encontraron filas para cargar.")

if __name__ == "__main__":
    populate()
