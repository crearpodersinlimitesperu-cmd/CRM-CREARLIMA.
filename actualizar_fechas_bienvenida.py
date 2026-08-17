import json
import os
import csv
from datetime import datetime

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================
JSON_SOURCE = r'C:\Users\josem\Downloads\CREAR_CALENDAR\programacion_data.json'
CSV_FALLBACK = 'calendario_2027_todas_sedes.csv'

SEDE_MAP = {
    'LIM': 'LIM',
    'CUE': 'CUE',
    'MED': 'MED',
    'UIO1': 'UIO1',
    'UIO C1': 'UIO1',
    'UIO2': 'UIO2',
    'UIO C2': 'UIO2',
    'UIO': 'UIO1',
    'GYE': 'GYE',
    'MEX': 'MEX',
    'CDMX': 'MEX',
}

SEDE_CSV_MAP = {
    'LIM': 'LIM',
    'CUE': 'CUE',
    'MED': 'MED',
    'UIO C1': 'UIO1',
    'UIO C2': 'UIO2',
    'UIO': 'UIO1',
    'GYE': 'GYE',
    'MEX': 'MEX'
}

def extract_events(keyword, start_hour=9, json_output='calendario_c1.json'):
    print(f"\n--- Procesando eventos para '{keyword}' (Salida: {json_output}) ---")
    events_dict = {code: [] for code in set(SEDE_MAP.values())}

    # 1. Cargar desde JSON primario si existe
    if os.path.exists(JSON_SOURCE):
        print(f"Leyendo fuente primaria: {JSON_SOURCE}")
        with open(JSON_SOURCE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        eventos = data.get('eventos', data if isinstance(data, list) else [])
        for evento in eventos:
            tipo = str(evento.get('evento', '') or '').upper()
            if keyword.upper() not in tipo:
                continue
            
            sede_raw = str(evento.get('sede_key', '') or '').strip()
            sede_code = SEDE_MAP.get(sede_raw)
            if not sede_code:
                continue
            
            f_ini = str(evento.get('fecha_inicio', '') or '').strip()
            f_fin = str(evento.get('fecha_fin', '') or '').strip()
            try:
                start_obj = datetime.strptime(f_ini, '%Y-%m-%d')
            except ValueError:
                continue

            start_with_time = start_obj.replace(hour=start_hour, minute=0, second=0)
            entry = {
                'start': start_with_time.isoformat(),
                'equipo': str(evento.get('equipo', '')),
                'entrenador': str(evento.get('entrenador', '')),
            }
            if f_fin:
                try:
                    end_obj = datetime.strptime(f_fin, '%Y-%m-%d')
                    entry['end'] = end_obj.isoformat()
                except ValueError:
                    pass
            events_dict[sede_code].append(entry)

    # 2. Complementar con CSV Fallback
    if os.path.exists(CSV_FALLBACK):
        print(f"Leyendo fallback CSV: {CSV_FALLBACK}")
        with open(CSV_FALLBACK, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tipo = row.get('Entrenamiento', '').strip().upper()
                if keyword.upper() not in tipo:
                    continue
                sede_code = SEDE_CSV_MAP.get(row.get('Sede', '').strip())
                if not sede_code:
                    continue
                try:
                    date_obj = datetime.strptime(row.get('Fecha', '').strip(), '%d/%m/%Y')
                    start_with_time = date_obj.replace(hour=start_hour, minute=0, second=0)
                    events_dict[sede_code].append({
                        'start': start_with_time.isoformat(),
                        'equipo': str(row.get('Equipo', '')),
                        'entrenador': str(row.get('Entrenador', '')),
                    })
                except ValueError:
                    continue

    # 3. Deduplicar y ordenar
    for sede in events_dict:
        seen = set()
        deduped = []
        for ev in events_dict[sede]:
            key = (ev['start'][:10], ev['equipo'])
            if key not in seen:
                seen.add(key)
                deduped.append(ev)
        deduped.sort(key=lambda x: x['start'])
        events_dict[sede] = deduped

    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(events_dict, f, indent=4, ensure_ascii=False)

    print(f"OK Guardado: '{json_output}'")
    for sede, evs in sorted(events_dict.items()):
        if evs:
            now_str = datetime.now().isoformat()[:10]
            upcoming = [e for e in evs if e['start'][:10] >= now_str]
            prox = upcoming[0]['start'][:10] if upcoming else 'sin futuros'
            print(f"  - {sede}: {len(evs)} eventos | Proximo: {prox}")

def main():
    # Generar Capítulo Uno (inicia viernes a las 09:00)
    extract_events('CAPITULO UNO', start_hour=9, json_output='calendario_c1.json')
    # Generar Capítulo Dos (inicia jueves a las 13:00)
    extract_events('CAPITULO DOS', start_hour=13, json_output='calendario_c2.json')

if __name__ == "__main__":
    main()
