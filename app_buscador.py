import streamlit as st
import pandas as pd
import io
import re
import unicodedata
import os
import time
import sys
import requests
import datetime

st.set_page_config(
    page_title="CREAR LIMA – CRM Maestro",
    layout="wide",
    page_icon="🔱",
    initial_sidebar_state="expanded"
)

FILE_PATH = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Master_Database.xlsx"

# ── ESTILOS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
/* Global Light Theme */
.stApp { background: #f8fafc; min-height: 100vh; }
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] * { color: #334155 !important; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #4f46e5 !important; font-size:0.75rem !important;
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 4px !important;
}
/* Métricas */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 1rem 1.2rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}
[data-testid="metric-container"] label { color: #64748b !important; font-size:0.72rem !important; letter-spacing:0.05em; font-weight:600;}
[data-testid="metric-container"] [data-testid="stMetricValue"] { color:#0f172a !important; font-size:1.9rem !important; font-weight:800 !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size:0.75rem !important; }
/* Inputs */
.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important; color: #0f172a !important;
    font-size: 1rem !important; padding: 0.65rem 1rem !important;
    box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05) !important;
}
.stTextInput > div > div > input:focus { border-color: #4f46e5 !important; box-shadow: 0 0 0 3px rgba(79,70,229,0.2) !important; }
.stTextInput > div > div > input::placeholder { color: #94a3b8 !important; }
/* Toggle */
.stToggle label { color: #334155 !important; font-weight: 500; }
/* Tabla */
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.dataframe tbody tr { background: #ffffff !important; }
.dataframe tbody tr:nth-child(even) { background: #f8fafc !important; }
.dataframe tbody tr:hover { background: #f1f5f9 !important; }
/* Download */
.stDownloadButton button {
    background: linear-gradient(135deg, #4f46e5, #4338ca) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    padding: 0.6rem 2rem !important; font-size: 0.95rem !important;
    box-shadow: 0 4px 10px rgba(79,70,229,0.2) !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(79,70,229,0.3) !important; }
/* Multiselect */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: #eef2ff !important;
    border: 1px solid #a5b4fc !important; color:#4338ca !important;
}
/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f8fafc; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── CARGA ────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_excel(FILE_PATH, dtype=str).fillna("")
        
        # --- CARGA DINÁMICA DE COORDINADORES ---
        asig_path = r"C:\Users\josem\Downloads\Asignacion_C1.xlsx"
        coord_map = {
            "jmarin": "Joyce Marin",
            "zurteaga": "Zuley Urteaga",
            "dmoscoso": "Diana Moscoso",
            "lvalencia": "L. Valencia"
        }
        
        if os.path.exists(asig_path):
            try:
                df_asig = pd.read_excel(asig_path, dtype=str)
                # Normalizar columnas para el merge por DNI
                dni_col = next((c for c in df_asig.columns if 'IDENTI' in str(c).upper()), None)
                if dni_col and 'DNI' in df.columns:
                    # Crear diccionario DNI -> ID Coordinador
                    d_map = dict(zip(df_asig[dni_col].str.strip(), df_asig['Usuario Registro'].str.strip()))
                    # Inyectar si la columna Coordinador está vacía o no existe
                    if 'Coordinador' not in df.columns:
                        df['Coordinador'] = ""
                    
                    def get_coord(row):
                        current = str(row.get('Coordinador', '')).strip()
                        if current and current != "—": return current
                        dni = str(row.get('DNI', '')).strip()
                        c_id = d_map.get(dni)
                        return coord_map.get(c_id, c_id) if c_id else current
                        
                    df['Coordinador'] = df.apply(get_coord, axis=1)
            except Exception as e:
                st.sidebar.warning(f"Error cargando asignaciones: {e}")

        # --- MAPEO DE CONTACTOS PARA GESTIÓN ---
        # Creamos un índice NombreCompleto -> Teléfono para buscar a los IMOs
        df['NombreCompletoNorm'] = (df['Nombres'].str.strip() + " " + df['Apellidos'].str.strip()).str.title().str.strip()
        imo_map = {}
        for _, row in df.iterrows():
            name = str(row['NombreCompletoNorm'])
            phone = str(row['Teléfono']).strip()
            if name and phone and phone != "—" and len(phone) >= 9:
                imo_map[name] = phone
        st.session_state['imo_phones'] = imo_map

        return df
    except Exception as e:
        st.error(f"Error general de carga: {e}")
        return pd.DataFrame()

def norm(text):
    if not text or pd.isna(text): return ""
    s = str(text).split('.')[0].upper().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

# ── MOTOR DE CONSOLIDACIÓN DE REPORTES ────────────────────────
def parse_whatsapp_report(text):
    """Extrae KPIs de reportes tipo Zuley"""
    sections = {}
    current_section = "General"
    
    # Limpiar asteriscos y normalizar
    lines = [line.replace('*', '').strip() for line in text.split('\n') if line.strip()]
    
    for line in lines:
        # Detectar Secciones (ej: ✅ Nuevos Cap 1:)
        if '✅' in line or ':' in line and '=' not in line:
            current_section = line.replace('✅', '').split(':')[0].strip()
            sections[current_section] = {}
            continue
            
        # Detectar Valores (ej: OK = 2 o CONFIRMADOS = 5)
        if '=' in line:
            parts = line.split('=')
            if len(parts) == 2:
                key = parts[0].strip().upper()
                # Unificación de Patrones: CONFIRMADO / CONFIRMADOS / CONF -> OK
                if key.startswith('CONF') or key == 'CONFIRMADOS':
                    key = 'OK'
                
                try:
                    val = int(re.sub(r'\D', '', parts[1]))
                    if current_section not in sections: sections[current_section] = {}
                    sections[current_section][key] = val
                except: pass
    return sections

def save_report_history(coordinator, data, raw_text, overwrite_ts=None, target_date=None, notes=""):
    hist_path = "Historial_Reportes.csv"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    today = time.strftime("%Y-%m-%d")
    final_date = target_date if target_date else today
    
    # Preparar nuevas filas (usamos un ID único por reporte: el timestamp de creación)
    report_id = overwrite_ts if overwrite_ts else timestamp
    rows = []
    for section, kpis in data.items():
        for k, v in kpis.items():
            # Lógica Incremental: Calcular Delta (Avance)
            delta = v
            if os.path.exists(hist_path):
                try:
                    df_check = pd.read_csv(hist_path)
                    prev = df_check[(df_check['Fecha'] == final_date) & 
                                    (df_check['Coordinadora'] == coordinator) & 
                                    (df_check['Seccion'] == section) & 
                                    (df_check['Estado'] == k)]
                    if not prev.empty:
                        delta = max(0, v - prev['Cantidad'].max())
                except: pass
                
            rows.append({
                "ID_Reporte": report_id,
                "Fecha": final_date,
                "Hora": timestamp.split()[1] if ' ' in timestamp else timestamp,
                "Coordinadora": coordinator,
                "Seccion": section,
                "Estado": k,
                "Cantidad": v,
                "Avance": delta,
                "RawText": raw_text,
                "Observaciones": notes
            })
    df_new = pd.DataFrame(rows)
    
    if os.path.exists(hist_path):
        df_old = pd.read_csv(hist_path)
        # Si es edición, eliminamos el anterior con ese ID
        if overwrite_ts:
            df_old = df_old[df_old['ID_Reporte'] != overwrite_ts]
        
        # Verificar límite de 2 (solo si es nuevo para ese día)
        if not overwrite_ts:
            if 'ID_Reporte' in df_old.columns:
                coord_reports = df_old[(df_old['Fecha'] == final_date) & (df_old['Coordinadora'] == coordinator)]['ID_Reporte'].unique()
                if len(coord_reports) >= 2:
                    return False, f"Límite de 2 reportes para el {final_date} alcanzado."
            else:
                # Si el archivo es viejo y no tiene ID, dejamos pasar este primer guardado
                pass
        
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
        df_combined.to_csv(hist_path, index=False)
    else:
        df_new.to_csv(hist_path, index=False)
        
    return True, report_id
def color_cell(val):
    v = str(val).upper()
    # INACTIVO / CUPO CEDIDO → gris suave  
    if 'CUPO CEDIDO' in v or 'REPOSA' in v:
        return 'background:#f1f5f9;color:#64748b;font-style:italic'
    # GRADUADO / ESTRELLA → DORADO vibrante pero legible
    if 'GRADUADO' in v or '★' in v:
        return 'background:#fefce8;color:#a16207;font-weight:800;letter-spacing:0.03em'
    # SENTADO → VERDE claro
    if 'SENTADO' in v:
        return 'background:#f0fdf4;color:#15803d;font-weight:700'
    # ENROLADO TOTAL MJ → verde esmeralda claro
    if 'ENROLADO TOTAL' in v:
        return 'background:#ecfdf5;color:#047857;font-weight:700'
    # ABONO C2 (permitido) → azul cian claro
    if 'ABONO' in v and '—' not in v:
        return 'background:#ecfeff;color:#0369a1;font-weight:600'
    # APTO PARA MJ → celeste suave
    if 'APTO PARA MJ' in v:
        return 'background:#eff6ff;color:#1d4ed8;font-weight:600'
    # SIG → índigo claro
    if 'SIG' in v or 'PROXIMA' in v:
        return 'background:#eef2ff;color:#4338ca;font-weight:600'
    # XC PENDIENTE → NARANJA ambar claro
    if 'XC' in v or 'PENDIENTE' in v:
        return 'background:#fffbeb;color:#b45309;font-weight:700'
    # NI → ROJO claro
    if 'NI -' in v or 'NO CONT' in v:
        return 'background:#fef2f2;color:#b91c1c;font-weight:700'
    # PRE-C1 REZAGADO → violeta suave
    if 'REZAGADO' in v or 'PRE-C1' in v:
        return 'background:#faf5ff;color:#7e22ce;font-weight:600'
    # CUPO DEVUELTO → naranja claro
    if 'DEVUELTO' in v:
        return 'background:#fff7ed;color:#c2410c;font-weight:600'
    # PARTICIPACION INACTIVO
    if 'INACTIVO' in v:
        return 'background:#f1f5f9;color:#64748b;font-style:italic'
    # PARTICIPACION REZAGADO
    if 'REZAGADO' in v and 'PRE-C1' in v:
        return 'background:#faf5ff;color:#7e22ce;font-weight:600'
    # Colores para Liderazgo en Trayectoria
    if any(x in v for x in ['MANAGER', '👑']): return 'background-color: #fef3c7; color: #92400e; font-weight: bold; border-left: 5px solid #d97706;' # Gold
    if any(x in v for x in ['QUANTUM', '🌀']): return 'background-color: #f3e8ff; color: #6b21a8; font-weight: bold; border-left: 5px solid #9333ea;' # Purple
    if any(x in v for x in ['CAPITÁN', '🛡️']): return 'background-color: #e0f2fe; color: #075985; font-weight: bold; border-left: 5px solid #0284c7;' # Blue
    if any(x in v for x in ['ALIADO', '🤝']): return 'background-color: #dcfce7; color: #166534; font-weight: bold; border-left: 5px solid #16a34a;' # Green
    
    # PARTICIPACION
    if 'DESERTOR' in v:
        return 'background-color: #fecaca; color: #b91c1c; font-weight: bold'
    # GRADUADOS
    if '★' in v or 'Graduado' in v:
        return 'background-color: #fef3c7; color: #b45309; font-weight: bold'
    # ACTIVO / SENTADO
    if 'Sentado' in v:
        return 'background-color: #dcfce7; color: #15803d; font-weight: bold'
    # PARTICIPACION ACTIVO
    if 'ACTIVO' in v and 'PROCESO' in v:
        return 'background:#f0fdfa;color:#0f766e;font-weight:700'
    if 'ACTIVO' in v and 'CANDIDATO' in v:
        return 'background:#eff6ff;color:#1d4ed8'
    # NO APLICA
    if '—' in v and len(v) < 3:
        return 'color:#94a3b8'
    return ''

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    logo_path = r"C:\Users\josem\Downloads\logo_crear.png"
    if os.path.exists(logo_path):
        st.markdown("<br>", unsafe_allow_html=True)
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("## 🔱 CREAR LIMA")
        
    st.divider()
    st.markdown("### 🧭 Navegación")
    app_mode = st.radio("Sección", ["🔍 Buscador", "📊 Sala de Guerra", "📊 Reporte de Desempeño 🔱", "🔱 Centro de Integridad"], label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        st.error("No se pudo cargar el master. Ejecuta construir_super_master.py")
        st.stop()

    st.markdown("### 🤖 Administración Autónoma")
    
    # MÉTRICAS DE MINADO (Dinámicas e Híbridas)
    if not df.empty:
        total_rec = len(df)
        
        # 1. Contar desde el Master
        minados_master = set(df[df['Verificado_RENIEC'] == 'SI']['DNI'].astype(str).unique())
        
        # 2. Contar desde el Cache (en vivo)
        minados_cache = set()
        ultimo_m = "—"
        try:
            cache_path = os.path.join(os.path.dirname(__file__), "Mineria_DNIs.xlsx")
            if os.path.exists(cache_path):
                df_c = pd.read_excel(cache_path, dtype=str)
                df_v = df_c[df_c['Estatus'].str.contains('VERIFICADO', na=False)]
                minados_cache = set(df_v['DNI'].unique())
                if not df_v.empty:
                    last_row = df_v.iloc[-1]
                    ultimo_m = f"{last_row.get('RENIEC_Nombres','')} {last_row.get('RENIEC_Paterno','')}".title()
        except: pass
        
        total_minados_unicos = len(minados_master | minados_cache)
        pendientes = total_rec - total_minados_unicos
        progreso = total_minados_unicos / total_rec if total_rec > 0 else 0
        
        st.markdown(f"""
        <div style='background:#f8fafc;padding:1rem;border-radius:12px;border:1px solid #e2e8f0;margin-bottom:1.2rem;box-shadow: 0 1px 3px rgba(0,0,0,0.1)'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem'>
                <div style='font-size:0.75rem;color:#64748b;font-weight:700;letter-spacing:0.05em'>SEGUIMIENTO EN VIVO</div>
                <div style='width:10px;height:10px;background:#22c55e;border-radius:50%;box-shadow:0 0 8px #22c55e' title='Robot Activo'></div>
            </div>
            <div style='display:flex;justify-content:space-between;margin-bottom:0.4rem'>
                <span style='font-size:0.9rem;color:#1e293b'>✅ Minados</span>
                <span style='font-size:0.9rem;font-weight:800;color:#16a34a'>{total_minados_unicos:,}</span>
            </div>
            <div style='display:flex;justify-content:space-between;margin-bottom:1rem'>
                <span style='font-size:0.9rem;color:#64748b'>⏳ Pendientes</span>
                <span style='font-size:0.9rem;font-weight:800;color:#ef4444'>{pendientes:,}</span>
            </div>
            <div style='height:10px;background:#e2e8f0;border-radius:10px;overflow:hidden;margin-bottom:0.5rem'>
                <div style='width:{progreso*100}%;height:100%;background:linear-gradient(90deg,#22c55e,#16a34a);transition: width 1s ease-in-out'></div>
            </div>
            <div style='display:flex;justify-content:space-between;align-items:center'>
                <div style='font-size:0.65rem;color:#94a3b8'>Último: <span style='color:#475569;font-weight:600'>{ultimo_m}</span></div>
                <div style='font-size:0.75rem;color:#16a34a;font-weight:700'>{progreso*100:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-refresco si hay actividad (cada 30s)
        # st.empty() # Placeholder
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = time.time()
        
        # Solo refrescar si el robot inicio hace poco (heuristica simple)
        # O simplemente dejarlo activo
        # st.info("🔄 Autorefresco activo cada 30s")


    if st.button("🚀 1. Minar DNIs Ocultos (Invisible)", use_container_width=True):
        import subprocess
        import sys
        try:
            # Ejecución en segundo plano sin ventana de consola
            subprocess.Popen([sys.executable, "robot_dni.py"], 
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                             cwd=os.path.dirname(os.path.abspath(__file__)))
            st.toast("✅ Robot iniciado en segundo plano. Minando DNIs de forma invisible.")
        except Exception as e:
            st.error(f"Error al iniciar robot: {e}")
    if st.button("💉 2. Sincronizar RENIEC", use_container_width=True):
        import subprocess
        import sys
        try:
            subprocess.Popen([sys.executable, "inyectar_reniec.py"], 
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                             cwd=os.path.dirname(os.path.abspath(__file__)))
            st.cache_data.clear()
            st.toast("✅ Sincronización iniciada en segundo plano. Refresca en unos segundos.")
        except Exception as e:
            st.error(f"Error al iniciar sincronización: {e}")
    st.divider()

    st.markdown("### Filtros de Fase")

    STATUS_COLS = {
        'Estatus C1': '**C1 — Capítulo Uno**',
        'Estatus C2': '**C2 — Capítulo Dos**',
        'Estatus MJ': '**MJ — Maestría del Juego**',
        'Participación': '**Participación**',
    }
    filters = {}
    for col, label in STATUS_COLS.items():
        if col in df.columns:
            opts = sorted([x for x in df[col].unique() if x and x != '—'])
            st.markdown(label)
            filters[col] = st.multiselect("", opts, key=f"f_{col}", label_visibility="collapsed")

    st.divider()
    st.markdown("### Por IMO Enrolador")
    imos = sorted([x for x in df['IMO Enrolador'].unique() if x]) if 'IMO Enrolador' in df.columns else []
    sel_imo = st.multiselect("IMO", imos, key="f_imo", label_visibility="collapsed")

    st.divider()
    st.markdown("### Accesos Rápidos")
    solo_sin_imo  = st.toggle("🔴 Sin IMO asignado",       value=False)
    solo_sin_c1   = st.toggle("⚪ No sentados en C1",       value=False)
    solo_sin_c2   = st.toggle("⚪ No sentados en C2",       value=False)
    solo_inactivo = st.toggle("⛔ Excluir Inactivos (CN)", value=True)

# ── HEADER ────────────────────────────────────────────────────
import os
import base64
folder = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(folder, "logo_crear.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    img_tag = f"<img src='data:image/png;base64,{encoded_string}' style='max-height:65px; margin: 0.5rem 0'>"
else:
    img_tag = "<div style='font-size:2.8rem;font-weight:900;color:#4f46e5;line-height:1;margin: 0.5rem 0'>🔱 CREAR LIMA</div>"

st.markdown(f"""
<div style='padding:1.5rem 0 0.5rem'>
  <div style='font-size:0.75rem;color:#6366f1;letter-spacing:0.15em;text-transform:uppercase;font-weight:600'>Sistema CRM Maestro E2E</div>
  {img_tag}
  <div style='color:#64748b;font-size:0.9rem;margin-top:0.2rem'>Base Unificada · C1 → C2 → Maestría del Juego · Deduplicada al 80%</div>
</div>
""", unsafe_allow_html=True)
st.divider()

# Inicializamos variables para evitar NameError en cualquier modo
df_result = pd.DataFrame()
query = ""

if app_mode == "🔍 Buscador":
    # ── APLICAR FILTROS ──────────────────────────────────────────
    df_view = df.copy()

    for col, vals in filters.items():
        if vals and col in df_view.columns:
            df_view = df_view[df_view[col].isin(vals)]

    if sel_imo and 'IMO Enrolador' in df_view.columns:
        df_view = df_view[df_view['IMO Enrolador'].isin(sel_imo)]
    if solo_sin_imo and 'IMO Enrolador' in df_view.columns:
        df_view = df_view[df_view['IMO Enrolador'] == '']
    if solo_sin_c1 and 'Estatus C1' in df_view.columns:
        df_view = df_view[~df_view['Estatus C1'].str.contains('Sentado', na=False)]
    if solo_sin_c2 and 'Estatus C2' in df_view.columns:
        df_view = df_view[~df_view['Estatus C2'].str.contains('Sentado', na=False)]
    if solo_inactivo and 'Participación' in df_view.columns:
        df_view = df_view[df_view['Participación'] != 'INACTIVO — Cupo Cedido']

    # ── MÉTRICAS COHERENTES ───────────────────────────────────────
    is_grad = df['Estatus MJ'].str.contains('GRADUADO', na=False) if 'Estatus MJ' in df.columns else pd.Series([False]*len(df))
    
    total_activos = (df['Participación'] != 'INACTIVO — Cupo Cedido').sum() if 'Participación' in df.columns else len(df)
    sentados_c1 = (df['Estatus C1'].str.contains('Sentado|SI', case=False, na=False) | is_grad).sum() if 'Estatus C1' in df.columns else 0
    sentados_c2 = (df['Estatus C2'].str.contains('Sentado|SI', case=False, na=False) | is_grad).sum() if 'Estatus C2' in df.columns else 0
    graduados   = df['Estatus MJ'].str.contains('★|Graduado', na=False).sum() if 'Estatus MJ' in df.columns else 0
    desertores  = df['Estatus MJ'].str.contains('DESERTOR', na=False).sum() if 'Estatus MJ' in df.columns else 0
    inactivos   = (df['Participación'] == 'INACTIVO — Cupo Cedido').sum() if 'Participación' in df.columns else 0
    sin_imo     = (df['IMO Enrolador'] == '').sum() if 'IMO Enrolador' in df.columns else 0

    m1,m2,m3,m4,m5,m6 = st.columns(6)
    m1.metric("🌎 Universo Total",    f"{len(df):,}")
    m2.metric("✅ Candidatos Activos", f"{total_activos:,}")
    m3.metric("🔵 Sentados C1",       f"{sentados_c1:,}", f"{sentados_c1/len(df)*100:.0f}%" if len(df) else "")
    m4.metric("🟣 Sentados C2",       f"{sentados_c2:,}", f"{sentados_c2/len(df)*100:.0f}%" if len(df) else "")
    m5.metric("⭐ Graduados MJ",      f"{graduados:,}")
    m6.metric("🛑 Desertores MJ",    f"{desertores:,}", delta_color="inverse")

    st.divider()

    # ── BUSCADOR ──────────────────────────────────────────────────
    c_q, c_r = st.columns([5,1])
    with c_q:
        query = st.text_input("🔍  Buscar por nombre, teléfono, equipo (ej: LOBOS) o IMO...",
                              placeholder="Ej: María García  |  987654321  |  Nombre Equipo o IMO",
                              key="query")
    with c_r:
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("Resultados", len(df_view))

    # Lógica de Búsqueda Abierta (Token-based)
    if query:
        tokens = [t.lower() for t in query.split() if t.strip()]
        if tokens:
            mask = df_view.apply(lambda row: all(t in str(row.values).lower() for t in tokens), axis=1)
            df_result = df_view[mask].reset_index(drop=True)
    else:
        df_result = df_view.reset_index(drop=True)

    # ── TABLA ─────────────────────────────────────────────────────
    if 'Nombres' in df_result.columns and 'Apellidos' in df_result.columns:
        df_result['Participante'] = df_result['Nombres'] + " " + df_result['Apellidos'].replace('—', '')
        df_result['Participante'] = df_result['Participante'].str.strip()
    
    # ── ESTANDARIZACIÓN ESTÉTICA (PROPER CASE) ──────────────────
    name_cols = ['Participante', 'IMO Enrolador', 'Coordinador', 'Aliado C1', 'Aliado C2']
    for col in name_cols:
        if col in df_result.columns:
            df_result[col] = df_result[col].astype(str).str.strip().str.title().replace(['Nan', 'None', ''], '—')

    # ── GESTIÓN DE DATOS Y ALERTAS ───────────────────────────────
    def get_gestion_link(row):
        dni = str(row.get('DNI', '')).strip()
        imo_name = str(row.get('IMO Enrolador', '')).strip().title()
        part_name = str(row.get('Participante', '')).strip()
        c1_status = str(row.get('Estatus C1','')).upper()
        
        # Alerta de Huérfano (Sin IMO en C1E27)
        if ('SENTADO' in c1_status or 'SI' == c1_status) and (imo_name in ['', '—', 'None']):
            return '⚠️ SOLICITAR IMO'

        # Detectar DNI sospechoso
        is_bad = len(dni) < 8 or dni.startswith('999') or dni.startswith('T_')
        
        if is_bad:
            imo_phone = st.session_state.get('imo_phones', {}).get(imo_name)
            if imo_phone:
                clean_ph = re.sub(r'\D', '', imo_phone)
                if clean_ph.startswith('51'): clean_ph = clean_ph[2:]
                msg = f"Hola {imo_name} te escribe Jose de Crear por favor pasame el numero DNI de {part_name}. Gracias, ya que en el registro quedo mal"
                # Protocolo directo para WhatsApp de Escritorio
                url = f"whatsapp://send?phone=51{clean_ph}&text={requests.utils.quote(msg)}"
                return url  # Devolvemos solo la URL para el LinkColumn
            return ""
        return ""

    if not df_result.empty:
        df_result['Gestión DNI'] = df_result.apply(get_gestion_link, axis=1)

    col_order = ['Participante','DNI','Gestión DNI','Teléfono','Participación','IMO Enrolador',
                 'Aliado C1','Aliado C2','Estatus C1','Estatus C2','Estatus MJ',
                 'Coordinador']
    col_order = [c for c in col_order if c in df_result.columns]
    df_display = df_result[col_order]

    # ── GESTIÓN MASIVA (SIDEBAR PRO) ──────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 PERSECUCIÓN PRO C1E27")
    st.sidebar.caption("Ordenado por urgencia (más pendientes)")
    
    # 1. Identificar Casos de Gestión (PRECISIÓN QUIRÚRGICA)
    # Excluir: Sentados, Graduados, Sello de Oro
    excluir_keywords = ['SENTADO', 'SI', '★', 'GRADUADO']
    def es_pendiente_real(row):
        st_c1 = str(row.get('Estatus C1', '')).upper()
        dni_v = str(row.get('DNI', '')).strip()
        is_bad_dni = len(dni_v) < 8 or dni_v.startswith('999') or dni_v.startswith('T_')
        is_not_seated = not any(k in st_c1 for k in excluir_keywords)
        return is_bad_dni and is_not_seated

    bad_mask = df_result.apply(es_pendiente_real, axis=1)
    df_bad = df_result[bad_mask].copy()
    
    if not df_bad.empty:
        # Agrupar por IMO y Contar
        summary = df_bad.groupby('IMO Enrolador')['Participante'].apply(list).to_dict()
        
        # 2. Cargar Historial de Envío para Descarte
        log_path = "Log_WhatsApp.csv"
        sent_today = set()
        if os.path.exists(log_path):
            try:
                df_log = pd.read_csv(log_path)
                today = time.strftime("%Y-%m-%d")
                sent_today = set(df_log[df_log['Fecha'] == today]['IMO'].unique())
            except: pass

        # 3. Buscador de Persecución
        search_persec = st.sidebar.text_input("🔍 Filtrar IMO en Persecución", "").strip().lower()
        
        # 4. Ordenar por Urgencia (Descendente por número de casos)
        sorted_summary = sorted(summary.items(), key=lambda x: len(x[1]), reverse=True)
        
        for imo, participants in sorted_summary:
            imo_norm = str(imo).title().strip()
            if search_persec and search_persec not in imo_norm.lower(): continue
            
            imo_phone = st.session_state.get('imo_phones', {}).get(imo_norm)
            
            if imo_phone:
                p_list_str = ", ".join(participants)
                clean_ph = re.sub(r'\D', '', imo_phone)
                if clean_ph.startswith('51'): clean_ph = clean_ph[2:]
                
                plural = "los números DNI" if len(participants) > 1 else "el número DNI"
                plural_reg = "registros quedaron" if len(participants) > 1 else "registro quedó"
                msg_masivo = f"Hola {imo_norm} te escribe Jose de Crear por favor pasame {plural} de: {p_list_str}. Gracias, ya que en el {plural_reg} mal"
                url_masivo = f"whatsapp://send?phone=51{clean_ph}&text={requests.utils.quote(msg_masivo)}"
                
                label = f"📩 {len(participants)} Casos: {imo_norm}"
                
                with st.sidebar.expander(label):
                    st.write(f"**Integrantes:** {p_list_str}")
                    if imo_norm not in sent_today:
                        st.markdown(f'''
                            <a href="{url_masivo}" style="text-decoration:none;">
                                <div style="background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 8px; text-align: center; font-size: 0.85rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                                    🚀 ENVIAR AHORA
                                </div>
                            </a>
                        ''', unsafe_allow_html=True)
                        if st.button(f"Marcar como Enviado: {imo_norm}", key=f"mark_{imo_norm}"):
                            new_log = pd.DataFrame([{"Fecha": time.strftime("%Y-%m-%d"), "Hora": time.strftime("%H:%M"), "IMO": imo_norm}])
                            new_log.to_csv(log_path, mode='a', header=not os.path.exists(log_path), index=False)
                            st.rerun()
                    else:
                        st.success("✅ Gestionado Hoy")
                        st.markdown(f'''
                            <a href="{url_masivo}" style="text-decoration:none;">
                                <div style="background: #f1f5f9; color: #64748b; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 8px; text-align: center; font-size: 0.85rem; border: 1px solid #e2e8f0;">
                                    🔄 REENVIAR RECORDATORIO
                                </div>
                            </a>
                        ''', unsafe_allow_html=True)

    if not df_display.empty:
        # Usamos column_config para renderizar el link de Gestión
        st.dataframe(
            df_display.style.map(color_cell, subset=[c for c in ['Participación','Estatus C1','Estatus C2','Estatus MJ'] if c in df_display.columns]),
            column_config={
                "Gestión DNI": st.column_config.LinkColumn("Gestión DNI", help="Click para pedir DNI al IMO via WhatsApp"),
                "DNI": st.column_config.TextColumn("DNI", help="DNIs rojos requieren validación")
            },
            use_container_width=True,
            height=580,
            hide_index=True
        )
    else:
        st.markdown("""
        <div style='text-align:center;padding:3rem;color:#475569'>
            <div style='font-size:3rem'>🔍</div>
            <div style='font-size:1.1rem;margin-top:0.5rem'>No se encontraron resultados</div>
            <div style='font-size:0.85rem;margin-top:0.25rem;color:#334155'>Ajusta los filtros del panel izquierdo</div>
        </div>""", unsafe_allow_html=True)

    # ── DETALLE EXPANDIBLE (Solo en modo Buscador) ────────────────
    if not df_result.empty and query and len(df_result) <= 20:
        with st.expander(f"📋 Ver detalle de los {len(df_result)} resultados"):
            for _, row in df_result.iterrows():
                nombre_full = f"{row.get('Nombres','')} {row.get('Apellidos','')}".strip()
                part = row.get('Participación', '')
                import os
                import base64
                
                foto_dir = r"C:\Users\josem\OneDrive\Documentos\campana-cpsl\excel c1e27 nw\Fotos_Participantes"
                
                # Buscar foto ignorando mayúsculas, minúsculas, espacios extra y tildes
                n_norm = norm(nombre_full).replace(' ', '').lower()
                foto_path = None
                if os.path.isdir(foto_dir):
                    for fname in os.listdir(foto_dir):
                        f_norm = norm(os.path.splitext(fname)[0]).replace(' ', '').lower()
                        if n_norm == f_norm or n_norm in f_norm or f_norm in n_norm:
                            foto_path = os.path.join(foto_dir, fname)
                            # Debug: mostrar ruta encontrada en la UI
                            st.write(f"🔎 Foto encontrada: {foto_path}")
                            break

                
                verificado = str(row.get('Verificado_RENIEC', 'NO')).upper() == 'SI'
                check_html = " <span title='Verificado por RENIEC' style='color:#16a34a;margin-left:5px;font-size:1.2rem'>✅</span>" if verificado else ""
                
                color_part = '#16a34a' if 'ACTIVO' in part else '#64748b'

                # Renderizar avatar o foto dentro del layout
                if foto_path:
                    # Mostrar foto con Streamlit (más fiable que embed HTML)
                    st.image(foto_path, width=70)
                    img_html = ""
                else:
                    # Generar iniciales de placeholder
                    iniciales = "".join([p[0] for p in nombre_full.split() if p][:2]).upper()
                    img_html = f"<div style='width:55px;height:55px;border-radius:50%;background:linear-gradient(135deg,#c7d2fe,#a5b4fc);display:flex;align-items:center;justify-content:center;font-weight:bold;color:#312e81;font-size:1.2rem;border:2px solid #e0e7ff'>{iniciales}</div>"

                card_html = f"""
                <div style='border:1px solid #e2e8f0;border-radius:10px;
                            padding:0.8rem 1rem;margin:0.4rem 0;background:#ffffff;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05)'>
                  <div style='display:flex;justify-content:space-between;align-items:center'>
                    <div style='display:flex;align-items:center;gap:15px'>
                        {img_html}
                        <div>
                            <div style='font-weight:800;font-size:1.2rem;color:#0f172a'>{nombre_full}</div>
                            <div style='font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.05em'>
                                { '🛡️ VERIFICADO RENIEC' if verificado else 'PARTICIPANTE OFICIAL' }
                            </div>
                        </div>
                    </div>
                    <span style='font-size:0.75rem;color:{color_part};font-weight:600'>{part}</span>
                  </div>
                  <div style='margin-top:0.8rem;display:grid;grid-template-columns:repeat(3,1fr);gap:0.4rem;font-size:0.8rem;color:#475569'>
                    <span>📞 {row.get('Teléfono','—') or '—'}</span>
                    <span>🧭 IMO: {row.get('IMO Enrolador','—') or '—'}</span>
                    <span>👩‍💻 Coord: {row.get('Coordinador','—') or '—'}</span>
                    <span>🪪 DNI: {str(row.get('DNI','—')).split('.')[0]}</span>
                    <span>🟢 C1: {row.get('Estatus C1','—') or '—'}</span>
                    <span>🔵 C2: {row.get('Estatus C2','—') or '—'}</span>
                    <span>⭐ MJ: {row.get('Estatus MJ','—') or '—'}</span>
                    <span>🛡️ {row.get('Origen/Equipo','—') or '—'}</span>
                  </div>
                  
                  {f"""
                  <div style='margin-top:0.8rem; padding:0.6rem; background:#f8fafc; border-radius:8px; border:1px dashed #cbd5e1'>
                    <div style='font-size:0.65rem; color:#64748b; font-weight:bold; margin-bottom:5px; text-transform:uppercase'>🏆 Trayectoria de Liderazgo (E5-E28)</div>
                    <div style='font-size:0.85rem; color:#1e293b; display:flex; flex-wrap:wrap; gap:5px'>
                      {''.join([f"<span style='background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:12px;font-size:0.7rem;font-weight:bold'>👑 {r.strip()}</span>" if 'Manager' in r else f"<span style='background:#f3e8ff;color:#6b21a8;padding:2px 8px;border-radius:12px;font-size:0.7rem;font-weight:bold'>🌀 {r.strip()}</span>" if 'Quantum' in r else f"<span style='background:#e0f2fe;color:#075985;padding:2px 8px;border-radius:12px;font-size:0.7rem;font-weight:bold'>🛡️ {r.strip()}</span>" if 'Capitán' in r else f"<span style='background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:0.7rem;font-weight:bold'>🤝 {r.strip()}</span>" if 'Aliado' in r else r for r in str(row.get('Trayectoria','—')).split(',')]) if str(row.get('Trayectoria','—')) != '—' else 'Sin histórico de liderazgo registrado'}
                    </div>
                  </div>
                  """ if str(row.get('Trayectoria','—')) != '—' else ""}
                  
                  <div style='margin-top:1rem'></div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Botón para abrir carpeta de OneDrive
                team_info = str(row.get('Origen/Equipo','')).strip()
                if "Equipo" in team_info:
                    if st.button(f"📂 Abrir Carpeta de {team_info.split('—')[-1].strip() if '—' in team_info else team_info}", key=f"btn_{row.get('DNI','')}"):
                        try:
                            dir_base = r"C:\Users\josem\OneDrive - QUANTUM COACHING TECHNOLOGY BVS CIA. LTDA\MAESTRIA DEL JUEGO GLOBAL\Equipos\Lima"
                            # Extraer número de equipo
                            t_num = team_info.split('—')[0].replace('Equipo','').strip()
                            # Buscar carpeta que empiece por EQUIPO {t_num}
                            found = False
                            if os.path.exists(dir_base):
                                for folder in os.listdir(dir_base):
                                    if folder.startswith(f"EQUIPO {t_num}"):
                                        os.startfile(os.path.join(dir_base, folder))
                                        st.toast(f"Abriendo carpeta: {folder}")
                                        found = True
                                        break
                            if not found:
                                st.error("No se encontró la carpeta física del equipo en OneDrive.")
                        except Exception as e:
                            st.error(f"Error al abrir carpeta: {e}")
                
                # Formulario de edicion in-line
                idx_row = str(row.name)
                with st.expander("📝 Editar Datos Manuales", expanded=False):
                    with st.form(key=f"edit_{idx_row}"):
                        c1, c2 = st.columns(2)
                        nuevo_imo = c1.text_input("IMO Enrolador", value=str(row.get('IMO Enrolador','')).replace('nan','').replace('—',''))
                        nuevo_tel = c2.text_input("Teléfono", value=str(row.get('Teléfono','')).replace('nan','').replace('—',''))
                        submit_ed = st.form_submit_button("💾 Guardar Cambios permanentemente")
                        if submit_ed:
                            try:
                                db_path = FILE_PATH
                                df_live = pd.read_excel(db_path)
                                n_match = str(row.get('Nombres','')).strip()
                                a_match = str(row.get('Apellidos','')).strip()
                                
                                # Busqueda de fila exacta
                                mask_ed = (df_live['Nombres'].astype(str).str.strip().str.upper() == n_match.upper()) & \
                                       (df_live['Apellidos'].astype(str).str.strip().str.upper() == a_match.upper())
                                
                                if mask_ed.any():
                                    df_live.loc[mask_ed, 'IMO Enrolador'] = nuevo_imo
                                    df_live.loc[mask_ed, 'Teléfono'] = nuevo_tel
                                    df_live.to_excel(db_path, index=False)
                                    st.cache_data.clear()
                                    st.success("¡Cambios guardados con éxito!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("No se pudo localizar el registro original en el Excel para guardar.")
                            except Exception as e:
                                st.error(f"Fallo de escritura (¿Archivo abierto?): {e}")

# ── DESCARGA ──────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if not df_result.empty:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df_display.to_excel(writer, index=False, sheet_name='Resultados')
        wb = writer.book; ws = writer.sheets['Resultados']
        hfmt = wb.add_format({'bold':True,'bg_color':'#0d1b2a','font_color':'#818cf8','border':1,'font_size':10})
        for i, col in enumerate(col_order):
            ws.write(0, i, col, hfmt)
            ws.set_column(i, i, 30)
    _, c_dl, _ = st.columns([1,2,1])
    with c_dl:
        st.download_button(
            label=f"📥  Exportar {len(df_result):,} registros — Excel",
            data=buf.getvalue(),
            file_name="CREAR_LIMA_CRM.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width='stretch'
        )

elif app_mode == "📊 Reporte de Desempeño 🔱":
    st.markdown("### 📊 Reporte de Desempeño y Auditoría de Gestión")
    st.caption("Foco en pendientes: Identificación de brechas en la gestión de coordinadoras.")
    
    col_sync, col_info = st.columns([1, 1])
    with col_sync:
        if st.button("🔄 Sincronizar Data de la Web Ahora", use_container_width=True):
            with st.spinner("🤖 El Robot está entrando al portal y extrayendo los reportes..."):
                import subprocess
                try:
                    result = subprocess.run(["python", "robot_productividad.py"], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ Sincronización completada con éxito.")
                        st.rerun()
                    else:
                        st.error(f"❌ Error en el robot: {result.stdout}\n{result.stderr}")
                except Exception as e:
                    st.error(f"❌ Fallo al lanzar el robot: {e}")
    
    if os.path.exists("Productividad_Web.xlsx"):
        df_w = pd.read_excel("Productividad_Web.xlsx")
        # Identificar columnas
        col_res = df_w.columns[9] # Resultado Gestión
        df_w['Status'] = df_w[col_res].fillna('SIN GESTIONAR')
        
        # Clasificación Maestra
        df_ni = df_w[df_w['Status'] == 'NO LE INTERESA']
        df_nc = df_w[df_w['Status'] == 'NO CONTESTAN']
        df_sg = df_w[df_w['Status'] == 'SIN GESTIONAR']
        df_ok = df_w[df_w['Asistencia'].astype(str).str.upper().str.contains('SI', na=False)]
        
        # Métricas de Auditoría
        st.markdown("#### 🚩 Semáforo de Pendientes (Data Web)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("✅ Sentados", len(df_ok), help="Asistencia confirmada")
        m2.metric("🚫 NI", len(df_ni), delta=f"-{len(df_ni)}", delta_color="inverse")
        m3.metric("📵 Sin Contestar", len(df_nc))
        m4.metric("❓ Sin Gestionar", len(df_sg))
        
        st.divider()
        
        # Listas con Nombres Propios
        cc_opts = sorted(df_w['CC_Reportada'].unique().tolist())
        cc_sel = st.selectbox("Auditar Coordinadora:", ["Todas"] + cc_opts)
        df_aud = df_w if cc_sel == "Todas" else df_w[df_w['CC_Reportada'] == cc_sel]
        
        with st.expander(f"📵 Lista: Personas que NO CONTESTAN ({len(df_nc[df_nc['CC_Reportada']==cc_sel]) if cc_sel!='Todas' else len(df_nc)})"):
            cols_view = ['NombreCompleto', 'ApellidoCompleto', 'Nombre IMO']
            st.dataframe(df_aud[df_aud['Status'] == 'NO CONTESTAN'][cols_view], use_container_width=True, hide_index=True)
            
        with st.expander(f"❓ Lista: Personas SIN GESTIONAR ({len(df_sg[df_sg['CC_Reportada']==cc_sel]) if cc_sel!='Todas' else len(df_sg)})"):
            st.dataframe(df_aud[df_aud['Status'] == 'SIN GESTIONAR'][cols_view], use_container_width=True, hide_index=True)

        with st.expander("🚫 Detalle: No Interesados (NI)"):
            st.dataframe(df_aud[df_aud['Status'] == 'NO LE INTERESA'][cols_view], use_container_width=True, hide_index=True)
    else:
        st.info("Pulse el botón de sincronización para cargar la auditoría de nombres.")

# ── SECCIÓN: CENTRO DE INTEGRIDAD 🔱 ──────────────────────────
elif app_mode == "🔱 Centro de Integridad":
    st.markdown("## 🔱 Centro de Integridad y Unificación Maestra")
    st.info("Este motor autónomo unifica identidades por DNI y Nombre (Fuzzy Matching >82%).")
    
    st.divider()
    tab1, tab2 = st.tabs(["🚀 Unificación Maestra", "🛠️ Fusión de Duplicados"])
    
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### 📊 Salud de Identidad")
            total_p = len(df)
            grads = df[df['Estatus MJ'].str.contains('GRADUADO', na=False, case=False)]
            st.metric("Total Integrantes", f"{total_p:,}")
            st.metric("Graduados Identificados", f"{len(grads)}", f"{len(grads)/318*100:.1f}% de la meta")
            
        with col_b:
            st.markdown("### 🏹 Acciones")
            if st.button("🔱 Ejecutar Unificación Inteligente (Patrones)", use_container_width=True):
                with st.spinner("Fusionando duplicados y vinculando graduados..."):
                    try:
                        import subprocess
                        script_path = os.path.join(os.getcwd(), "reconstruir_maestro_total.py")
                        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, encoding='latin-1')
                        if result.returncode == 0:
                            st.success("✅ ¡Unificación Completada!")
                            st.cache_data.clear()
                            st.rerun()
                        else: st.error("Error en el proceso")
                    except Exception as e: st.error(f"Falla: {e}")

    with tab2:
        st.markdown("### 🛠️ Fusión Manual de Conflictos")
        st.info("Aquí aparecen personas con el mismo teléfono pero nombres distintos. Tú decides si son la misma persona.")
        
        conflict_file = "conflictos_pendientes.json"
        decision_file = "decisiones_fusion.json"
        
        if os.path.exists(conflict_file):
            with open(conflict_file, 'r', encoding='utf-8') as f:
                conflicts = json.load(f)
            
            if not conflicts:
                st.success("✨ ¡No hay conflictos de identidad pendientes!")
            else:
                for idx, c in enumerate(conflicts):
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.markdown(f"**Registro A**")
                            st.caption(c['A']['name'])
                        with col2:
                            st.markdown(f"**Registro B**")
                            st.caption(c['B']['name'])
                        with col3:
                            st.caption(f"📞 {c['phone']}")
                            if st.button(f"🔱 Fusionar", key=f"fuse_{idx}"):
                                # Guardar decision
                                decisions = {}
                                if os.path.exists(decision_file):
                                    with open(decision_file, 'r', encoding='utf-8') as f:
                                        decisions = json.load(f)
                                # Apuntar A hacia B
                                decisions[c['A']['key']] = c['B']['key']
                                with open(decision_file, 'w', encoding='utf-8') as f:
                                    json.dump(decisions, f, ensure_ascii=False, indent=2)
                                st.success("¡Decisión guardada! Ejecutando unificación...")
                                # Re-correr motor
                                import subprocess
                                subprocess.run([sys.executable, "reconstruir_maestro_total.py"])
                                st.cache_data.clear()
                                st.rerun()
        else:
            st.success("✨ ¡Tu base de datos está libre de duplicados por teléfono!")

elif app_mode == "📊 Sala de Guerra":
    st.markdown("### 🔱 Sala de Guerra: Gestión Histórica de Llamadas")
    st.caption("Gestiona los KPIs diarios y observaciones de las coordinadoras.")
    
    col_d, col_c = st.columns([1, 2])
    with col_d:
        sel_date = st.date_input("📅 Fecha de Gestión:", value=datetime.date.today())
        str_date = sel_date.strftime("%Y-%m-%d")
    with col_c:
        report_coord = st.selectbox("Coordinadora que reporta:", ["Zuley", "Joyce", "Diana", "Otro"])
    
    # Lógica de Edición Histórica
    existing_reports = []
    if os.path.exists("Historial_Reportes.csv"):
        df_h = pd.read_csv("Historial_Reportes.csv")
        # Filtrar por fecha seleccionada y coordinadora
        mask = (df_h['Fecha'] == str_date) & (df_h['Coordinadora'] == report_coord)
        date_data = df_h[mask]
        if not date_data.empty:
            for rid in date_data['ID_Reporte'].unique():
                row = date_data[date_data['ID_Reporte'] == rid].iloc[0]
                existing_reports.append({
                    "id": rid, 
                    "label": f"Reporte ({row['Hora']})", 
                    "text": row.get('RawText', ''),
                    "obs": row.get('Observaciones', '')
                })
    
    # Selector de Modo
    mode_options = ["✨ Nuevo Reporte"] + [r['label'] for r in existing_reports]
    sel_mode = st.radio("Sesión del día:", mode_options, horizontal=True)
    
    # Pre-cargar datos si es edición
    default_text = ""
    default_obs = ""
    edit_id = None
    if sel_mode != "✨ Nuevo Reporte":
        idx = mode_options.index(sel_mode) - 1
        default_text = existing_reports[idx]['text']
        default_obs = existing_reports[idx]['obs']
        edit_id = existing_reports[idx]['id']

    report_text = st.text_area("📋 Pega el reporte numérico (WhatsApp):", value=default_text, height=250)
    obs_text = st.text_area("📝 Observaciones de la Jornada (Opcional):", value=default_obs, height=100)
    
    btn_label = "🚀 Consolidar y Guardar" if edit_id is None else "💾 Actualizar Reporte Histórico"
    if st.button(btn_label, use_container_width=True):
        if report_text:
            parsed_data = parse_whatsapp_report(report_text)
            if parsed_data:
                success, result = save_report_history(
                    report_coord, parsed_data, report_text, 
                    overwrite_ts=edit_id, target_date=str_date, notes=obs_text
                )
                if success:
                    st.success(f"✅ Reporte del {str_date} {'actualizado' if edit_id else 'guardado'} con éxito.")
                    st.rerun()
                else:
                    st.error(f"❌ {result}")
            else:
                st.error("❌ Formato no reconocido. Asegúrate de incluir 'Nombre_Seccion:' y 'Clave = Numero'.")
        else:
            st.warning("⚠️ El área de texto está vacía.")

    # ── ANALÍTICA ESTRATÉGICA (GESTIÓN DE LLAMADAS) ───────────
    if os.path.exists("Historial_Reportes.csv"):
        st.markdown("---")
        st.markdown("### 🎯 Tablero de Gestión: Confirmación de Llamadas")
        st.caption("Nota: Estas cifras representan promesas telefónicas, no asistencia física en salón.")
        df_hist_full = pd.read_csv("Historial_Reportes.csv")
        
        # PESTAÑAS ESTRATÉGICAS
        tab_war, tab_ai = st.tabs(["🔱 Sala de Guerra", "🧠 Autonomía IA"])
        
        with tab_war:
            # 1. KPIs del Día Seleccionado (Lógica Max Snapshot)
            df_day = df_hist_full[df_hist_full['Fecha'] == str_date]
            resumen_day = df_day.groupby(['Coordinadora', 'Seccion', 'Estado'])['Cantidad'].max().reset_index()
            
            total_ok_hoy = resumen_day[resumen_day['Estado'] == 'OK']['Cantidad'].sum()
            
            # FILTRO RIGUROSO: Solo Aliados en estado OK
            df_aliados_ok = resumen_day[(resumen_day['Seccion'].str.contains('Aliados', case=False, na=False)) & (resumen_day['Estado'] == 'OK')]
            total_aliados_hoy = df_aliados_ok['Cantidad'].sum()

            # Metas
            meta_gestion = 325 
            aliados_requeridos = round(total_ok_hoy / 6)
            
            # --- PANEL EJECUTIVO (VISUAL) ---
            import plotly.graph_objects as go
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = total_ok_hoy,
                title = {'text': "🚀 OKs de Participantes", 'font': {'size': 20}},
                delta = {'reference': meta_gestion, 'increasing': {'color': "#16a34a"}},
                gauge = {'axis': {'range': [None, meta_gestion]}, 'bar': {'color': "#16a34a"}}))
        
        fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # --- MONITOR DE CLARIDAD: RED DE ALIADOS ---
        st.markdown("### 🛡️ Monitor de Red de Aliados (Solo OKs)")
        c_al1, c_al2 = st.columns([2, 1])
        
        with c_al1:
            st.markdown(f"#### **Total Aliados Confirmados: {total_aliados_hoy}**")
            # Desglose por CC para claridad total
            cols_cc = st.columns(3)
            coords_list = ["Zuley", "Joyce", "Diana"]
            for i, name in enumerate(coords_list):
                cc_al = df_aliados_ok[df_aliados_ok['Coordinadora'] == name]['Cantidad'].sum()
                cols_cc[i].metric(f"OK Aliados {name}", cc_al)
        
        with c_al2:
            cumplimiento_red = (total_aliados_hoy / aliados_requeridos * 100) if aliados_requeridos > 0 else 100
            st.metric("Salud de Red (1:6)", f"{cumplimiento_red:.1f}%", f"Necesitas {aliados_requeridos}")

        st.markdown("---")
        st.markdown("### 🔍 Área de Oportunidad (Brecha de Participantes)")
        c1, c2 = st.columns(2)
        c1.metric("📦 Avance Real", f"{total_ok_hoy} OKs", f"{(total_ok_hoy/meta_gestion)*100:.1f}%")
        c2.metric("🚨 Brecha (Faltante)", f"{max(0, meta_gestion - total_ok_hoy)} Pax", delta_color="inverse")

        # 2. Auditoría de Veracidad: Local vs Web
        st.divider()
        st.markdown("#### 🕵️‍♂️ Auditoría de Veracidad: Local vs Web")
        st.caption("Comparando solo gestiones confirmadas (OK) para detectar inflación de reportes.")
        
        web_data = {"DIANA": 196, "JOYCE": 173, "ZULEY": 190}
        audit_cols = st.columns(3)
        
        # Filtramos el resumen para contar solo OKs en la auditoría
        resumen_ok_audit = resumen_day[resumen_day['Estado'] == 'OK']
        
        for i, (name, web_val) in enumerate(web_data.items()):
            local_val_ok = resumen_ok_audit[resumen_ok_audit['Coordinadora'].str.upper().str.contains(name)]['Cantidad'].sum()
            diff = local_val_ok - web_val
            with audit_cols[i]:
                st.metric(f"Audit OK: {name}", f"{local_val_ok} WA", f"{diff} vs Web ({web_val})", delta_color="inverse" if abs(diff) > 10 else "normal")

        # 3. Ranking Individual de Gestión (Meta 110)
        st.markdown("#### 🏆 Ranking de Gestión Telefónica (Meta 110)")
        cols = st.columns(3)
        coords_list = ["Zuley", "Joyce", "Diana"]
        for i, name in enumerate(coords_list):
            cc_ok = resumen_day[(resumen_day['Coordinadora'] == name) & (resumen_day['Estado'] == 'OK')]['Cantidad'].sum()
            with cols[i]:
                st.metric(name, f"{cc_ok}/110", f"{cc_ok-110 if cc_ok < 110 else '¡META LOGRADA!'}")
                st.progress(min(cc_ok/110, 1.0))

        # 3. Monitor de Aliados (Regla 1:6)
        st.divider()
        st.markdown("#### 🛡️ Salud de la Red: Aliados (Meta 1 por cada 6 OKs)")
        aliados_requeridos = round(total_ok_hoy / 6)
        progreso_aliados = min(total_aliados_hoy / aliados_requeridos, 1.0) if aliados_requeridos > 0 else 0
        
        c_al_1, c_al_2 = st.columns(2)
        with c_al_1:
            st.metric("Aliados Actuales", total_aliados_hoy, f"Necesitas: {aliados_requeridos}")
        with c_al_2:
            st.metric("Fulfillment Red", f"{progreso_aliados*100:.1f}%")
        
        st.progress(progreso_aliados)
        if total_aliados_hoy < aliados_requeridos:
            st.warning(f"⚠️ Alerta de Red: Faltan {aliados_requeridos - total_aliados_hoy} aliados para soportar los {total_ok_hoy} OKs.")
        else:
            st.success("✅ Estructura de aliados sólida para el volumen actual.")

        st.divider()
        st.markdown("### 📈 Evolución de la Gestión (Promesas vs Tiempo)")
        
        # 3. Evolución Grupal de OKs (Max por día)
        df_daily_max = df_hist_full[df_hist_full['Estado'] == 'OK'].groupby(['Fecha', 'Coordinadora'])['Cantidad'].max().reset_index()
        df_ok_history = df_daily_max.groupby('Fecha')['Cantidad'].sum().reset_index()
        
        import plotly.express as px
        fig_evol = px.line(df_ok_history, x='Fecha', y='Cantidad', title="🚀 Crecimiento de Compromisos Telefónicos (OK)",
                           markers=True, line_shape='spline', color_discrete_sequence=['#16a34a'])
        fig_evol.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_evol, use_container_width=True)
        
        # 4. Bitácora de Gestión
        st.markdown(f"#### 🗒️ Detalle de Llamadas Reportadas: {str_date}")
        if not df_day.empty:
            st.dataframe(df_day[['Hora', 'Coordinadora', 'Seccion', 'Estado', 'Cantidad', 'Avance', 'Observaciones']], 
                         use_container_width=True, hide_index=True)
        else:
            st.info(f"No hay reportes de llamadas detallados para el {str_date}.")

        with tab_ai:
            st.markdown("### 🧠 Centro de Autonomía Cuántica")
            st.caption("5 Motores de IA analizando tu gestión en tiempo real para aprender de tus procesos.")
            
            from brain_ai import obtener_consejo_ia_global
            consejos = obtener_consejo_ia_global(None)
            
            c_ia1, c_ia2 = st.columns([1, 2])
            with c_ia1:
                st.info("🤖 **Estado de los Agentes:**\n\n✅ Gemini: Activo\n✅ Groq: Aprendiendo\n✅ Mistral: Auditando\n✅ Cohere: Resumiendo\n✅ HF: Clasificando")
            
            with c_ia2:
                st.markdown("#### ⚡ Sugerencias de Autonomía")
                for c in consejos:
                    st.write(f"- {c}")
            
            st.divider()
            st.markdown("#### 🚀 Despliegue en la Nube (GitHub & Render)")
            st.write("Tu sistema está configurado para ser compartido. Presiona el botón para validar la integridad del despliegue.")
            if st.button("🔗 Validar Archivos de Despliegue"):
                archivos = [".gitignore", "requirements.txt", "brain_ai.py", "Procfile"]
                faltantes = [f for f in archivos if not os.path.exists(f)]
                if not faltantes:
                    st.success("✅ Todo listo para el despliegue. ¡Puedes subirlo a GitHub y conectar con Render!")
                else:
                    st.warning(f"⚠️ Faltan archivos: {', '.join(faltantes)}")
                    if "Procfile" in faltantes:
                        with open("Procfile", "w") as f: f.write("web: streamlit run app_buscador.py --server.port $PORT")
                        st.info("🪄 Procfile generado automáticamente.")
    else:
        st.info("No hay reportes registrados en el historial de llamadas.")

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#1e293b;font-size:0.72rem;margin-top:2rem'>
CREAR LIMA · CRM Maestro E2E · Confidencial · Datos deduplicados al 80%
</div>""", unsafe_allow_html=True)
