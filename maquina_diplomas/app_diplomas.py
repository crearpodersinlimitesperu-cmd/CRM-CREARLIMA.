import sys
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import pandas as pd
import tempfile
import pathlib
import os
from generador_diplomas import generar_diploma_unico, generar_diplomas_masivo

# Configurar página
st.set_page_config(page_title="Máquina de Diplomas", page_icon="🎓", layout="wide")

# Estilos básicos
st.markdown("""
<style>
    .main-header {
        font-family: 'Montserrat', sans-serif;
        color: #0f1c3f;
        text-align: center;
    }
    .sub-header {
        font-family: 'Cinzel', serif;
        color: #b8913e;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>CREAR Poder sin límites</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-header'>Fábrica Automática de Reconocimientos</h3>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📄 Generación Individual", "📂 Generación Masiva (Lotes)"])

with tab1:
    st.subheader("Crear Diploma Individual")
    with st.form("form_individual"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Receptor", placeholder="Ej: Juan Perez")
            rol = st.selectbox("Rol", ["Capitan", "PX Manager", "Trainer", "Staff"])
            curso = st.text_input("Curso / Entrenamiento", value="Transformación Cuántica Global")
            equipo = st.text_input("Nombre del Equipo", placeholder="Ej: Los Cuánticos")
            
            st.markdown("**Fechas del Entrenamiento**")
            fecha_inicio_input = st.date_input("Fecha de Inicio")
        with col2:
            sede = st.text_input("Sede", placeholder="Ej: LIMA")
            gerente_sede = st.text_input("Firma: Gerente de Sede", placeholder="Ej: Lic. Carlos Mendoza")
            num_equipo = st.text_input("Número de Equipo", placeholder="Ej: 01")
            
            st.markdown("&nbsp;") # Spacing
            fecha_final_input = st.date_input("Fecha de Finalización")
            
        # Formatear fechas
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        fecha_inicio = f"{fecha_inicio_input.day} de {meses[fecha_inicio_input.month - 1]} de {fecha_inicio_input.year}"
        fecha_final = f"{fecha_final_input.day} de {meses[fecha_final_input.month - 1]} de {fecha_final_input.year}"
        
        submitted = st.form_submit_button("🏆 Fabricar Diploma")
        
    if submitted:
        if not nombre or not sede or not gerente_sede:
            st.error("Por favor llena los campos principales (Nombre, Sede, Gerente).")
        else:
            with st.spinner("Generando diseño con gráficos de alta calidad..."):
                try:
                    pdf_path = generar_diploma_unico(nombre, rol, curso, equipo, num_equipo, sede, fecha_inicio, fecha_final, gerente_sede)
                    st.success(f"¡Diploma creado con éxito!")
                    with open(pdf_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=file,
                            file_name=f"{nombre.replace(' ', '_')}_Diploma.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    import traceback
                    st.error(f"Ocurrió un error:\n\n{traceback.format_exc()}")

with tab2:
    st.subheader("Producción en Masa")
    st.markdown("Sube tu archivo **CSV** con las siguientes columnas exactas: `Nombre`, `Rol`, `Curso`, `Sede`, `Fecha`.")
    
    uploaded_file = st.file_uploader("Elige un archivo CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("🚀 Iniciar Producción Masiva"):
                with st.spinner("Procesando lote. Esto tomará unos segundos por cada diploma..."):
                    # Guardar el CSV temporalmente
                    temp_dir = tempfile.mkdtemp()
                    temp_csv = pathlib.Path(temp_dir) / "upload.csv"
                    df.to_csv(temp_csv, index=False, encoding='utf-8-sig')
                    
                    zip_path = generar_diplomas_masivo(temp_csv)
                    
                    st.success("¡Lote procesado correctamente!")
                    with open(zip_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar Paquete Completo (ZIP)",
                            data=file,
                            file_name="Lote_Diplomas_CREAR.zip",
                            mime="application/zip"
                        )
        except Exception as e:
            st.error(f"Error procesando el archivo: {e}")
