"""
FULL_DERIVACIONES_CC.py  v2 — SYNC BIDIRECCIONAL
1. LEE los Excels de las CCs en OneDrive (preserva GESTIONADO + COMENTARIOS)
2. Detecta casos NUEVOS del historial que no estan en los Excels
3. Agrega solo los nuevos AL FINAL, sin tocar los existentes
4. Sube el progreso de las CCs a LOG_DERIVACIONES en Sheets
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
import pandas as pd
import os
import re

BASE_ONEDRIVE = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA"
FILE_DIANA = os.path.join(BASE_ONEDRIVE, "DERIVACIONES_DIANA_30ABR.xlsx")
FILE_JOYCE = os.path.join(BASE_ONEDRIVE, "DERIVACIONES_JOYCE_30ABR.xlsx")

CC_POR_EQUIPO = {
    "EQUIPO 26": "Diana Moscoso", "EQUIPO 25": "Joyce Marin",
    "EQUIPO 24": "Diana Moscoso", "EQUIPO 23": "Joyce Marin",
    "EQUIPO 22": "Joyce Marin",   "EQUIPO 21": "Joyce Marin",
    "EQUIPO 20": "Joyce Marin",   "EQUIPO 19": "Diana Moscoso",
    "EQUIPO 18": "Diana Moscoso", "EQUIPO 17": "Diana Moscoso",
    "EQUIPO 16": "Diana Moscoso", "EQUIPO 15": "Diana Moscoso",
    "EQUIPO 14": "Diana Moscoso",
}

def clean_tel(t):
    t = re.sub(r'[^\d]', '', str(t))
    if len(t) == 9: t = "51" + t
    return t

def leer_excel_local(path):
    """Lee el Excel local y devuelve un dict {telefono: {GESTIONADO, COMENTARIOS CC, ...}}"""
    if not os.path.exists(path):
        return {}, pd.DataFrame()
    try:
        df = pd.read_excel(path)
        # Asegurar columnas de gestion
        if 'GESTIONADO' not in df.columns:
            df['GESTIONADO'] = 'NO'
        if 'COMENTARIOS CC' not in df.columns:
            df['COMENTARIOS CC'] = ''
        # Crear mapa de avances por telefono (normalizado)
        avances = {}
        for _, row in df.iterrows():
            tel_raw = str(row.get('Telefono', '')).strip()
            # Normalizar: quitar .0 de float, limpiar
            tel_raw = tel_raw.replace('.0', '')
            tel = clean_tel(tel_raw)
            avances[tel] = {
                'GESTIONADO': str(row.get('GESTIONADO', 'NO')).strip(),
                'COMENTARIOS CC': str(row.get('COMENTARIOS CC', '')).strip()
            }
        return avances, df
    except Exception as e:
        print(f"Error leyendo {path}: {e}")
        return {}, pd.DataFrame()

def run():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = SAC.from_json_keyfile_name('credenciales.json', scope)
    client = gspread.authorize(creds)

    # ══════════════════════════════════════════════════
    # PASO 0: LEER AVANCES EXISTENTES DE LAS CCs
    # ══════════════════════════════════════════════════
    avances_diana, df_diana_local = leer_excel_local(FILE_DIANA)
    avances_joyce, df_joyce_local = leer_excel_local(FILE_JOYCE)

    tels_ya_diana = set(avances_diana.keys())
    tels_ya_joyce = set(avances_joyce.keys())

    print(f"Avances leidos - Diana: {len(tels_ya_diana)} casos | Joyce: {len(tels_ya_joyce)} casos")
    gestionados_d = sum(1 for v in avances_diana.values() if v['GESTIONADO'].upper() == 'SI')
    gestionados_j = sum(1 for v in avances_joyce.values() if v['GESTIONADO'].upper() == 'SI')
    print(f"Ya gestionados - Diana: {gestionados_d} | Joyce: {gestionados_j}")

    # ══════════════════════════════════════════════════
    # PASO 1: CARGAR HISTORIAL COMPLETO
    # ══════════════════════════════════════════════════
    sh_hist = client.open_by_key('1NqEgzCkixVhMn3VLhsy_GVWwYBfwLQ1rwdHVcKTRyjo')
    ws_hist = sh_hist.worksheet("Historial Completo")
    all_vals = ws_hist.get_all_values()
    headers_h = all_vals[0]
    df_h = pd.DataFrame(all_vals[1:], columns=headers_h)

    col_fecha = [c for c in headers_h if 'FECHA' in c.upper()][0]
    col_tel   = [c for c in headers_h if 'TEL' in c.upper()][0]
    col_tipo  = [c for c in headers_h if 'TIPO' in c.upper()][0]
    col_msg   = [c for c in headers_h if 'MENSAJE' in c.upper()][0]
    col_id    = [c for c in headers_h if 'IDENTIDAD' in c.upper() or 'IDENT' in c.upper()][0]

    print(f"Historial cargado: {len(df_h)} filas")

    # ══════════════════════════════════════════════════
    # PASO 2: CARGAR BASE MAESTRA (NOMBRES + EQUIPOS)
    # ══════════════════════════════════════════════════
    sh_master = client.open_by_key('1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y')
    ws_p = sh_master.worksheet("Hoja 1")
    data_p = ws_p.get_all_values()
    headers_p = data_p[0]
    df_p = pd.DataFrame(data_p[1:], columns=headers_p)

    c_nom = [c for c in headers_p if 'NOMBRE' in c.upper()][0]
    c_ape = [c for c in headers_p if 'APELLIDO' in c.upper()][0]
    c_tel = [c for c in headers_p if 'TEL' in c.upper() and 'IMO' not in c.upper()][0]
    c_eq  = [c for c in headers_p if 'EQUIPO' in c.upper()][0]

    df_p['tel_clean'] = df_p[c_tel].apply(clean_tel)
    p_map = {}
    for _, row in df_p.iterrows():
        p_map[row['tel_clean']] = {
            "nombre": f"{row[c_nom]} {row[c_ape]}".strip(),
            "equipo": str(row[c_eq]).upper().strip()
        }

    # ══════════════════════════════════════════════════
    # PASO 3: PROCESAR HISTORIAL - SOLO CASOS NUEVOS
    # ══════════════════════════════════════════════════
    df_clientes = df_h[df_h[col_tipo].str.contains('CLIENTE', case=False, na=False)].copy()
    df_clientes['tel_clean'] = df_clientes[col_tel].apply(clean_tel)
    df_bot = df_h[df_h[col_tipo].str.contains('BOT', case=False, na=False)].copy()

    nuevos_diana = []
    nuevos_joyce = []
    # Tambien reconstruimos TODOS para actualizar el ultimo contacto en existentes
    actualizaciones = {}  # tel -> {ultima_fecha, ultimo_msg, total_msgs}
    tels_procesados = set()

    for tel_clean, grp in df_clientes.groupby('tel_clean'):
        if tel_clean in tels_procesados:
            continue
        # Ignorar tels invalidos (simulaciones, basura)
        if len(tel_clean) < 9 or tel_clean.startswith('SIM'):
            continue
        tels_procesados.add(tel_clean)

        p_data = p_map.get(tel_clean, None)
        if p_data:
            nombre = p_data["nombre"]
            equipo = p_data["equipo"]
        else:
            identidades = grp[col_id].tolist()
            nombre_raw = ""
            for ident in identidades:
                m = re.search(r'\((?:PX|IMO|CC)\)\s*(.*)', str(ident))
                if m:
                    nombre_raw = m.group(1).strip()
                    break
            nombre = nombre_raw if nombre_raw else f"Desconocido ({tel_clean})"
            equipo = "DESCONOCIDO"

        cc = CC_POR_EQUIPO.get(equipo, None)
        if not cc:
            bot_msgs_tel = df_bot[df_bot[col_tel] == tel_clean][col_msg].tolist()
            for bm in bot_msgs_tel:
                if "Diana" in str(bm):
                    cc = "Diana Moscoso"; break
                elif "Joyce" in str(bm):
                    cc = "Joyce Marin"; break
        if not cc:
            cc = "Diana Moscoso"

        mensajes = grp[col_msg].tolist()
        fechas = grp[col_fecha].tolist()
        primera_fecha = fechas[0] if fechas else ""
        ultima_fecha = fechas[-1] if fechas else ""

        ultimo_msg_real = ""
        for m in reversed(mensajes):
            if m.strip() and "[button]" not in m and "[sticker]" not in m:
                ultimo_msg_real = m.strip()
                break

        todos_msgs = []
        seen = set()
        for m in mensajes:
            m_clean = m.strip()
            if m_clean and m_clean not in seen:
                seen.add(m_clean)
                todos_msgs.append(m_clean)

        es_confirmacion = any(x in " ".join(todos_msgs).upper() for x in
            ["CONFIRMO", "SI CONFIRMO", "SI, CONFIRMO", "ASISTIRE", "VOY A ASISTIR", "SI ESTARE"])
        es_negativa = any(x in " ".join(todos_msgs).upper() for x in
            ["NO ASISTIRE", "NO PODRE", "NO VOY", "STOP", "CANCELAR", "NO PUEDO", "REEMBOLSO", "DEVOLUCION"])
        es_autoresponder = any(x in " ".join(todos_msgs).upper() for x in
            ["GRACIAS POR COMUNICARTE CON", "SOY PARTE DEL EQUIPO DE", "ESTOY PARA BRINDARLE"])

        if es_confirmacion:
            tipo = "CONFIRMACION"
        elif es_negativa:
            tipo = "NEGATIVA / NO ASISTE"
        elif es_autoresponder:
            tipo = "AUTORESPONDER (verificar)"
        else:
            tipo = "CONSULTA / PENDIENTE"

        # Guardar actualizaciones de ultimo contacto para TODOS
        actualizaciones[tel_clean] = {
            "ultima_fecha": ultima_fecha,
            "ultimo_msg": ultimo_msg_real[:200],
            "total_msgs": len(todos_msgs),
            "clasificacion": tipo
        }

        # Verificar si es NUEVO (no existe en el Excel actual de la CC)
        es_nuevo = False
        if cc == "Diana Moscoso" and tel_clean not in tels_ya_diana:
            es_nuevo = True
        elif cc == "Joyce Marin" and tel_clean not in tels_ya_joyce:
            es_nuevo = True

        if es_nuevo:
            caso = {
                "Participante": nombre,
                "Telefono": tel_clean,
                "WhatsApp": f"wa.me/{tel_clean}",
                "Equipo": equipo,
                "CC Asignada": cc,
                "Primer Contacto": primera_fecha,
                "Ultimo Contacto": ultima_fecha,
                "Total Msgs": len(todos_msgs),
                "Ultimo Mensaje": ultimo_msg_real[:200],
                "Todos los Mensajes": " | ".join(todos_msgs)[:500],
                "Clasificacion": tipo,
                "GESTIONADO": "NO",
                "COMENTARIOS CC": ""
            }
            if cc == "Diana Moscoso":
                nuevos_diana.append(caso)
            else:
                nuevos_joyce.append(caso)

    print(f"Casos NUEVOS detectados - Diana: {len(nuevos_diana)} | Joyce: {len(nuevos_joyce)}")

    # ══════════════════════════════════════════════════
    # PASO 4: ACTUALIZAR EXCELS (preservar avances + agregar nuevos)
    # ══════════════════════════════════════════════════
    for name, path, df_local, nuevos, avances in [
        ("Diana", FILE_DIANA, df_diana_local, nuevos_diana, avances_diana),
        ("Joyce", FILE_JOYCE, df_joyce_local, nuevos_joyce, avances_joyce)
    ]:
        if df_local.empty and not nuevos:
            continue

        # Actualizar campos dinamicos en filas existentes (ultimo contacto, msgs, clasificacion)
        if not df_local.empty:
            for idx, row in df_local.iterrows():
                tel_raw = str(row.get('Telefono', '')).strip().replace('.0', '')
                tel = clean_tel(tel_raw)
                # Normalizar el telefono en el DataFrame tambien
                df_local.at[idx, 'Telefono'] = tel
                if tel in actualizaciones:
                    upd = actualizaciones[tel]
                    df_local.at[idx, 'Ultimo Contacto'] = upd['ultima_fecha']
                    df_local.at[idx, 'Ultimo Mensaje'] = upd['ultimo_msg']
                    df_local.at[idx, 'Total Msgs'] = upd['total_msgs']
                    df_local.at[idx, 'Clasificacion'] = upd['clasificacion']
                    # NUNCA tocar GESTIONADO ni COMENTARIOS CC

        # Agregar nuevos al final
        if nuevos:
            df_nuevos = pd.DataFrame(nuevos)
            if df_local.empty:
                df_final = df_nuevos
            else:
                df_final = pd.concat([df_local, df_nuevos], ignore_index=True)
        else:
            df_final = df_local

        # DEDUPLICAR: mantener la primera (que tiene los avances de la CC)
        df_final['Telefono'] = df_final['Telefono'].astype(str).str.replace('.0', '', regex=False)
        df_final = df_final.drop_duplicates(subset='Telefono', keep='first')

        df_final.to_excel(path, index=False)
        print(f"Excel {name} guardado: {len(df_final)} filas ({len(nuevos)} nuevas)")


    # ══════════════════════════════════════════════════
    # PASO 5: SUBIR PROGRESO DE CCs A SHEETS
    # ══════════════════════════════════════════════════
    try:
        ws_log = sh_master.worksheet("LOG_DERIVACIONES")
    except gspread.exceptions.WorksheetNotFound:
        ws_log = sh_master.add_worksheet(title="LOG_DERIVACIONES", rows="5000", cols="12")

    ws_log.clear()
    header = ["Fecha", "Hora", "Coordinadora", "Participante", "Telefono",
              "Equipo", "Clasificacion", "Ultimo Mensaje", "Total Msgs",
              "GESTIONADO", "COMENTARIOS CC"]
    ws_log.update(values=[header], range_name='A1:K1')

    # Combinar avances existentes de ambas CCs
    todos_avances = {}
    todos_avances.update(avances_diana)
    todos_avances.update(avances_joyce)
    # Tambien agregar los nuevos (con GESTIONADO=NO)
    for caso in nuevos_diana + nuevos_joyce:
        tel = caso['Telefono']
        if tel not in todos_avances:
            todos_avances[tel] = {'GESTIONADO': 'NO', 'COMENTARIOS CC': ''}

    # Reconstruir filas completas para Sheets
    all_rows = []

    # Leer los Excels finales para tener datos actualizados
    for path, cc_name in [(FILE_DIANA, "Diana Moscoso"), (FILE_JOYCE, "Joyce Marin")]:
        if not os.path.exists(path):
            continue
        df = pd.read_excel(path)
        for _, row in df.iterrows():
            tel = str(row.get('Telefono', '')).strip()
            primer = str(row.get('Primer Contacto', '')).strip()
            fecha_p = primer.split()[0] if primer else ""
            hora_p = primer.split()[1] if len(primer.split()) > 1 else ""
            gestionado = str(row.get('GESTIONADO', 'NO')).strip()
            comentarios = str(row.get('COMENTARIOS CC', '')).strip()
            if comentarios == 'nan': comentarios = ''
            if gestionado == 'nan': gestionado = 'NO'
            
            all_rows.append([
                fecha_p, hora_p, cc_name,
                str(row.get('Participante', '')),
                tel,
                str(row.get('Equipo', '')),
                str(row.get('Clasificacion', '')),
                str(row.get('Ultimo Mensaje', ''))[:150],
                str(row.get('Total Msgs', '')),
                gestionado,
                comentarios
            ])

    if all_rows:
        for i in range(0, len(all_rows), 100):
            chunk = all_rows[i:i+100]
            start_row = i + 2
            end_row = start_row + len(chunk) - 1
            cell_range = f'A{start_row}:K{end_row}'
            ws_log.update(values=chunk, range_name=cell_range)
        print(f"LOG_DERIVACIONES actualizado: {len(all_rows)} filas (con avances de CCs)")

    print("SYNC COMPLETO - Avances preservados, nuevos agregados, progreso subido a Sheets.")

if __name__ == "__main__":
    run()
