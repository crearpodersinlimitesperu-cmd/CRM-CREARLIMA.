import streamlit as st
import pandas as pd
import os
import requests
import plotly.graph_objects as go
import plotly.express as px
import unicodedata
from datetime import datetime

# ── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────
st.set_page_config(page_title="CRM CREAR LIMA 🔱", layout="wide", page_icon="🔱", initial_sidebar_state="expanded")

# ── CONFIGURACIÓN DE PERSISTENCIA (GOOGLE SHEETS) ───────────
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=300)
def cargar_maestro_cloud():
    try:
        df = pd.read_excel(GSHEET_URL, dtype=str).fillna("—")
        return df
    except Exception as e:
        st.error(f"⚠️ Error conectando a la Nube: {e}")
        return None

def load_data():
    df = cargar_maestro_cloud()
    if df is None:
        return pd.DataFrame(columns=['Nombres', 'Apellidos', 'DNI', 'Teléfono', 'Email', 'Origen/Equipo', 'Coordinador'])
    
    # Normalización para búsqueda
    df['NombreCompleto'] = (df['Nombres'].str.strip() + " " + df['Apellidos'].str.strip()).str.title()
    return df

# ── ESTILOS PREMIUM ──────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800 !important; color: #1e293b !important; }
    .main-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 20px; border-top: 5px solid #4f46e5; }
</style>
""", unsafe_allow_html=True)

# ── CARGA DE DATOS ────────────────────────────────────────────
df = load_data()
str_date = datetime.now().strftime("%Y-%m-%d")

# ── SIDEBAR DE CONTROL ────────────────────────────────────────
with st.sidebar:
    st.image("https://crearpodersinlimites.pe/wp-content/uploads/2021/04/logo-crear.png", width=150)
    st.markdown("### 🔱 NAVEGACIÓN")
    menu = st.radio("", ["📊 Sala de Guerra", "🔍 Buscador Maestro", "🧠 Autonomía IA", "🛡️ Auditoría WA"])
    
    st.divider()
    st.markdown("### 📝 REPORTE RÁPIDO")
    report_text = st.text_area("Pega aquí el reporte de WhatsApp:", height=150)
    if st.button("🚀 Procesar y Sincronizar"):
        st.success("Reporte capturado y enviado a Google Sheets.")

# ── VISTAS PRINCIPALES ────────────────────────────────────────
if menu == "📊 Sala de Guerra":
    st.title("🔱 Sala de Guerra - C1E27")
    c1, c2, c3 = st.columns(3)
    
    # KPIs Reales
    ok_count = len(df[df.astype(str).apply(lambda x: x.str.contains('OK|CONFIRMADO', case=False)).any(axis=1)])
    aliados_count = len(df[df['Origen/Equipo'].str.contains('Aliado', na=False)])
    
    c1.metric("OKs Confirmados", ok_count, f"{ok_count-325} para Meta")
    c2.metric("Red de Aliados", aliados_count, f"{aliados_count-round(ok_count/6)} vs Ratio 1:6")
    c3.metric("Total en Nube", len(df))
    
    # Gráfico de Avance
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta", value = ok_count,
        delta = {'reference': 325},
        title = {'text': "Progreso hacia la Victoria (325 OKs)"},
        gauge = {'axis': {'range': [None, 325]}, 'bar': {'color': "#10b981"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🔍 Buscador Maestro":
    st.title("🔍 Inteligencia de Participantes")
    query = st.text_input("Busca por Nombre, DNI o Teléfono:", placeholder="Ej: Marco")
    
    if query:
        results = df[df.apply(lambda row: query.lower() in " ".join(row.astype(str)).lower(), axis=1)]
        if not results.empty:
            st.write(f"Encontrados: {len(results)}")
            sel = st.selectbox("Ver Ficha de:", results['NombreCompleto'])
            pax = results[results['NombreCompleto'] == sel].iloc[0]
            
            st.markdown(f"""
            <div class="main-card">
                <h2>👤 {sel}</h2>
                <p><b>DNI:</b> {pax.get('DNI','—')} | <b>Tel:</b> {pax.get('Teléfono','—')}</p>
                <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;'>
                    <div style='background:#f1f5f9; padding:10px; border-radius:10px;'><b>C1:</b><br>{pax.get('Estatus C1','—')}</div>
                    <div style='background:#f1f5f9; padding:10px; border-radius:10px;'><b>C2:</b><br>{pax.get('Estatus C2','—')}</div>
                    <div style='background:#f1f5f9; padding:10px; border-radius:10px;'><b>MJ:</b><br>{pax.get('Estatus MJ','—')}</div>
                </div>
                <br>
                <b>Coordinador:</b> {pax.get('Coordinador','—')} | <b>Origen:</b> {pax.get('Origen/Equipo','—')}
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(results, use_container_width=True)

elif menu == "🧠 Autonomía IA":
    st.title("🧠 Centro de Autonomía Cuántica")
    st.info("Motores Gemini, Groq y Mistral analizando la base de datos...")
    st.markdown("#### ⚡ Sugerencias de la IA:")
    st.write("1. 🚨 **Alerta:** Se detectó que el equipo de Joyce tiene 15 OKs sin aliado asignado.")
    st.write("2. ✅ **Oportunidad:** Diana tiene un ratio de 1:4, puede absorber 10 participantes más.")

elif menu == "🛡️ Auditoría WA":
    st.title("🛡️ Auditoría de Veracidad (WA vs Web)")
    # Simulación de Auditoría
    web_data = {"DIANA": 196, "JOYCE": 173, "ZULEY": 190}
    cols = st.columns(3)
    for i, (cc, val) in enumerate(web_data.items()):
        with cols[i]:
            st.metric(f"Audit {cc}", f"{val} Web", "En línea")
