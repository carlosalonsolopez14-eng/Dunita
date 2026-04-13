@echo off
REM Script para iniciar Dunita automáticamente en Windows
REM Detecta si Docker está instalado y levanta los servicios

cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  DUNITA - Dune Dominion Multi-Agent Simulator          ║
echo ║  Inicializador Automático con Docker                   ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado. Por favor instala Docker Desktop desde:
    echo    https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Verificar si docker-compose está instalado
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no está instalado. Por favor instala Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker está instalado
echo.

echo 📦 Levantando servicios con Docker Compose...
docker-compose up -d

if errorlevel 1 (
    echo ❌ Error al iniciar los servicios
    pause
    exit /b 1
)

echo.
echo ✅ Servicios iniciados!
echo.
echo 🌐 Aplicación web disponible en: http://localhost:5000
echo 📊 Documentación disponible en: http://localhost:8080
echo.
echo Para ver los logs ejecuta:  docker-compose logs -f
echo Para detener los servicios ejecuta:  docker-compose down
echo.

REM Intentar abrir el navegador
start http://localhost:5000

echo 🏜️ ¡Disfruta jugando Dune Dominion!
pause