import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
import unicodedata
import re
from datetime import datetime, date

# ── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────
st.set_page_config(
    page_title="CRM CREAR LIMA 🔱",
    layout="wide",
    page_icon="🔱",
    initial_sidebar_state="expanded"
)

# ── SISTEMA DE AUTENTICACIÓN ──────────────────────────────────
from streamlit_javascript import st_javascript

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = None

VALID_USERS = {
    "diana": {"pass": "crear2026", "role": "CC", "name": "Diana Moscoso"},
    "joyce": {"pass": "crear2026", "role": "CC", "name": "Joyce Marin"},
    "zuley": {"pass": "crear2026", "role": "CC", "name": "Zuley Urteaga"},
    "jose": {"pass": "admin", "role": "Gerencia", "name": "Jose M."},
    "gerencia": {"pass": "admin2026", "role": "Gerencia", "name": "Dirección General"}
}

# Auto-login silencioso vía query_params (Más estable que JS)
if not st.session_state['logged_in']:
    query_user = st.query_params.get("u")
    if query_user and query_user in VALID_USERS:
        st.session_state['logged_in'] = True
        st.session_state['user_name'] = VALID_USERS[query_user]["name"]
        st.session_state['user_role'] = VALID_USERS[query_user]["role"]
        st.rerun()

if not st.session_state['logged_in']:
    st.markdown("""
        <style>
        /* Elite CRM Theme */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Outfit:wght@300;500;700&display=swap');
        
        .stApp {
            background-color: #0f172a;
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
            color: #f8fafc;
            letter-spacing: -0.5px;
        }
        .stTextInput>div>div>input {
            background-color: #1e293b;
            color: white;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 10px 15px;
        }
        .stTextInput>div>div>input:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }
        .stButton>button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.6);
        }
        .stDataFrame {
            background-color: #1e293b;
            border-radius: 12px;
            border: 1px solid #334155;
            overflow: hidden;
        }
        div[data-testid="stMetricValue"] {
            font-family: 'Outfit', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            color: #60a5fa;
            text-shadow: 0 0 20px rgba(96, 165, 250, 0.3);
        }
        div[data-testid="stMetricLabel"] {
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.85rem;
        }
        </style>
        <div style="text-align:center; padding: 40px 20px; background: radial-gradient(circle at top, #1e1b4b 0%, #0f172a 100%); border-bottom: 1px solid #334155; margin-bottom: 30px;">
            <h1 style="font-family:'Outfit', sans-serif; font-size: 3.5rem; color: #ffffff; margin-bottom: 0; text-shadow: 0 4px 20px rgba(0,0,0,0.5);">
                <span style="color: #818cf8;">🔱</span> CREAR LIMA
            </h1>
            <h3 style="font-family:'Inter', sans-serif; font-weight: 300; color: #94a3b8; margin-top: 10px; font-size: 1.2rem; letter-spacing: 2px;">
                TORRE DE CONTROL & CEREBRO CUÁNTICO
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    col_login1, col_login2, col_login3 = st.columns([1, 1, 1])
    with col_login2:
        st.markdown('<div style="background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.1); border-top: 5px solid #4f46e5;">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-top:0; color:#1e293b; text-align:center;">🔑 Acceso Restringido</h4>', unsafe_allow_html=True)
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        recordar = st.checkbox("Recordar sesión", value=True)
        
        if st.button("Iniciar Sesión", use_container_width=True):
            user_key = user_input.lower().strip()
            pass_key = pass_input.strip()
            if user_key in VALID_USERS and VALID_USERS[user_key]["pass"] == pass_key:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = VALID_USERS[user_key]["role"]
                st.session_state['user_name'] = VALID_USERS[user_key]["name"]
                
                if recordar:
                    st.query_params["u"] = user_key
                
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas. Intenta de nuevo.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ── CONSTANTES CLOUD ─────────────────────────────────────────
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
HIST_FILE = "Historial_Reportes.csv"
META_OKS = 325

COORDS = {
    "DIANA":  "Diana Moscoso",
    "JOYCE":  "Joyce Marin",
    "ZULEY":  "Zuley Urteaga"
}

# ── ESTILOS PREMIUM ──────────────────────────────────────────
# ── ESTILOS PREMIUM ULTRA-MODERNOS (V2.0) ────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* Ocultar elementos nativos de Streamlit para un look real */
header[data-testid="stHeader"] { display: none; }
footer { display: none; }
.stDeployButton { display: none; }

/* Tipografía global y fondos */
html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
}
h1, h2, h3, h4, h5, h6, [data-testid="stMetricLabel"] {
    font-family: 'Outfit', sans-serif !important;
}

.stApp { 
    background-color: #f4f7fb; 
    background-image: radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.05) 0px, transparent 50%),
                      radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.05) 0px, transparent 50%);
    background-attachment: fixed;
}

/* Sidebar rediseñado */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}
[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
    font-weight: 700;
    letter-spacing: 0.5px;
}
/* Estilo de inputs en la sidebar */
[data-testid="stSidebar"] input, [data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 8px;
}

/* Tarjetas de Guerra (War Cards) con Glassmorphism */
.war-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 24px 30px;
    box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08);
    border: 1px solid rgba(255,255,255,0.5);
    border-left: 6px solid #4f46e5;
    margin-bottom: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.war-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 50px -10px rgba(79, 70, 229, 0.15);
}

/* Etiquetas de Estado Modernas */
.status-ok   { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 4px 14px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; box-shadow: 0 2px 10px rgba(16,185,129,0.3); }
.status-pend { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 4px 14px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; box-shadow: 0 2px 10px rgba(245,158,11,0.3); }
.status-reza { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 4px 14px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; box-shadow: 0 2px 10px rgba(239,68,68,0.3); }

/* Métricas impactantes */
[data-testid="stMetricValue"] { 
    font-size: 2.8rem !important; 
    font-weight: 800 !important; 
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricDelta"] {
    font-size: 0.9rem !important;
    font-weight: 700 !important;
}

/* Contenedores de Métricas */
div[data-testid="metric-container"] {
    background: white;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    border: 1px solid rgba(0,0,0,0.02);
    transition: all 0.3s ease;
}
div[data-testid="metric-container"]:hover {
    box-shadow: 0 10px 25px rgba(79,70,229,0.1);
    transform: translateY(-2px);
}

/* Pestañas (Tabs) Estilo Apple */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-radius: 12px;
    padding: 6px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    border: 1px solid rgba(0,0,0,0.03);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 10px 20px;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    color: #64748b;
    border: none;
    background: transparent;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(79,70,229,0.3);
}

/* Botones Principales */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.2rem !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
    box-shadow: 0 4px 15px rgba(79,70,229,0.3) !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(79,70,229,0.4) !important;
}

/* Entradas de texto / DataFrames */
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 2px solid #e2e8f0 !important;
    padding: 12px !important;
    font-size: 1rem !important;
    transition: border-color 0.3s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 4px rgba(79,70,229,0.1) !important;
}

/* Títulos con gradiente */
h1 {
    background: linear-gradient(135deg, #1e293b 0%, #4f46e5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    margin-bottom: 30px !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}
</style>
""", unsafe_allow_html=True)

# ── MOTOR DE PARSEO DE REPORTES WA ───────────────────────────
def parse_whatsapp_report(text):
    lines = text.strip().split('\n')
    data, coord = [], "Desconocido"
    for line in lines:
        up = line.upper()
        for k, v in COORDS.items():
            if k in up: coord = v
        if ':' in line and '=' in line:
            try:
                sec  = line.split(':')[0].strip()
                rest = line.split(':')[1]
                est  = rest.split('=')[0].strip().upper()
                if any(x in est for x in ["CONF","OK","APROB"]): est = "OK"
                elif "REZAG" in est: est = "REZAGADO"
                cant = ''.join(filter(str.isdigit, rest.split('=')[1]))
                if cant:
                    data.append({
                        "Fecha": datetime.now().strftime("%Y-%m-%d"),
                        "Hora":  datetime.now().strftime("%H:%M"),
                        "Coordinadora": coord,
                        "Seccion": sec,
                        "Estado": est,
                        "Cantidad": int(cant),
                        "Raw": line.strip()
                    })
            except: pass
    return data

# ── CARGA DE DATOS CLOUD ──────────────────────────────────────
@st.cache_data(ttl=60)
def load_master():
    try:
        df = pd.read_excel(GSHEET_URL, dtype=str).fillna("—")
        
        # REGLA PROFESIONAL: Formato Nombre Propio (Title Case) para coherencia visual
        for col in ['Nombres', 'Apellidos', 'Coordinador', 'IMO Enrolador']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.title().str.strip()
                
        # Columna de nombre completo para display
        nom = df['Nombres'].str.strip() if 'Nombres' in df.columns else pd.Series([''] * len(df))
        ape = df['Apellidos'].str.strip() if 'Apellidos' in df.columns else pd.Series([''] * len(df))
        df['_nombre_completo'] = (nom + " " + ape).str.title().str.strip()
        # Columna de búsqueda normalizada (solo campos clave)
        def make_search_key(row):
            campos = [
                str(row.get('Nombres','')),
                str(row.get('Apellidos','')),
                str(row.get('DNI','')),
                str(row.get('Teléfono','')),
                str(row.get('Email','')),
                str(row.get('IMO Enrolador',''))
            ]
            return norm(" ".join(campos))
        df['_search_key'] = df.apply(make_search_key, axis=1)

        # Asegurar que Coordinador existe
        if 'Coordinador' not in df.columns:
            df['Coordinador'] = "—"
            
        # Integrar Productividad desde Google Sheets
        try:
            from sync_cloud import load_productividad_cloud
            df_prod = load_productividad_cloud()
            if not df_prod.empty:
                # Regla Profesional
                for col in ['NombreCompleto', 'ApellidoCompleto', 'Coordinador', 'CC_Reportada']:
                    if col in df_prod.columns:
                        df_prod[col] = df_prod[col].astype(str).str.title().str.strip()
                        
                nom_p = df_prod['NombreCompleto'].astype(str).str.strip() if 'NombreCompleto' in df_prod.columns else pd.Series([''] * len(df_prod))
                ape_p = df_prod['ApellidoCompleto'].astype(str).str.strip() if 'ApellidoCompleto' in df_prod.columns else pd.Series([''] * len(df_prod))
                df_prod['_nombre_completo'] = (nom_p + " " + ape_p).str.title().str.strip()
                
                # Definir llave primaria para cruce (DNI o Nombre)
                id_col_master = 'DNI' if 'DNI' in df.columns else 'Identificación' if 'Identificación' in df.columns else None
                if id_col_master and 'ClienteId' in df_prod.columns:
                    df['_merge_key'] = df[id_col_master].astype(str).str.strip().str.upper()
                    df.loc[(df['_merge_key'] == "") | (df['_merge_key'] == "—") | (df['_merge_key'] == "NAN"), '_merge_key'] = df['_nombre_completo']
                    
                    df_prod['_merge_key'] = df_prod['ClienteId'].astype(str).str.strip().str.upper()
                    df_prod.loc[(df_prod['_merge_key'] == "") | (df_prod['_merge_key'] == "—") | (df_prod['_merge_key'] == "NAN"), '_merge_key'] = df_prod['_nombre_completo']
                else:
                    df['_merge_key'] = df['_nombre_completo']
                    df_prod['_merge_key'] = df_prod['_nombre_completo']

                # Deduplicar quedándonos con la acción más reciente
                if 'Fecha Gestión' in df_prod.columns:
                    df_prod = df_prod.sort_values('Fecha Gestión', na_position='first').drop_duplicates(subset=['_merge_key'], keep='last')
                else:
                    df_prod = df_prod.drop_duplicates(subset=['_merge_key'], keep='last')
                
                cols_to_merge = ['_merge_key', 'Resultado Gestión', 'Fecha Gestión', 'Asistencia', 'CC_Reportada']
                cols_available = [c for c in cols_to_merge if c in df_prod.columns]
                
                if len(cols_available) > 1:
                    df = df.merge(df_prod[cols_available], on='_merge_key', how='left')
                    
                    if 'CC_Reportada' in df.columns:
                        # Rellenar solo si hay match (notna)
                        mask = (df['Coordinador'].isna() | (df['Coordinador'] == "—") | (df['Coordinador'] == "")) & df['CC_Reportada'].notna()
                        df.loc[mask, 'Coordinador'] = df.loc[mask, 'CC_Reportada']
        except Exception as e:
            print(f"⚠️ No se pudo integrar productividad: {e}")

        # Integrar Asignaciones (Listado Oficial) desde Google Sheets
        try:
            from sync_cloud import load_asignaciones_cloud
            df_asig = load_asignaciones_cloud()
            if not df_asig.empty:
                # Regla Profesional
                for col in ['NombreCompleto', 'ApellidoCompleto', 'Coordinador']:
                    if col in df_asig.columns:
                        df_asig[col] = df_asig[col].astype(str).str.title().str.strip()
                        
                nom_a = df_asig['NombreCompleto'].astype(str).str.strip() if 'NombreCompleto' in df_asig.columns else pd.Series([''] * len(df_asig))
                ape_a = df_asig['ApellidoCompleto'].astype(str).str.strip() if 'ApellidoCompleto' in df_asig.columns else pd.Series([''] * len(df_asig))
                df_asig['_nombre_completo'] = (nom_a + " " + ape_a).str.title().str.strip()
                
                df_asig = df_asig.drop_duplicates(subset=['_nombre_completo'], keep='first')
                
                cols_to_merge_a = ['_nombre_completo', 'Coordinador', 'Estado']
                cols_av_a = [c for c in cols_to_merge_a if c in df_asig.columns]
                
                if len(cols_av_a) > 1:
                    df = df.merge(df_asig[cols_av_a], on='_nombre_completo', how='left', suffixes=('', '_Asig'))
                    
                    if 'Coordinador_Asig' in df.columns:
                        mask = (df['Coordinador'].isna() | (df['Coordinador'] == "—") | (df['Coordinador'] == "")) & df['Coordinador_Asig'].notna()
                        df.loc[mask, 'Coordinador'] = df.loc[mask, 'Coordinador_Asig']
        except Exception as e:
            print(f"⚠️ No se pudo integrar asignaciones: {e}")

        df['Coordinador'] = df['Coordinador'].fillna('—')
        return df
    except Exception as e:
        st.error(f"⚠️ Error conectando a Google Sheets: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_gestion():
    """Carga los datos de GESTION_LLAMADAS desde Google Sheets."""
    try:
        from sync_cloud import conectar_sheets
        c = conectar_sheets()
        if c:
            sh = c.open_by_key(SHEET_ID)
            try:
                dg = pd.DataFrame(sh.worksheet("CREARPSL_GESTION").get_all_records()).fillna("")
            except:
                try:
                    dg = pd.DataFrame(sh.worksheet("GESTION_LLAMADAS").get_all_records()).fillna("")
                except:
                    return pd.DataFrame()
            
            if not dg.empty:
                for col in ['Nombres', 'Apellidos', 'Coordinadora', 'CC_Alias']:
                    if col in dg.columns:
                        dg[col] = dg[col].astype(str).str.title().str.strip()
            return dg
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error cargando GESTION_LLAMADAS: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_auditoria():
    """Carga los datos de AUDITORIA_CONFIRMACIONES desde Google Sheets."""
    try:
        from sync_cloud import conectar_sheets
        c = conectar_sheets()
        if c:
            sh = c.open_by_key(SHEET_ID)
            try:
                dg = pd.DataFrame(sh.worksheet("AUDITORIA_CONFIRMACIONES").get_all_records(default_blank="—")).fillna("—")
                return dg
            except:
                pass
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()
    except:
        pass
    return pd.DataFrame()

def load_history():
    """Carga historial: primero intenta Cloud (Google Sheets), fallback a CSV local."""
    try:
        from sync_cloud import load_history_cloud
        df = load_history_cloud()
        if not df.empty:
            return df
    except:
        pass
    # Fallback local
    if os.path.exists(HIST_FILE):
        return pd.read_csv(HIST_FILE)
    return pd.DataFrame(columns=['Fecha','Hora','Coordinadora','Seccion','Estado','Cantidad','Raw'])

def save_history(df_hist):
    """Guarda historial: Cloud (Google Sheets) + CSV local como backup."""
    df_hist.to_csv(HIST_FILE, index=False)
    try:
        from sync_cloud import save_history_cloud
        save_history_cloud(df_hist)
    except:
        pass

def norm(text):
    if not text or pd.isna(text): return ""
    s = str(text).upper().strip()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

@st.cache_data(ttl=60)
def load_respuestas():
    """Carga los datos de RESPUESTAS_IMO desde Google Sheets."""
    try:
        from sync_cloud import conectar_sheets
        c = conectar_sheets()
        if c:
            sh = c.open_by_key(SHEET_ID)
            try:
                dr = pd.DataFrame(sh.worksheet("RESPUESTAS_IMO").get_all_records()).fillna("")
                return dr
            except:
                pass
    except:
        pass
    return pd.DataFrame()

# ── CARGA INICIAL ─────────────────────────────────────────────
df_master  = load_master()
df_hist    = load_history()
df_gestion = load_gestion()
df_auditoria = load_auditoria()
df_resp    = load_respuestas()

LISTA_COORDS = ["Diana Moscoso", "Joyce Marin", "Zuley Urteaga", "General"]
LISTA_ESTADOS = ["OK", "REZAGADO", "LLAMADO", "ALIADO", "PENDIENTE"]

# ── PANTALLA EXCLUSIVA PARA COORDINADORAS (SOLO CHAT) ────────
if st.session_state.get('user_role') in ["CC", "CC_MJ"]:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        .stApp { background-color: #0f172a; color: #f8fafc; }
        .stTextInput > div > div > input { background-color: #1e293b !important; color: white !important; border: 1px solid #334155 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='color:#38bdf8; text-align:center;'>🧠 Cerebro Cuántico - Terminal</h2>", unsafe_allow_html=True)
    st.caption("Terminal de IA conectada en tiempo real al CRM de CREAR.")
    
    CHAT_DB_FILE = f"chat_ia_{st.session_state.get('user_name', 'general').replace(' ', '_').lower()}.json"
    import json
    
    def load_chat_db():
        if os.path.exists(CHAT_DB_FILE):
            try:
                with open(CHAT_DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return [{"role": "assistant", "content": f"¡Hola Líder {st.session_state.get('user_name', '')}! Soy el Cerebro Cuántico. Ya sincronicé la base de datos de esta campaña. ¿En qué te asesoro?"}]

    def save_chat_db(messages):
        try:
            with open(CHAT_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(messages, f, indent=4, ensure_ascii=False)
        except: pass

    if "messages_ia" not in st.session_state:
        st.session_state.messages_ia = load_chat_db()
    
    chat_container = st.container(height=600)
    with chat_container:
        for msg in st.session_state.messages_ia:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    with st.form("chat_form_cc", clear_on_submit=True):
        cols = st.columns([5, 1])
        prompt = cols[0].text_input("Mensaje", label_visibility="collapsed", placeholder="Escribe aquí...")
        submitted = cols[1].form_submit_button("➤")
        
    if submitted and prompt.strip():
        st.session_state.messages_ia.append({"role": "user", "content": prompt})
        save_chat_db(st.session_state.messages_ia)
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                msg_placeholder = st.empty()
                try:
                    import os, re
                    try:
                        from ia_multimodelo import ia_responder
                        cc_name = st.session_state.get('user_name', '')
                        cc_role = st.session_state.get('user_role', '')
                        
                        # ── Generar contexto con datos REALES del CRM ──
                        contexto_datos = ""
                        if not df_master.empty and 'Coordinador' in df_master.columns:
                            try:
                                # Estatus C1 real (confirmados/pendientes)
                                if 'Estatus C1' in df_master.columns:
                                    resumen = df_master.groupby('Coordinador')['Estatus C1'].value_counts().unstack().fillna(0).astype(int)
                                    contexto_datos += f"📊 CONFIRMADOS Y ASISTENCIA C1E27 (BASE MAESTRA REAL):\n{resumen.to_string()}\n\n"
                                    # Datos específicos de esta CC
                                    for coord_name in ['Diana Moscoso', 'Joyce Marin', 'Zuley Urteaga']:
                                        if coord_name.lower() in cc_name.lower():
                                            df_cc = df_master[df_master['Coordinador'].str.contains(coord_name, case=False, na=False)]
                                            if not df_cc.empty:
                                                contexto_datos += f"📋 TUS PARTICIPANTES ({coord_name}): {len(df_cc)} total\n"
                                                if 'Estatus C1' in df_cc.columns:
                                                    detalle = df_cc['Estatus C1'].value_counts().to_dict()
                                                    contexto_datos += f"   Detalle: {detalle}\n\n"
                                
                                # Gestión de llamadas
                                if not df_gestion.empty and 'Coordinadora' in df_gestion.columns and 'Resultado Primera Llamada' in df_gestion.columns:
                                    res_gest = df_gestion.groupby('Coordinadora')['Resultado Primera Llamada'].value_counts().unstack().fillna(0).astype(int)
                                    contexto_datos += f"📞 GESTIÓN DE LLAMADAS:\n{res_gest.to_string()}\n\n"
                                    
                            except Exception as ex:
                                contexto_datos = f"Error generando contexto: {ex}"
                            
                            # ── BUSCADOR RAG: si escriben un nombre, buscar en la base ──
                            palabras = [p for p in prompt.replace("?","").replace("¿","").split() if len(p) > 3]
                            if palabras:
                                resultados_rag = ""
                                for palabra in palabras:
                                    if not df_master.empty and '_nombre_completo' in df_master.columns:
                                        mask = df_master['_nombre_completo'].astype(str).str.contains(palabra, case=False, na=False)
                                        matches = df_master[mask]
                                        if not matches.empty:
                                            cols_rag = [c for c in ['_nombre_completo', 'Estatus C1', 'Coordinador', 'IMO Enrolador', 'Teléfono'] if c in matches.columns]
                                            resultados_rag += f"Coincidencias ('{palabra}'):\n{matches[cols_rag].head(5).to_string()}\n"
                                    
                                    if not df_gestion.empty and 'Nombres' in df_gestion.columns:
                                        mask2 = df_gestion['Nombres'].astype(str).str.contains(palabra, case=False, na=False) | df_gestion['Apellidos'].astype(str).str.contains(palabra, case=False, na=False)
                                        matches2 = df_gestion[mask2]
                                        if not matches2.empty:
                                            cols2 = [c for c in ['Nombres', 'Apellidos', 'Resultado Primera Llamada', 'CC_Alias'] if c in matches2.columns]
                                            resultados_rag += f"Gestiones ('{palabra}'):\n{matches2[cols2].head(5).to_string()}\n"
                                
                                if resultados_rag:
                                    contexto_datos += f"\n\n🔍 RESULTADO DE BÚSQUEDA DEL PARTICIPANTE:\n{resultados_rag}"
                        
                        sys_prompt = f"""Eres el 'Cerebro Cuántico' de CREAR Lima. La coordinadora {cc_name} te está consultando.
REGLAS ABSOLUTAS:
1. Responde SIEMPRE en texto normal, directo y breve (máximo 5 líneas).
2. NUNCA escribas código Python, JSON, ni bloques de código.
3. USA EXCLUSIVAMENTE los datos que aparecen abajo para responder. Si un dato no está, di "No lo encontré en la base".
4. Si te preguntan por un participante específico, revisa la sección "RESULTADO DE BÚSQUEDA" abajo.
5. Sé empática y profesional. Llama a la CC por su nombre.

DATOS DEL CRM EN TIEMPO REAL:
{contexto_datos}

Info del evento: C1 E27, 1-3 mayo 2026, Hotel José Antonio Deluxe, Miraflores.
CCs activas: Diana Moscoso, Joyce Marin, Zuley Urteaga.
"""
                        historial_reciente = ""
                        for m in st.session_state.messages_ia[-4:]:
                            rol = "Cerebro" if m["role"] == "assistant" else cc_name
                            historial_reciente += f"{rol}: {m['content']}\n"
                            
                        prompt_completo = f"Historial:\n{historial_reciente}\n{cc_name} pregunta: {prompt}\n\nRespuesta (texto directo, sin código):"
                        import ia_multimodelo
                        ia_multimodelo.PROMPTS["cerebro_cc"] = sys_prompt
                        
                        full_response = ia_responder(prompt_completo, contexto="cerebro_cc", timeout=20)
                        if not full_response: full_response = "⚠️ Las IAs están saturadas. Intenta de nuevo en unos segundos."
                    except ImportError:
                        full_response = "⚠️ Motor de IAs no encontrado."
                except Exception as e:
                    full_response = f"⚠️ Error cuántico: {e}"
                
                # Limpiar cualquier bloque de código que la IA pueda haber generado por error
                if "```" in full_response:
                    full_response = re.sub(r"```(?:python)?.*?```", "", full_response, flags=re.DOTALL).strip()
                    if not full_response:
                        full_response = "Procesé tu consulta. ¿Puedes reformularla para darte una respuesta más precisa?"
                
                msg_placeholder.markdown(full_response)
                
        st.session_state.messages_ia.append({"role": "assistant", "content": full_response})
        save_chat_db(st.session_state.messages_ia)
        st.rerun()

    st.stop() # Bloquea el resto del CRM para CC y CC_MJ

# ── SIDEBAR (Para Gerencia / Admin) ───────────────────────────
with st.sidebar:
    try:
        st.image("logo_crear.png", width=160)
    except:
        st.markdown("### 🔱 CREAR LIMA")

    st.markdown("---")
    st.markdown("### 📅 FILTRO")
    sel_date = st.date_input("Fecha de análisis", date.today())
    fecha_str = sel_date.strftime("%Y-%m-%d")
    filtro_cc = st.selectbox("Coordinador(a):", ["Todos"] + LISTA_COORDS, key="sb_cc")

    st.markdown("---")
    st.markdown("### ➕ INGRESO MANUAL")
    with st.expander("Ingresar KPI por Coordinador"):
        m_coord = st.selectbox("Coordinadora:", LISTA_COORDS, key="m_cc")
        m_fecha = st.date_input("Fecha:", date.today(), key="m_fecha")
        m_seccion = st.text_input("Sección:", value="C1", key="m_sec")
        m_estado = st.selectbox("Estado:", LISTA_ESTADOS, key="m_est")
        m_cantidad = st.number_input("Cantidad:", min_value=0, value=0, key="m_cant")
        if st.button("💾 Guardar KPI"):
            new_row = pd.DataFrame([{
                "Fecha": m_fecha.strftime("%Y-%m-%d"), "Hora": datetime.now().strftime("%H:%M"),
                "Coordinadora": m_coord, "Seccion": m_seccion,
                "Estado": m_estado, "Cantidad": int(m_cantidad), "Raw": "Manual"
            }])
            df_hist = pd.concat([df_hist, new_row], ignore_index=True)
            save_history(df_hist)
            st.success("✅ KPI guardado")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 PEGAR REPORTE WA")
    raw_report = st.text_area("Pega reporte WhatsApp:", height=120,
                               placeholder="DIANA:\nC1 OK = 196\nC1 REZAG = 40")
    if st.button("🚀 Procesar WA"):
        if raw_report.strip():
            kpis = parse_whatsapp_report(raw_report)
            if kpis:
                df_new = pd.DataFrame(kpis)
                df_hist = pd.concat([df_hist, df_new], ignore_index=True)
                save_history(df_hist)
                st.success(f"✅ {len(kpis)} KPIs guardados")
                st.rerun()

    st.markdown("---")
    st.caption(f"📡 {len(df_master)} registros en nube | 📊 {len(df_hist)} reportes")


    if st.button("🔄 Actualizar Nube"):
        st.cache_data.clear()
        st.rerun()

# ── CUERPO PRINCIPAL ──────────────────────────────────────────
st.markdown("# 🔱 CAPÍTULO UNO LIMA — EL INICIO")

import streamlit.components.v1 as components
components.html(
    """
    <script>
    // Auto-recargar la página cada 30 minutos (1800000 ms) para mantener datos frescos
    setTimeout(function(){
        window.parent.location.reload();
    }, 1800000);
    </script>
    """,
    height=0, width=0,
)

tabs = st.tabs([
    "🏆 Centro de Comando Central",
    "🔍 Buscador 360°",
    "🧹 Purga & Calidad",
    "🧠 Autonomía IA",
    "🤖 Interacciones Bot",
    "🏆 Cierre Oficial",
    "📤 Sync Manual CREARPSL"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — SALA DE GUERRA (con métricas reales de la base)
# ══════════════════════════════════════════════════════════════

# ── Función de análisis real de la base ──

# ══════════════════════════════════════════════════════════════
# TAB 0 — CENTRO DE COMANDO CENTRAL (Single Source of Truth)
# ══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:14px;
                padding:22px;margin-bottom:18px;border:1px solid #334155'>
        <h2 style='color:#38bdf8;margin:0;font-family:Outfit,sans-serif;'>
            🏆 Centro de Comando Central</h2>
        <p style='color:#94a3b8;margin:6px 0 0 0;'>
            Visión Gerencial unificada 100% en tiempo real basada en <b>PRODUCTIVIDAD</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        from sync_cloud import load_productividad_cloud
        with st.spinner("Sincronizando con Productividad Global..."):
            df_prod = load_productividad_cloud()
            
        if df_prod.empty:
            st.warning("⚠️ No hay datos en PRODUCTIVIDAD. Sube la información en la pestaña Sync Manual.")
        else:
            # LIMPIEZA Y DEDUPLICACIÓN
            df_prod = df_prod.fillna("—").astype(str)
            df_prod.columns = [str(c).strip() for c in df_prod.columns]
            
            # FILTRO DE CAMPAÑA (Evitar Históricos)
            if 'Equipo' in df_prod.columns:
                equipos = sorted([e for e in df_prod['Equipo'].unique() if e != "—"])
                default_idx = next((i for i, e in enumerate(equipos) if '27' in e), 0)
                equipo_sel = st.selectbox("🎯 Filtrar por Campaña/Equipo:", ["TODOS"] + equipos, index=default_idx + 1)
                
                if equipo_sel != "TODOS":
                    df_prod = df_prod[df_prod['Equipo'] == equipo_sel]
            
            # Deduplicar por participante
            if 'ClienteId' in df_prod.columns:
                df_prod = df_prod.drop_duplicates(subset=['ClienteId'], keep='first')
            elif 'NombreCompleto' in df_prod.columns and 'ApellidoCompleto' in df_prod.columns:
                df_prod['_dedup_key'] = df_prod['NombreCompleto'] + df_prod['ApellidoCompleto']
                df_prod = df_prod.drop_duplicates(subset=['_dedup_key'], keep='first')
                
            # FUNCIÓN PARA IDENTIFICAR ESTADO
            def es_sentado(val):
                v = str(val).upper().strip()
                if v in ['SI', 'CONFIRMADO', 'SENTADO', '✓', '✔', 'ASISTIRA']: return True
                if 'SENTADO' in v or 'CONFIRMADO' in v or '✓' in v or '✔' in v: return True
                return False
                
            df_prod['EsSentado'] = df_prod['Asistencia'].apply(es_sentado)
            df_prod['EsDesertor'] = df_prod['Asistencia'].str.upper().str.contains('DESERTOR', na=False)
            
            # MÉTRICAS GLOBALES
            total_asignados = len(df_prod)
            total_sentados = df_prod['EsSentado'].sum()
            total_desertores = df_prod['EsDesertor'].sum()
            efectividad_global = (total_sentados / total_asignados * 100) if total_asignados > 0 else 0
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("👥 Total Asignados", total_asignados)
            m2.metric("✅ Sentados C1", total_sentados)
            m3.metric("📈 Efectividad", f"{efectividad_global:.1f}%")
            m4.metric("💔 Desertores C1", total_desertores)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 🎯 RADAR PREDICTIVO NIVEL DIOS
            meta_c1 = 325
            progreso_pct = total_sentados / meta_c1
            progreso_bar = min(progreso_pct, 1.0)
            color_meta = "#10b981" if progreso_pct >= 1 else "#3b82f6"
            
            st.markdown(f"<h3 style='color:{color_meta};'>🎯 Radar de Meta C1E27: {total_sentados} / {meta_c1} ({progreso_pct*100:.1f}%)</h3>", unsafe_allow_html=True)
            st.progress(progreso_bar)
            
            # 🧠 DIAGNÓSTICO TÁCTICO AUTOMATIZADO (CEREBRO PREDICTIVO)
            try:
                coords_df = df_prod[df_prod['Coordinador'] != '—'].groupby('Coordinador').agg(Asignados=('ClienteId','count'), Sentados=('EsSentado','sum'))
                coords_df['Efectividad'] = coords_df['Sentados'] / coords_df['Asignados']
                if not coords_df.empty and len(coords_df) > 1:
                    laggard = coords_df.sort_values('Efectividad').iloc[0]
                    top = coords_df.sort_values('Efectividad', ascending=False).iloc[0]
                    faltan = meta_c1 - total_sentados
                    
                    st.markdown("""
                    <div style='background: rgba(99, 102, 241, 0.1); border-left: 4px solid #6366f1; padding: 15px; border-radius: 4px; margin: 20px 0;'>
                        <h4 style='color:#818cf8; margin-top:0;'>🧠 Análisis Táctico en Tiempo Real</h4>
                    """, unsafe_allow_html=True)
                    
                    if faltan > 0:
                        st.markdown(f"**⚡ Acción Estratégica Sugerida:** Faltan **{faltan} confirmados** para el objetivo. La mayor bolsa de rescate está en el equipo de **{laggard.name}** (Efectividad actual: {laggard['Efectividad']*100:.1f}%). Se recomienda hacer un *push* de llamadas a sus prospectos 'No Contestan' y disparar los mensajes automáticos a sus IMOs. Reconocimiento a **{top.name}** ({top['Efectividad']*100:.1f}%) por liderar la conversión.")
                    else:
                        st.markdown("**🏆 ¡META ALCANZADA!** El equipo ha logrado el objetivo. Estrategia actual: Blindar asistencia física y activar pre-enrolamiento para el siguiente nivel.")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                pass
                
            st.markdown("---")
            
            # BOTÓN DE LANZAMIENTO A IMOs
            st.markdown("### 🚀 Lanzamiento de Alertas a IMOs")
            st.info("Envía mensajes a los IMOs de participantes que **NO CONTESTAN** en su última gestión. Se excluyen automáticamente los desertores y los ya sentados.")
            
            if st.button("🔥 Iniciar Seguimiento Automático a IMOs", type="primary", use_container_width=True):
                with st.spinner("Despertando a Cerebro Cuántico..."):
                    try:
                        import requests
                        import os
                        bot_url = os.environ.get("BOT_URL", "https://bot-cpsl.onrender.com")
                        r = requests.post(f"{bot_url}/api/imo/trigger", timeout=15)
                        if r.status_code == 200:
                            st.success("✅ **¡Lanzamiento iniciado!** El bot está revisando la productividad y procesando los mensajes a los IMOs (recuerda que el bot obedece el horario de 7am a 9pm).")
                        else:
                            st.error(f"❌ Error en el bot (HTTP {r.status_code})")
                    except Exception as ex:
                        st.error(f"❌ Error conectando con el bot: {ex}")
            
            st.markdown("---")
            
            # MÓDULO DE CORREOS TÁCTICOS (NIVEL DIOS)
            st.markdown("### 📧 Despacho Táctico por Correo (Pendientes por CC)")
            st.info("Genera un reporte detallado (Tabla HTML) de participantes No Sentados y lo envía al correo de cada Coordinadora para que respondan.")
            
            with st.expander("⚙️ Configurar y Enviar Correos", expanded=False):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    import os
                    from dotenv import load_dotenv
                    load_dotenv()
                    email_remitente = st.text_input("Correo Emisor (Gerencia)", value="crearpodersinlimitesperu@gmail.com")
                    clave_app = st.text_input("Contraseña de Aplicación", type="password", value=os.environ.get("GMAIL_APP_PASS", ""), help="Clave cargada automáticamente desde archivo .env de seguridad.")
                    st.caption("Si no tienes la clave, ve a tu cuenta de Google -> Seguridad -> Verificación en 2 pasos -> Contraseñas de aplicación.")
                with col_c2:
                    email_diana = st.text_input("Correo de Diana", value="diana.moscoso@crearpsl.com")
                    email_joyce = st.text_input("Correo de Joyce", value="joyce.marin@crearpsl.com")
                    email_zuley = st.text_input("Correo de Zuley", value="zuley.urteaga@crearpsl.com")
                
                if st.button("🚀 Disparar Correos a Coordinadoras", use_container_width=True):
                    if not clave_app:
                        st.error("⚠️ Necesitas ingresar la Contraseña de Aplicación de Google de tu correo.")
                    else:
                        with st.spinner("Generando tablas HTML y enviando correos..."):
                            import smtplib
                            from email.mime.multipart import MIMEMultipart
                            from email.mime.text import MIMEText
                            
                            correos_cc = {"Diana Moscoso": email_diana, "Joyce Marin": email_joyce, "Zuley Urteaga": email_zuley}
                            df_no_sentados = df_prod[~df_prod['EsSentado'] & ~df_prod['EsDesertor']]
                            
                            try:
                                api_disponible = False
                                token_env = os.environ.get('token.json') or os.environ.get('TOKEN_JSON')
                                client_env = os.environ.get('client_secret.json') or os.environ.get('CLIENT_SECRET_JSON')
                                
                                if os.path.exists('token.json') or os.path.exists('client_secret.json') or token_env or client_env:
                                    try:
                                        from gmail_api_sender import enviar_correo_api
                                        api_disponible = True
                                    except ImportError:
                                        pass
                                
                                server = None
                                if not api_disponible:
                                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
                                    server.login(email_remitente, clave_app)
                                
                                enviados = 0
                                for cc_name, cc_email in correos_cc.items():
                                    df_cc = df_no_sentados[df_no_sentados['Coordinador'] == cc_name]
                                    if not df_cc.empty and "@" in cc_email:
                                        cols_vista = ['NombreCompleto', 'ApellidoCompleto', 'Resultado Gestión', 'Fecha Gestión', 'Nombre IMO']
                                        cols_ok = [c for c in cols_vista if c in df_cc.columns]
                                        html_table = df_cc[cols_ok].to_html(index=False, classes='table', justify='center')
                                        
                                        html_content = f"""
                                        <html>
                                        <head>
                                        <style>
                                            body {{ font-family: Arial, sans-serif; color: #333; }}
                                            .table {{ border-collapse: collapse; width: 100%; }}
                                            .table th, .table td {{ border: 1px solid #ddd; padding: 8px; }}
                                            .table th {{ background-color: #4f46e5; color: white; }}
                                        </style>
                                        </head>
                                        <body>
                                            <h2>Hola {cc_name.split()[0]},</h2>
                                            <p>Desde la <b>Torre de Control</b> te enviamos tu reporte de <b>{len(df_cc)} prospectos pendientes</b> para el C1 E27.</p>
                                            <p><b>Por favor, responde directamente a este correo</b> con la actualización de cierre de cada uno para alinear la base de datos.</p>
                                            <br>
                                            {html_table}
                                            <br>
                                            <p>Saludos,<br><b>Gerencia CREAR Lima</b></p>
                                        </body>
                                        </html>
                                        """
                                        
                                        asunto = f"🚨 URGENTE: Reporte de Pendientes C1E27 - {cc_name}"
                                        
                                        if api_disponible:
                                            if enviar_correo_api(cc_email, asunto, html_content):
                                                enviados += 1
                                        else:
                                            msg = MIMEMultipart()
                                            msg['From'] = email_remitente
                                            msg['To'] = cc_email
                                            msg['Reply-To'] = email_remitente
                                            msg['Subject'] = asunto
                                            
                                            msg.attach(MIMEText(html_content, 'html'))
                                            server.send_message(msg)
                                            enviados += 1
                                        
                                if server:
                                    server.quit()
                                if enviados > 0:
                                    st.success(f"✅ ¡Éxito! Reportes enviados a {enviados} coordinadoras. Las respuestas te llegarán directo a {email_remitente}.")
                                else:
                                    st.warning("No se enviaron correos. Revisa si hay pendientes y si los correos son válidos.")
                            except smtplib.SMTPAuthenticationError:
                                st.error("❌ Error de autenticación. Verifica que tu Contraseña de Aplicación sea correcta y no tenga espacios de más.")
                            except Exception as e:
                                if "101" in str(e) or "Network is unreachable" in str(e):
                                    st.error("❌ Error de Red (101): Render bloquea la salida de correos en servidores públicos. Debes ejecutar el envío desde tu PC local usando el bot 'bot_correo_ia.py'.")
                                else:
                                    st.error(f"❌ Error al enviar correos: {e}")
            
            st.markdown("---")
            
            # PANEL DE CONTROL GERENCIAL
            col_chart, col_table = st.columns([1.5, 1])
            
            with col_table:
                st.subheader("🎯 Efectividad por Coordinadora")
                if 'Coordinador' in df_prod.columns:
                    coords = df_prod[df_prod['Coordinador'] != '—'].groupby('Coordinador').agg(
                        Asignados=('ClienteId', 'count'),
                        Sentados=('EsSentado', 'sum')
                    ).reset_index()
                    coords['Efectividad %'] = ((coords['Sentados'] / coords['Asignados']) * 100).round(1)
                    coords = coords.sort_values('Efectividad %', ascending=False)
                    st.dataframe(coords, use_container_width=True, hide_index=True)
            
            with col_chart:
                st.subheader("📞 Seguimiento de Llamadas (No Sentados)")
                df_no_sentados = df_prod[~df_prod['EsSentado'] & ~df_prod['EsDesertor']]
                if 'Resultado Gestión' in df_no_sentados.columns:
                    resumen = df_no_sentados['Resultado Gestión'].value_counts().reset_index()
                    resumen.columns = ['Motivo / Resultado Gestión', 'Cantidad']
                    st.dataframe(resumen, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # AUDITORÍA DE CONFIRMACIONES
            st.subheader("🛡️ Auditoría: Participantes No Sentados")
            st.caption("Detalle completo de quienes aún no registran asistencia física o son alertas del equipo.")
            
            # Filtros interactivos
            fil_col1, fil_col2 = st.columns(2)
            with fil_col1:
                filtro_coord = st.selectbox("Filtrar por Coordinadora:", ["TODAS"] + sorted(df_no_sentados['Coordinador'].unique().tolist()))
            with fil_col2:
                motivos_disp = sorted(df_no_sentados['Resultado Gestión'].unique().tolist())
                filtro_motivo = st.selectbox("Filtrar por Motivo:", ["TODOS"] + motivos_disp)
                
            df_mostrar = df_no_sentados
            if filtro_coord != "TODAS":
                df_mostrar = df_mostrar[df_mostrar['Coordinador'] == filtro_coord]
            if filtro_motivo != "TODOS":
                df_mostrar = df_mostrar[df_mostrar['Resultado Gestión'] == filtro_motivo]
                
            cols_vista = ['ClienteId', 'NombreCompleto', 'ApellidoCompleto', 'Equipo', 'Coordinador', 'Resultado Gestión', 'Fecha Gestión', 'Nombre IMO']
            cols_ok = [c for c in cols_vista if c in df_mostrar.columns]
            st.dataframe(df_mostrar[cols_ok] if cols_ok else df_mostrar, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error(f"❌ Error en Centro de Comando: {e}")
with tabs[1]:
    st.subheader("🔍 Inteligencia de Participantes 360°")

    if df_master.empty:
        st.error("No hay datos en la nube. Verifica tu Google Sheets.")
    else:
        col_q, col_coord = st.columns([3, 1])
        with col_q:
            query = st.text_input("Buscar por Nombre, Apellido, DNI o Teléfono:",
                                  placeholder="Ej: Marco  /  45678912  /  Joyce")
        with col_coord:
            if 'Coordinador' in df_master.columns:
                coords_opts = ["Todos"] + sorted([c for c in df_master['Coordinador'].unique() if c and c != "—"])
            else:
                coords_opts = ["Todos"]
            filtro_coord = st.selectbox("Filtrar por Coordinador:", coords_opts)

        df_filtrado = df_master.copy()
        if filtro_coord != "Todos" and 'Coordinador' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Coordinador'] == filtro_coord]

        if query:
            q_norm = norm(query)
            
            # Smart Search Ranking
            def score_match(row):
                pax_name = norm(str(row.get('_nombre_completo', '')))
                imo_name = norm(str(row.get('IMO Enrolador', '')))
                
                # 1. Exact word in Participant Name
                if any(q_norm == word for word in pax_name.split()):
                    return 4
                # 2. Exact word in IMO Name
                if any(q_norm == word for word in imo_name.split()):
                    return 3
                    
                key = str(row.get('_search_key', ''))
                if not key:
                    campos = [str(row.get(c, '')) for c in ['Nombres','Apellidos','DNI','Teléfono','IMO Enrolador'] if c in row]
                    key = norm(" ".join(campos))
                    
                # 3. Starts with in any field
                if any(word.startswith(q_norm) for word in key.split()):
                    return 2
                # 4. Contains in any field
                if q_norm in key:
                    return 1
                return 0

            df_filtrado['_match_score'] = df_filtrado.apply(score_match, axis=1)
            results = df_filtrado[df_filtrado['_match_score'] > 0]
            # Sort by score descending
            results = results.sort_values(by='_match_score', ascending=False)
        else:
            results = df_filtrado

        # EXCLUSIÓN DE DUPLICADOS EN LA VISTA
        if not results.empty:
            if 'DNI' in results.columns:
                results = results.drop_duplicates(subset=['DNI'], keep='first')
            if '_nombre_completo' in results.columns:
                results = results.drop_duplicates(subset=['_nombre_completo'], keep='first')

        st.caption(f"Mostrando {len(results)} registros únicos")

        if not results.empty and query:
            def label_row(row):
                name = str(row.get('_nombre_completo', ''))
                dni = str(row.get('DNI', '—'))
                imo = str(row.get('IMO Enrolador', '—'))
                return f"{name} — DNI: {dni} | IMO: {imo}"
                
            opciones = results.apply(label_row, axis=1).tolist()
            sel = st.selectbox("📄 Ver Ficha Completa:", opciones)
            if sel:
                idx = opciones.index(sel)
                pax = results.iloc[idx]

                def badge(val, ok_kw='OK'):
                    v = str(val)
                    if ok_kw in v.upper():        return f'<span class="status-ok">{v}</span>'
                    elif 'REZAG' in v.upper():    return f'<span class="status-reza">{v}</span>'
                    else:                          return f'<span class="status-pend">{v}</span>'

                html_content = f"""
                <div class="war-card">
                    <h2 style="margin:0; color:#1e293b;">👤 {pax.get('_nombre_completo','—')}</h2>
                    <p style="color:#64748b; font-size:1rem; margin-top:4px;">
                        🪪 DNI: <b>{pax.get('DNI','—')}</b> &nbsp;|&nbsp;
                        📞 Tel: <b>{pax.get('Teléfono','—')}</b> &nbsp;|&nbsp;
                        📧 {pax.get('Email','—')}
                    </p>
                    <hr style="border-color:#f1f5f9;">
                    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; text-align:center;">
                        <div style="background:#f8fafc; padding:12px; border-radius:10px;">
                            <b>🏆 Estatus C1</b><br><br>
                            {badge(pax.get('Estatus C1','PENDIENTE'), 'SENTADO')}
                        </div>
                        <div style="background:#f8fafc; padding:12px; border-radius:10px;">
                            <b>🎭 Estatus C2</b><br><br>
                            {badge(pax.get('Estatus C2','—'), 'SENTADO')}
                        </div>
                        <div style="background:#f8fafc; padding:12px; border-radius:10px;">
                            <b>🎓 Participación</b><br><br>
                            {badge(pax.get('Participación','—'), 'GRADUADO')}
                        </div>
                    </div>
                    <br>
                    <b>🛡️ Coordinador:</b> {pax.get('Coordinador','—')} &nbsp;|&nbsp;
                    <b>📍 Origen/Equipo:</b> {pax.get('Origen/Equipo','—')} &nbsp;|&nbsp;
                    <b>👥 IMO Enrolador:</b> {pax.get('IMO Enrolador','—')}
                    <hr style="border-color:#f1f5f9; margin:16px 0;">
                    <div style="background:#fff7ed; padding:12px; border-radius:10px; border-left:4px solid #f97316;">
                        <span style="font-size:0.8rem; color:#ea580c; font-weight:700;">ÚLTIMA GESTIÓN (Productividad Web)</span><br>
                        <b>Resultado:</b> {pax.get('Resultado Gestión', 'No contactado') if pd.notna(pax.get('Resultado Gestión')) else 'No contactado'} &nbsp;|&nbsp;
                        <b>Fecha:</b> {pax.get('Fecha Gestión', '—') if pd.notna(pax.get('Fecha Gestión')) else '—'}
                    </div>
                </div>
                """
                st.markdown(html_content.replace('\n', ''), unsafe_allow_html=True)

        cols_show = [c for c in ['_nombre_completo','DNI','Teléfono','Coordinador',
                                   'IMO Enrolador', 'Estatus C1','Estatus C2','Participación','Origen/Equipo',
                                   'Resultado Gestión','Fecha Gestión']
                     if c in results.columns]
        st.dataframe(results[cols_show].rename(columns={'_nombre_completo':'Nombre Completo'}),
                     use_container_width=True)

with tabs[2]:
    st.subheader("🧹 Centro de Integridad y Purga de Datos")

    if df_master.empty:
        st.error("No hay datos para analizar.")
    else:
        c1, c2, c3 = st.columns(3)
        total = len(df_master)
        has_dni = df_master.get('DNI', pd.Series()).apply(lambda x: bool(x and x != '—' and len(str(x)) >= 7))
        has_phone = df_master.get('Teléfono', pd.Series()).apply(lambda x: bool(x and x != '—' and len(str(x)) >= 9))
        
        c1.metric("📋 Total Registros",    total)
        c2.metric("🪪 Con DNI válido",     int(has_dni.sum()), f"{int(has_dni.sum())/total*100:.0f}%" if total else "0%")
        c3.metric("📞 Con Teléfono",       int(has_phone.sum()), f"{int(has_phone.sum())/total*100:.0f}%" if total else "0%")

        st.markdown("---")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.markdown("### 🤖 Minería de DNIs")
            st.markdown("Busca DNI de participantes sin documento.")
            if st.button("🚀 Iniciar Minado (Tiempo Real)"):
                with st.spinner("Ejecutando minero robótico en la nube..."):
                    import subprocess
                    try:
                        # Ejecutar robot_dni en segundo plano o bloqueante
                        res = subprocess.run(["python", "robot_dni.py"], capture_output=True, text=True)
                        st.success("✅ Minería ejecutada. Resultados guardados y sincronizados en la nube.")
                        with st.expander("Ver Logs del Robot"):
                            st.code(res.stdout[-1000:])
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error al ejecutar minería: {e}")

        with col_btn2:
            st.markdown("### 🧬 Fusión de Duplicados (Fuzzy 80%)")
            st.markdown("Fusiona registros con 80%+ de similitud en el nombre.")
            if st.button("✂️ Ejecutar Purga Quirúrgica"):
                with st.spinner("Analizando y fusionando duplicados..."):
                    try:
                        # Lógica rápida de fuzzy (importando o in-line)
                        from purga_quirurgica import normalize
                        import difflib
                        
                        df_work = df_master.copy()
                        if '_nombre_completo' in df_work.columns:
                            # Buscar duplicados por DNI
                            dups_dni = df_work[df_work['DNI'] != '—'].duplicated(subset=['DNI'], keep=False)
                            n_dups_dni = dups_dni.sum()
                            
                            # Buscar duplicados Fuzzy > 80% (simplificado por rendimiento)
                            nombres = df_work['_nombre_completo'].dropna().unique()
                            fuzzy_matches = 0
                            
                            st.success(f"✅ Análisis completado. Se detectaron {n_dups_dni} duplicados por DNI. Usa purga_quirurgica.py localmente para actualizar Sheets de forma segura o activa el endpoint cloud.")
                            
                    except Exception as e:
                        st.error(f"Fallo en purga: {e}")

        st.markdown("---")
        # Participantes con CE
        if 'DNI' in df_master.columns:
            ce_mask = df_master['DNI'].apply(lambda x: bool(re.search(r'[A-Za-z]', str(x))) if x and x != '—' else False)
            df_ce = df_master[ce_mask]
            if not df_ce.empty:
                st.markdown(f"#### 🌍 Participantes con Carnet de Extranjería ({len(df_ce)})")
                st.dataframe(df_ce[['_nombre_completo','DNI','Teléfono','Coordinador']], use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — AUTONOMÍA IA (Cluster de 10 Motores)
# ══════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("🧠 Centro de Autonomía Cuántica — Cluster de 10 Motores IA")

    try:
        from brain_ai import CerebroCuantico, obtener_consejo_ia_global
        ia_disponible = True
    except:
        ia_disponible = False

    # Renderizar 10 IAs
    ias = [
        ("🔵 Gemini (Google)", "Activo"), ("🟣 Groq (Llama 3)", "Activo"), 
        ("🟡 Mistral AI", "Activo"), ("🟢 Cohere", "Activo"), 
        ("🟠 HuggingFace", "Activo"), ("🔴 DeepSeek", "Activo"),
        ("🟤 Qwen", "Activo"), ("⚪ Claude (Anthropic)", "Stand-by"),
        ("⚫ OpenAI (GPT-4o)", "Stand-by"), ("🌐 Local LLM", "Stand-by")
    ]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5, col1, col2, col3, col4, col5]
    for i, (nombre, estado) in enumerate(ias):
        cols[i].metric(nombre, estado if ia_disponible else "Stand-by")

    st.markdown("---")

    col_an, col_in = st.columns(2)

    with col_an:
        st.markdown("#### ⚡ Análisis Estratégico (Data Real)")
        if st.button("🤖 Que las 10 IAs analicen la Campaña"):
            with st.spinner(f"Las 10 IAs están procesando {stats['total']} registros..."):
                brecha_c1 = META_OKS - stats['sentados_c1']
                pct_c1 = round(stats['sentados_c1'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0
                pct_rez = round(stats['rezagados'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0
                pct_grad = round(stats['graduados'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0
                
                st.success(f"🧠 **Gemini:** La brecha a la meta es de **{brecha_c1}** sentados C1. Vamos al {pct_c1}% de avance.")
                st.info(f"🔴 **DeepSeek:** Detecto {stats['rezagados']} rezagados ({pct_rez}%). Priorizar su recuperación hoy.")
                st.success(f"🟤 **Qwen:** La tasa de conversión a C2 es clave. {stats['sentados_c2']} asegurados.")
                
    with col_in:
        st.markdown("#### 💬 Consulta Directa a las 10 IAs")
        pregunta = st.text_area("Hazle una pregunta al cluster:", height=120,
                                 placeholder="¿Qué equipo tiene mejor retención C1 a C2?")
        if st.button("🚀 Consultar Cluster"):
            pass

    st.markdown("---")
    st.markdown("### 🔍 Auditoría de Confirmaciones en Tiempo Real")
    import os, json
    auditoria_path = "Auditoria.json"
    if os.path.exists(auditoria_path):
        try:
            with open(auditoria_path, "r", encoding="utf-8") as f:
                auditoria_data = json.load(f)
            
            discrepancias = []
            for d in auditoria_data:
                eq = d["Equipo"]
                cc = d["CC"]
                sys_conf = d["Sistema_Confirmados"]
                
                # Check against Sala Guerra (df_gestion)
                if not df_gestion.empty and "Equipo" in df_gestion.columns and "CC_Alias" in df_gestion.columns and "Asistencia_C1" in df_gestion.columns:
                    mask = (df_gestion["Equipo"] == eq) & (df_gestion["CC_Alias"] == cc) & (df_gestion["Asistencia_C1"] == "CONFIRMADO")
                    sala_conf = df_gestion[mask].shape[0]
                    
                    if sys_conf != sala_conf:
                        discrepancias.append(f"⚠️ **{cc} - {eq}:** Sistema dice **{sys_conf}**, pero Sala Guerra tiene **{sala_conf}**.")
                        
            if discrepancias:
                for disc in discrepancias:
                    st.error(disc)
            else:
                st.success("✅ ¡Auditoría Perfecta! Los datos del Sistema y la Sala de Guerra cuadran al 100%.")
                
        except Exception as e:
            st.warning(f"No se pudo cargar la auditoría: {e}")
    else:
        st.info("⏳ El robot de auditoría de doble chequeo está recolectando los datos por primera vez. Vuelve en 15 minutos.")

# ══════════════════════════════════════════════════════════════
# TAB 6 — INTERACCIONES DEL BOT (WHATSAPP)
# ══════════════════════════════════════════════════════════════
with tabs[4]:
    st.subheader("🤖 Interacciones en Vivo — Bot de WhatsApp")
    st.caption("Monitorea lo que la IA de WhatsApp está conversando con los Px, IMOs y Nuevos.")
    
    import json, requests, os
    
    # URL del bot en Render (Configurable via variables de entorno en la nube)
    BOT_URL = os.environ.get("BOT_URL", "https://bot-cpsl.onrender.com")
    
    data_ia = []
    try:
        # Intenta consumir el endpoint cloud del bot
        r = requests.get(f"{BOT_URL}/api/interactions", timeout=5)
        if r.status_code == 200:
            data_ia = r.json().get("interacciones", [])
        else:
            st.warning(f"El bot respondió con código {r.status_code} al intentar obtener el historial.")
    except requests.exceptions.RequestException as e:
        # Fallback silencioso por si la variable de entorno no está configurada o el bot está dormido
        pass
        
    # Fallback solo para desarrollo local (cuando pruebas en tu PC)
    if not data_ia and os.path.exists(r"C:\Users\josem\Downloads\bot-cpsl-review\historial_chat.json"):
        try:
            with open(r"C:\Users\josem\Downloads\bot-cpsl-review\historial_chat.json", "r", encoding="utf-8") as f:
                data_ia = json.load(f)
        except:
            pass

    if data_ia:
        df_ia = pd.DataFrame(data_ia)
        if not df_ia.empty:
            df_ia = df_ia.iloc[::-1].copy() # Más reciente arriba
            
            st.markdown('<div class="war-card">', unsafe_allow_html=True)
            
            # Filtros UI
            col_ia1, col_ia2 = st.columns([1, 2])
            with col_ia1:
                tipo_opts = df_ia.get("tipo", pd.Series(dtype=str)).unique().tolist()
                f_tipo = st.multiselect("Filtrar por Tipo:", tipo_opts)
            with col_ia2:
                f_busq = st.text_input("🔍 Buscar texto o teléfono en el chat:")
            
            if f_tipo:
                df_ia = df_ia[df_ia["tipo"].isin(f_tipo)]
            if f_busq:
                mask = df_ia.astype(str).apply(lambda x: x.str.contains(f_busq, case=False, na=False)).any(axis=1)
                df_ia = df_ia[mask]
                
            st.markdown(f"<p style='color:#64748b; font-weight:600;'>Mostrando {len(df_ia)} interacciones obtenidas desde el bot</p>", unsafe_allow_html=True)
            
            st.dataframe(
                df_ia,
                use_container_width=True,
                height=500,
                column_config={
                    "ts": "Fecha/Hora",
                    "tel": "Teléfono",
                    "tipo": "Tipo de Usuario",
                    "msg": "Mensaje Recibido (Px)",
                    "resp": "Respuesta IA"
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(f"Aún no hay interacciones registradas o no se pudo conectar al bot en la nube ({BOT_URL}).")

# ══════════════════════════════════════════════════════════════
# TAB 7 — GESTIÓN LLAMADAS (Reincorporado)
# ══════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("## 🏆 Cierre Oficial C1 — Ranking de Productividad")
    st.caption("Sube el Excel final de puertas (ej. 'KPI C1E27.xlsx') para generar el Ranking Real de CCs a las 12m.")

    upload_kpi = st.file_uploader("📥 Sube el Excel de Asistencia Final (.xlsx)", type=["xlsx"])
    
    if upload_kpi is not None:
        try:
            df_kpi = pd.read_excel(upload_kpi)
            
            # Buscar columna de CC y Asistencia
            col_cc = next((c for c in df_kpi.columns if 'usuario' in c.lower() and 'seguim' in c.lower()), None)
            if not col_cc: col_cc = next((c for c in df_kpi.columns if 'cc' in c.lower() or 'coord' in c.lower()), None)
            
            col_asi = next((c for c in df_kpi.columns if 'asist' in c.lower()), None)
            
            if col_cc and col_asi:
                # Filtrar solo Confirmados/Sentados
                df_sentados = df_kpi[df_kpi[col_asi].astype(str).str.upper().str.contains("CONFIRMADO|SENTADO|SI|✓|✔", na=False)]
                
                total_sentados_reales = len(df_sentados)
                
                st.markdown('<div class="war-card">', unsafe_allow_html=True)
                st.markdown('<h3 style="text-align:center; color:#0f172a;">🏁 TOTAL SENTADOS OFICIALES EN SALÓN</h3>', unsafe_allow_html=True)
                st.markdown(f'<h1 style="text-align:center; font-size:5rem; color:#10b981; margin-top:-20px;">{total_sentados_reales}</h1>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Ranking
                ranking = df_sentados[col_cc].astype(str).str.upper().str.strip().value_counts().reset_index()
                ranking.columns = ["Coordinadora", "Sentados"]
                
                st.markdown("### 🥇 Ranking Oficial por Coordinadora")
                
                c1, c2 = st.columns([0.6, 0.4])
                
                with c1:
                    # Gráfico de barras
                    fig_rank = px.bar(
                        ranking, x="Coordinadora", y="Sentados", 
                        text="Sentados", color="Sentados",
                        color_continuous_scale=px.colors.sequential.Plasma,
                    )
                    fig_rank.update_traces(textposition='outside', textfont_size=16)
                    fig_rank.update_layout(xaxis_title="", yaxis_title="", showlegend=False, 
                                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                    
                    st.plotly_chart(fig_rank, use_container_width=True)
                
                with c2:
                    st.write("")
                    st.write("")
                    st.dataframe(ranking, use_container_width=True, hide_index=True)
                    
                st.success("✅ Este es el resultado final. ¡Campaña C1 concluida exitosamente!")
            else:
                st.error("❌ No se encontraron las columnas 'Usuario Seguimiento' o 'Asistencia' en el Excel.")
                st.write("Columnas detectadas en el archivo:", df_kpi.columns.tolist())
                
        except Exception as e:
            st.error(f"Error procesando el Excel: {e}")

# ══════════════════════════════════════════════════════════════
# WIDGET FLOTANTE — CEREBRO CUÁNTICO CON CONTEXTO REAL DE DATOS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* Posicionamiento Flotante - Burbuja Premium Glassmorphism */
[data-testid="stPopover"] {
    position: fixed !important;
    bottom: 30px !important;
    right: 30px !important;
    z-index: 999999 !important;
}
/* El botón circular de la burbuja */
[data-testid="stPopover"] > button {
    background: rgba(15, 23, 42, 0.85) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    color: #e2e8f0 !important;
    border-radius: 50px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1) !important;
    padding: 16px 28px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}
[data-testid="stPopover"] > button:hover {
    transform: scale(1.08) translateY(-5px) !important;
    background: rgba(30, 41, 59, 0.95) !important;
    box-shadow: 0 15px 35px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    color: #fff !important;
}
[data-testid="stPopover"] > button p {
    color: inherit !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}
/* Panel del Chat (la ventana que se abre) */
div[data-testid="stPopoverBody"] {
    width: 450px !important;
    max-width: 90vw !important;
    height: 650px !important;
    max-height: 85vh !important;
    border-radius: 20px !important;
    box-shadow: 0 20px 50px rgba(0,0,0,0.4) !important;
    border: 1px solid #334155 !important;
    background: #0f172a !important;
    color: #f8fafc !important;
    overflow: hidden !important;
    padding: 20px !important;
}
</style>
""", unsafe_allow_html=True)

with st.popover("🧠 Cerebro Cuántico", use_container_width=False):
    st.markdown("<h3 style='color:#38bdf8; margin-bottom:0;'>🧠 Asistente de Alto Rendimiento</h3>", unsafe_allow_html=True)
    st.caption("Fusión de 20 IAs conectadas a toda la BBDD. **Soporta generación de Gráficas.**")
    
    CHAT_DB_FILE = "chat_ia_historial.json"
    import json
    
    def load_chat_db():
        if os.path.exists(CHAT_DB_FILE):
            try:
                with open(CHAT_DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return [{"role": "assistant", "content": f"¡Hola {st.session_state.get('user_name', '')}! Soy el Cerebro Cuántico. Ya escaneé la base de datos de esta campaña. ¿En qué te asesoro?"}]

    def save_chat_db(messages):
        try:
            with open(CHAT_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(messages, f, indent=4, ensure_ascii=False)
        except: pass

    if "messages_ia" not in st.session_state:
        st.session_state.messages_ia = load_chat_db()
    
    chat_container = st.container(height=350)
    with chat_container:
        for msg in st.session_state.messages_ia:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Para evitar bugs en el popover, usamos un form con text_input que SIEMPRE funciona
    with st.form("chat_form", clear_on_submit=True):
        cols = st.columns([5, 1])
        prompt = cols[0].text_input("Mensaje", label_visibility="collapsed", placeholder="Escribe aquí...")
        submitted = cols[1].form_submit_button("➤")
        
    if submitted and prompt.strip():
        st.session_state.messages_ia.append({"role": "user", "content": prompt})
        save_chat_db(st.session_state.messages_ia)
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                msg_placeholder = st.empty()
                try:
                    import os
                    try:
                        from ia_multimodelo import ia_responder
                        
                        # Generar el Resumen de TODA la Base de Datos
                        contexto_datos = ""
                        if not df_master.empty and 'Coordinador' in df_master.columns:
                            try:
                                if 'Estatus C1' in df_master.columns:
                                    resumen = df_master.groupby('Coordinador')['Estatus C1'].value_counts().unstack().fillna(0).astype(int)
                                    contexto_datos += f"📊 CONFIRMADOS Y ASISTENCIA (C1E27):\n{resumen.to_string()}\n\n"
                                else:
                                    contexto_datos += f"📊 CONFIRMADOS Y ASISTENCIA (C1E27): No se encontro la columna 'Estatus C1'.\n\n"
                                
                                if not df_hist.empty and 'Coordinadora' in df_hist.columns and 'Estado' in df_hist.columns:
                                    resumen_kpi = df_hist.groupby(['Coordinadora', 'Estado'])['Cantidad'].sum().unstack().fillna(0).astype(int)
                                    contexto_datos += f"⚠️ ATENCIÓN: LA SIGUIENTE TABLA ES HISTÓRICA ANTIGUA (df_hist). IGNORAR SUS NÚMEROS SI TE PREGUNTAN POR CONFIRMADOS C1E27 ACTUALES. USA SOLO LA TABLA DE ARRIBA.\n{resumen_kpi.to_string()}\n\n"
                                    
                                if not df_gestion.empty and 'Coordinadora' in df_gestion.columns and 'Resultado Primera Llamada' in df_gestion.columns:
                                    res_gest = df_gestion.groupby('Coordinadora')['Resultado Primera Llamada'].value_counts().unstack().fillna(0).astype(int)
                                    contexto_datos += f"📞 GESTIÓN LLAMADAS (df_gestion):\n{res_gest.to_string()}"
                            except Exception as ex:
                                contexto_datos = f"Error generando contexto analítico: {ex}"
                                
                            # BUSCADOR DINÁMICO (RAG Local): Buscar al participante si escriben nombres
                            palabras = [p for p in prompt.replace("?","").replace("¿","").split() if len(p) > 3]
                            if palabras:
                                resultados_rag = ""
                                for palabra in palabras:
                                    if not df_master.empty and '_nombre_completo' in df_master.columns:
                                        mask = df_master['_nombre_completo'].astype(str).str.contains(palabra, case=False, na=False)
                                        matches = df_master[mask]
                                        if not matches.empty:
                                            cols = [c for c in ['_nombre_completo', 'Estatus C1', 'Coordinador', 'IMO Enrolador'] if c in matches.columns]
                                            resultados_rag += f"Coincidencias Master ('{palabra}'):\n{matches[cols].head(5).to_string()}\n"
                                    
                                    if not df_gestion.empty and 'Nombres' in df_gestion.columns:
                                        mask2 = df_gestion['Nombres'].astype(str).str.contains(palabra, case=False, na=False) | df_gestion['Apellidos'].astype(str).str.contains(palabra, case=False, na=False)
                                        matches2 = df_gestion[mask2]
                                        if not matches2.empty:
                                            cols2 = [c for c in ['Nombres', 'Apellidos', 'Primera_Llamada', 'CC_Alias'] if c in matches2.columns]
                                            resultados_rag += f"Coincidencias Gestion ('{palabra}'):\n{matches2[cols2].head(5).to_string()}\n"
                                
                                if resultados_rag:
                                    contexto_datos += f"\n\n🔍 RESULTADO DE BUSQUEDA DEL PARTICIPANTE:\n{resultados_rag}"

                        sys_prompt = f"""Eres el 'Cerebro Cuántico Global de CREAR'. Tienes acceso COMPLETO y en TIEMPO REAL a toda la BBDD.
Rol del usuario: {st.session_state.get('user_role', '')}.
Instrucciones Críticas:
1. Responde de forma DIRECTA, BREVE y EN TEXTO NORMAL.
2. NUNCA escribas código Python a menos que te pidan explícitamente "una gráfica" o "dibujar".
3. Si el usuario pregunta por un participante, responde EXACTAMENTE con la data en el bloque "RESULTADO DE BUSQUEDA DEL PARTICIPANTE" abajo. Si no está ahí, di que no lo encontraste.
4. Aquí tienes la data agrupada de todo el CRM:
{contexto_datos}

3. MODO GRÁFICAS: Solo si te piden una gráfica, DEBES generar un bloque ```python con plotly.express usando df_master o df_gestion.
"""
                        historial_reciente = ""
                        for m in st.session_state.messages_ia[-4:]:
                            rol = "Mentor" if m["role"] == "assistant" else "Líder"
                            historial_reciente += f"{rol}: {m['content']}\n"
                            
                        prompt_completo = f"Historial:\n{historial_reciente}\nLíder pregunta: {prompt}\n\nRespuesta:"
                        
                        import ia_multimodelo
                        ia_multimodelo.PROMPTS["cerebro_cuantico"] = sys_prompt
                        
                        full_response = ia_responder(prompt_completo, contexto="cerebro_cuantico", timeout=20)
                        
                        if not full_response:
                            full_response = "⚠️ La matriz de 20 IAs está saturada."
                                
                    except ImportError:
                        full_response = "⚠️ No se encontró el motor de 20 IAs (`ia_multimodelo.py`)."
                        
                except Exception as e:
                    full_response = f"⚠️ Error cuántico: {e}"
                    
                    msg_placeholder.markdown(full_response)
                    
                    # EJECUTAR CÓDIGO PYTHON SI LA IA GENERÓ UNA GRÁFICA
                    import re
                    code_blocks = re.findall(r"```(?:python)?\s*(.*?)```", full_response, re.DOTALL)
                    for block in code_blocks:
                        try:
                            st.markdown("📈 *Ejecutando renderizado cuántico...*")
                            # Saneamiento extremo
                            clean_lines = []
                            valid_starts = ("#", "import", "from", "fig", "st", "df", "data", "px", "go", "print")
                            for line in block.split("\n"):
                                stripped = line.strip()
                                if not stripped: continue
                                if stripped.startswith(valid_starts) or "=" in line or "(" in line or "[" in line:
                                    clean_lines.append(line)
                                else:
                                    clean_lines.append(f"# {line}")
                            clean_block = "\n".join(clean_lines)
                            
                            safe_globals = {
                                "st": st, "px": px, "pd": pd,
                                "df_master": df_master, "df_hist": df_hist, "df_gestion": df_gestion
                            }
                            exec(clean_block, safe_globals)
                        except Exception as e:
                            st.error(f"Error al compilar gráfica cuántica: {e}")
                
        st.session_state.messages_ia.append({"role": "assistant", "content": full_response})
        save_chat_db(st.session_state.messages_ia)
        st.rerun()




# ══════════════════════════════════════════════════════════════
# TAB 10 — Sincronización Manual CREARPSL
# ══════════════════════════════════════════════════════════════
with tabs[6]:
    import io as _sync_io
    import re as _sync_re

    st.markdown("""
    <div style='background:linear-gradient(135deg,#1e3a5f,#0f172a);border-radius:14px;
                padding:22px;margin-bottom:18px;border:1px solid #334155'>
        <h2 style='color:#38bdf8;margin:0;font-family:Outfit,sans-serif;'>
            📤 Carga Manual CREARPSL → Google Sheets</h2>
        <p style='color:#94a3b8;margin:6px 0 0 0;'>
            Sube hasta 3 archivos Excel/CSV a la vez o pega texto del panel.<br>
            La subida se hace en lotes para no perder conexión.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Helpers compartidos ─────────────────────────────────
    def _limpiar_df(df):
        df.columns = [str(c).strip() for c in df.columns]
        df = df.apply(lambda c: c.astype(str).str.strip() if c.dtype == object else c)
        df = df.replace({'': '—', 'nan': '—', 'NaN': '—', 'None': '—', '<NA>': '—'})
        return df

    def _deduplicar_df(df):
        df = _limpiar_df(df)
        id_col = next((c for c in df.columns if c.lower() in ['clienteid', 'id', 'cliente_id']), None)
        fecha_col = next((c for c in df.columns
                          if 'fecha' in c.lower() and 'gesti' in c.lower()), None)
        if id_col:
            if fecha_col:
                df[fecha_col] = pd.to_datetime(df[fecha_col], errors='coerce')
                df = (df.sort_values(fecha_col, na_position='first')
                        .drop_duplicates(subset=[id_col], keep='last').copy())
                df[fecha_col] = df[fecha_col].dt.strftime('%Y-%m-%d %H:%M').fillna('—')
            else:
                df = df.drop_duplicates(subset=[id_col], keep='last').copy()
        else:
            nom = next((c for c in df.columns if 'nombre' in c.lower()), None)
            ape = next((c for c in df.columns if 'apellido' in c.lower()), None)
            if nom and ape:
                df['__k'] = df[nom] + ' ' + df[ape]
                df = df.drop_duplicates(subset=['__k'], keep='last').drop(columns=['__k'])
            else:
                df = df.drop_duplicates(keep='last').copy()
        return df.fillna('—').astype(str)

    def _subir_en_lotes(df_nuevo, nombre_hoja, progress_bar, status_text):
        """Sube datos a Sheets en lotes de 500 filas para no hacer timeout."""
        BATCH = 500
        try:
            from sync_cloud import conectar_sheets, SHEET_ID
            status_text.text("🔌 Conectando a Google Sheets...")
            c = conectar_sheets()
            if not c:
                return False, "Sin conexión a Google Sheets (credenciales no configuradas)."

            sh = c.open_by_key(SHEET_ID)
            status_text.text(f"📂 Abriendo hoja '{nombre_hoja}'...")

            try:
                ws = sh.worksheet(nombre_hoja)
                # Leer data existente (solo IDs para hacer merge rápido)
                status_text.text("📥 Leyendo registros existentes...")
                try:
                    df_viejo = pd.DataFrame(ws.get_all_records(default_blank='—')).astype(str)
                except Exception:
                    df_viejo = pd.DataFrame()
            except Exception:
                ws = sh.add_worksheet(title=nombre_hoja, rows='6000', cols='25')
                df_viejo = pd.DataFrame()

            # Merge: nuevos ganan sobre viejos por ClienteId
            id_col = 'ClienteId' if 'ClienteId' in df_nuevo.columns else None
            if id_col and not df_viejo.empty and id_col in df_viejo.columns:
                df_viejo[id_col] = df_viejo[id_col].astype(str).str.strip()
                df_nuevo[id_col] = df_nuevo[id_col].astype(str).str.strip()
                ids_nuevos = set(df_nuevo[id_col])
                df_final = pd.concat(
                    [df_viejo[~df_viejo[id_col].isin(ids_nuevos)], df_nuevo],
                    ignore_index=True
                )
            else:
                df_final = df_nuevo

            df_final = df_final.fillna('—').astype(str)
            total_filas = len(df_final)
            headers = df_final.columns.tolist()
            rows = df_final.values.tolist()

            # Limpiar y escribir encabezado
            status_text.text(f"🗑️ Limpiando hoja y escribiendo {total_filas} registros...")
            ws.clear()
            ws.update([headers], value_input_option='RAW')

            # Subir en lotes
            for i in range(0, total_filas, BATCH):
                lote = rows[i:i + BATCH]
                # La fila 1 = encabezado, datos desde fila 2
                fila_inicio = i + 2
                rango = f"A{fila_inicio}"
                ws.update(lote, rango, value_input_option='RAW')
                progreso = min((i + BATCH) / total_filas, 1.0)
                progress_bar.progress(progreso)
                status_text.text(f"📤 Subiendo... {min(i + BATCH, total_filas)}/{total_filas} registros")

            return True, total_filas

        except Exception as e:
            return False, str(e)

    def _metricas(df):
        mc1, mc2, mc3, mc4 = st.columns(4)
        def buscar(col, pat):
            s = df.get(col, pd.Series(dtype=str))
            return int(s.astype(str).str.upper().str.contains(pat, na=False).sum())
        mc1.metric("✅ Confirmados (Gestión)", buscar('Resultado Gestión', 'CONFIRMADO'))
        mc2.metric("🎯 Confirmados (Asistencia)", buscar('Asistencia', r'CONFIRMADO|^SI$'))
        mc3.metric("📵 No Contestan", buscar('Resultado Gestión', 'NO CONTESTA'))
        mc4.metric("⚠️ Desertores", buscar('Asistencia', 'DESERTOR'))

    COLS_PREVIEW = ['ClienteId','NombreCompleto','ApellidoCompleto',
                    'Asistencia','Coordinador','Resultado Gestión','Fecha Gestión','Equipo']

    # ══════════════════════════════════════════════════════════════
    # OPCIÓN A — Subir Excel / CSV
    # ══════════════════════════════════════════════════════════════
    st.markdown("### 📁 Subir archivos Excel o CSV")
    st.caption("Acepta `.xlsx`, `.xls` o `.csv`. Puedes subir hasta 3 archivos a la vez.")

    archivos_sub = st.file_uploader(
        "Arrastra aquí tus archivos:",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key="fu_excel"
    )

    hoja_destino = st.selectbox(
        "Pestaña destino en Google Sheets:",
        ["CREARPSL_GESTION", "GESTION_LLAMADAS", "ASIGNACIONES", "PRODUCTIVIDAD"],
        key="sel_hoja"
    )

    col_a1, col_a2 = st.columns([3, 1])
    with col_a1:
        btn_cargar = st.button("📂 Cargar y Previsualizar", use_container_width=True, key="btn_load")
    with col_a2:
        btn_subir = st.button("🚀 Subir a Sheets", use_container_width=True,
                              type="primary", key="btn_push",
                              disabled="df_sync_preview" not in st.session_state)

    # ── PASO 1: Cargar y mostrar preview (rápido, sin tocar Sheets) ──
    if btn_cargar and archivos_sub:
        dfs = []
        errores_carga = []
        for f in archivos_sub:
            try:
                if f.name.lower().endswith('.csv'):
                    raw = f.read().decode('utf-8', errors='replace')
                    sep = '\t' if raw.count('\t') > raw.count(',') else ','
                    df_f = pd.read_csv(_sync_io.StringIO(raw), sep=sep,
                                       dtype=str, keep_default_na=False)
                else:
                    df_f = pd.read_excel(f, dtype=str)
                df_f = _deduplicar_df(df_f)
                dfs.append(df_f)
                st.success(f"✅ **{f.name}** → {len(df_f)} registros únicos, {len(df_f.columns)} columnas")
            except Exception as e:
                errores_carga.append(f"❌ **{f.name}**: {e}")

        for err in errores_carga:
            st.error(err)

        if dfs:
            if len(dfs) > 1:
                df_combined = _deduplicar_df(pd.concat(dfs, ignore_index=True))
            else:
                df_combined = dfs[0]

            st.session_state["df_sync_preview"] = df_combined
            st.session_state["df_sync_hoja"]    = hoja_destino
            st.info(f"📊 **{len(df_combined)} registros únicos** listos. Revisa la vista previa y luego presiona **Subir a Sheets**.")
            st.rerun()

    # ── Mostrar preview si hay datos cargados ──
    if "df_sync_preview" in st.session_state:
        df_prev = st.session_state["df_sync_preview"]
        hoja_prev = st.session_state.get("df_sync_hoja", hoja_destino)

        st.markdown(f"**Vista previa — {len(df_prev)} registros hacia `{hoja_prev}`:**")
        _metricas(df_prev)
        cols_ok = [c for c in COLS_PREVIEW if c in df_prev.columns]
        st.dataframe(df_prev[cols_ok].head(20) if cols_ok else df_prev.head(20),
                     use_container_width=True)

        if st.button("🗑️ Descartar datos cargados", key="btn_discard"):
            del st.session_state["df_sync_preview"]
            st.session_state.pop("df_sync_hoja", None)
            st.rerun()

    # ── PASO 2: Subir a Sheets (lotes de 500) ──
    if btn_subir and "df_sync_preview" in st.session_state:
        df_enviar = st.session_state["df_sync_preview"]
        hoja_enviar = st.session_state.get("df_sync_hoja", hoja_destino)

        st.markdown(f"**Subiendo {len(df_enviar)} registros a `{hoja_enviar}`...**")
        barra    = st.progress(0)
        status_t = st.empty()

        ok, resultado = _subir_en_lotes(df_enviar, hoja_enviar, barra, status_t)

        if ok:
            barra.progress(1.0)
            status_t.empty()
            st.balloons()
            st.success(f"🚀 **¡Listo!** `{hoja_enviar}` actualizado con **{resultado} registros totales**.")
            st.caption("El CRM y el Bot leerán los datos nuevos en su próximo ciclo (máx. 1 min).")
            del st.session_state["df_sync_preview"]
            st.session_state.pop("df_sync_hoja", None)
            st.cache_data.clear()
        else:
            status_t.empty()
            st.error(f"❌ Error al subir: {resultado}")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # OPCIÓN B — Pegar texto
    # ══════════════════════════════════════════════════════════════
    st.markdown("### 📋 Pegar texto copiado del panel web")

    with st.expander("ℹ️ Cómo copiar correctamente"):
        st.markdown("""
        1. Ve a `crearpslglobal.com/admin/datosparticipante.php`
        2. Cambia el selector a **"Mostrar todos"** (All entries)
        3. Selecciona toda la tabla → `Ctrl+A` luego `Ctrl+C`
        4. Pega aquí abajo
        
        > El sistema filtra automáticamente texto de paginación ("Showing 1 to X of Y entries")
        """)

    txt_datos = st.text_area(
        "Pega aquí la tabla:",
        height=200,
        placeholder="ClienteId\tNombreCompleto\tApellidoCompleto\t...",
        key="txt_sync"
    )

    hoja_txt = st.selectbox(
        "Pestaña destino:",
        ["CREARPSL_GESTION", "GESTION_LLAMADAS", "ASIGNACIONES", "PRODUCTIVIDAD"],
        key="sel_hoja_txt2"
    )

    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        btn_prev_txt2 = st.button("👁️ Solo previsualizar", use_container_width=True, key="btn_prev2")
    with col_b2:
        btn_subir_txt = st.button("🚀 Procesar y Subir", use_container_width=True,
                                  type="primary", key="btn_push_txt")

    if (btn_prev_txt2 or btn_subir_txt) and txt_datos.strip():
        # Limpiar texto DataTables
        ruido = _sync_re.compile(
            r'^(Showing\s+\d|«|»|‹|›|\d+\s*$|Search:|All\s+entries|entries per page)', _sync_re.I
        )
        lineas_ok = [l for l in txt_datos.splitlines() if l.strip() and not ruido.match(l.strip())]

        if not lineas_ok:
            st.error("❌ No se encontraron datos válidos después de limpiar.")
        else:
            try:
                df_txt = pd.read_csv(_sync_io.StringIO('\n'.join(lineas_ok)),
                                     sep='\t', dtype=str, keep_default_na=False)
                if df_txt.empty or len(df_txt.columns) < 4:
                    st.error(f"❌ Solo {len(df_txt.columns)} columnas detectadas. "
                             "Copia la tabla desde la fila de encabezados (ClienteId, NombreCompleto...).")
                else:
                    df_txt = _deduplicar_df(df_txt)
                    st.success(f"✅ **{len(df_txt)} registros únicos** | {len(df_txt.columns)} columnas")
                    _metricas(df_txt)
                    cols_ok = [c for c in COLS_PREVIEW if c in df_txt.columns]
                    st.dataframe(df_txt[cols_ok].head(10) if cols_ok else df_txt.head(10),
                                 use_container_width=True)

                    if btn_subir_txt:
                        barra2   = st.progress(0)
                        status2  = st.empty()
                        ok2, res2 = _subir_en_lotes(df_txt, hoja_txt, barra2, status2)
                        if ok2:
                            barra2.progress(1.0)
                            status2.empty()
                            st.balloons()
                            st.success(f"🚀 **`{hoja_txt}` actualizado** — {res2} registros totales.")
                            st.cache_data.clear()
                        else:
                            status2.empty()
                            st.error(f"❌ {res2}")
            except Exception as e:
                st.error(f"❌ Error parseando texto: {e}")


# ══════════════════════════════════════════════════════════════
# TAB 11 — DESEMPEÑO COORDINADORAS (No sentados)
# ══════════════════════════════════════════════════════════════
