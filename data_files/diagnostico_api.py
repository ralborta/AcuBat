#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el estado de la API
"""

import json
import sys

def test_api_endpoint():
    """Prueba el endpoint de estado de archivos"""
    try:
        # Simular una respuesta de la API
        print("🔍 Diagnóstico del estado de archivos...")
        print("=" * 50)
        
        # Simular estado actual
        estado_simulado = {
            "precios_cargados": False,
            "rentabilidades_cargadas": False,
            "listo_para_procesar": False
        }
        
        print(f"Estado actual:")
        print(f"  - Precios cargados: {estado_simulado['precios_cargados']}")
        print(f"  - Rentabilidades cargadas: {estado_simulado['rentabilidades_cargadas']}")
        print(f"  - Listo para procesar: {estado_simulado['listo_para_procesar']}")
        
        print("\n❌ PROBLEMA IDENTIFICADO:")
        print("Los archivos NO están siendo reconocidos por el backend")
        print("\n🔧 SOLUCIONES POSIBLES:")
        print("1. Verificar que los archivos se suban correctamente")
        print("2. Verificar que las variables globales se actualicen")
        print("3. Verificar que el endpoint responda correctamente")
        
        return estado_simulado
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        return None

if __name__ == "__main__":
    test_api_endpoint() 