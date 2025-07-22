#!/usr/bin/env python3
import sys
import os

# Agregar el directorio api al path
sys.path.append('api')

from moura_rentabilidad import analizar_rentabilidades_moura

def test_reglas():
    print("🧪 PRUEBA DE APLICACIÓN DE REGLAS")
    print("=" * 50)
    
    # Analizar el archivo
    resultado = analizar_rentabilidades_moura('Rentalibilidades-2.xlsx')
    
    print(f"📊 Reglas Minorista encontradas: {len(resultado['reglas_minorista'])}")
    print(f"📊 Reglas Mayorista encontradas: {len(resultado['reglas_mayorista'])}")
    print()
    
    print("🔍 PRIMERAS 5 REGLAS MINORISTA:")
    for i, regla in enumerate(resultado['reglas_minorista'][:5]):
        print(f"  {i+1}. {regla['codigo']}: Markup {regla['markup']:.2f}%, Rentabilidad {regla['rentabilidad']:.2f}%")
    
    print()
    print("🔍 PRIMERAS 5 REGLAS MAYORISTA:")
    for i, regla in enumerate(resultado['reglas_mayorista'][:5]):
        print(f"  {i+1}. {regla['codigo']}: Markup {regla['markup']:.2f}%, Rentabilidad {regla['rentabilidad']:.2f}%")
    
    print()
    print("🎯 VERIFICACIÓN:")
    print("Los markups deberían ser:")
    print("  Minorista: ~22%, ~17%, ~22%, ~19% (valores bajos)")
    print("  Mayorista: ~60%, ~60%, ~60%, ~60% (valores altos)")

if __name__ == "__main__":
    test_reglas() 