import streamlit as st
import pandas as pd
import os
import requests
import plotly.graph_objects as go
import plotly.express as px
import unicodedata
from datetime import datetime, date

# ── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────
st.set_page_config(page_title="CRM CREAR LIMA 🔱", layout="wide", page_icon="🔱", initial_sidebar_state="expanded")

# ── CONFIGURACIÓN DE PERSISTENCIA (GOOGLE SHEETS) ───────────
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"
GSHEET_MASTER_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx&gid=0"
# Usamos export directo para leer el historial si existe
GSHEET_HIST_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=11111111" # ID de la pestaña historial

@st.cache_data(ttl=60)
def load_cloud_data():
    try:
        # Carga Master
        df_master = pd.read_excel(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx", dtype=str).fillna("—")
        return df_master
    except:
        return pd.DataFrame(columns=['Nombres', 'Apellidos', 'DNI', 'Teléfono', 'Email', 'Origen/Equipo', 'Coordinador'])

def load_history():
    # En esta versión, si no hay archivo local, intentamos leer un CSV temporal
    if os.path.exists("Historial_Reportes.csv"):
        return pd.read_csv("Historial_Reportes.csv")
    return pd.DataFrame(columns=['Fecha', 'Hora', 'Coordinadora', 'Seccion', 'Estado', 'Cantidad', 'Avance', 'Observaciones'])

# ── MOTOR DE INTELIGENCIA (WHATSAPP PARSER) ──────────────────
def parse_whatsapp_report(text):
    lines = text.split('\n')
    report_data = []
    current_coord = "DESCONOCIDO"
    
    # Mapeo de nombres
    coords_map = {"ZULEY": "Zuley", "JOYCE": "Joyce", "DIANA": "Diana", "LUZ": "L. Valencia"}
    
    for line in lines:
        upper_line = line.upper()
        # Detectar Coordinadora
        for key, val in coords_map.items():
            if key in upper_line: current_coord = val
        
        # Detectar Patrón: SECCION: ESTADO = CANTIDAD
        if ':' in line and '=' in line:
            try:
                seccion = line.split(':')[0].strip()
                resto = line.split(':')[1]
                estado = resto.split('=')[0].strip().upper()
                # Unificar: Confirmado = OK
                if any(x in estado for x in ["CONF", "CONFI", "CONFIRMADO"]): estado = "OK"
                
                cantidad = ''.join(filter(str.isdigit, resto.split('=')[1]))
                if cantidad:
                    report_data.append({
                        "Fecha": datetime.now().strftime("%Y-%m-%d"),
                        "Hora": datetime.now().strftime("%H:%M"),
                        "Coordinadora": current_coord,
                        "Seccion": seccion,
                        "Estado": estado,
                        "Cantidad": int(cantidad),
                        "Avance": "Capturado via Web",
                        "Observaciones": line.strip()
                    })
            except: pass
    return report_data

# ── INTERFAZ PREMIUM ──────────────────────────────────────────
df_master = load_cloud_data()
df_hist = load_history()

with st.sidebar:
    st.title("🔱 CONTROL CRM")
    sel_date = st.date_input("📅 Seleccionar Fecha de Análisis", date.today())
    str_sel_date = sel_date.strftime("%Y-%m-%d")
    
    st.divider()
    st.markdown("### 📝 CARGA DE REPORTES")
    raw_text = st.text_area("Pega el reporte de WhatsApp aquí:", height=200)
    if st.button("🚀 PROCESAR E INTELIGENCIAR"):
        new_data = parse_whatsapp_report(raw_text)
        if new_data:
            df_new = pd.DataFrame(new_data)
            df_hist = pd.concat([df_hist, df_new], ignore_index=True)
            df_hist.to_csv("Historial_Reportes.csv", index=False)
            st.success(f"✅ {len(new_data)} KPIs extraídos con éxito.")
            st.rerun()

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🔱 SALA DE GUERRA", "🔍 BUSCADOR", "📈 HISTÓRICO", "🧠 IA AUTÓNOMA"])

with tab1:
    st.subheader(f"Snapshot Estratégico: {str_sel_date}")
    df_day = df_hist[df_hist['Fecha'] == str_sel_date]
    
    if not df_day.empty:
        # Agregación por Coordinadora (Max snapshot)
        resumen = df_day.groupby(['Coordinadora', 'Estado'])['Cantidad'].max().reset_index()
        total_ok = resumen[resumen['Estado'] == 'OK']['Cantidad'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total OKs Hoy", total_ok, f"{total_ok-325}")
        c2.metric("Meta Campaña", "325")
        c3.metric("Aliados Req.", round(total_ok/6))
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = total_ok,
            title = {'text': "Avance a la Meta"},
            gauge = {'axis': {'range': [None, 325]}, 'bar': {'color': "#10b981"}}
        ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay reportes para la fecha seleccionada.")

with tab2:
    st.subheader("🔍 Buscador Maestro 360°")
    query = st.text_input("Buscar por Nombre o DNI")
    if query:
        res = df_master[df_master.apply(lambda r: query.lower() in " ".join(r.astype(str)).lower(), axis=1)]
        st.dataframe(res, use_container_width=True)

with tab4:
    st.subheader("🧠 Centro de Inteligencia Autónoma")
    from brain_ai import obtener_consejo_ia_global
    consejos = obtener_consejo_ia_global(None)
    for c in consejos:
        st.write(f"🤖 **IA Sugiere:** {c}")
