#!/bin/bash

# Script para iniciar Dunita automáticamente
# Detecta si Docker está instalado y levanta los servicios

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║  DUNITA - Dune Dominion Multi-Agent Simulator          ║"
echo "║  Inicializador Automático con Docker                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker Desktop desde:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Verificar si docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Desktop."
    exit 1
fi

echo "✅ Docker está instalado"
echo ""

# Navegar al directorio del proyecto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📦 Levantando servicios con Docker Compose..."
docker-compose up -d

echo ""
echo "✅ Servicios iniciados!"
echo ""
echo "🌐 Aplicación web disponible en: http://localhost:5000"
echo "📊 Documentación disponible en: http://localhost:8080"
echo ""
echo "Para ver los logs ejecuta:  docker-compose logs -f"
echo "Para detener los servicios ejecuta:  docker-compose down"
echo ""

# Intentar abrir el navegador
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:5000" || true
elif command -v open &> /dev/null; then
    open "http://localhost:5000" || true
fi

echo "🏜️ ¡Disfruta jugando Dune Dominion!"