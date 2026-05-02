@echo off
title Brasil Transparente - Iniciador

echo ========================================
echo   Brasil Transparente
echo   Iniciando backend e frontend...
echo ========================================

REM Inicia o backend (FastAPI)
echo [1/2] Iniciando backend em http://localhost:8000
start "Backend" cmd /k "cd backend && ..\.venv\Scripts\activate && uvicorn main:app --reload"

REM Aguarda 3 segundos para o backend subir
timeout /t 3 /nobreak > nul

REM Inicia o frontend (React)
echo [2/2] Iniciando frontend em http://localhost:5173
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   Ambientes iniciados!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ========================================
echo   Pressione qualquer tecla para sair (os terminais continuarão abertos)
pause > nul