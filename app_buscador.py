import streamlit as st
import pandas as pd
import os
import requests

# ── CONFIGURACIÓN DE PERSISTENCIA (GOOGLE SHEETS) ───────────
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=300)
def cargar_maestro_cloud():
    try:
        return pd.read_excel(GSHEET_URL, dtype=str).fillna("—")
    except Exception as e:
        st.error(f"⚠️ Error cargando Google Sheets: {e}")
        return None

def load_data():
    df = cargar_maestro_cloud()
    if df is None:
        return pd.DataFrame(columns=['Nombres', 'Apellidos', 'DNI', 'Teléfono', 'Email', 'Origen/Equipo', 'Coordinador'])
    return df

# --- INICIO DE LA APP ---
st.set_page_config(page_title="CRM CREAR LIMA 🔱", layout="wide")
st.title("🔱 CRM Maestro - Sala de Guerra C1E27")

df = load_data()

# PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📊 Sala de Guerra", "🔍 Buscador", "🧠 Autonomía IA"])

with tab1:
    st.header("Monitoreo en Tiempo Real")
    st.write(f"Total Registros en la Nube: {len(df)}")
    # Aquí irá tu dashboard Plotly...

with tab2:
    st.header("Buscador de Participantes")
    query = st.text_input("Buscar por Nombre o DNI")
    if query:
        res = df[df.apply(lambda row: query.lower() in row.astype(str).str.lower().values, axis=1)]
        st.dataframe(res)

with tab3:
    st.header("🧠 Centro de IA")
    st.info("Motores: Gemini, Groq, Mistral, Cohere, HF activos.")
    st.write("- Sugerencia IA: Reforzar red de aliados en equipo Joyce.")
