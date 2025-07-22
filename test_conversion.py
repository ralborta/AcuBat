#!/usr/bin/env python3
import pandas as pd
import sys
import os

# Agregar el directorio api al path
sys.path.append('api')

from moura_rentabilidad import _convertir_porcentaje

def test_conversion():
    print("🧪 PRUEBA DE CONVERSIÓN DE PORCENTAJES")
    print("=" * 50)
    
    # Valores de prueba basados en el diagnóstico
    valores_prueba = [
        0.22154301680813168,  # M18FD Minorista
        0.1382771098001326,   # M18FD Rent Minorista
        0.5998796239724281,   # M18FD Mayorista
        0.3749529745762712,   # M18FD Rent Mayorista
        0.17229496031043454,  # M22ED Minorista
        0.10207617145379357,  # M22ED Rent Minorista
        0.5998661681418553,   # M22ED Mayorista
        0.3749477175572519,   # M22ED Rent Mayorista
    ]
    
    print("Valor Original | Valor Convertido | Es Porcentaje")
    print("-" * 50)
    
    for valor in valores_prueba:
        convertido = _convertir_porcentaje(valor)
        es_porcentaje = "SÍ" if convertido > 1 else "NO"
        print(f"{valor:12.6f} | {convertido:14.2f} | {es_porcentaje}")
    
    print()
    print("📊 VERIFICACIÓN:")
    print("Los valores deberían ser:")
    print("  M18FD Minorista: ~22.15% (no 0.22%)")
    print("  M18FD Mayorista: ~59.99% (no 0.60%)")
    print("  M22ED Minorista: ~17.23% (no 0.17%)")
    print("  M22ED Mayorista: ~59.99% (no 0.60%)")

if __name__ == "__main__":
    test_conversion() 