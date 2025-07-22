#!/usr/bin/env python3
import sys
import os

# Agregar el directorio api al path
sys.path.append('api')

from moura_rentabilidad import analizar_rentabilidades_moura

def test_columnas_correctas():
    print("🧪 PRUEBA DE COLUMNAS CORREGIDAS")
    print("=" * 50)
    
    # Analizar el archivo con las columnas corregidas
    resultado = analizar_rentabilidades_moura('Rentalibilidades-2.xlsx')
    
    print(f"📊 Reglas Minorista encontradas: {len(resultado['reglas_minorista'])}")
    print(f"📊 Reglas Mayorista encontradas: {len(resultado['reglas_mayorista'])}")
    print()
    
    print("🔍 PRIMERAS 5 REGLAS MINORISTA (Columna Y):")
    for i, regla in enumerate(resultado['reglas_minorista'][:5]):
        print(f"  {i+1}. {regla['codigo']}: Markup {regla['markup']:.2f}%, Rentabilidad {regla['rentabilidad']:.2f}%")
    
    print()
    print("🔍 PRIMERAS 5 REGLAS MAYORISTA (Columna Q):")
    for i, regla in enumerate(resultado['reglas_mayorista'][:5]):
        print(f"  {i+1}. {regla['codigo']}: Markup {regla['markup']:.2f}%, Rentabilidad {regla['rentabilidad']:.2f}%")
    
    print()
    print("🎯 VERIFICACIÓN:")
    print("Los markups deberían ser:")
    print("  Minorista: ~93%, ~82%, ~86%, etc. (valores altos)")
    print("  Mayorista: ~33% (valor consistente)")

if __name__ == "__main__":
    test_columnas_correctas() 