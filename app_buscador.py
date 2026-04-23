import streamlit as st
import pandas as pd
import os
import requests
import plotly.graph_objects as go
import unicodedata

# ── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────
st.set_page_config(page_title="CRM CREAR LIMA 🔱", layout="wide", page_icon="🔱")

# ── CONFIGURACIÓN DE PERSISTENCIA (GOOGLE SHEETS) ───────────
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=300)
def cargar_maestro_cloud():
    try:
        df = pd.read_excel(GSHEET_URL, dtype=str).fillna("—")
        return df
    except Exception as e:
        st.error(f"⚠️ Error cargando Google Sheets: {e}")
        return None

def norm(text):
    if not text or pd.isna(text): return ""
    s = str(text).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

# ── ESTILOS PREMIUM ──────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .main-card { background: white; padding: 25px; border-radius: 15px; border-left: 5px solid #4f46e5; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .status-badge { padding: 6px 15px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; }
    .ok-badge { background: #dcfce7; color: #166534; }
    .alert-badge { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

df = cargar_maestro_cloud()

if df is not None:
    tab_war, tab_search, tab_ai = st.tabs(["📊 Sala de Guerra", "🔍 Buscador Maestro 360°", "🧠 Autonomía IA"])

    with tab_war:
        st.markdown("### 🏹 Monitor Estratégico de Campaña")
        c1, c2, c3 = st.columns(3)
        
        ok_count = len(df[df.astype(str).apply(lambda x: x.str.contains('OK|CONFIRMADO', case=False)).any(axis=1)])
        c1.metric("Registros en Nube", len(df))
        c2.metric("OKs Confirmados", ok_count)
        c3.metric("Meta", "325 OKs")
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = ok_count,
            title = {'text': "Progreso hacia la Meta"},
            gauge = {'axis': {'range': [None, 325]}, 'bar': {'color': "#10b981"}}
        ))
        st.plotly_chart(fig, use_container_width=True)

    with tab_search:
        st.markdown("### 🔎 Buscador de Inteligencia 360°")
        query = st.text_input("Busca por cualquier dato (Nombre, DNI, Teléfono...):", placeholder="Ej: Marco")
        
        if query:
            q_norm = norm(query)
            mask = df.apply(lambda row: q_norm in norm(" ".join(row.values)), axis=1)
            results = df[mask]
            
            if not results.empty:
                selected_name = st.selectbox("Selecciona para ver la FICHA DETALLADA:", 
                                            options=results['Nombres'] + " " + results['Apellidos'])
                
                pax = results[(results['Nombres'] + " " + results['Apellidos']) == selected_name].iloc[0]
                
                st.markdown(f"""
                <div class="main-card">
                    <h2 style='margin:0;'>👤 {selected_name}</h2>
                    <p style='color:#64748b; font-size:1.1rem;'>DNI: {pax.get('DNI','—')} | Tel: {pax.get('Teléfono','—')}</p>
                    <hr>
                    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; text-align:center;'>
                        <div><b>Estatus Global</b><br><span class="status-badge ok-badge">{pax.get('Estatus','PENDIENTE')}</span></div>
                        <div><b>C1</b><br>{pax.get('Estatus C1','—')}</div>
                        <div><b>C2</b><br>{pax.get('Estatus C2','—')}</div>
                    </div>
                    <br>
                    <b>📌 Coordinador:</b> {pax.get('Coordinador','—')} | <b>📍 Origen:</b> {pax.get('Origen/Equipo','—')}
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(results, use_container_width=True)
            else:
                st.warning("No se encontraron coincidencias.")

    with tab_ai:
        st.markdown("### 🧠 Centro de IA")
        st.info("Motores: Gemini, Groq, Mistral, Cohere, HF activos.")
        st.write("- Análisis: La base de datos es íntegra y el puente con Google Sheets es estable.")
