#!/usr/bin/env python3
"""
🧪 TEST FRONTEND - FUNCIONALIDAD DE CARGA
Verifica si el problema está en el frontend o backend
"""
import webbrowser
import os
import time
from pathlib import Path

def test_frontend():
    """Abre el test standalone del frontend"""
    
    print("🧪 INICIANDO TEST DEL FRONTEND")
    print("=" * 40)
    
    # Ruta del archivo test
    test_file = Path(__file__).parent / "test_show_standalone.html"
    
    if not test_file.exists():
        print("❌ Error: No se encontró test_show_standalone.html")
        return False
    
    # Convertir a URL file://
    file_url = f"file://{test_file.absolute()}"
    
    print(f"📁 Archivo test: {test_file}")
    print(f"🌐 URL: {file_url}")
    print()
    print("🔍 INSTRUCCIONES DEL TEST:")
    print("1. Se abrirá una página web en tu navegador")
    print("2. Arrastra cualquier archivo Excel/CSV a la zona de carga")
    print("3. O haz clic en 'Seleccionar Archivo'")
    print("4. Observa el log de eventos en la parte inferior")
    print()
    print("✅ SI FUNCIONA: El problema está en el servidor/backend")
    print("❌ SI NO FUNCIONA: El problema está en el frontend/JavaScript")
    print()
    
    input("Presiona ENTER para abrir el test en el navegador...")
    
    try:
        # Abrir en navegador
        webbrowser.open(file_url)
        print("🚀 Test abierto en el navegador")
        print()
        print("📋 DIAGNÓSTICO:")
        print("- Si puedes seleccionar/arrastrar archivos → Frontend OK")
        print("- Si NO puedes seleccionar archivos → Frontend tiene problemas")
        print()
        print("📍 Después del test, revisa:")
        print("1. ¿Se detectaron los eventos de carga?")
        print("2. ¿Se mostró la información del archivo?")
        print("3. ¿Aparece 'TEST EXITOSO' en el log?")
        
        return True
        
    except Exception as e:
        print(f"❌ Error abriendo navegador: {e}")
        print(f"📖 Abre manualmente: {file_url}")
        return False

def diagnosticar_problema():
    """Diagnostica posibles problemas"""
    
    print("\n🔍 DIAGNÓSTICO DE PROBLEMAS COMUNES:")
    print("=" * 45)
    
    # Verificar archivos clave
    archivos_clave = [
        "templates/pricing_show.html",
        "api/main.py",
        "api/dynamic_pricing_show.py"
    ]
    
    print("📁 Verificando archivos clave:")
    for archivo in archivos_clave:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - NO ENCONTRADO")
    
    print(f"\n🐍 Verificando Python:")
    try:
        import sys
        print(f"   ✅ Python {sys.version}")
    except:
        print(f"   ❌ Error con Python")
    
    print(f"\n📦 Verificando dependencias:")
    dependencias = ['fastapi', 'pandas', 'openpyxl', 'uvicorn']
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - NO INSTALADO")
    
    print(f"\n💡 POSIBLES SOLUCIONES:")
    print("1. Si el frontend funciona pero el servidor no:")
    print("   → Instalar dependencias: pip install fastapi uvicorn pandas openpyxl")
    print("   → Iniciar servidor: python3 api/main.py")
    print()
    print("2. Si el frontend no funciona:")
    print("   → Problema en el JavaScript/HTML")
    print("   → Revisar consola del navegador (F12)")
    print()
    print("3. Si todo funciona localmente pero no en producción:")
    print("   → Problema de deployment/configuración")

if __name__ == "__main__":
    print("🎭" * 20)
    print("   TEST DE FUNCIONALIDAD DE CARGA")
    print("🎭" * 20 + "\n")
    
    # Ejecutar test del frontend
    test_exitoso = test_frontend()
    
    if test_exitoso:
        print("\n⏳ Esperando que completes el test...")
        print("(El navegador debería haberse abierto)")
        
        input("\nPresiona ENTER cuando hayas terminado el test...")
        
        # Diagnosticar problemas
        diagnosticar_problema()
    
    print(f"\n🏁 Test completado")
    print(f"📞 Si necesitas ayuda, reporta:")
    print(f"   1. ¿Se abrió el navegador?")
    print(f"   2. ¿Pudiste seleccionar/arrastrar archivos?")
    print(f"   3. ¿Qué mensajes aparecieron en el log?")