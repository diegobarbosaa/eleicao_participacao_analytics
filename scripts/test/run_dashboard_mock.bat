@echo off
REM Script para testar dashboard com mocks (simula Render)
REM Define variaveis de ambiente para carregar dados mockados

set STREAMLIT_SERVER_HEADLESS=true
set RENDER=true

echo Iniciando dashboard com mocks...
streamlit run src/participacao_eleitoral/dashboard.py

echo Dashboard fechado.