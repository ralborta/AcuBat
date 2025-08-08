#!/usr/bin/env python3
"""
Script de inicio para el Backend Acubat
"""

import uvicorn
import os
import sys

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Iniciando Backend Acubat...")
    print("🌐 Servidor disponible en: http://localhost:8000")
    print("📚 API Docs en: http://localhost:8000/docs")
    print("⏹️  Presiona Ctrl+C para detener")
    print("-" * 50)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 