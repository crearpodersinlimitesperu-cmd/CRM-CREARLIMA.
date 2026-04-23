@echo off
title CRM MAESTRO CREAR LIMA - Centro de Mando
echo 🔱 Iniciando Centro de Inteligencia CPSL...
echo 🛡️ Cargando Sala de Guerra y Auditoria Web...
cd /d "%~dp0"
python -m streamlit run app_buscador.py --server.port 8515
pause
