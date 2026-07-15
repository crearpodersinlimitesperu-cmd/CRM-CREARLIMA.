import io

code = """
# ══════════════════════════════════════════════════════════════
# TAB 9 — CASOS CERRADOS
# ══════════════════════════════════════════════════════════════
with tabs[9]:
    st.markdown('''
    <div style='background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:14px;
                padding:22px;margin-bottom:18px;border:1px solid #334155'>
        <h2 style='color:#38bdf8;margin:0;font-family:Outfit,sans-serif;'>
            ✅ Gestión de Casos Cerrados</h2>
        <p style='color:#94a3b8;margin:6px 0 0 0;'>
            Visualización de los casos resueltos por las coordinadoras extraídos directamente de Google Sheets.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    try:
        from sync_cloud import conectar_sheets
        client = conectar_sheets()
        if client:
            sh = client.open_by_key('1IoCYs1qfOTdn3XWyeK64jsUfAXOFgv3Wa6uJBM-lR2Y')
            try:
                ws_casos = sh.worksheet('CASOS')
                df_casos = pd.DataFrame(ws_casos.get_all_records()).fillna('')
                
                if not df_casos.empty:
                    st.success(f'✔️ Se encontraron {len(df_casos)} casos gestionados.')
                    st.dataframe(df_casos, use_container_width=True)
                    
                    csv_casos = df_casos.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label='📥 Descargar Casos Cerrados (CSV)',
                        data=csv_casos,
                        file_name='casos_cerrados.csv',
                        mime='text/csv'
                    )
                else:
                    st.info('No hay casos registrados aún.')
            except Exception as e:
                st.error(f'No se pudo cargar la hoja CASOS: {e}')
    except Exception as e:
        st.error(f'Error conectando a Sheets: {e}')
"""

with open("app_buscador.py", "a", encoding="utf-8") as f:
    f.write(code)

print("Append completed")
