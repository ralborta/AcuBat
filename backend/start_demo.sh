#!/bin/bash

echo "🚀 Iniciando AcuBat Demo - Modo SQLite"
echo "========================================"

# Verificar que estemos en el directorio correcto
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Debes ejecutar este script desde el directorio backend/"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    exit 1
fi

# Verificar dependencias
echo "📦 Verificando dependencias..."
if ! python3 -c "import fastapi, sqlalchemy" &> /dev/null; then
    echo "❌ Error: Faltan dependencias. Instala con: pip install -r requirements.txt"
    exit 1
fi

# Configurar variables de entorno para demo
echo "⚙️  Configurando modo demo..."
export DEMO_MODE=true
export DATABASE_URL="sqlite:///:memory:"
export DEBUG=true

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env para demo..."
    cat > .env << EOF
# Configuración para DEMO - SQLite en memoria
DEMO_MODE=true
DATABASE_URL=sqlite:///:memory:

# Configuración de la aplicación
DEBUG=true
ENVIRONMENT=development
PORT=8000

# Seguridad (valores de demo)
SECRET_KEY=demo-secret-key-2024
API_SECRET=demo-api-secret-2024

# CORS
CORS_ORIGINS=https://acubat.vercel.app,https://acubat-production.up.railway.app

# Almacenamiento
UPLOAD_DIR=/app/uploads

# Límites
MAX_FILE_SIZE=52428800
MAX_UPLOAD_FILES=10

# QA Gates
QA_GLOBAL_THRESHOLD=0.08
QA_SKU_THRESHOLD=0.15
AUTO_PUBLISH=false

# Logging
LOG_LEVEL=INFO
EOF
    echo "✅ Archivo .env creado"
else
    echo "✅ Archivo .env ya existe"
fi

# Iniciar la aplicación
echo "🚀 Iniciando AcuBat en modo demo..."
echo "📊 Base de datos: SQLite en memoria"
echo "🌐 URL: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🔍 Demo data: http://localhost:8000/demo/data"
echo ""
echo "Presiona Ctrl+C para detener"
echo "========================================"

# Ejecutar la aplicación
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
