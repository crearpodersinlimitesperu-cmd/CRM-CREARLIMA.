import pandas as pd
import os
import unicodedata

def normalize(string):
    if pd.isna(string): return ""
    s = str(string).strip().upper()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return ' '.join(s.split())

# Rutas de Archivos
folder = os.path.dirname(os.path.abspath(__file__))
f_equipos = r"C:\Users\josem\Downloads\reporte_equipos.xlsx"
f_asignacion = r"C:\Users\josem\Downloads\Asignacion_C1.xlsx"
f_participantes = r"C:\Users\josem\Downloads\Hojas de Cálculo\participantes_2026-04-20.csv"
f_mineria = os.path.join(folder, "Mineria_DNIs.xlsx")

print("Iniciando Cruce de Datos para Contactos Google...")

try:
    # 1. Cargar Reporte de Equipos (Base de Email y Equipo 27)
    df_eq = pd.read_excel(f_equipos)
    df_27 = df_eq[df_eq['NombreEquipo'] == 'EQUIPO 27'].copy()
    print(f"Total en Equipo 27: {len(df_27)}")

    # 2. Cargar Asignación C1 (Para el nombre de la Coordinadora)
    try:
        df_asig = pd.read_excel(f_asignacion)
        # Buscar columna de ID flexiblemente
        c_id_asig = next((c for c in df_asig.columns if 'ID' in str(c).upper() or 'IDENTI' in str(c).upper()), None)
        if c_id_asig:
            # Forzamos a string y limpiamos para el mapeo
            df_asig[c_id_asig] = df_asig[c_id_asig].astype(str).str.split('.').str[0].str.strip()
            asig_map = df_asig.set_index(c_id_asig)['Usuario Registro'].to_dict()
        else:
            asig_map = {}
    except Exception as e:
        print(f"Aviso: No se pudo cargar asignacion ({e})")
        asig_map = {}

    # 3. Cargar Minería RENIEC (Nombres Oficiales)
    if os.path.exists(f_mineria):
        df_min = pd.read_excel(f_mineria)
        df_min = df_min[df_min['Estatus'].str.contains('VERIFICADO', na=False)]
        # Forzar DNI a string para el cruce
        df_min['DNI'] = df_min['DNI'].astype(str).str.split('.').str[0].str.strip()
        min_map = df_min.set_index('DNI').to_dict('index')
    else:
        min_map = {}

    # 4. Cargar Participantes CSV (Para "Nombre que prefieren" / Apodo)
    try:
        df_p = pd.read_csv(f_participantes, encoding='latin-1', on_bad_lines='skip')
        c_id_p = next((c for c in df_p.columns if 'ID' in str(c).upper() or 'IDENTI' in str(c).upper()), None)
        if c_id_p:
            df_p[c_id_p] = df_p[c_id_p].astype(str).str.split('.').str[0].str.strip()
            p_map = df_p.set_index(c_id_p)['Nombre'].to_dict() 
        else:
            p_map = {}
    except:
        p_map = {}

    # Mapeo de Coordinadoras (IDs técnicos a Nombres Reales)
    coord_map = {
        "jmarin": "Joyce Marin",
        "zurteaga": "Zuley Urteaga",
        "dmoscoso": "Diana Moscoso",
        "lvalencia": "L. Valencia"
    }

    # --- PROCESAMIENTO ---
    final_data = []
    # Usar nombre real de la columna de equipos
    c_id_eq = next((c for c in df_eq.columns if 'ID' in str(c).upper() or 'IDENTI' in str(c).upper()), 'Identificacin')
    
    for _, row in df_27.iterrows():
        dni = str(row[c_id_eq]).split('.')[0].strip()
        
        # Teléfono con Código de País (+51)
        raw_phone = str(row.get('TelefonoMovil', '')).split('.')[0].strip()
        if raw_phone and not raw_phone.startswith('+'):
            phone = f"+51{raw_phone}"
        else:
            phone = raw_phone
            
        email = str(row.get('Correo', '')).strip()
        
        # Nombre Oficial (RENIEC)
        m_data = min_map.get(dni)
        if m_data:
            nombre_reniec = f"{m_data['RENIEC_Nombres']} {m_data['RENIEC_Paterno']} {m_data['RENIEC_Materno']}".title()
        else:
            nombre_reniec = f"{row['NombreCompleto']} {row['ApellidoCompleto']}".title()
            
        # Apodo (Original Form)
        apodo = p_map.get(dni, "")
        
        # Construir Nombre para Google
        display_name = nombre_reniec
        if apodo and normalize(apodo) != normalize(nombre_reniec.split()[0]):
            display_name = f"{nombre_reniec} ({apodo.title()})"
            
        # Notas
        coord_id = asig_map.get(dni, "Sin asignar")
        coordinadora = coord_map.get(coord_id, coord_id) # Usar nombre real si existe
        
        imo = str(row.get('NombreIMO', '—')).title()
        eq_imo = str(row.get('EquipoIMO', '—'))
        
        notes = f"IMO: {imo} | Coord: {coordinadora} | Equipo C1: 27 | Eq. IMO: {eq_imo}"
        
        final_data.append({
            "Name": display_name,
            "Given Name": nombre_reniec.split()[0] if ' ' in nombre_reniec else nombre_reniec,
            "Family Name": " ".join(nombre_reniec.split()[1:]) if ' ' in nombre_reniec else "",
            "Mobile Phone": phone,       # GANADOR: Google lo reconoció correctamente
            "E-mail Address": email,     # GANADOR: Google lo reconoció correctamente
            "Notes": notes
        })

    # Guardar CSV Final
    df_final = pd.DataFrame(final_data)
    # Guardar en sistema de control Y en Descargas directamente
    out_path = os.path.join(folder, "Google_Contacts_EQUIPO27.csv")
    downloads_root = r"C:\Users\josem\Downloads\Google_Contacts_EQUIPO27.csv"
    
    # Usar utf-8 estándar sin BOM para evitar confusiones al parser de Google
    df_final.to_csv(out_path, index=False, encoding='utf-8')
    df_final.to_csv(downloads_root, index=False, encoding='utf-8')
    
    print(f"Archivo generado con exito en: {downloads_root}")
    print(f"Total contactos listos para subir: {len(df_final)}")

except Exception as e:
    print(f"Error fatal en la generacion: {e}")
