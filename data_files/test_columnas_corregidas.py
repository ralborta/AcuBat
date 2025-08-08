#!/usr/bin/env python3
from api.moura_rentabilidad import analizar_rentabilidades_moura

def test_columnas_corregidas():
    print("🧪 PROBANDO COLUMNAS CORREGIDAS")
    print("=" * 50)
    
    # Analizar rentabilidades
    resultado = analizar_rentabilidades_moura('Rentalibilidades-2.xlsx')
    
    print(f"📊 Reglas Minorista: {len(resultado['reglas_minorista'])}")
    print(f"📊 Reglas Mayorista: {len(resultado['reglas_mayorista'])}")
    
    print("\n🔍 PRIMERAS 5 REGLAS MINORISTA (Varta):")
    for i, regla in enumerate(resultado['reglas_minorista'][:5]):
        print(f"  {i+1}. {regla['codigo']}: {regla['markup']}% (rent: {regla['rentabilidad']}%)")
    
    print("\n🔍 PRIMERAS 5 REGLAS MAYORISTA (Varta):")
    for i, regla in enumerate(resultado['reglas_mayorista'][:5]):
        print(f"  {i+1}. {regla['codigo']}: {regla['markup']}% (rent: {regla['rentabilidad']}%)")
    
    # Buscar productos específicos
    productos_buscar = ['M40FD', 'M18FD (100)', 'M22ED (100)']
    
    print(f"\n🎯 BUSCANDO PRODUCTOS ESPECÍFICOS:")
    for producto in productos_buscar:
        print(f"\n🔍 {producto}:")
        
        # Buscar en minorista
        for regla in resultado['reglas_minorista']:
            if regla['codigo'] == producto:
                print(f"  Minorista: {regla['markup']}% (rent: {regla['rentabilidad']}%)")
                break
        
        # Buscar en mayorista
        for regla in resultado['reglas_mayorista']:
            if regla['codigo'] == producto:
                print(f"  Mayorista: {regla['markup']}% (rent: {regla['rentabilidad']}%)")
                break

if __name__ == "__main__":
    test_columnas_corregidas() 