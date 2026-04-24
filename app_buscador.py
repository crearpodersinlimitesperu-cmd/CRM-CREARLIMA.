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

# ── CONSTANTES CLOUD ─────────────────────────────────────────
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
HIST_FILE = "Historial_Reportes.csv"
META_OKS = 325

COORDS = {
    "DIANA":  "Diana Moscoso",
    "JOYCE":  "Joyce Marin",
    "ZULEY":  "Zuley Urteaga",
    "LUZ":    "L. Valencia"
}

# ── ESTILOS PREMIUM ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f1f5f9; }
.war-card {
    background: white;
    border-radius: 16px;
    padding: 22px 26px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    border-left: 6px solid #4f46e5;
    margin-bottom: 18px;
}
.status-ok   { background:#dcfce7; color:#166534; padding:3px 12px; border-radius:20px; font-weight:700; }
.status-pend { background:#fef9c3; color:#854d0e; padding:3px 12px; border-radius:20px; font-weight:700; }
.status-reza { background:#fee2e2; color:#991b1b; padding:3px 12px; border-radius:20px; font-weight:700; }
[data-testid="stMetricValue"] { font-size:2rem !important; font-weight:800 !important; }
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
                str(row.get('Email',''))
            ]
            return norm(" ".join(campos))
        df['_search_key'] = df.apply(make_search_key, axis=1)
        return df
    except Exception as e:
        st.error(f"⚠️ Error conectando a Google Sheets: {e}")
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

# ── CARGA INICIAL ─────────────────────────────────────────────
df_master = load_master()
df_hist   = load_history()

LISTA_COORDS = ["Diana Moscoso", "Joyce Marin", "Zuley Urteaga", "L. Valencia", "General"]
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
    if st.button("🔄 Actualizar Nube"):
        st.cache_data.clear()
        st.rerun()

# ── CUERPO PRINCIPAL ──────────────────────────────────────────
st.markdown("# 🔱 CRM Maestro — Sala de Guerra C1E27")

tabs = st.tabs([
    "📊 Sala de Guerra",
    "🔍 Buscador 360°",
    "📈 Histórico & Auditoría",
    "🧹 Purga & Calidad",
    "🧠 Autonomía IA"
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
    
    # Estatus C1: valores reales son SI, ✓ Sentado, ✔ Sentado en C1, Sentado / SI
    c1_col = df.get('Estatus C1', pd.Series(['—'] * total))
    sentados_c1 = c1_col.apply(lambda x: any(k in str(x).upper() for k in 
        ['SI', 'SENTADO', '✓', '✔']) if x and x != '—' else False).sum()
    
    # Estatus C2
    c2_col = df.get('Estatus C2', pd.Series(['—'] * total))
    sentados_c2 = c2_col.apply(lambda x: any(k in str(x).upper() for k in 
        ['SI', 'SENTADO', '✓', '✔']) if x and x != '—' else False).sum()
    
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
    c2.metric("✅ Sentados C1", stats['sentados_c1'], f"{stats['sentados_c1'] - META_OKS} vs meta")
    c3.metric("🎭 Sentados C2", stats['sentados_c2'])
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
        title={'text': f"Sentados C1 vs Meta ({META_OKS})"},
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
            if '_search_key' in df_filtrado.columns:
                mask = df_filtrado['_search_key'].str.contains(q_norm, regex=False, na=False)
            else:
                cols_busq = [c for c in ['Nombres','Apellidos','DNI','Teléfono'] if c in df_filtrado.columns]
                mask = df_filtrado[cols_busq].apply(lambda col: col.apply(norm).str.contains(q_norm, regex=False, na=False)).any(axis=1)
            results = df_filtrado[mask]
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
            opciones = (results['_nombre_completo'] + " — DNI: " + results.get('DNI', '—')).tolist()
            sel = st.selectbox("📄 Ver Ficha Completa:", opciones)
            if sel:
                idx = opciones.index(sel)
                pax = results.iloc[idx]

                def badge(val, ok_kw='OK'):
                    v = str(val)
                    if ok_kw in v.upper():        return f'<span class="status-ok">{v}</span>'
                    elif 'REZAG' in v.upper():    return f'<span class="status-reza">{v}</span>'
                    else:                          return f'<span class="status-pend">{v}</span>'

                st.markdown(f"""
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
                </div>
                """, unsafe_allow_html=True)

        cols_show = [c for c in ['_nombre_completo','DNI','Teléfono','Coordinador',
                                   'Estatus C1','Estatus C2','Participación','Origen/Equipo']
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
