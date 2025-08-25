#!/usr/bin/env python3
"""
🎭 TEST DEL PRICING SHOW COMPLETO
Script para probar todas las funcionalidades del show dinámico
"""
import os
import sys
import requests
import time
import tempfile
import pandas as pd

def crear_archivo_ejemplo():
    """Crea un archivo Excel de ejemplo para probar"""
    
    print("📝 Creando archivo Excel de ejemplo...")
    
    # Datos de ejemplo realistas
    datos = {
        'Codigo': ['M20GD-001', 'ACU-45-002', 'VT-E39-003', 'WIL-70-004', 'M32-87-005'],
        'Descripcion': [
            'Moura 20 Gold 45Ah',
            'AcuBat Premium 45Ah', 
            'Varta Blue Dynamic E39 70Ah',
            'Willard Standard 70Ah',
            'Moura 32-87 87Ah'
        ],
        'Marca': ['Moura', 'AcuBat', 'Varta', 'Willard', 'Moura'],
        'Precio_Base': [35000, 28000, 65000, 32000, 52000],
        'Stock': [45, 67, 23, 89, 34],
        'Capacidad': ['45Ah', '45Ah', '70Ah', '70Ah', '87Ah']
    }
    
    df = pd.DataFrame(datos)
    
    # Guardar archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        return tmp.name

def test_pricing_show_standalone():
    """Prueba el show sin servidor"""
    
    print("\n🧪 TEST 1: Show Standalone")
    print("=" * 40)
    
    try:
        # Importar y ejecutar directamente
        sys.path.append('api')
        from api.dynamic_pricing_show import DynamicPricingShow
        
        show = DynamicPricingShow()
        resultado = show.ejecutar_show_completo()
        
        print("✅ Show standalone ejecutado exitosamente")
        print(f"📊 Productos generados: {len(resultado.get('productos_generados', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en show standalone: {e}")
        return False

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    
    print("\n🧪 TEST 2: API Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Health check
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor activo")
        else:
            print("❌ Servidor no responde correctamente")
            return False
        
        # Test 2: Status del pricing show
        response = requests.get(f"{base_url}/api/pricing-show-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pricing show status: {data.get('status')}")
            print(f"   Capacidades: {len(data.get('capacidades', []))}")
        else:
            print("❌ Pricing show status falló")
            return False
        
        # Test 3: Página del show
        response = requests.get(f"{base_url}/show", timeout=5)
        if response.status_code == 200:
            print("✅ Página del show carga correctamente")
        else:
            print("❌ Página del show falló")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("   Asegúrate de ejecutar: python api/main.py")
        return False
    except Exception as e:
        print(f"❌ Error en API endpoints: {e}")
        return False

def test_file_upload():
    """Prueba el upload de archivo con show completo"""
    
    print("\n🧪 TEST 3: Upload de Archivo")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        # Crear archivo de ejemplo
        archivo_ejemplo = crear_archivo_ejemplo()
        print(f"📁 Archivo ejemplo creado: {archivo_ejemplo}")
        
        # Upload del archivo
        with open(archivo_ejemplo, 'rb') as f:
            files = {'file': ('ejemplo.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print("🚀 Subiendo archivo y ejecutando show...")
            response = requests.post(f"{base_url}/api/pricing-show-upload", files=files, timeout=30)
        
        # Limpiar archivo temporal
        os.unlink(archivo_ejemplo)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload exitoso: {data.get('status')}")
            print(f"   Archivo procesado: {data.get('archivo_procesado')}")
            
            # Verificar resultados
            resultado = data.get('resultado', {})
            metricas = resultado.get('metricas_impacto', {})
            resumen = metricas.get('resumen_general', {})
            
            if resumen:
                print(f"📊 Productos generados: {resumen.get('productos_generados', 0)}")
                print(f"💰 Revenue anual: ${resumen.get('revenue_anual_proyectado', 0):,}")
                print(f"📈 Margen promedio: {resumen.get('margen_promedio', 0):.1f}%")
            
            return True
        else:
            print(f"❌ Upload falló: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error en upload: {e}")
        return False

def mostrar_urls_importantes():
    """Muestra las URLs importantes para la demo"""
    
    print("\n🌐 URLs IMPORTANTES PARA LA DEMO:")
    print("=" * 45)
    print("🎭 SHOW PRINCIPAL: http://localhost:8000/show")
    print("📊 Dashboard Demo: http://localhost:8000/demo") 
    print("🏠 Sistema Principal: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")

def main():
    """Función principal de testing"""
    
    print("🎭" * 25)
    print("   TEST COMPLETO - ACUBAT PRICING SHOW")
    print("🎭" * 25 + "\n")
    
    resultados = []
    
    # Test 1: Show standalone
    resultado1 = test_pricing_show_standalone()
    resultados.append(("Show Standalone", resultado1))
    
    # Test 2: API endpoints
    resultado2 = test_api_endpoints()
    resultados.append(("API Endpoints", resultado2))
    
    # Test 3: Upload con show
    if resultado2:  # Solo si el servidor está activo
        resultado3 = test_file_upload()
        resultados.append(("Upload + Show", resultado3))
    
    # Resumen final
    print("\n📋 RESUMEN DE TESTS:")
    print("=" * 30)
    
    todos_ok = True
    for nombre, resultado in resultados:
        status = "✅ OK" if resultado else "❌ FALLO"
        print(f"   {nombre}: {status}")
        if not resultado:
            todos_ok = False
    
    print(f"\n🎯 RESULTADO GENERAL: {'✅ TODOS LOS TESTS OK' if todos_ok else '❌ HAY TESTS FALLIDOS'}")
    
    if todos_ok:
        mostrar_urls_importantes()
        print("\n🚀 SISTEMA LISTO PARA DEMO CON CLIENTE")
        print("💡 Ejecuta: python api/main.py")
        print("🎭 Luego ve a: http://localhost:8000/show")
    else:
        print("\n🔧 REVISAR ERRORES ANTES DE LA DEMO")
    
    return todos_ok

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")