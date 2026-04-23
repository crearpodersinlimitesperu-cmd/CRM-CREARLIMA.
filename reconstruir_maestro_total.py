import pandas as pd
import os
import unicodedata
import datetime
import json
import re
from difflib import SequenceMatcher

def normalize_text(text):
    if not text or pd.isna(text) or text == '—': return ""
    s = str(text).strip().upper()
    s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', s).strip()

def to_proper_case(text):
    if not text or pd.isna(text) or text == '—': return "—"
    return str(text).strip().title()

def get_name_tokens(full_name_norm):
    if not full_name_norm: return set()
    return set(full_name_norm.split())

def balance_name_fields(nom, ape):
    nom = str(nom).strip() if not pd.isna(nom) else ""
    ape = str(ape).strip() if not pd.isna(ape) else ""
    if (not ape or ape == '—') and nom:
        parts = nom.split()
        if len(parts) >= 4: return " ".join(parts[:-2]), " ".join(parts[-2:])
        elif len(parts) == 3: return parts[0], " ".join(parts[1:])
        elif len(parts) == 2: return parts[0], parts[1]
    return nom, ape

def clean_phone(val):
    if not val or pd.isna(val) or val == '—': return ""
    s = str(val).strip().replace(".0", "").replace(" ", "").replace("-", "")
    if s.startswith("51") and len(s) > 9: s = s[2:]
    return s

def clean_id_robust(val):
    """Acepta DNI (8 dígitos), Carnet de Extranjería (CE + alfanum) y otros documentos válidos."""
    if not val or pd.isna(val) or val == '—': return ""
    s = str(val).strip().upper()
    try:
        if 'E+' in s: s = "{:.0f}".format(float(s))
    except: pass
    s = s.split('.')[0].strip()
    # DNI peruano: 8 dígitos
    if re.fullmatch(r'\d{8}', s): return s
    # Carnet de Extranjería: CE + alfanumérico o solo alfanumérico 9-15 chars
    clean = re.sub(r'[^A-Z0-9]', '', s)
    if len(clean) >= 7:
        return clean  # válido como CE o pasaporte
    return ""

# GLOBAL STATE
universe_dni = {}
universe_name_tokens = {} 
universe_phone = {}
manual_decisions = {}
conflicts = []

DECISION_FILE = r"C:\Users\josem\Downloads\CONTROL_SISTEMA_CREARLIMA\decisiones_fusion.json"

def load_manual_decisions():
    global manual_decisions
    if os.path.exists(DECISION_FILE):
        try:
            with open(DECISION_FILE, 'r', encoding='utf-8') as f:
                manual_decisions = json.load(f)
        except: pass

def are_tokens_similar(t1, t2, threshold=0.85):
    if t1 == t2: return True
    return SequenceMatcher(None, t1, t2).ratio() >= threshold

def get_fuzzy_intersection(set1, set2):
    count = 0
    used_t2 = set()
    for t1 in set1:
        for t2 in set2:
            if t2 not in used_t2 and are_tokens_similar(t1, t2):
                count += 1
                used_t2.add(t2)
                break
    return count

def add_to_universe(dni, data, is_official_grad=False):
    global universe_dni, universe_name_tokens, universe_phone, manual_decisions, conflicts
    
    nom_raw, ape_raw = balance_name_fields(data.get('Nombres'), data.get('Apellidos'))
    dni = clean_id_robust(dni or data.get('DNI'))
    phone = clean_phone(data.get('Teléfono'))
    full_name_norm = normalize_text(f"{nom_raw} {ape_raw}")
    tokens = get_name_tokens(full_name_norm)
    
    key = None
    temp_id = f"T_{full_name_norm[:30]}"
    if temp_id in manual_decisions: key = manual_decisions[temp_id]
    if not key and dni and len(dni) >= 7: key = dni
    if not key and tokens:
        for ex_key, ex_tokens in universe_name_tokens.items():
            if not ex_tokens: continue
            
            # Cálculo de Coincidencia Difusa
            common_count = get_fuzzy_intersection(tokens, ex_tokens)
            target_data = universe_dni.get(ex_key, {})
            is_ex_grad = 'GRADUADO' in str(target_data.get('Estatus MJ',''))
            
            # Lógica de Fusión Inteligente
            if tokens.issubset(ex_tokens) or ex_tokens.issubset(tokens):
                # Si una es subconjunto, y comparten al menos 2 tokens significativos (difusos)
                if common_count >= 2: key = ex_key; break
            elif common_count >= 3:
                # Si no son subconjuntos puros pero comparten 3+ tokens difusos
                key = ex_key; break
            elif is_ex_grad and common_count >= 2:
                # Si el destino es Graduado, bajamos la guardia a 2 tokens difusos
                key = ex_key; break

    if not key and phone and len(phone) >= 9:
        if phone in universe_phone:
            ex_key = universe_phone[phone]
            if len(tokens.intersection(universe_name_tokens.get(ex_key, set()))) >= 1: key = ex_key

    if key and key in universe_dni:
        target = universe_dni[key]
        if is_official_grad: target['Estatus MJ'] = 'GRADUADO ★'
        
        # Merge Trayectoria
        t_new = data.get('Trayectoria', '')
        if t_new and t_new != '—':
            ot = str(target.get('Trayectoria', '')).replace('—', '')
            if t_new not in ot: target['Trayectoria'] = f"{ot}, {t_new}".strip(", ") if ot else t_new

        # Estandarizacion
        if len(full_name_norm) > len(normalize_text(f"{target.get('Nombres')} {target.get('Apellidos')}")):
            target['Nombres'] = to_proper_case(nom_raw); target['Apellidos'] = to_proper_case(ape_raw)
        
        for k, v in data.items():
            if k not in ['Nombres', 'Apellidos', 'Trayectoria'] and v and v != '—' and (target.get(k) in ['', '—', None]):
                target[k] = v
    else:
        new_key = key if key else (dni if (dni and len(dni) >= 7) else temp_id)
        data['Nombres'] = to_proper_case(nom_raw); data['Apellidos'] = to_proper_case(ape_raw)
        universe_dni[new_key] = data
        universe_name_tokens[new_key] = tokens
        if phone: universe_phone[phone] = new_key

def apply_logical_coherence():
    """
    ALGORITMO DE CASCADA DE COHERENCIA 🔱
    Propaga los estatus de nivel superior a los inferiores.
    Graduado -> MJ -> C2 -> C1
    """
    print("--- APLICANDO CASCADA DE COHERENCIA LOGICA ---")
    for key, data in universe_dni.items():
        is_grad = 'GRADUADO' in str(data.get('Estatus MJ', '')).upper()
        
        # 1. Si es Graduado, asegurar C1, C2 y MJ
        if is_grad:
            data['Estatus MJ'] = 'GRADUADO ★'
            if data.get('Estatus C2') in ['—', 'Pendiente', 'NO', '']: data['Estatus C2'] = '✓ Sentado'
            if data.get('Estatus C1') in ['—', 'Pendiente', 'NO', '']: data['Estatus C1'] = '✓ Sentado'
            if data.get('Participación') != 'GRADUADO': data['Participación'] = 'GRADUADO'
        
        # 2. Si tiene C2, asegurar C1
        c2_status = str(data.get('Estatus C2', '')).upper()
        if 'SENTADO' in c2_status or 'SI' == c2_status:
            if data.get('Estatus C1') in ['—', 'Pendiente', 'NO', '']: data['Estatus C1'] = '✓ Sentado'

def process_unification():
    print("--- MOTOR MAESTRO DE COHERENCIA UNIVERSAL ---")
    load_manual_decisions()
    
    file_master = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"
    file_grads_318 = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\GRADUADOS LIMA.xlsx"
    file_purgado = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\participantes_2026-04-19.csv"

    # 1. Carga Master
    if os.path.exists(file_master):
        df_b = pd.read_excel(file_master, dtype=str).fillna("—")
        for _, row in df_b.iterrows():
            d = row.to_dict(); d['Estatus MJ'] = 'Pendiente'; d['Trayectoria'] = '—'
            add_to_universe(row.get('DNI'), d)

    # 2. Carga Campania
    if os.path.exists(file_purgado):
        try:
            df_p = pd.read_csv(file_purgado, on_bad_lines='skip', sep=None, engine='python', encoding='utf-8').fillna("—")
            for _, row in df_p.iterrows():
                dni = clean_id_robust(row.get('IDENTIFICACION') or row.get('DNI'))
                d = {'Nombres': row.get('NOMBRE',''), 'Apellidos': row.get('APELLIDO',''), 'DNI': dni, 'Participación': 'ACTIVO'}
                add_to_universe(dni, d)
        except: pass

    # 3. Aplicar 318 Graduados (Prioridad)
    try:
        df_g = pd.read_excel(file_grads_318, sheet_name='GRADUADOS ', dtype=str).fillna("—")
        rm = {'M': 'Manager', 'C': 'Capitán', 'Q': 'Quantum Team', 'A': 'Aliado'}
        for _, row in df_g.iterrows():
            nr = str(row['CREAR CUANTICO']).strip()
            if len(nr) < 5: continue
            tray = []
            for col in [c for c in df_g.columns if c.startswith('E')]:
                if str(row[col]).upper().strip() in rm: tray.append(f"{rm[str(row[col]).upper().strip()]} ({col})")
            d = {'Nombres': nr, 'Apellidos': '—', 'Trayectoria': ", ".join(tray) if tray else '—', 'Estatus MJ': 'GRADUADO ★'}
            add_to_universe("", d, is_official_grad=True)
    except: pass

    # 6.5 CARGAR MEMORIA INFINITA (MINERÍA)
    mineria_path = "Mineria_DNIs.xlsx"
    memoria_minada = {}
    if os.path.exists(mineria_path):
        try:
            df_min = pd.read_excel(mineria_path, dtype=str)
            for _, r in df_min.iterrows():
                if r.get('Estatus') in ['VERIFICADO', 'VERIFICADO_TABLA']:
                    memoria_minada[r['DNI']] = f"{r.get('RENIEC_Nombres','')} {r.get('RENIEC_Paterno','')} {r.get('RENIEC_Materno','')}".strip()
            print(f"--- MEMORIA INFINITA CARGADA: {len(memoria_minada)} identidades blindadas ---")
        except: pass

    # 7. MEGAFUSIÓN DE DATOS (PRIORIDAD ARCHIVOS NUEVOS)
    print("--- INICIANDO MEGAFUSIÓN DE ABRIL (PRIORIDAD ALTA) ---")
    mega_files = [
        r'C:\Users\josem\Downloads\participantes_2026-04-22.csv',
        r'C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\ASISTENCIA ENTRENAMIENTOS\ASISTENCIA CAPÍTULO UNO LIMA.xlsx',
        r'C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\ASISTENCIA ENTRENAMIENTOS\CAPITULO UNO E19 LIMA.xlsx',
        r'C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\CREAR LIMA\ASISTENCIA ENTRENAMIENTOS\ASISTENCIA CAPITULO DOS LIMA.xlsx'
    ]
    
    for f in mega_files:
        if not os.path.exists(f): continue
        print(f"Procesando Fuente Maestra: {os.path.basename(f)}")
        
        try:
            if f.endswith('.csv'):
                df_mega = pd.read_csv(f, dtype=str)
                sheets = [df_mega]
            else:
                xl = pd.ExcelFile(f)
                sheets = [xl.parse(sn, dtype=str) for sn in xl.sheet_names]
            
            for df_s in sheets:
                # Normalizar columnas para mapeo flexible
                df_s.columns = [str(c).strip().upper() for c in df_s.columns]
                
                for _, row in df_s.iterrows():
                    # Buscar DNI (Prioridad 1)
                    dni = ""
                    for c in ['DNI', 'IDENTIFICACIÓN', 'CEDULA', 'NRO DOC', 'DOCUMENTO']:
                        if c in df_s.columns: 
                            dni = str(row.get(c, '')).strip().split('.')[0]
                            if len(dni) > 5: break
                    
                    if not dni: continue
                    
                    # Extraer Datos
                    nombres = str(row.get('NOMBRES', '') or row.get('NOMBRE', '')).strip().title()
                    apellidos = str(row.get('APELLIDOS', '') or row.get('APELLIDO', '')).strip().title()
                    email = str(row.get('EMAIL', '') or row.get('CORREO', '')).strip().lower()
                    tel = re.sub(r'\D', '', str(row.get('TELEFONO', '') or row.get('CELULAR', '')))
                    
                    # Sobrescritura (Mandan sobre los anteriores)
                    if dni not in universe_dni:
                        universe_dni[dni] = {
                            "DNI": dni, "Nombres": nombres, "Apellidos": apellidos, 
                            "Email": email, "Telefono": tel, "Origen/Equipo": os.path.basename(f)
                        }
                    else:
                        # Actualizar campos solo si vienen con info
                        if nombres: universe_dni[dni]["Nombres"] = nombres
                        if apellidos: universe_dni[dni]["Apellidos"] = apellidos
                        if email: universe_dni[dni]["Email"] = email
                        if tel: universe_dni[dni]["Telefono"] = tel
                        universe_dni[dni]["Origen/Equipo"] = f"{universe_dni[dni].get('Origen/Equipo','')}, {os.path.basename(f)}".strip(", ")

                    # Lógica de Estatus por Archivo
                    fname = os.path.basename(f).upper()
                    if 'DOS LIMA' in fname:
                        universe_dni[dni]["Estatus C2"] = "Sentado / SI"
                        universe_dni[dni]["Estatus C1"] = "GRADUADO ★"
                    elif 'UNO LIMA' in fname or 'E19' in fname:
                        universe_dni[dni]["Estatus C1"] = "Sentado / SI"

        except Exception as e:
            print(f"Error procesando {f}: {e}")

    # 8. SELLO DE ORO (BLINDAJE DE GRADUADOS)
    print("--- APLICANDO SELLO DE ORO (BLINDAJE DE GRADUADOS) ---")
    blindados_path = "Graduados_Blindados.xlsx"
    dni_blindados = set()
    if os.path.exists(blindados_path):
        try:
            df_b = pd.read_excel(blindados_path, dtype=str)
            dni_blindados = set(df_b['DNI'].unique())
            print(f"   - {len(dni_blindados)} graduados blindados cargados.")
        except: pass

    # Aplicar Blindaje y Recolectar Nuevos
    nuevos_blindados = []
    for dni, data in universe_dni.items():
        # Si ya estaba blindado, forzar estatus
        if dni in dni_blindados:
            data["Estatus C1"] = "GRADUADO ★"
            data["Estatus C2"] = "Sentado / SI"
            
        # Si es nuevo graduado en esta corrida, añadir a la lista de blindaje
        if 'GRADUADO' in str(data.get('Estatus C1', '')).upper() or '★' in str(data.get('Estatus C1', '')):
            nuevos_blindados.append({"DNI": dni, "Participante": f"{data['Nombres']} {data['Apellidos']}"})

    # Guardar Libro de Oro Actualizado
    if nuevos_blindados:
        df_new_b = pd.DataFrame(nuevos_blindados).drop_duplicates(subset=['DNI'])
        df_new_b.to_excel(blindados_path, index=False)
        print(f"   - Libro de Oro actualizado: {len(df_new_b)} graduados inmortales.")

    # 9. APLICAR CASCADA DE COHERENCIA FINAL
    apply_logical_coherence()

    # Guardar Resultados
    cols = ['Nombres', 'Apellidos', 'DNI', 'Teléfono', 'Email', 'IMO Enrolador', 'Coordinador', 'Origen/Equipo', 'Participación', 'Estatus C1', 'Estatus C2', 'Estatus MJ', 'Trayectoria', 'Verificado_RENIEC']
    final_list = [{c: d.get(c, '—') for c in cols} for d in universe_dni.values()]
    pd.DataFrame(final_list).to_excel(file_master, index=False)
    
    g_count = len([x for x in final_list if 'GRADUADO' in str(x['Estatus MJ'])])
    print(f"--- UNIFICACION COHERENTE COMPLETADA ---")
    print(f"Total: {len(final_list)} | Graduados: {g_count} / 318")

if __name__ == "__main__":
    process_unification()
