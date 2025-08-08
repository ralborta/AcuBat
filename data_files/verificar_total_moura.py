#!/usr/bin/env python3
import pandas as pd

def verificar_total_moura():
    print("🔍 VERIFICANDO TOTAL REAL DE PRODUCTOS EN MOURA")
    print("=" * 60)
    
    # Leer la hoja Moura
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print(f"📊 Total de filas: {len(df)}")
    print()
    
    # Contar productos válidos (con código y precio)
    productos_validos = 0
    productos_con_datos = []
    
    for i in range(len(df)):
        try:
            codigo = str(df.iloc[i, 0]).strip()
            precio_base = df.iloc[i, 1]
            
            if codigo and codigo != 'nan' and pd.notna(precio_base) and precio_base > 0:
                productos_validos += 1
                productos_con_datos.append({
                    'fila': i+1,
                    'codigo': codigo,
                    'precio_base': precio_base
                })
        except:
            continue
    
    print(f"🎯 PRODUCTOS VÁLIDOS EN MOURA: {productos_validos}")
    print()
    
    print("📋 LISTA DE PRODUCTOS:")
    for i, producto in enumerate(productos_con_datos[:10]):  # Mostrar primeros 10
        print(f"  {i+1}. {producto['codigo']} - ${producto['precio_base']:,.0f}")
    
    if len(productos_con_datos) > 10:
        print(f"  ... y {len(productos_con_datos) - 10} productos más")
    
    print()
    print("🎯 CONCLUSIÓN:")
    print(f"  - Total de filas en Moura: {len(df)}")
    print(f"  - Productos válidos: {productos_validos}")
    print(f"  - ¿Deberían ser 32?: {'✅ SÍ' if productos_validos == 32 else '❌ NO'}")

if __name__ == "__main__":
    verificar_total_moura() 