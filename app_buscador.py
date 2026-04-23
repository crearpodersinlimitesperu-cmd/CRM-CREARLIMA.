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
    .main-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.8rem; }
    .ok-badge { background: #dcfce7; color: #166534; }
    .alert-badge { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# ── LÓGICA DE CARGA ──────────────────────────────────────────
df = cargar_maestro_cloud()

if df is not None:
    # PESTAÑAS PRINCIPALES
    tab_war, tab_search, tab_ai = st.tabs(["🔱 Sala de Guerra", "🔍 Buscador Maestro", "🧠 Autonomía IA"])

    with tab_war:
        st.markdown("### 📊 Tablero de Control Estratégico")
        c1, c2, c3, c4 = st.columns(4)
        
        # Métricas Rápidas
        total_pax = len(df)
        ok_count = len(df[df.astype(str).apply(lambda x: x.str.contains('OK|CONFIRMADO', case=False)).any(axis=1)])
        
        c1.metric("Total Base", total_pax)
        c2.metric("Total OKs", ok_count, f"{ok_count/total_pax*100:.1f}%")
        
        # Gauge de Progreso
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = ok_count,
            title = {'text': "Meta 325 OKs"},
            gauge = {'axis': {'range': [None, 325]}, 'bar': {'color': "#4f46e5"}}
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with tab_search:
        st.markdown("### 🔍 Inteligencia de Participantes")
        query = st.text_input("Ingresa Nombre, Apellido o DNI:", placeholder="Ej: Marco Perez o 45678912")
        
        if query:
            q_norm = norm(query)
            # Búsqueda Multicolumna
            mask = df.apply(lambda row: q_norm in norm(" ".join(row.values)), axis=1)
            results = df[mask]
            
            if not results.empty:
                st.write(f"Se encontraron {len(results)} coincidencias:")
                
                # Selector de Perfil Detallado
                selected_name = st.selectbox("Selecciona un participante para ver su FICHA COMPLETA:", 
                                            options=results['Nombres'] + " " + results['Apellidos'])
                
                if selected_name:
                    pax_data = results[(results['Nombres'] + " " + results['Apellidos']) == selected_name].iloc[0]
                    
                    # FICHA PREMIUM
                    st.markdown(f"""
                    <div class="main-card">
                        <h2 style='color:#1e293b; margin-bottom:5px;'>👤 {selected_name}</h2>
                        <p style='color:#64748b;'>DNI: {pax_data.get('DNI','—')} | Tel: {pax_data.get('Teléfono','—')}</p>
                        <hr>
                        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;'>
                            <div>
                                <b>🏆 Estatus General</b><br>
                                <span class="status-badge {'ok-badge' if 'OK' in str(pax_data.get('Estatus','')) else 'alert-badge'}">
                                    {pax_data.get('Estatus','PENDIENTE')}
                                </span>
                            </div>
                            <div>
                                <b>📅 Capítulo C1</b><br>
                                {pax_data.get('Estatus C1','—')}
                            </div>
                            <div>
                                <b>🎭 Capítulo C2</b><br>
                                {pax_data.get('Estatus C2','—')}
                            </div>
                        </div>
                        <br>
                        <b>🛡️ Gestión de Coordinador:</b> {pax_data.get('Coordinador','—')}<br>
                        <b>📍 Origen:</b> {pax_data.get('Origen/Equipo','—')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.dataframe(results, use_container_width=True)
            else:
                st.warning("No se encontraron resultados para esa búsqueda.")

    with tab_ai:
        st.markdown("### 🧠 Centro de Autonomía Cuántica")
        st.info("Motores activos: Gemini, Groq, Mistral, Cohere, Hugging Face.")
        st.success("Sugerencia IA: El participante Marco Gardini Ríos ya está sentado en C1, proceder a prospección para C2.")

else:
    st.error("No se pudo conectar con la base de datos de Google Sheets.")
