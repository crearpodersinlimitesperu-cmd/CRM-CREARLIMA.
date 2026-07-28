import json
import os
from datetime import datetime

# ==========================================
# CONFIGURACIÓN
# ==========================================
# Fuente primaria: JSON maestro (tiene toda la data de sedes, fechas inicio/fin, equipo)
JSON_SOURCE = r'C:\Users\josem\Downloads\CREAR_CALENDAR\programacion_data.json'

# Fallback: CSV general de todas las sedes 2027+
CSV_FALLBACK = 'calendario_2027_todas_sedes.csv'

# Salida: JSON que la página web usará para cargar fechas dinámicas
JSON_OUTPUT = 'calendario_c1.json'

# Mapeo de sede_key → código interno del HTML
SEDE_MAP = {
    'LIM': 'LIM',
    'CUE': 'CUE',
    'MED': 'MED',
    'UIO1': 'UIO1',
    'UIO C1': 'UIO1',
    'UIO2': 'UIO2',
    'UIO C2': 'UIO2',
    'GYE': 'GYE',
    'MEX': 'MEX',
    'CDMX': 'MEX',
}

def load_from_primary_json(filepath):
    """Lee el JSON maestro (programacion_data.json) y extrae todos los C1 futuros."""
    print(f"Leyendo fuente primaria: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    eventos = data.get('eventos', data if isinstance(data, list) else [])
    
    c1_events = {code: [] for code in set(SEDE_MAP.values())}
    
    for evento in eventos:
        evento_tipo = str(evento.get('evento', '') or '').strip()
        if 'CAPITULO UNO' not in evento_tipo:
            continue
        
        sede_key_raw = str(evento.get('sede_key', '') or '').strip()
        sede_code = SEDE_MAP.get(sede_key_raw)
        if not sede_code:
            continue
        
        fecha_inicio_str = str(evento.get('fecha_inicio', '') or '').strip()
        fecha_fin_str = str(evento.get('fecha_fin', '') or '').strip()
        
        try:
            start_obj = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        except ValueError:
            continue
        
        # Guardamos con hora de inicio estándar (09:00)
        start_with_time = start_obj.replace(hour=9, minute=0, second=0)
        
        entry = {
            'start': start_with_time.isoformat(),
            'equipo': str(evento.get('equipo', '')),
            'entrenador': str(evento.get('entrenador', '')),
        }
        
        if fecha_fin_str:
            try:
                end_obj = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
                entry['end'] = end_obj.isoformat()
            except ValueError:
                pass
        
        c1_events[sede_code].append(entry)
    
    # Ordenar por fecha
    for sede in c1_events:
        c1_events[sede].sort(key=lambda x: x['start'])
    
    total = sum(len(v) for v in c1_events.values())
    print(f"  >> Encontrados {total} eventos de C1 en total.")
    return c1_events


def load_from_fallback_csv(filepath):
    """Fallback: lee el CSV general si el JSON primario no existe."""
    import csv
    print(f"Usando fallback CSV: {filepath}")
    
    SEDE_CSV_MAP = {
        'LIM': 'LIM', 'CUE': 'CUE', 'MED': 'MED',
        'UIO C1': 'UIO1', 'UIO C2': 'UIO2', 'GYE': 'GYE', 'MEX': 'MEX'
    }
    
    c1_events = {code: [] for code in set(SEDE_MAP.values())}
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Entrenamiento', '').strip() != 'CAPITULO UNO':
                continue
            sede_code = SEDE_CSV_MAP.get(row.get('Sede', '').strip())
            if not sede_code:
                continue
            try:
                date_obj = datetime.strptime(row.get('Fecha', '').strip(), '%d/%m/%Y')
                start_with_time = date_obj.replace(hour=9, minute=0, second=0)
                c1_events[sede_code].append({
                    'start': start_with_time.isoformat(),
                    'equipo': str(row.get('Equipo', '')),
                    'entrenador': str(row.get('Entrenador', '')),
                })
            except ValueError:
                continue
    
    for sede in c1_events:
        c1_events[sede].sort(key=lambda x: x['start'])
    
    total = sum(len(v) for v in c1_events.values())
    print(f"  >> Fallback: {total} eventos encontrados.")
    return c1_events


def main():
    # Primary source: JSON with LIM, CUE, MED
    if os.path.exists(JSON_SOURCE):
        c1_events = load_from_primary_json(JSON_SOURCE)
    else:
        c1_events = {code: [] for code in set(SEDE_MAP.values())}
        print(f"Advertencia: No se encontro la fuente primaria ({JSON_SOURCE})")
    
    # Complement/fill from CSV (for GYE, UIO1, UIO2, MEX and any missing sedes)
    if os.path.exists(CSV_FALLBACK):
        csv_events = load_from_fallback_csv(CSV_FALLBACK)
        # Merge: for sedes that are empty in primary, use CSV data
        for sede, events in csv_events.items():
            if events and not c1_events.get(sede):
                c1_events[sede] = events
                print(f"  >> Sede {sede} completada desde CSV ({len(events)} eventos)")
    elif not any(c1_events.values()):
        print("ERROR: No se encontro ninguna fuente de datos.")
        return
    
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(c1_events, f, indent=4, ensure_ascii=False)
    
    print(f"\nOK Generado: '{JSON_OUTPUT}'")
    print("   Eventos por sede:")
    for sede, events in sorted(c1_events.items()):
        if events:
            # Find next upcoming event
            now_str = datetime.now().isoformat()[:10]
            upcoming = [e for e in events if e['start'][:10] >= now_str]
            proximo = upcoming[0]['start'][:10] if upcoming else 'ninguno proximo'
            print(f"   - {sede}: {len(events)} eventos | Proximo: {proximo}")


if __name__ == "__main__":
    main()

