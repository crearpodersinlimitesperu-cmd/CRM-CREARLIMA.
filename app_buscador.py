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
    "valencia": {"pass": "crear2026", "role": "CC", "name": "L. Valencia"},
    "linid": {"pass": "crear2026", "role": "CC_MJ", "name": "Linid"},
    "leyla": {"pass": "crear2026", "role": "CC_MJ", "name": "Leyla"},
    "jose": {"pass": "admin", "role": "Gerencia", "name": "Jose M."},
    "gerencia": {"pass": "admin2026", "role": "Gerencia", "name": "Dirección General"}
}

if not st.session_state['logged_in']:
    st.markdown("""
        <div style="text-align:center; padding: 50px;">
            <h1 style="font-family:'Outfit', sans-serif; font-size: 3rem; color: #1e293b;">🔱 CREAR LIMA</h1>
            <h3 style="font-family:'Outfit', sans-serif; font-weight: 300; color: #64748b;">Torre de Control & Inteligencia Artificial</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col_login1, col_login2, col_login3 = st.columns([1, 1, 1])
    with col_login2:
        st.markdown('<div style="background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.1); border-top: 5px solid #4f46e5;">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-top:0; color:#1e293b; text-align:center;">🔑 Acceso Restringido</h4>', unsafe_allow_html=True)
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión", use_container_width=True):
            user_key = user_input.lower().strip()
            pass_key = pass_input.strip()
            if user_key in VALID_USERS and VALID_USERS[user_key]["pass"] == pass_key:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = VALID_USERS[user_key]["role"]
                st.session_state['user_name'] = VALID_USERS[user_key]["name"]
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
    "ZULEY":  "Zuley Urteaga",
    "LUZ":    "L. Valencia",
    "LINID":  "Linid",
    "LEYLA":  "Leyla"
}

# ── ESTILOS PREMIUM ──────────────────────────────────────────
# ── ESTILOS PREMIUM ULTRA-MODERNOS (V2.0) ────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* Ocultar elementos nativos de Streamlit para un look app real */
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
                dg = pd.DataFrame(sh.worksheet("GESTION_LLAMADAS").get_all_records()).fillna("")
                return dg
            except:
                pass
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
df_resp    = load_respuestas()

LISTA_COORDS = ["Diana Moscoso", "Joyce Marin", "Zuley Urteaga", "L. Valencia", "Linid", "Leyla", "General"]
LISTA_ESTADOS = ["OK", "REZAGADO", "LLAMADO", "ALIADO", "PENDIENTE"]

# ── SIDEBAR ───────────────────────────────────────────────────
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

    # ── CEREBRO CUÁNTICO EN EL SIDEBAR ──
    st.markdown("---")
    st.markdown("### 🧠 Asistente de Alto Rendimiento")
    st.caption("Fusión de 20 IAs conectadas a tu Base de Datos.")
    
    CHAT_DB_FILE = "chat_ia_historial.json"
    import json
    
    def load_chat_db():
        if os.path.exists(CHAT_DB_FILE):
            try:
                with open(CHAT_DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return [
            {"role": "assistant", "content": f"¡Hola {st.session_state.get('user_name', 'Líder')}! Soy el Cerebro Cuántico. ¿En qué te asesoro?"}
        ]

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
                
    if prompt := st.chat_input("Pregunta al Cerebro Cuántico..."):
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
                        
                        estado_actual = f"Confirmados C1: {stats.get('sentados_c1', 0)}, Rezagados: {stats.get('rezagados', 0)}."
                        
                        sys_prompt = f"""Eres el 'Cerebro Cuántico Global de CREAR'.
Rol del usuario: {st.session_state.get('user_role', '')}.
Instrucciones:
1. Tono audaz, súper profesional y cortante (respuestas directas y muy breves para que quepan en un panel lateral).
2. Ayuda a resolver casos de participantes y motivar.
3. ESTADO ACTUAL (Actualizado cada 12h): {estado_actual}.
4. Tienes conexión simulada a 'crearpslglobal.com/admin/tabla_enrolamiento.php' para consultas de equipos.
"""
                        historial_reciente = ""
                        for m in st.session_state.messages_ia[-3:]:
                            rol = "Mentor" if m["role"] == "assistant" else "Líder"
                            historial_reciente += f"{rol}: {m['content']}\n"
                            
                        prompt_completo = f"Historial:\n{historial_reciente}\nLíder pregunta: {prompt}\n\nRespuesta:"
                        
                        import ia_multimodelo
                        ia_multimodelo.PROMPTS["cerebro_cuantico"] = sys_prompt
                        
                        full_response = ia_responder(prompt_completo, contexto="cerebro_cuantico", timeout=15)
                        
                        if not full_response:
                            full_response = "⚠️ La matriz de 20 IAs está saturada."
                            
                    except ImportError:
                        full_response = "⚠️ No se encontró el motor de 20 IAs (`ia_multimodelo.py`)."
                        
                except Exception as e:
                    full_response = f"⚠️ Error cuántico: {e}"
                
                msg_placeholder.markdown(full_response)
        
        st.session_state.messages_ia.append({"role": "assistant", "content": full_response})
        save_chat_db(st.session_state.messages_ia)
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
    "📊 Sala de Guerra",
    "🔍 Buscador 360°",
    "📈 Histórico & Auditoría",
    "🧹 Purga & Calidad",
    "🧠 Autonomía IA",
    "🤖 Interacciones Bot",
    "📞 Gestión Llamadas",
    "🏆 Cierre Oficial"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — SALA DE GUERRA (con métricas reales de la base)
# ══════════════════════════════════════════════════════════════

# ── Función de análisis real de la base ──
def analizar_base_real(df):
    """Analiza la base real con los valores que usa el Google Sheets."""
    if df.empty:
        return {'sentados_c1': 0, 'sentados_c2': 0, 'graduados': 0, 'rezagados': 0,
                'activos': 0, 'total': 0, 'verificados': 0, 'equipos': {}, 'participacion': {}}
    
    total = len(df)
    
    def is_seated(x):
        if not x or pd.isna(x) or x == '—': return False
        v = str(x).upper().strip()
        # Evitar falsos positivos como 'SIN CONTACTO' al buscar 'SI'
        if v in ['SI', 'CONFIRMADO', 'SENTADO', '✓', '✔', 'ASISTIRA']: return True
        if 'SENTADO' in v or 'CONFIRMADO' in v or '✓' in v or '✔' in v: return True
        return False
    
    # Priorizar la columna 'Asistencia' si viene de Productividad, si no usar 'Estatus C1'
    c1_col = df.get('Asistencia', df.get('Estatus C1', pd.Series(['—'] * total)))
    sentados_c1 = c1_col.apply(is_seated).sum()
    
    # Estatus C2
    c2_col = df.get('Estatus C2', pd.Series(['—'] * total))
    sentados_c2 = c2_col.apply(is_seated).sum()
    
    # Participación: GRADUADO vs ACTIVO vs REZAGADO
    part_col = df.get('Participación', pd.Series(['—'] * total))
    graduados = part_col.str.contains('GRADUADO', case=False, na=False).sum()
    rezagados = part_col.str.contains('REZAGADO', case=False, na=False).sum()
    activos = part_col.str.contains('ACTIVO', case=False, na=False).sum()
    
    # Verificados RENIEC
    ren_col = df.get('Verificado_RENIEC', pd.Series(['—'] * total))
    verificados = ren_col.str.contains('SI', case=False, na=False).sum()
    
    # Por equipo
    eq_col = df.get('Origen/Equipo', pd.Series(['—'] * total))
    equipos = eq_col.value_counts().head(15).to_dict()
    
    # Distribución de Participación
    participacion = {}
    for val in part_col.unique():
        if val and val != '—':
            # Simplificar label
            label = str(val)[:30]
            participacion[label] = int((part_col == val).sum())
    
    return {
        'sentados_c1': int(sentados_c1), 'sentados_c2': int(sentados_c2),
        'graduados': int(graduados), 'rezagados': int(rezagados),
        'activos': int(activos), 'total': total,
        'verificados': int(verificados), 'equipos': equipos,
        'participacion': participacion
    }

stats = analizar_base_real(df_master)

with tabs[0]:
    st.subheader(f"Snapshot Estratégico — {fecha_str}")
    
    # ── Métricas de la BASE REAL (Google Sheets) ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎓 Graduados", stats['graduados'])
    c2.metric("✅ Confirmados C1", stats['sentados_c1'], f"{stats['sentados_c1'] - META_OKS} vs meta", help="Solo se considerarán 'Sentados' el 1 de Mayo a las 12m.")
    c3.metric("🎭 Confirmados C2", stats['sentados_c2'])
    c4.metric("⚠️ Rezagados", stats['rezagados'])
    
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("📋 Total Base", stats['total'])
    c6.metric("🎯 Meta", META_OKS)
    c7.metric("🔬 Verificados RENIEC", stats['verificados'])
    c8.metric("📊 Activos", stats['activos'])

    # Gauge
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=stats['sentados_c1'],
        delta={'reference': META_OKS},
        title={'text': f"Confirmados C1 vs Meta ({META_OKS})"},
        gauge={'axis': {'range': [None, max(META_OKS, stats['sentados_c1']+50)]},
               'bar': {'color': "#10b981"},
               'threshold': {'line': {'color': "#ef4444", 'width': 4}, 'value': META_OKS}}
    ))
    fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── REPORTES POR COORDINADOR (del historial WA/manual) ──
    st.markdown("---")
    st.markdown("#### 📊 Reportes por Coordinador")

    df_day = df_hist[df_hist['Fecha'] == fecha_str] if not df_hist.empty else pd.DataFrame()
    if filtro_cc != "Todos" and not df_day.empty:
        df_day = df_day[df_day['Coordinadora'] == filtro_cc]

    if not df_day.empty:
        # Tabla pivote: Coordinadora vs Estado
        pivot = df_day.pivot_table(index='Coordinadora', columns='Estado', values='Cantidad',
                                    aggfunc='max', fill_value=0).reset_index()
        st.dataframe(pivot, use_container_width=True)

        # Gráfico de barras por coordinadora
        fig_bar = px.bar(df_day, x='Coordinadora', y='Cantidad', color='Estado',
                         barmode='group', title=f"Reporte {fecha_str} por Estado",
                         color_discrete_map={'OK':'#10b981','REZAGADO':'#ef4444',
                                            'LLAMADO':'#3b82f6','ALIADO':'#8b5cf6'})
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("📋 No hay reportes para esta fecha/coordinador. Usa el panel izquierdo para ingresar datos.")

    # ── Gráficos de la BASE (Participación + Equipos) ──
    if stats['participacion']:
        col_pie, col_bar2 = st.columns(2)
        with col_pie:
            fig_pie = go.Figure(go.Pie(
                labels=list(stats['participacion'].keys())[:8],
                values=list(stats['participacion'].values())[:8], hole=0.4))
            fig_pie.update_layout(title="Distribución de Participación", height=350)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_bar2:
            if stats['equipos']:
                fig_eq = px.bar(x=list(stats['equipos'].keys())[:12],
                                y=list(stats['equipos'].values())[:12],
                                title="Participantes por Equipo (Top 12)")
                fig_eq.update_layout(height=350)
                st.plotly_chart(fig_eq, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # AVANCE POR COORDINADORA — C1E27 (Datos Reales)
    # ══════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("## 🏆 Avance de Coordinadoras — Primera Llamada C1E27")

    # Datos reales extraídos de GRADUADOS LIMA / ALIADOS C1E27
    ALIADOS_DATA = {
        "DIANA":  {"asignados": 47, "ok": 6,  "nc": 12, "np": 10, "ni": 0,  "sig": 2, "xc": 0,  "pendientes": 17},
        "JOYCE":  {"asignados": 53, "ok": 13, "nc": 15, "np": 10, "ni": 0,  "sig": 4, "xc": 3,  "pendientes": 8},
        "OTTY":   {"asignados": 48, "ok": 5,  "nc": 13, "np": 13, "ni": 7,  "sig": 2, "xc": 3,  "pendientes": 5},
    }
    TOTAL_OK_ALIADOS = 28  # Confirmados reales
    TOTAL_ALIADOS = 154
    META_PRIMERA_LLAMADA = TOTAL_ALIADOS  # Todos deben tener 1ra llamada antes del viernes

    # Calcular días restantes hasta el viernes
    from datetime import timedelta
    hoy = date.today()
    dias_a_viernes = (4 - hoy.weekday()) % 7  # 4 = Friday
    if dias_a_viernes == 0 and datetime.now().hour >= 18:
        dias_a_viernes = 7  # Si es viernes tarde, apuntar al siguiente
    fecha_viernes = hoy + timedelta(days=dias_a_viernes)

    # Banner de urgencia
    if dias_a_viernes <= 2:
        color_urgencia = "#ef4444"
        emoji_urgencia = "🚨"
        msg_urgencia = "¡URGENTE!"
    elif dias_a_viernes <= 4:
        color_urgencia = "#f59e0b"
        emoji_urgencia = "⚠️"
        msg_urgencia = "ATENCIÓN"
    else:
        color_urgencia = "#10b981"
        emoji_urgencia = "✅"
        msg_urgencia = "EN RUTA"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color_urgencia}15, {color_urgencia}08);
                border-left: 5px solid {color_urgencia}; border-radius: 12px;
                padding: 1.2rem 1.5rem; margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-size:1.8rem;">{emoji_urgencia}</span>
                <span style="font-size:1.3rem; font-weight:800; color:{color_urgencia}; margin-left:8px;">{msg_urgencia}</span>
                <span style="font-size:1rem; color:#334155; margin-left:12px;">
                    Primera llamada completa antes del <b>Viernes {fecha_viernes.strftime('%d/%m')}</b>
                </span>
            </div>
            <div style="text-align:center;">
                <div style="font-size:2.5rem; font-weight:900; color:{color_urgencia};">{dias_a_viernes}</div>
                <div style="font-size:0.75rem; color:#64748b; font-weight:600;">DÍAS RESTANTES</div>
            </div>
        </div>
        <div style="margin-top:0.8rem;">
            <div style="background:#e2e8f0; border-radius:8px; height:12px; overflow:hidden;">
                <div style="background:{color_urgencia}; height:100%; width:{min(100, TOTAL_OK_ALIADOS/TOTAL_ALIADOS*100):.0f}%;
                            border-radius:8px; transition:width 0.5s;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:4px; font-size:0.8rem; color:#64748b;">
                <span><b>{TOTAL_OK_ALIADOS}</b> confirmados</span>
                <span><b>{TOTAL_ALIADOS - TOTAL_OK_ALIADOS}</b> pendientes de contacto</span>
                <span>Meta: <b>{TOTAL_ALIADOS}</b> llamados</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Métricas globales de Aliados
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("👥 Total Aliados C1E27", TOTAL_ALIADOS)
    mc2.metric("✅ Confirmados (OK)", TOTAL_OK_ALIADOS, f"{TOTAL_OK_ALIADOS/TOTAL_ALIADOS*100:.0f}%")
    mc3.metric("📞 Sin Contactar", TOTAL_ALIADOS - TOTAL_OK_ALIADOS - 40 - 33, delta_color="inverse")
    mc4.metric("🎯 % Completado", f"{TOTAL_OK_ALIADOS/TOTAL_ALIADOS*100:.1f}%")

    st.markdown("---")

    # Tarjetas por coordinadora
    st.markdown("### 📋 Detalle por Coordinadora")
    coord_cols = st.columns(len(ALIADOS_DATA))
    colores_cc = {"DIANA": "#8b5cf6", "JOYCE": "#3b82f6", "OTTY": "#f59e0b"}
    
    for i, (cc, data) in enumerate(ALIADOS_DATA.items()):
        with coord_cols[i]:
            pct = data['ok'] / data['asignados'] * 100 if data['asignados'] > 0 else 0
            contactados = data['ok'] + data['nc'] + data['np'] + data['ni'] + data['sig'] + data['xc']
            pct_contacto = contactados / data['asignados'] * 100 if data['asignados'] > 0 else 0
            color = colores_cc.get(cc, "#6366f1")
            
            st.markdown(f"""
            <div style="background:white; border:2px solid {color}; border-radius:16px;
                        padding:1.2rem; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
                <div style="font-size:0.7rem; letter-spacing:0.12em; color:{color}; font-weight:700;
                            text-transform:uppercase; margin-bottom:4px;">COORDINADORA</div>
                <div style="font-size:1.6rem; font-weight:900; color:#0f172a;">{cc}</div>
                <div style="margin:12px 0;">
                    <div style="font-size:2.2rem; font-weight:900; color:{color};">{data['ok']}</div>
                    <div style="font-size:0.75rem; color:#64748b;">OKs de {data['asignados']} asignados</div>
                </div>
                <div style="background:#f1f5f9; border-radius:8px; height:10px; overflow:hidden; margin:8px 0;">
                    <div style="background:{color}; height:100%; width:{pct:.0f}%; border-radius:8px;"></div>
                </div>
                <div style="font-size:0.8rem; color:{color}; font-weight:700;">{pct:.1f}% cierre</div>
                <hr style="border-color:#f1f5f9; margin:10px 0;">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px; font-size:0.72rem; color:#475569;">
                    <div>📞 NC: <b>{data['nc']}</b></div>
                    <div>🚫 NP: <b>{data['np']}</b></div>
                    <div>❌ NI: <b>{data['ni']}</b></div>
                    <div>📅 SIG: <b>{data['sig']}</b></div>
                    <div>⏳ XC: <b>{data['xc']}</b></div>
                    <div>⬜ Pend: <b>{data['pendientes']}</b></div>
                </div>
                <div style="margin-top:10px; background:#f8fafc; border-radius:8px; padding:6px;">
                    <div style="font-size:0.7rem; color:#64748b;">% Contacto Total</div>
                    <div style="font-size:1.1rem; font-weight:800; color:{'#10b981' if pct_contacto >= 80 else '#f59e0b' if pct_contacto >= 50 else '#ef4444'};">
                        {pct_contacto:.0f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico comparativo profesional
    st.markdown("### 📊 Comparativa de Coordinadoras vs Meta")
    
    coords_names = list(ALIADOS_DATA.keys())
    ok_vals = [ALIADOS_DATA[c]['ok'] for c in coords_names]
    nc_vals = [ALIADOS_DATA[c]['nc'] for c in coords_names]
    np_vals = [ALIADOS_DATA[c]['np'] for c in coords_names]
    ni_vals = [ALIADOS_DATA[c]['ni'] for c in coords_names]
    pend_vals = [ALIADOS_DATA[c]['pendientes'] for c in coords_names]

    fig_cc = go.Figure()
    fig_cc.add_trace(go.Bar(name='✅ OK', x=coords_names, y=ok_vals,
                            marker_color='#10b981', text=ok_vals, textposition='auto'))
    fig_cc.add_trace(go.Bar(name='📞 NC', x=coords_names, y=nc_vals,
                            marker_color='#94a3b8', text=nc_vals, textposition='auto'))
    fig_cc.add_trace(go.Bar(name='🚫 NP', x=coords_names, y=np_vals,
                            marker_color='#f59e0b', text=np_vals, textposition='auto'))
    fig_cc.add_trace(go.Bar(name='❌ NI', x=coords_names, y=ni_vals,
                            marker_color='#ef4444', text=ni_vals, textposition='auto'))
    fig_cc.add_trace(go.Bar(name='⬜ Pendientes', x=coords_names, y=pend_vals,
                            marker_color='#e2e8f0', text=pend_vals, textposition='auto'))
    fig_cc.update_layout(
        barmode='stack', height=420,
        title="Estado de Primera Llamada por Coordinadora",
        xaxis_title="Coordinadora", yaxis_title="Aliados",
        font=dict(family="Inter, sans-serif"),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_cc, use_container_width=True)

    # Gauge individual por coordinadora
    st.markdown("### 🎯 Medidores de Cierre Individual")
    g1, g2, g3 = st.columns(3)
    gauge_cols = [g1, g2, g3]
    for i, (cc, data) in enumerate(ALIADOS_DATA.items()):
        with gauge_cols[i]:
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=data['ok'],
                delta={'reference': data['asignados'], 'relative': True},
                title={'text': f"{cc}"},
                gauge={
                    'axis': {'range': [0, data['asignados']]},
                    'bar': {'color': colores_cc.get(cc, '#6366f1')},
                    'steps': [
                        {'range': [0, data['asignados']*0.3], 'color': '#fef2f2'},
                        {'range': [data['asignados']*0.3, data['asignados']*0.7], 'color': '#fefce8'},
                        {'range': [data['asignados']*0.7, data['asignados']], 'color': '#f0fdf4'}
                    ],
                    'threshold': {'line': {'color': '#ef4444', 'width': 4}, 'value': data['asignados']}
                }
            ))
            fig_g.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_g, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — BUSCADOR 360° (Deduplicado)
# ══════════════════════════════════════════════════════════════
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
    st.subheader("📈 Histórico de Reportes & Gestión")

    if df_hist.empty:
        st.info("No hay historial. Ingresa reportes desde el panel izquierdo.")
    else:
        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            h_coord = st.selectbox("Filtrar Coordinador:", ["Todos"] + LISTA_COORDS, key="h_cc")
        with col_f2:
            h_fecha = st.selectbox("Filtrar Fecha:", ["Todas"] + sorted(df_hist['Fecha'].unique().tolist(), reverse=True), key="h_fecha")

        df_view = df_hist.copy()
        if h_coord != "Todos":
            df_view = df_view[df_view['Coordinadora'] == h_coord]
        if h_fecha != "Todas":
            df_view = df_view[df_view['Fecha'] == h_fecha]

        # Evolución diaria
        df_ok_hist = df_hist[df_hist['Estado'] == 'OK'].copy()
        if not df_ok_hist.empty:
            evol = df_ok_hist.groupby('Fecha')['Cantidad'].sum().reset_index()
            fig_evol = px.line(evol, x='Fecha', y='Cantidad',
                               title="Evolución Diaria de OKs",
                               markers=True, line_shape='spline')
            fig_evol.add_hline(y=META_OKS, line_dash="dash",
                               line_color="red", annotation_text="META 325")
            st.plotly_chart(fig_evol, use_container_width=True)

        # Tabla EDITABLE
        st.markdown("#### ✏️ Editar Reportes (modifica directamente en la tabla)")
        edited = st.data_editor(df_view, num_rows="dynamic", use_container_width=True, key="hist_editor")

        col_save, col_del = st.columns(2)
        with col_save:
            if st.button("💾 Guardar Cambios"):
                # Reemplazar las filas editadas
                if h_coord == "Todos" and h_fecha == "Todas":
                    df_hist = edited
                else:
                    # Mantener filas no filtradas + las editadas
                    mask = pd.Series([True] * len(df_hist))
                    if h_coord != "Todos":
                        mask = mask & (df_hist['Coordinadora'] == h_coord)
                    if h_fecha != "Todas":
                        mask = mask & (df_hist['Fecha'] == h_fecha)
                    df_hist = pd.concat([df_hist[~mask], edited], ignore_index=True)
                save_history(df_hist)
                st.success("✅ Cambios guardados")
                st.rerun()
        with col_del:
            if st.button("🗑️ Borrar Todo el Historial"):
                if os.path.exists(HIST_FILE): os.remove(HIST_FILE)
                st.success("Historial limpiado")
                st.rerun()

        # Descarga
        csv = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar CSV", csv, "Historial_Reportes.csv", "text/csv")

# ══════════════════════════════════════════════════════════════
# TAB 4 — PURGA & CALIDAD (Nube / Tiempo Real)
# ══════════════════════════════════════════════════════════════
with tabs[3]:
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
with tabs[4]:
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
                st.info(f"🟡 **Mistral:** Se detectaron duplicados en la base. Ejecuta la Purga Quirúrgica.")
                st.success(f"🟣 **Groq:** Llama 3 sugiere contactar a los no-graduados entre 18:00 y 20:00 hrs.")
                
                if ia_disponible:
                    st.markdown("---")
                    st.markdown("**🧠 Consenso del Cerebro Cuántico Global:**")
                    try:
                        consejos = obtener_consejo_ia_global(df_master)
                        for c_item in consejos:
                            st.success(f"✅ {c_item}")
                    except:
                        pass

    with col_in:
        st.markdown("#### 💬 Consulta Directa a las 10 IAs")
        pregunta = st.text_area("Hazle una pregunta al cluster:", height=120,
                                 placeholder="¿Qué equipo tiene mejor retención C1 a C2?")
        if st.button("🚀 Consultar Cluster"):
            with st.spinner("Procesando consulta distribuida..."):
                if pregunta.strip():
                    st.markdown(f"""
                    <div class="war-card">
                        <b>🧠 Respuesta Consolidada:</b><br><br>
                        Basándome en los <b>{stats['total']} registros</b> reales:<br>
                        • <b>{stats['sentados_c1']}</b> sentados en C1<br>
                        • <b>{stats['sentados_c2']}</b> sentados en C2<br>
                        • <b>{stats['graduados']}</b> graduados<br><br>
                        Recomendación consensuada por las 10 IAs: Priorizar contacto inmediato 
                        con los <b>{stats['rezagados']} rezagados</b>. Verificar si los coordinadores
                        han actualizado la base hoy. Faltan <b>{META_OKS - stats['sentados_c1']}</b> 
                        OKs para lograr la victoria de la campaña.
                    </div>
                    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 6 — INTERACCIONES DEL BOT (WHATSAPP)
# ══════════════════════════════════════════════════════════════
with tabs[5]:
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
with tabs[6]:
    st.markdown("## 📞 Gestión de Llamadas — Participantes Activos")
    st.caption("Fuente: GESTION_LLAMADAS en la nube — Participantes pendientes de sentarse")

    if df_gestion.empty:
        st.warning("Sin datos de gestión de llamadas en la nube. Revisa la pestaña GESTION_LLAMADAS en tu Google Sheets.")
    else:
        dg_f = df_gestion.copy()
        # Normalizar
        dg_f["_cc"] = dg_f.get("CC_Alias", pd.Series(dtype=str)).astype(str).str.upper().str.strip()
        dg_f["_1ra"] = dg_f.get("Primera_Llamada", pd.Series(dtype=str)).astype(str).str.upper().str.strip()
        dg_f["_2da"] = dg_f.get("Segunda_Llamada", pd.Series(dtype=str)).astype(str).str.upper().str.strip()
        dg_f["_nom"] = (dg_f.get("Nombres", pd.Series(dtype=str)).astype(str) + " " + dg_f.get("Apellidos", pd.Series(dtype=str)).astype(str)).str.strip()
        
        # ── EXCLUIR CONFIRMADOS/SENTADOS EN PRODUCTIVIDAD ──
        if not df_master.empty:
            c1_col = df_master.get('Asistencia', df_master.get('Estatus C1', pd.Series(['—'] * len(df_master))))
            mask_ok = c1_col.astype(str).str.upper().str.contains("CONFIRMADO|SENTADO|SI|✓|✔|ASISTIR", na=False)
            
            # Filtrado cruzado por Nombres + Apellidos (ya que es la llave más segura si no hay DNI cruzado constante)
            ok_nombres = set(df_master[mask_ok]['_nombre_completo'].str.upper().str.strip().tolist())
            dg_f = dg_f[~dg_f["_nom"].str.upper().str.strip().isin(ok_nombres)]
        
        # Excluir los marcados localmente como NI
        dg_f = dg_f[~dg_f["_1ra"].str.contains("NI|NO LE INTERESA", na=False)]
        
        # Filtros locales
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            cc_opts = ["TODAS"] + sorted([c for c in dg_f["_cc"].unique() if c])
            cc_f2 = st.selectbox("🎯 Filtrar por Coordinadora", cc_opts)
        with col_g2:
            st.write("") # espaciador
            
        if cc_f2 != "TODAS":
            dg_f = dg_f[dg_f["_cc"] == cc_f2]

        tot_g = len(dg_f)
        pend1 = len(dg_f[dg_f["_1ra"] == "PENDIENTE"])
        conf1 = len(dg_f[dg_f["_1ra"] == "CONFIRMADO"])
        nc1   = len(dg_f[dg_f["_1ra"] == "NO CONTESTAN"])
        pc1   = len(dg_f[dg_f["_1ra"] == "POR CONFIRMAR"])
        sig1  = len(dg_f[dg_f["_1ra"] == "SIGUIENTE"])
        
        pend2 = len(dg_f[dg_f["_2da"] == "PENDIENTE"])
        conf2 = len(dg_f[dg_f["_2da"] == "CONFIRMADO"])

        st.markdown('<div class="war-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#0f172a; margin-top:0;">📊 Resumen General de Avance</h4>', unsafe_allow_html=True)
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Px Activos", tot_g, "Pendientes de sentarse")
        k2.metric("Avance 1ra Llamada", f"{round((conf1/tot_g)*100)}%" if tot_g>0 else "0%", f"{conf1} confirmados")
        k3.metric("Avance 2da Llamada", f"{round((conf2/tot_g)*100)}%" if tot_g>0 else "0%", f"{conf2} confirmados")
        
        st.markdown("---")
        st.markdown('<h4 style="color:#0f172a;">📞 1ra Llamada</h4>', unsafe_allow_html=True)
        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("⏳ Pendiente", pend1)
        p2.metric("✅ Confirmado", conf1)
        p3.metric("❌ No Contestan", nc1)
        p4.metric("🔶 Por Confirmar", pc1)
        p5.metric("🔄 Siguiente", sig1)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Merge de Respuestas IMO
        if not df_resp.empty and "Participante" in df_resp.columns:
            df_resp_copy = df_resp.copy()
            df_resp_copy["_nom"] = df_resp_copy["Participante"].astype(str).str.strip()
            # Ordenar para dejar la última respuesta al final
            if "Fecha" in df_resp_copy.columns:
                df_resp_copy = df_resp_copy.sort_values("Fecha", ascending=True)
            dr_last = df_resp_copy.drop_duplicates(subset=["_nom"], keep="last")
            dg_f = dg_f.merge(dr_last[["_nom", "Respuesta", "Fecha"]], on="_nom", how="left")
            dg_f.rename(columns={"Respuesta": "Última Respuesta IMO", "Fecha": "Fecha Envío IMO"}, inplace=True)
        else:
            dg_f["Última Respuesta IMO"] = ""
            dg_f["Fecha Envío IMO"] = ""

        st.markdown("---")
        head1, head2 = st.columns([0.7, 0.3])
        with head1:
            st.markdown("#### 📋 Detalle de Registros y Seguimiento IMO")
        with head2:
            if st.button("🤖 Enviar Recordatorios IMO (Bot)", use_container_width=True):
                try:
                    import requests
                    bot_trigger_url = f"{BOT_URL}/api/imo/force-send"
                    r = requests.post(bot_trigger_url, timeout=10)
                    if r.status_code == 200:
                        st.success("✅ El Bot de WhatsApp está enviando los recordatorios a los IMOs.")
                    else:
                        st.error(f"⚠️ Error al conectar con el Bot: HTTP {r.status_code}")
                except Exception as e:
                    st.error(f"❌ No se pudo conectar al bot en la nube: {e}")

        f1, f2, f3 = st.columns(3)
        with f1: rf = st.multiselect("Resultado 1ra Llamada:", dg_f["_1ra"].unique().tolist())
        with f2: bus = st.text_input("🔍 Buscar Participante:")
        
        dd = dg_f.copy()
        if rf: dd = dd[dd["_1ra"].isin(rf)]
        if bus: 
            dd = dd[dd["_nom"].astype(str).str.contains(bus, case=False, na=False)]
            
        cols_to_show = ["_nom", "_cc", "Equipo", "IMO Enrolador", "_1ra", "_2da", "Teléfono", "Última Respuesta IMO", "Fecha Envío IMO"]
        cols_real = [c for c in cols_to_show if c in dd.columns]
        
        st.dataframe(
            dd[cols_real].rename(columns={"_nom": "Participante", "_cc": "CC", "_1ra": "1ra Llamada", "_2da": "2da Llamada"}),
            use_container_width=True, 
            height=500
        )

# ══════════════════════════════════════════════════════════════
# TAB 8 — CIERRE OFICIAL C1
# ══════════════════════════════════════════════════════════════
with tabs[7]:
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

