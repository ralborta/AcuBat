#!/usr/bin/env python3
import pandas as pd

def verificar_lista_precios():
    print("🔍 VERIFICANDO LISTADO DE PRECIOS")
    print("=" * 60)
    
    # Leer el archivo de listado de precios
    archivo = 'Lista Moura 04 (1).xlsx'
    
    try:
        # Leer todas las hojas
        xl = pd.ExcelFile(archivo)
        hojas = xl.sheet_names
        print(f"📊 Hojas disponibles: {hojas}")
        print()
        
        # Procesar cada hoja
        for hoja in hojas:
            print(f"🔍 Procesando hoja: {hoja}")
            df = pd.read_excel(archivo, sheet_name=hoja)
            
            print(f"  📊 Forma del DataFrame: {df.shape}")
            print(f"  📊 Total de filas: {len(df)}")
            
            # Contar productos válidos (con código y precio)
            productos_validos = 0
            productos_con_datos = []
            
            for i in range(len(df)):
                try:
                    # Buscar código en diferentes columnas
                    codigo = None
                    precio = None
                    
                    # Intentar encontrar código y precio
                    for col in range(min(5, len(df.columns))):
                        valor = df.iloc[i, col]
                        if pd.notna(valor) and str(valor).strip() and str(valor).strip() != 'nan':
                            if codigo is None:
                                codigo = str(valor).strip()
                            elif precio is None and isinstance(valor, (int, float)) and valor > 0:
                                precio = valor
                                break
                    
                    if codigo and precio:
                        productos_validos += 1
                        productos_con_datos.append({
                            'fila': i+1,
                            'codigo': codigo,
                            'precio': precio
                        })
                        
                except Exception as e:
                    continue
            
            print(f"  🎯 PRODUCTOS VÁLIDOS: {productos_validos}")
            
            # Mostrar primeros 10 productos
            if productos_con_datos:
                print("  📋 PRIMEROS 10 PRODUCTOS:")
                for i, producto in enumerate(productos_con_datos[:10]):
                    print(f"    {i+1}. {producto['codigo']} - ${producto['precio']:,.0f}")
                
                if len(productos_con_datos) > 10:
                    print(f"    ... y {len(productos_con_datos) - 10} productos más")
            
            print()
            
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

if __name__ == "__main__":
    verificar_lista_precios() 