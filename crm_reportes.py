"""
CRM REPORTES — Dashboard Profesional de Gestión C1 E27
======================================================
Sala de Guerra en tiempo real para seguimiento de llamadas
por coordinadora, con métricas de confirmados, NC, pendientes.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import unicodedata, re, os

# ── CONFIG ────────────────────────────────────────────────────
st.set_page_config(page_title="CRM Reportes C1 E27 🔱", layout="wide", page_icon="🔱")
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"
META_C1 = 325

# ── ESTILOS ───────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
* { font-family: 'Inter', sans-serif; }
.main { background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0d1117 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f1629 0%, #1a2332 100%); border-right: 1px solid #2d3748; }
.metric-card { background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
    border: 1px solid rgba(99,102,241,0.3); border-radius: 16px; padding: 20px;
    text-align: center; backdrop-filter: blur(10px); transition: all 0.3s; }
.metric-card:hover { border-color: rgba(99,102,241,0.7); transform: translateY(-2px); box-shadow: 0 8px 32px rgba(99,102,241,0.2); }
.metric-value { font-size: 2.8rem; font-weight: 900; background: linear-gradient(135deg, #818cf8, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px; }
.cc-card { background: rgba(30,41,59,0.8); border: 1px solid rgba(99,102,241,0.2); border-radius: 14px; padding: 18px; margin: 8px 0; }
.cc-diana { border-left: 4px solid #f472b6; }
.cc-joyce { border-left: 4px solid #60a5fa; }
.cc-zuley { border-left: 4px solid #34d399; }
h1, h2, h3 { color: #e2e8f0 !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background: rgba(30,41,59,0.6); border-radius: 8px; color: #94a3b8; border: 1px solid rgba(99,102,241,0.2); }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #4f46e5, #6366f1) !important; color: white !important; }
.progress-bar { background: rgba(30,41,59,0.8); border-radius: 12px; height: 28px; overflow: hidden; border: 1px solid rgba(99,102,241,0.3); }
.progress-fill { height: 100%; border-radius: 12px; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem; color: white; transition: width 0.8s ease; }
div[data-testid="stDataFrame"] { border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; overflow: hidden; }
</style>""", unsafe_allow_html=True)

def norm(t):
    if not t: return ""
    s = str(t).strip().upper()
    return re.sub(r'\s+', ' ', ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')).strip()

@st.cache_data(ttl=120)
def cargar_datos():
    """Carga Productividad, Master y Gestion Llamadas desde Google Sheets."""
    try:
        from sync_cloud import conectar_sheets
        c = conectar_sheets()
        sh = c.open_by_key(SHEET_ID)
        ws_p = sh.worksheet("PRODUCTIVIDAD")
        dp = pd.DataFrame(ws_p.get_all_records()).fillna("")
        ws_m = sh.get_worksheet(0)
        dm = pd.DataFrame(ws_m.get_all_records()).fillna("")
        # Gestion de Llamadas (px activos sin sentarse)
        try:
            ws_g = sh.worksheet("GESTION_LLAMADAS")
            dg = pd.DataFrame(ws_g.get_all_records()).fillna("")
        except:
            dg = pd.DataFrame()
        return dp, dm, dg
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def metric_html(valor, label, color="#818cf8"):
    return f"""<div class="metric-card">
        <div class="metric-value" style="background:linear-gradient(135deg,{color},{color}dd);-webkit-background-clip:text;">{valor}</div>
        <div class="metric-label">{label}</div></div>"""

def progress_html(pct, label, color="#6366f1"):
    w = min(max(pct, 2), 100)
    return f"""<div class="progress-bar"><div class="progress-fill" style="width:{w}%;background:linear-gradient(90deg,{color},{color}bb);">{label}</div></div>"""

# ── CARGAR DATOS ──────────────────────────────────────────────
dp, dm, dg = cargar_datos()

if dp.empty:
    st.warning("⚠️ Sin datos de productividad. Ejecuta el robot primero.")
    st.stop()

# Normalizar columnas
if "Resultado Gestión" not in dp.columns and "Resultado Gesti\u00f3n" not in dp.columns:
    for c in dp.columns:
        if "resultado" in c.lower():
            dp.rename(columns={c: "Resultado Gestión"}, inplace=True)
            break

col_res = [c for c in dp.columns if "resultado" in c.lower() and "gesti" in c.lower()]
if col_res:
    RES_COL = col_res[0]
else:
    RES_COL = "Resultado Gestión"

dp["_res"] = dp[RES_COL].astype(str).str.upper().str.strip()
dp["_cc"] = dp["CC_Reportada"].astype(str).str.upper().str.strip()
dp["_equipo"] = dp["Equipo"].astype(str).str.upper().str.strip()
dp["_imo"] = dp["Nombre IMO"].astype(str).str.strip()
dp["_nombre"] = (dp["NombreCompleto"].astype(str) + " " + dp["ApellidoCompleto"].astype(str)).str.strip()
dp["_asist"] = dp["Asistencia"].astype(str).str.upper().str.strip() if "Asistencia" in dp.columns else ""

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🔱 CRM Reportes")
    st.markdown(f"**C1 E27 — Lima**")
    st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.markdown("---")
    
    cc_filter = st.selectbox("🎯 Coordinadora", ["TODAS", "DIANA", "JOYCE", "ZULEY"])
    equipos_disp = sorted(dp["_equipo"].unique().tolist())
    eq_filter = st.multiselect("📋 Equipos", equipos_disp, default=equipos_disp)
    
    st.markdown("---")
    if st.button("🔄 Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Filtrar
df = dp.copy()
if cc_filter != "TODAS":
    df = df[df["_cc"] == cc_filter]
if eq_filter:
    df = df[df["_equipo"].isin(eq_filter)]

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📞 Gestion Llamadas", "👥 Por Coordinadora", "📞 No Contestan", "📋 Detalle"])

# ══════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD GENERAL
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 📊 Sala de Guerra — C1 E27")
    
    # ── ASISTENCIA C1 (quiénes REALMENTE se sentaron) ──
    sentados = len(df[df["_asist"] == "CONFIRMADO"])
    desertores = len(df[df["_asist"] == "DESERTOR"])
    sin_asist = len(df[df["_asist"] == ""])
    
    # ── RESULTADO LLAMADAS (gestión telefónica) ──
    total = len(df)
    conf_llamada = len(df[df["_res"] == "CONFIRMADO"])
    nc = len(df[df["_res"] == "NO CONTESTAN"])
    por_confirmar = len(df[df["_res"] == "POR CONFIRMAR"])
    siguiente = len(df[df["_res"] == "SIGUIENTE"])
    no_interesa = len(df[df["_res"] == "NO LE INTERESA"])
    
    # ═══ SECCIÓN 1: ASISTENCIA REAL C1 (lo que importa) ═══
    st.markdown("### 🏆 Asistencia REAL al C1 — Quiénes se sentaron")
    st.caption("⚠️ Esta es la métrica real. 'Confirmado en llamada' ≠ 'Sentado en C1'")
    
    a1, a2, a3, a4 = st.columns(4)
    with a1: st.markdown(metric_html(sentados, "🪑 Sentados C1", "#22c55e"), unsafe_allow_html=True)
    with a2: st.markdown(metric_html(desertores, "💨 Desertores", "#ef4444"), unsafe_allow_html=True)
    with a3: st.markdown(metric_html(sin_asist, "⏳ Sin registro", "#64748b"), unsafe_allow_html=True)
    with a4:
        tasa_deser = round((desertores / (sentados + desertores)) * 100, 1) if (sentados + desertores) > 0 else 0
        st.markdown(metric_html(f"{tasa_deser}%", "📉 Tasa Deserción", "#f59e0b"), unsafe_allow_html=True)
    
    # Barra de progreso META (basada en SENTADOS, no en llamadas)
    pct_meta = round((sentados / META_C1) * 100, 1) if META_C1 > 0 else 0
    faltan = max(META_C1 - sentados, 0)
    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1:
        st.markdown(f"### 🎯 Meta C1: {sentados}/{META_C1} SENTADOS")
        color_bar = "#22c55e" if pct_meta >= 80 else "#f59e0b" if pct_meta >= 50 else "#ef4444"
        st.markdown(progress_html(min(pct_meta, 100), f"{pct_meta}% ({sentados} sentados)", color_bar), unsafe_allow_html=True)
    with col_prog2:
        st.markdown(metric_html(faltan if faltan > 0 else "✅ META", "Faltan para Meta" if faltan > 0 else "¡META LOGRADA!", "#f59e0b" if faltan > 0 else "#22c55e"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ═══ SECCIÓN 2: LLAMADAS (trabajo de coordinadoras) ═══
    st.markdown("### 📞 Resultado de Llamadas — Trabajo de Coordinadoras")
    st.caption("Esto mide el esfuerzo de gestión telefónica, NO la asistencia real")
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.markdown(metric_html(conf_llamada, "📞 Confirmados Llamada", "#60a5fa"), unsafe_allow_html=True)
    with c2: st.markdown(metric_html(nc, "❌ No Contestan", "#ef4444"), unsafe_allow_html=True)
    with c3: st.markdown(metric_html(por_confirmar, "⏳ Por Confirmar", "#f59e0b"), unsafe_allow_html=True)
    with c4: st.markdown(metric_html(siguiente, "🔄 Siguiente", "#3b82f6"), unsafe_allow_html=True)
    with c5: st.markdown(metric_html(no_interesa, "🚫 No Interesa", "#8b5cf6"), unsafe_allow_html=True)
    with c6: st.markdown(metric_html(total, "📞 Total Gestiones", "#06b6d4"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos
    col_g1, col_g2 = st.columns(2)
    color_map = {"CONFIRMADO": "#60a5fa", "NO CONTESTAN": "#ef4444", "POR CONFIRMAR": "#f59e0b",
                 "SIGUIENTE": "#3b82f6", "NO LE INTERESA": "#8b5cf6", "YA ASISTIO A UN ENTRENAMIENTO": "#06b6d4"}
    
    with col_g1:
        estados = df["_res"].value_counts().reset_index()
        estados.columns = ["Estado", "Cantidad"]
        estados = estados[estados["Estado"] != ""]
        fig_donut = px.pie(estados, values="Cantidad", names="Estado", hole=0.55,
                           color="Estado", color_discrete_map=color_map)
        fig_donut.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                font=dict(color="#e2e8f0", family="Inter"), showlegend=True,
                                legend=dict(font=dict(size=11)), margin=dict(t=30, b=10, l=10, r=10),
                                title=dict(text="Resultado de Llamadas", font=dict(size=16)))
        st.plotly_chart(fig_donut, use_container_width=True)
    
    with col_g2:
        # Donut de asistencia real
        asist_data = df["_asist"].value_counts().reset_index()
        asist_data.columns = ["Estado", "Cantidad"]
        asist_data = asist_data[asist_data["Estado"] != ""]
        color_asist = {"CONFIRMADO": "#22c55e", "DESERTOR": "#ef4444"}
        fig_asist = px.pie(asist_data, values="Cantidad", names="Estado", hole=0.55,
                           color="Estado", color_discrete_map=color_asist)
        fig_asist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                font=dict(color="#e2e8f0", family="Inter"), showlegend=True,
                                margin=dict(t=30, b=10, l=10, r=10),
                                title=dict(text="Asistencia REAL al C1", font=dict(size=16)))
        st.plotly_chart(fig_asist, use_container_width=True)
    
    # Barras por equipo
    eq_stats = df[df["_res"] != ""].groupby(["_equipo", "_res"]).size().reset_index(name="Cantidad")
    fig_eq = px.bar(eq_stats, x="_equipo", y="Cantidad", color="_res", barmode="stack",
                    color_discrete_map=color_map, labels={"_equipo": "Equipo", "_res": "Resultado Llamada"})
    fig_eq.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(color="#e2e8f0", family="Inter"),
                          xaxis=dict(gridcolor="rgba(99,102,241,0.1)"), yaxis=dict(gridcolor="rgba(99,102,241,0.1)"),
                          margin=dict(t=40, b=10), height=400,
                          title=dict(text="Llamadas por Equipo", font=dict(size=16)))
    st.plotly_chart(fig_eq, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2: POR COORDINADORA
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 👥 Detalle por Coordinadora")
    
    for cc_name, css_class, color in [("DIANA", "cc-diana", "#f472b6"), ("JOYCE", "cc-joyce", "#60a5fa"), ("ZULEY", "cc-zuley", "#34d399")]:
        dc = dp[dp["_cc"] == cc_name]
        tot = len(dc)
        # LLAMADAS
        conf = len(dc[dc["_res"] == "CONFIRMADO"])
        nc_c = len(dc[dc["_res"] == "NO CONTESTAN"])
        pconf = len(dc[dc["_res"] == "POR CONFIRMAR"])
        sig = len(dc[dc["_res"] == "SIGUIENTE"])
        ni = len(dc[dc["_res"] == "NO LE INTERESA"])
        # ASISTENCIA REAL
        sent_c = len(dc[dc["_asist"] == "CONFIRMADO"])
        des_c = len(dc[dc["_asist"] == "DESERTOR"])
        efect = round((conf / tot) * 100, 1) if tot > 0 else 0
        conv = round((sent_c / conf) * 100, 1) if conf > 0 else 0
        
        with st.expander(f"{'🟢' if efect >= 50 else '🟡' if efect >= 30 else '🔴'} {cc_name} — 🪑 {sent_c} sentados | 📞 {conf} confirmados llamada | {tot} gestiones", expanded=True):
            st.markdown("**🪑 Asistencia REAL C1:**")
            r1, r2, r3 = st.columns(3)
            with r1: st.metric("🪑 Sentados C1", sent_c)
            with r2: st.metric("💨 Desertores", des_c)
            with r3: st.metric("📊 Conversión Llamada→Sentado", f"{conv}%")
            
            st.markdown("**📞 Resultado de Llamadas:**")
            k1, k2, k3, k4, k5 = st.columns(5)
            with k1: st.metric("📞 Confirmados Llamada", conf)
            with k2: st.metric("❌ No Contestan", nc_c)
            with k3: st.metric("⏳ Por Confirmar", pconf)
            with k4: st.metric("🔄 Siguiente", sig)
            with k5: st.metric("🚫 No Interesa", ni)
            
            st.markdown(progress_html(efect, f"Efectividad llamadas: {efect}%", color), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3: NO CONTESTAN + PLANTILLA IMO
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 📞 Participantes que No Contestan")
    st.markdown("_Estos participantes necesitan ser contactados por sus IMOs_")
    
    df_nc = dp[dp["_res"] == "NO CONTESTAN"].copy()
    
    if df_nc.empty:
        st.success("🎉 No hay participantes sin contactar.")
    else:
        # Resumen por IMO
        st.markdown("### 📊 No Contestan por IMO")
        imo_nc = df_nc.groupby("_imo").agg(
            Cantidad=("_nombre", "count"),
            Participantes=("_nombre", lambda x: ", ".join(x.head(5)))
        ).sort_values("Cantidad", ascending=False).reset_index()
        imo_nc.columns = ["IMO", "NC", "Participantes (primeros 5)"]
        st.dataframe(imo_nc, use_container_width=True, height=400)
        
        st.markdown("---")
        st.markdown("### 📱 Generador de Plantilla para IMOs")
        
        imos_lista = df_nc["_imo"].unique().tolist()
        imo_sel = st.selectbox("Selecciona un IMO:", ["Todos"] + sorted(imos_lista))
        
        if imo_sel == "Todos":
            df_tpl = df_nc
        else:
            df_tpl = df_nc[df_nc["_imo"] == imo_sel]
        
        # Generar plantilla
        participantes_list = df_tpl["_nombre"].tolist()
        n_px = len(participantes_list)
        px_txt = "\n".join(f"  • {p}" for p in participantes_list[:20])
        if n_px > 20:
            px_txt += f"\n  ... y {n_px - 20} más"
        
        plantilla = f"""🔔 *Aviso importante — CREAR Poder Sin Límites Perú*

Hola {imo_sel if imo_sel != 'Todos' else 'IMO'},

Te escribimos porque los siguientes enrolados tuyos *no contestan* nuestras llamadas para el entrenamiento C1 E27:

{px_txt}

Total: *{n_px} participantes*

🙏 Te pedimos por favor que los contactes y les confirmes su asistencia al próximo entrenamiento.

Es muy importante que todos asistan. Tu apoyo es fundamental. 💪

— Equipo CREAR Lima 🔱"""
        
        st.text_area("📋 Plantilla generada (copia y envía al IMO):", plantilla, height=350)
        
        st.download_button(
            "📥 Descargar lista NC como CSV",
            df_nc[["_nombre", "_imo", "_equipo", "_cc"]].rename(columns={
                "_nombre": "Participante", "_imo": "IMO", "_equipo": "Equipo", "_cc": "Coordinadora"
            }).to_csv(index=False).encode("utf-8"),
            "nc_participantes.csv", "text/csv", use_container_width=True
        )

# ══════════════════════════════════════════════════════════════
# TAB 4: DETALLE COMPLETO
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📋 Detalle de Gestiones")
    
    # Filtros
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        res_filter = st.multiselect("Resultado:", df["_res"].unique().tolist())
    with fc2:
        imo_filter = st.multiselect("IMO:", sorted(df["_imo"].unique().tolist()))
    with fc3:
        buscar = st.text_input("🔍 Buscar participante:")
    
    df_det = df.copy()
    if res_filter:
        df_det = df_det[df_det["_res"].isin(res_filter)]
    if imo_filter:
        df_det = df_det[df_det["_imo"].isin(imo_filter)]
    if buscar:
        b = norm(buscar)
        df_det = df_det[df_det["_nombre"].apply(norm).str.contains(b, na=False)]
    
    cols_show = ["_nombre", "_res", "_cc", "_equipo", "_imo", "Fecha Gestión"]
    cols_rename = {"_nombre": "Participante", "_res": "Resultado", "_cc": "CC", "_equipo": "Equipo", "_imo": "IMO"}
    
    available_cols = [c for c in cols_show if c in df_det.columns]
    st.dataframe(
        df_det[available_cols].rename(columns=cols_rename).reset_index(drop=True),
        use_container_width=True, height=600
    )
    
    st.download_button(
        "📥 Exportar todo a CSV",
        df_det[available_cols].rename(columns=cols_rename).to_csv(index=False).encode("utf-8"),
        "gestiones_detalle.csv", "text/csv", use_container_width=True
    )
