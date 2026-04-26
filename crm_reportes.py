"""
CRM REPORTES — Sala de Guerra C1 E27 🔱
========================================
Dashboard profesional con datos en tiempo real.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import unicodedata, re

st.set_page_config(page_title="CRM Sala de Guerra 🔱", layout="wide", page_icon="🔱")
SHEET_ID = "1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y"
META_C1 = 325

# ── PREMIUM CSS ───────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*{font-family:'Inter',sans-serif}
.main{background:linear-gradient(160deg,#080b1a 0%,#0f1629 30%,#131b2e 60%,#0a0e1a 100%)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0c1222 0%,#111a2e 50%,#0a1020 100%);border-right:1px solid rgba(99,102,241,.15)}
[data-testid="stSidebar"] *{color:#94a3b8}
h1,h2,h3{color:#f1f5f9 !important;letter-spacing:-0.02em}
.stTabs [data-baseweb="tab-list"]{gap:4px;background:rgba(15,22,42,.6);padding:5px;border-radius:14px;border:1px solid rgba(99,102,241,.15);flex-wrap:wrap}
.stTabs [data-baseweb="tab"]{background:transparent;border-radius:10px;color:#64748b;font-weight:600;font-size:.8rem;padding:7px 14px;border:none}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:#fff!important;box-shadow:0 4px 15px rgba(99,102,241,.4)}
.glass{background:rgba(15,23,42,.7);backdrop-filter:blur(20px);border:1px solid rgba(99,102,241,.12);border-radius:18px;padding:22px;transition:all .3s ease}
.glass:hover{border-color:rgba(99,102,241,.35);box-shadow:0 8px 40px rgba(99,102,241,.12);transform:translateY(-1px)}
.kpi{text-align:center}
.kpi-val{font-size:2.6rem;font-weight:900;line-height:1;margin-bottom:4px}
.kpi-lab{font-size:.7rem;color:#64748b;text-transform:uppercase;letter-spacing:2px;font-weight:600}
.kpi-sub{font-size:.75rem;color:#475569;margin-top:2px}
.prog-wrap{background:rgba(30,41,59,.6);border-radius:14px;height:32px;overflow:hidden;border:1px solid rgba(99,102,241,.15);position:relative}
.prog-fill{height:100%;border-radius:14px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem;color:#fff;transition:width 1s cubic-bezier(.4,0,.2,1)}
.section-title{font-size:1.1rem;font-weight:700;color:#cbd5e1;margin:8px 0 12px;display:flex;align-items:center;gap:8px}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.7rem;font-weight:700;letter-spacing:.5px}
.badge-green{background:rgba(34,197,94,.15);color:#22c55e;border:1px solid rgba(34,197,94,.3)}
.badge-red{background:rgba(239,68,68,.15);color:#ef4444;border:1px solid rgba(239,68,68,.3)}
.badge-yellow{background:rgba(245,158,11,.15);color:#f59e0b;border:1px solid rgba(245,158,11,.3)}
.badge-blue{background:rgba(96,165,250,.15);color:#60a5fa;border:1px solid rgba(96,165,250,.3)}
.resp-card{background:rgba(30,41,59,.6);border:1px solid rgba(99,102,241,.15);border-radius:14px;padding:16px;margin:8px 0}
div[data-testid="stDataFrame"]{border:1px solid rgba(99,102,241,.15);border-radius:14px;overflow:hidden}
div[data-testid="stExpander"]{border:1px solid rgba(99,102,241,.12);border-radius:14px;overflow:hidden;background:rgba(15,23,42,.5)}
@media(max-width:768px){
  .kpi-val{font-size:1.8rem}
  .kpi-lab{font-size:.6rem;letter-spacing:1px}
  .glass{padding:14px;border-radius:12px}
  .stTabs [data-baseweb="tab"]{padding:6px 10px;font-size:.7rem}
}
</style>""", unsafe_allow_html=True)

def norm(t):
    if not t: return ""
    s = str(t).strip().upper()
    return re.sub(r'\s+', ' ', ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def kpi(val, label, color="#818cf8", sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="glass kpi"><div class="kpi-val" style="color:{color}">{val}</div><div class="kpi-lab">{label}</div>{sub_html}</div>'

def prog(pct, label, color="#6366f1"):
    w = min(max(pct, 3), 100)
    return f'<div class="prog-wrap"><div class="prog-fill" style="width:{w}%;background:linear-gradient(90deg,{color},{color}cc)">{label}</div></div>'

def chart_layout(fig, title="", h=380):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter", size=12), showlegend=True,
        legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=40 if title else 10, b=10, l=10, r=10), height=h,
        title=dict(text=title, font=dict(size=15, color="#e2e8f0")) if title else None,
        xaxis=dict(gridcolor="rgba(99,102,241,.08)", zeroline=False),
        yaxis=dict(gridcolor="rgba(99,102,241,.08)", zeroline=False))
    return fig

# ── CARGAR DATOS ──────────────────────────────────────────────
@st.cache_data(ttl=120)
def cargar_datos():
    try:
        from sync_cloud import conectar_sheets
        c = conectar_sheets(); sh = c.open_by_key(SHEET_ID)
        dp = pd.DataFrame(sh.worksheet("PRODUCTIVIDAD").get_all_records()).fillna("")
        dm = pd.DataFrame(sh.get_worksheet(0).get_all_records()).fillna("")
        try: dg = pd.DataFrame(sh.worksheet("GESTION_LLAMADAS").get_all_records()).fillna("")
        except: dg = pd.DataFrame()
        try: dr = pd.DataFrame(sh.worksheet("RESPUESTAS_IMO").get_all_records()).fillna("")
        except: dr = pd.DataFrame()
        return dp, dm, dg, dr
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

dp, dm, dg, dr = cargar_datos()
if dp.empty: st.warning("Sin datos. Ejecuta el robot."); st.stop()

# Normalizar Productividad
col_res = [c for c in dp.columns if "resultado" in c.lower() and "gesti" in c.lower()]
RES = col_res[0] if col_res else "Resultado Gestión"
dp["_res"] = dp[RES].astype(str).str.upper().str.strip()
dp["_cc"] = dp["CC_Reportada"].astype(str).str.upper().str.strip()
dp["_eq"] = dp["Equipo"].astype(str).str.upper().str.strip()
dp["_imo"] = dp["Nombre IMO"].astype(str).str.strip()
dp["_nom"] = (dp["NombreCompleto"].astype(str) + " " + dp["ApellidoCompleto"].astype(str)).str.strip()
dp["_asi"] = dp["Asistencia"].astype(str).str.upper().str.strip() if "Asistencia" in dp.columns else ""

# Normalizar Gestion Llamadas
if not dg.empty:
    dg["_cc"] = dg["CC_Alias"].astype(str).str.upper().str.strip()
    dg["_eq"] = dg["Equipo"].astype(str).str.upper().str.strip()
    dg["_1ra"] = dg["Primera_Llamada"].astype(str).str.upper().str.strip()
    dg["_2da"] = dg["Segunda_Llamada"].astype(str).str.upper().str.strip()
    dg["_asi"] = dg["Asistencia_C1"].astype(str).str.upper().str.strip()
    dg["_nom"] = (dg["Nombres"].astype(str) + " " + dg["Apellidos"].astype(str)).str.strip()

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🔱 Sala de Guerra")
    st.markdown(f"**C1 E27 — Lima**")
    st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.markdown("---")
    cc_f = st.selectbox("🎯 Coordinadora", ["TODAS", "DIANA", "JOYCE", "ZULEY"])
    eqs = sorted(dp["_eq"].unique().tolist())
    eq_f = st.multiselect("📋 Equipos", eqs, default=eqs)
    st.markdown("---")
    if st.button("🔄 Actualizar", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.markdown("---")
    st.caption("🔱 CREAR Poder Sin Límites Perú")

df = dp.copy()
if cc_f != "TODAS": df = df[df["_cc"] == cc_f]
if eq_f: df = df[df["_eq"].isin(eq_f)]

dg_f = dg.copy() if not dg.empty else pd.DataFrame()
if not dg_f.empty:
    if cc_f != "TODAS": dg_f = dg_f[dg_f["_cc"] == cc_f]

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "📞 Gestión", "👥 CCs", "🚨 NC", "💬 Respuestas IMO", "📋 Detalle"])

# ══════════════════════ TAB 1: DASHBOARD ══════════════════════
with tab1:
    st.markdown("## 📊 Sala de Guerra — C1 E27")
    # Asistencia
    sentados = len(df[df["_asi"] == "CONFIRMADO"])
    desertores = len(df[df["_asi"] == "DESERTOR"])
    tasa_d = round(desertores/(sentados+desertores)*100,1) if (sentados+desertores)>0 else 0
    pct_meta = round(sentados/META_C1*100,1) if META_C1>0 else 0
    faltan = max(META_C1-sentados, 0)
    # Px activos sin sentarse (Gestión)
    px_activos = len(dg_f) if not dg_f.empty else 0

    st.markdown('<div class="section-title">🏆 Asistencia REAL al C1 — Quiénes se sentaron</div>', True)
    st.caption("⚠️ Confirmado en llamada ≠ Sentado en C1")
    a1,a2,a3,a4,a5 = st.columns(5)
    with a1: st.markdown(kpi(sentados,"🪑 Sentados C1","#22c55e"), True)
    with a2: st.markdown(kpi(desertores,"💨 Desertores","#ef4444"), True)
    with a3: st.markdown(kpi(f"{tasa_d}%","📉 Deserción","#f59e0b"), True)
    with a4: st.markdown(kpi(px_activos,"📞 Px Activos","#60a5fa","Sin sentarse aún"), True)
    with a5: st.markdown(kpi("✅" if faltan==0 else faltan, "META" if faltan==0 else "Faltan Meta", "#22c55e" if faltan==0 else "#f59e0b"), True)

    st.markdown("<br>", True)
    st.markdown(f"### 🎯 Meta C1: {sentados}/{META_C1} SENTADOS")
    cbar = "#22c55e" if pct_meta>=80 else "#f59e0b" if pct_meta>=50 else "#ef4444"
    st.markdown(prog(min(pct_meta,100), f"{pct_meta}% ({sentados})", cbar), True)
    st.markdown("---")

    # Llamadas
    total=len(df); conf_ll=len(df[df["_res"]=="CONFIRMADO"]); nc=len(df[df["_res"]=="NO CONTESTAN"])
    pc=len(df[df["_res"]=="POR CONFIRMAR"]); sig=len(df[df["_res"]=="SIGUIENTE"]); ni=len(df[df["_res"]=="NO LE INTERESA"])

    st.markdown('<div class="section-title">📞 Productividad — Trabajo de Coordinadoras</div>', True)
    c1,c2,c3,c4,c5,c6=st.columns(6)
    with c1: st.markdown(kpi(conf_ll,"Confirm. Llamada","#60a5fa"), True)
    with c2: st.markdown(kpi(nc,"No Contestan","#ef4444"), True)
    with c3: st.markdown(kpi(pc,"Por Confirmar","#f59e0b"), True)
    with c4: st.markdown(kpi(sig,"Siguiente","#8b5cf6"), True)
    with c5: st.markdown(kpi(ni,"No Interesa","#64748b"), True)
    with c6: st.markdown(kpi(total,"Total Gestiones","#06b6d4"), True)

    st.markdown("<br>", True)
    g1,g2=st.columns(2)
    cmap={"CONFIRMADO":"#60a5fa","NO CONTESTAN":"#ef4444","POR CONFIRMAR":"#f59e0b","SIGUIENTE":"#8b5cf6","NO LE INTERESA":"#64748b"}
    with g1:
        es=df["_res"].value_counts().reset_index(); es.columns=["E","N"]; es=es[es["E"]!=""]
        fig=px.pie(es,values="N",names="E",hole=.6,color="E",color_discrete_map=cmap)
        st.plotly_chart(chart_layout(fig,"Resultado Llamadas",340), True)
    with g2:
        ad=df["_asi"].value_counts().reset_index(); ad.columns=["E","N"]; ad=ad[ad["E"]!=""]
        fig2=px.pie(ad,values="N",names="E",hole=.6,color="E",color_discrete_map={"CONFIRMADO":"#22c55e","DESERTOR":"#ef4444"})
        st.plotly_chart(chart_layout(fig2,"Asistencia REAL C1",340), True)

    eqs_d=df[df["_res"]!=""].groupby(["_eq","_res"]).size().reset_index(name="N")
    fig3=px.bar(eqs_d,x="_eq",y="N",color="_res",barmode="stack",color_discrete_map=cmap,labels={"_eq":"Equipo","_res":"Resultado"})
    st.plotly_chart(chart_layout(fig3,"Llamadas por Equipo",380), True)

# ══════════════════ TAB 2: GESTIÓN LLAMADAS ═══════════════════
with tab2:
    st.markdown("## 📞 Gestión de Llamadas — Px Activos sin Sentarse C1")
    st.caption("Fuente: reporte_detallegestion.php — Participantes que aún no se sientan")

    if dg_f.empty:
        st.warning("Sin datos de gestión. Ejecuta: `python robot_gestion_llamadas.py`")
    else:
        tot_g=len(dg_f)
        # 1ra Llamada
        pend1=len(dg_f[dg_f["_1ra"]=="PENDIENTE"]); conf1=len(dg_f[dg_f["_1ra"]=="CONFIRMADO"])
        nc1=len(dg_f[dg_f["_1ra"]=="NO CONTESTAN"]); pc1=len(dg_f[dg_f["_1ra"]=="POR CONFIRMAR"])
        sig1=len(dg_f[dg_f["_1ra"]=="SIGUIENTE"])
        # 2da Llamada
        pend2=len(dg_f[dg_f["_2da"]=="PENDIENTE"]); conf2=len(dg_f[dg_f["_2da"]=="CONFIRMADO"])

        st.markdown('<div class="section-title">📊 Resumen General</div>', True)
        k1,k2,k3=st.columns(3)
        with k1: st.markdown(kpi(tot_g,"Px Activos Total","#f472b6","Pendientes de sentarse"), True)
        with k2: st.markdown(kpi(f"{round((conf1/tot_g)*100)}%","Avance 1ra Llamada","#60a5fa",f"{conf1} confirmados"), True)
        with k3: st.markdown(kpi(f"{round((conf2/tot_g)*100)}%","Avance 2da Llamada","#8b5cf6",f"{conf2} confirmados"), True)

        st.markdown("---")
        st.markdown('<div class="section-title">📞 Primera Llamada</div>', True)
        p1,p2,p3,p4,p5=st.columns(5)
        with p1: st.markdown(kpi(pend1,"⏳ Pendiente","#64748b"), True)
        with p2: st.markdown(kpi(conf1,"✅ Confirmado","#22c55e"), True)
        with p3: st.markdown(kpi(nc1,"❌ No Contestan","#ef4444"), True)
        with p4: st.markdown(kpi(pc1,"🔶 Por Confirmar","#f59e0b"), True)
        with p5: st.markdown(kpi(sig1,"🔄 Siguiente","#8b5cf6"), True)

        avance1=round(((conf1+nc1+pc1+sig1)/tot_g)*100,1) if tot_g>0 else 0
        st.markdown(prog(avance1,f"1ra Llamada: {avance1}% contactados","#60a5fa"), True)

        st.markdown("<br>", True)
        st.markdown('<div class="section-title">📞 Segunda Llamada</div>', True)
        s1,s2,s3=st.columns(3)
        with s1: st.markdown(kpi(pend2,"⏳ Pendiente","#64748b"), True)
        with s2: st.markdown(kpi(conf2,"✅ Confirmado","#22c55e"), True)
        avance2_done=tot_g-pend2
        with s3: st.markdown(kpi(avance2_done,"Gestionados","#06b6d4"), True)
        avance2=round((avance2_done/tot_g)*100,1) if tot_g>0 else 0
        st.markdown(prog(avance2,f"2da Llamada: {avance2}%","#8b5cf6"), True)

        st.markdown("---")
        st.markdown('<div class="section-title">👥 Por Coordinadora</div>', True)
        for cc,color in [("DIANA","#f472b6"),("JOYCE","#60a5fa"),("ZULEY","#34d399")]:
            dc=dg_f[dg_f["_cc"]==cc] if not dg_f.empty else pd.DataFrame()
            if dc.empty: continue
            t=len(dc); c1v=len(dc[dc["_1ra"]=="CONFIRMADO"]); nc_v=len(dc[dc["_1ra"]=="NO CONTESTAN"])
            pe=len(dc[dc["_1ra"]=="PENDIENTE"]); ef=round((c1v/t)*100) if t>0 else 0
            emoji="🟢" if ef>=40 else "🟡" if ef>=20 else "🔴"
            with st.expander(f"{emoji} {cc} — {t} px | ✅{c1v} | ❌{nc_v} | ⏳{pe} pendientes",expanded=True):
                x1,x2,x3,x4=st.columns(4)
                with x1: st.metric("Total Px",t)
                with x2: st.metric("✅ Confirm 1ra",c1v)
                with x3: st.metric("❌ NC 1ra",nc_v)
                with x4: st.metric("⏳ Pendiente",pe)
                st.markdown(prog(ef,f"Avance: {ef}%",color), True)
                # Tabla por equipo
                eq_res=dc.groupby("_eq")["_1ra"].value_counts().unstack(fill_value=0)
                if not eq_res.empty:
                    st.dataframe(eq_res, use_container_width=True, height=150)

# ══════════════════ TAB 3: COORDINADORAS ══════════════════════
with tab3:
    st.markdown("## 👥 Detalle por Coordinadora")
    for cc,color in [("DIANA","#f472b6"),("JOYCE","#60a5fa"),("ZULEY","#34d399")]:
        dc=dp[dp["_cc"]==cc]; t=len(dc)
        cn=len(dc[dc["_res"]=="CONFIRMADO"]); ncv=len(dc[dc["_res"]=="NO CONTESTAN"])
        pcv=len(dc[dc["_res"]=="POR CONFIRMAR"]); sv=len(dc[dc["_res"]=="SIGUIENTE"])
        niv=len(dc[dc["_res"]=="NO LE INTERESA"])
        se=len(dc[dc["_asi"]=="CONFIRMADO"]); de_v=len(dc[dc["_asi"]=="DESERTOR"])
        ef=round(cn/t*100,1) if t>0 else 0; conv=round(se/cn*100,1) if cn>0 else 0
        emoji="🟢" if ef>=50 else "🟡" if ef>=30 else "🔴"
        with st.expander(f"{emoji} {cc} — 🪑{se} sentados | 📞{cn} confirm. | {t} gestiones",expanded=True):
            st.markdown("**🪑 Asistencia REAL:**")
            r1,r2,r3=st.columns(3)
            with r1: st.metric("🪑 Sentados",se)
            with r2: st.metric("💨 Desertores",de_v)
            with r3: st.metric("📊 Conversión",f"{conv}%")
            st.markdown("**📞 Llamadas:**")
            k1,k2,k3,k4,k5=st.columns(5)
            with k1: st.metric("📞 Confirm",cn)
            with k2: st.metric("❌ NC",ncv)
            with k3: st.metric("⏳ x Confirm",pcv)
            with k4: st.metric("🔄 Siguiente",sv)
            with k5: st.metric("🚫 No Interesa",niv)
            st.markdown(prog(ef,f"Efectividad: {ef}%",color), True)

# ══════════════════ TAB 4: NO CONTESTAN ═══════════════════════
with tab4:
    st.markdown("## 🚨 Participantes que No Contestan")
    st.caption("Contactar vía IMO para confirmar asistencia")
    df_nc=dp[dp["_res"]=="NO CONTESTAN"].copy()
    if df_nc.empty:
        st.success("🎉 Sin participantes NC.")
    else:
        imo_nc=df_nc.groupby("_imo").agg(NC=("_nom","count"),Px=("_nom",lambda x:", ".join(x.head(5)))).sort_values("NC",ascending=False).reset_index()
        imo_nc.columns=["IMO","NC","Participantes (5 primeros)"]
        st.dataframe(imo_nc, use_container_width=True, height=400)
        st.markdown("---")
        st.markdown("### 📱 Plantilla WhatsApp para IMO")
        imos=sorted(df_nc["_imo"].unique().tolist())
        imo_sel=st.selectbox("IMO:",["Todos"]+imos)
        dt=df_nc if imo_sel=="Todos" else df_nc[df_nc["_imo"]==imo_sel]
        pxl=dt["_nom"].tolist(); n=len(pxl)
        ptx="\n".join(f"  • {p}" for p in pxl[:20])
        if n>20: ptx+=f"\n  ...y {n-20} más"
        plantilla=f"🔔 *CREAR Poder Sin Límites Perú*\n\nHola {imo_sel},\n\nEstos enrolados tuyos *no contestan*:\n\n{ptx}\n\nTotal: *{n}*\n\n🙏 Contáctalos para confirmar C1 E27.\n\n— Equipo CREAR Lima 🔱"
        st.text_area("Plantilla:",plantilla,height=300)
        st.download_button("📥 CSV No Contestan",dt[["_nom","_imo","_eq","_cc"]].rename(columns={"_nom":"Px","_imo":"IMO","_eq":"Equipo","_cc":"CC"}).to_csv(index=False).encode("utf-8"),"nc.csv","text/csv",use_container_width=True)

# ══════════════════ TAB 5: RESPUESTAS IMO ═════════════════════
with tab5:
    st.markdown("## 💬 Respuestas de IMOs")
    st.caption("Respuestas recibidas de IMOs sobre participantes NC — para gestion de coordinadoras")

    if dr.empty:
        st.info("Sin respuestas de IMOs aun. Se llenara automaticamente cuando los IMOs respondan al bot.")
    else:
        # Filtro por CC
        cc_resp = st.selectbox("Filtrar por CC:", ["TODAS"] + sorted(dr["CC"].unique().tolist()), key="resp_cc")
        dr_f = dr if cc_resp == "TODAS" else dr[dr["CC"].str.upper() == cc_resp.upper()]

        # KPIs
        total_r = len(dr_f)
        pend = len(dr_f[dr_f["Estado"].str.upper() == "PENDIENTE_CC"])
        atend = total_r - pend
        r1, r2, r3 = st.columns(3)
        with r1: st.markdown(kpi(total_r, "Total Respuestas", "#60a5fa"), True)
        with r2: st.markdown(kpi(pend, "Pendientes CC", "#f59e0b"), True)
        with r3: st.markdown(kpi(atend, "Atendidas", "#22c55e"), True)

        st.markdown("---")
        # Tabla de respuestas
        st.dataframe(
            dr_f[["Fecha", "IMO", "Participante", "Respuesta", "CC", "Estado"]].reset_index(drop=True),
            use_container_width=True, height=500
        )

# ══════════════════ TAB 6: DETALLE ════════════════════════════
with tab6:
    st.markdown("## 📋 Detalle de Gestiones")
    f1,f2,f3=st.columns(3)
    with f1: rf=st.multiselect("Resultado:",df["_res"].unique().tolist())
    with f2: imf=st.multiselect("IMO:",sorted(df["_imo"].unique().tolist()))
    with f3: bus=st.text_input("🔍 Buscar:")
    dd=df.copy()
    if rf: dd=dd[dd["_res"].isin(rf)]
    if imf: dd=dd[dd["_imo"].isin(imf)]
    if bus: dd=dd[dd["_nom"].apply(norm).str.contains(norm(bus),na=False)]
    cols=[c for c in ["_nom","_res","_asi","_cc","_eq","_imo"] if c in dd.columns]
    st.dataframe(dd[cols].rename(columns={"_nom":"Participante","_res":"Resultado Llamada","_asi":"Asistencia C1","_cc":"CC","_eq":"Equipo","_imo":"IMO"}).reset_index(drop=True),use_container_width=True,height=600)
    st.download_button("📥 Exportar CSV",dd[cols].rename(columns={"_nom":"Px","_res":"Resultado","_asi":"Asistencia","_cc":"CC","_eq":"Equipo","_imo":"IMO"}).to_csv(index=False).encode("utf-8"),"detalle.csv","text/csv",use_container_width=True)
