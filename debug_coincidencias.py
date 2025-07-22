#!/usr/bin/env python3
import sys
import os

# Agregar el directorio api al path
sys.path.append('api')

from moura_rentabilidad import analizar_rentabilidades_moura

def debug_coincidencias():
    print("🔍 DEBUGGEANDO COINCIDENCIAS DE CÓDIGOS")
    print("=" * 60)
    
    # Analizar reglas de rentabilidad
    resultado_rentabilidades = analizar_rentabilidades_moura('Rentalibilidades-2.xlsx')
    
    # Simular algunos códigos de productos que podrían venir del archivo de precios
    codigos_prueba = [
        "VGM60HD/E",
        "VDA75PD", 
        "VDA95MD",
        "VA38JD",
        "VA34JD",
        "M18FD (100)",  # Este no debería coincidir
        "M22ED (100)",  # Este no debería coincidir
    ]
    
    print("📋 CÓDIGOS DE REGLAS DISPONIBLES:")
    print("Minorista:")
    for i, regla in enumerate(resultado_rentabilidades['reglas_minorista'][:10]):
        print(f"  {i+1}. {regla['codigo']}: {regla['markup']:.2f}%")
    
    print()
    print("Mayorista:")
    for i, regla in enumerate(resultado_rentabilidades['reglas_mayorista'][:10]):
        print(f"  {i+1}. {regla['codigo']}: {regla['markup']:.2f}%")
    
    print()
    print("🔍 VERIFICANDO COINCIDENCIAS:")
    
    for codigo_prueba in codigos_prueba:
        print(f"\n📦 Producto: {codigo_prueba}")
        
        # Buscar coincidencia exacta minorista
        regla_minorista_exacta = None
        for regla in resultado_rentabilidades['reglas_minorista']:
            if regla['codigo'] == codigo_prueba:
                regla_minorista_exacta = regla
                break
        
        # Buscar coincidencia exacta mayorista
        regla_mayorista_exacta = None
        for regla in resultado_rentabilidades['reglas_mayorista']:
            if regla['codigo'] == codigo_prueba:
                regla_mayorista_exacta = regla
                break
        
        # Buscar coincidencia por similitud minorista
        regla_minorista_similar = None
        for regla in resultado_rentabilidades['reglas_minorista']:
            if codigo_prueba.startswith(regla['codigo'][:3]) or regla['codigo'].startswith(codigo_prueba[:3]):
                regla_minorista_similar = regla
                break
        
        # Buscar coincidencia por similitud mayorista
        regla_mayorista_similar = None
        for regla in resultado_rentabilidades['reglas_mayorista']:
            if codigo_prueba.startswith(regla['codigo'][:3]) or regla['codigo'].startswith(codigo_prueba[:3]):
                regla_mayorista_similar = regla
                break
        
        print(f"  Minorista exacta: {regla_minorista_exacta['codigo'] if regla_minorista_exacta else 'NO'}")
        print(f"  Minorista similar: {regla_minorista_similar['codigo'] if regla_minorista_similar else 'NO'}")
        print(f"  Mayorista exacta: {regla_mayorista_exacta['codigo'] if regla_mayorista_exacta else 'NO'}")
        print(f"  Mayorista similar: {regla_mayorista_similar['codigo'] if regla_mayorista_similar else 'NO'}")

if __name__ == "__main__":
    debug_coincidencias() 