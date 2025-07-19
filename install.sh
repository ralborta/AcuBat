#!/bin/bash

echo "🚀 Instalando Backend Acubat..."

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p data static

# Crear archivo de ejemplo
echo "📄 Creando archivo de ejemplo..."
python3 -c "
import sys
sys.path.append('.')
from api.parser import ExcelParser
parser = ExcelParser()
parser.crear_archivo_ejemplo()
print('✅ Archivo de ejemplo creado exitosamente')
"

echo "✅ Instalación completada!"
echo ""
echo "🎯 Para ejecutar el servidor:"
echo "   source venv/bin/activate"
echo "   uvicorn api.main:app --reload"
echo ""
echo "🌐 Accede a: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs" 