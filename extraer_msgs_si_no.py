"""
Extraer los mensajes REALES enviados por el bot a quienes confirmaron (SI) y a quienes dijeron NO.
Muestra el flujo completo: mensaje del PX -> respuesta del bot.
"""
import json

with open('historial_dump.json', 'r', encoding='utf-8') as f:
    vals = json.load(f)

headers = vals[0]
rows = vals[1:]

# Columnas
ci_fecha = 0  # FECHA Y HORA
ci_ident = 1  # IDENTIDAD
ci_tel   = 2  # TELEFONO
ci_tipo  = 3  # TIPO
ci_msg   = 4  # MENSAJE

# Buscar secuencias: PX dice algo -> Bot responde
# Agrupar por telefono, mantener orden cronologico
from collections import defaultdict
convos = defaultdict(list)
for row in rows:
    tel = row[ci_tel]
    convos[tel].append(row)

# Clasificar
confirmados = {}  # tel -> {px_msg, bot_response}
negativos = {}

for tel, msgs in convos.items():
    for i, row in enumerate(msgs):
        tipo = row[ci_tipo].strip().upper()
        msg = row[ci_msg].strip()
        
        if 'CLIENTE' not in tipo:
            continue
        
        msg_upper = msg.upper()
        
        # Buscar la respuesta del bot (siguiente mensaje BOT para este tel)
        bot_response = ""
        for j in range(i+1, min(i+5, len(msgs))):
            if 'BOT' in msgs[j][ci_tipo].upper() or 'STAFF' in msgs[j][ci_tipo].upper():
                bot_response = msgs[j][ci_msg].strip()
                break
        
        # Clasificar
        es_si = any(x in msg_upper for x in ['CONFIRMO', 'SI CONFIRMO', 'SI, CONFIRMO', 'SI ESTARE', 'SI ASISTIRE', 'VOY A ASISTIR'])
        es_no = any(x in msg_upper for x in ['NO ASISTIRE', 'NO PODRE', 'STOP', 'NO VOY', 'NO PUEDO ASISTIR', 'NO ASISTIRÉ'])
        
        if es_si and tel not in confirmados:
            nombre = row[ci_ident]
            confirmados[tel] = {
                "nombre": nombre,
                "fecha": row[ci_fecha],
                "px_msg": msg,
                "bot_response": bot_response
            }
        elif es_no and tel not in negativos:
            nombre = row[ci_ident]
            negativos[tel] = {
                "nombre": nombre,
                "fecha": row[ci_fecha],
                "px_msg": msg,
                "bot_response": bot_response
            }

# Escribir resultado
with open('MENSAJES_ENVIADOS_SI_NO.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("  MENSAJES ENVIADOS A QUIENES RESPONDIERON 'SÍ' (CONFIRMARON)\n")
    f.write("=" * 70 + "\n\n")
    
    for tel, data in confirmados.items():
        f.write(f"👤 {data['nombre']} | Tel: {tel}\n")
        f.write(f"📅 {data['fecha']}\n")
        f.write(f"💬 PX dijo: \"{data['px_msg']}\"\n")
        f.write(f"🤖 Bot respondió:\n")
        f.write(f"   {data['bot_response']}\n")
        f.write("-" * 70 + "\n\n")
    
    f.write("\n\n")
    f.write("=" * 70 + "\n")
    f.write("  MENSAJES ENVIADOS A QUIENES RESPONDIERON 'NO' (NEGATIVAS)\n")
    f.write("=" * 70 + "\n\n")
    
    for tel, data in negativos.items():
        f.write(f"👤 {data['nombre']} | Tel: {tel}\n")
        f.write(f"📅 {data['fecha']}\n")
        f.write(f"💬 PX dijo: \"{data['px_msg']}\"\n")
        f.write(f"🤖 Bot respondió:\n")
        f.write(f"   {data['bot_response']}\n")
        f.write("-" * 70 + "\n\n")

    f.write(f"\n\nRESUMEN: {len(confirmados)} confirmados, {len(negativos)} negativos\n")

print(f"Archivo generado: MENSAJES_ENVIADOS_SI_NO.txt")
print(f"Confirmados (SI): {len(confirmados)}")
print(f"Negativos (NO): {len(negativos)}")
