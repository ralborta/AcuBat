#!/usr/bin/env python3
"""
Buscar columnas que contengan porcentajes de markup
"""
import pandas as pd
import os

def buscar_porcentajes():
    """Buscar columnas con porcentajes de markup"""
    
    archivo = 'Rentalibilidades-2.xlsx'
    
    if not os.path.exists(archivo):
        print(f"❌ Archivo {archivo} no encontrado")
        return
    
    try:
        # Leer la hoja Moura
        df = pd.read_excel(archivo, sheet_name='Moura')
        print(f"✅ Hoja Moura leída correctamente")
        print(f"📊 Dimensiones: {df.shape}")
        
        print(f"\n🔍 Buscando columnas con porcentajes:")
        
        # Buscar en todas las columnas valores que parezcan porcentajes
        for i, col in enumerate(df.columns):
            try:
                # Obtener valores numéricos de la columna
                valores = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(valores) > 0:
                    # Buscar valores que estén en el rango de porcentajes (0-100)
                    porcentajes = valores[(valores >= 0) & (valores <= 100)]
                    
                    if len(porcentajes) > 5:  # Si hay varios valores en rango de porcentaje
                        valores_unicos = porcentajes.unique()
                        print(f"\n📋 Columna {i}: {col}")
                        print(f"   Valores en rango 0-100: {len(valores_unicos)}")
                        
                        if len(valores_unicos) <= 15:
                            print(f"   Todos los valores: {sorted(valores_unicos)}")
                        else:
                            print(f"   Primeros 15: {sorted(valores_unicos[:15])}")
                            print(f"   ... y {len(valores_unicos) - 15} más")
                        
                        # Verificar si hay valores como los de la imagen
                        valores_imagen = [19.34, 22.22, 21.70, 23.90, 39.06, 14.49, 15.78, 19.80, 18.71, 16.56, 28.22, 19.61, 29.01]
                        coincidencias = [v for v in valores_unicos if any(abs(v - vi) < 0.1 for vi in valores_imagen)]
                        if coincidencias:
                            print(f"   ✅ ¡COINCIDENCIAS CON LA IMAGEN!: {coincidencias}")
                            
            except Exception as e:
                continue
        
        # También buscar en las filas de datos específicas
        print(f"\n🔍 Buscando en filas de productos específicos:")
        for i in range(2, min(10, len(df))):  # Empezar desde fila 2 (después de headers)
            codigo = df.iloc[i, 0]
            if pd.notna(codigo) and str(codigo).startswith('M'):
                print(f"   Producto {codigo}: {list(df.iloc[i, :10])}")
                        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

if __name__ == "__main__":
    buscar_porcentajes() 