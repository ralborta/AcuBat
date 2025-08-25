#!/usr/bin/env python3
"""
🧪 TEST ESPECÍFICO DEL ANÁLISIS DE RENTABILIDAD
Prueba las metodologías del sector baterías
"""
import sys
import os
import json
from pprint import pprint

# Agregar path para importar módulos
sys.path.append('api')

def test_rentabilidad_sector():
    """Prueba el analizador de rentabilidad del sector baterías"""
    
    print("📊 TEST DE ANÁLISIS DE RENTABILIDAD SECTOR BATERÍAS")
    print("=" * 55)
    
    try:
        from api.rentabilidad_sector_baterias import RentabilidadSectorBaterias
        
        # Crear analizador
        analizador = RentabilidadSectorBaterias()
        print("✅ Analizador de rentabilidad inicializado")
        
        # Producto de prueba con pricing por canales
        producto_test = {
            "codigo": "M20GD-001",
            "nombre": "Moura 20 Gold 45Ah",
            "marca": "moura",
            "precio_base": 35000,
            "pricing_canales": {
                "mayorista": {
                    "precio_final": 41300,
                    "markup_aplicado": 18.0,
                    "margen": 15.4,
                    "rentabilidad": "ÓPTIMA"
                },
                "minorista": {
                    "precio_final": 64800,
                    "markup_aplicado": 85.1,
                    "margen": 46.0,
                    "rentabilidad": "ÓPTIMA"
                },
                "distribuidor": {
                    "precio_final": 40200,
                    "markup_aplicado": 14.9,
                    "margen": 12.9,
                    "rentabilidad": "ACEPTABLE"
                }
            }
        }
        
        print(f"\n🔍 Analizando producto: {producto_test['codigo']}")
        print(f"   Marca: {producto_test['marca'].title()}")
        print(f"   Precio base: ${producto_test['precio_base']:,}")
        
        # Ejecutar análisis
        resultado = analizador.analizar_rentabilidad_producto(producto_test)
        
        print(f"\n📈 RESULTADOS DEL ANÁLISIS:")
        print(f"   Metodología: {resultado['metodologia']}")
        
        # Mostrar costos base
        costos = resultado['costos_base']
        print(f"\n💰 ESTRUCTURA DE COSTOS:")
        print(f"   Materia prima: ${costos['materia_prima']:,.0f}")
        print(f"   Mano obra: ${costos['mano_obra_directa']:,.0f}")
        print(f"   Costos industriales: ${costos['costos_industriales']:,.0f}")
        print(f"   TOTAL PRODUCCIÓN: ${costos['costo_produccion']:,.0f}")
        
        # Mostrar análisis por canal
        print(f"\n📊 ANÁLISIS POR CANAL:")
        for canal, analisis in resultado['analisis_por_canal'].items():
            print(f"\n   🔹 {canal.upper()}:")
            print(f"      Metodología: {analisis['metodologia']}")
            print(f"      Precio venta: ${analisis['precio_venta']:,.0f}")
            
            if 'margen_neto_pct' in analisis:
                print(f"      Margen neto: {analisis['margen_neto_pct']:.1f}%")
                print(f"      ROI: {analisis['roi']:.1f}%")
            elif 'margen_contribucion_pct' in analisis:
                print(f"      Margen contribución: {analisis['margen_contribucion_pct']:.1f}%")
            elif 'margen_zona_pct' in analisis:
                print(f"      Margen zona: {analisis['margen_zona_pct']:.1f}%")
                print(f"      Eficiencia territorial: {analisis['eficiencia_territorial']:.1f}%")
            
            evaluacion = analisis.get('evaluacion_rentabilidad', {})
            print(f"      Evaluación: {evaluacion.get('evaluacion', 'N/A')}")
            print(f"      Recomendación: {evaluacion.get('recomendacion', 'N/A')}")
        
        # Mostrar consolidado
        consolidado = resultado['rentabilidad_consolidada']
        print(f"\n🎯 ANÁLISIS CONSOLIDADO:")
        print(f"   Revenue potencial total: ${consolidado['total_revenue_potencial']:,.0f}")
        print(f"   Margen promedio canales: {consolidado['margen_promedio_canales']:.1f}%")
        print(f"   Canal más rentable: {consolidado['canal_mas_rentable']['canal']} ({consolidado['canal_mas_rentable']['margen']:.1f}%)")
        print(f"   Evaluación general: {consolidado['evaluacion_general']}")
        print(f"   Recomendación estratégica: {consolidado['recomendacion_estrategica']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de rentabilidad: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_show_completo_con_rentabilidad():
    """Prueba el show completo con análisis de rentabilidad"""
    
    print("\n🎭 TEST DEL SHOW COMPLETO CON RENTABILIDAD")
    print("=" * 45)
    
    try:
        from api.dynamic_pricing_show import DynamicPricingShow
        
        # Ejecutar show completo
        show = DynamicPricingShow()
        resultado = show.ejecutar_show_completo()
        
        # Verificar que incluya análisis de rentabilidad
        productos = resultado.get('productos_generados', [])
        if productos and 'analisis_rentabilidad' in productos[0]:
            print("✅ Show incluye análisis de rentabilidad")
            
            # Mostrar métricas de rentabilidad
            metricas = resultado.get('metricas_impacto', {})
            analisis_canales = metricas.get('analisis_por_canal', {})
            
            print(f"\n📊 RENTABILIDAD POR CANAL:")
            for canal, datos in analisis_canales.items():
                print(f"   {canal.capitalize()}: {datos.get('rentabilidad_promedio', 0):.1f}% ({datos.get('metodologia', 'N/A')})")
            
            rentabilidad_global = metricas.get('rentabilidad_global', {})
            if rentabilidad_global:
                print(f"\n🌟 CLASIFICACIÓN DE PRODUCTOS:")
                print(f"   Productos estrella: {rentabilidad_global.get('productos_estrella', 0)}")
                print(f"   Productos rentables: {rentabilidad_global.get('productos_rentables', 0)}")
                print(f"   Productos marginales: {rentabilidad_global.get('productos_marginales', 0)}")
                print(f"   Productos problemáticos: {rentabilidad_global.get('productos_problematicos', 0)}")
                
            resumen = metricas.get('resumen_general', {})
            print(f"\n💰 PROYECCIÓN FINANCIERA:")
            print(f"   Revenue anual: ${resumen.get('revenue_anual_proyectado', 0):,}")
            print(f"   Beneficio proyectado: ${resumen.get('beneficio_anual_proyectado', 0):,}")
            print(f"   Rentabilidad promedio: {resumen.get('rentabilidad_promedio_sector', 0):.1f}%")
            
        else:
            print("⚠️ Show no incluye análisis de rentabilidad")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en show completo: {e}")
        return False

def mostrar_metodologias():
    """Muestra las metodologías implementadas"""
    
    print("\n📚 METODOLOGÍAS IMPLEMENTADAS")
    print("=" * 35)
    
    metodologias = {
        "MAYORISTA": {
            "nombre": "Margen de Contribución",
            "enfoque": "Contribución a gastos fijos",
            "kpis": ["Margen bruto", "Rotación inventario", "Contribución fija"],
            "costos_especificos": ["Crédito clientes", "Logística mayor", "Descuentos volumen"]
        },
        "MINORISTA": {
            "nombre": "Rentabilidad Integral",
            "enfoque": "Análisis completo de rentabilidad",
            "kpis": ["Margen neto", "Ticket promedio", "Frecuencia compra"],
            "costos_especificos": ["Atención cliente", "Exhibición", "Garantías"]
        },
        "DISTRIBUIDOR": {
            "nombre": "Eficiencia Territorial",
            "enfoque": "Eficiencia por zona geográfica",
            "kpis": ["Margen zona", "Penetración mercado", "Costo territorio"],
            "costos_especificos": ["Representantes", "Territorio", "Soporte técnico"]
        }
    }
    
    for canal, info in metodologias.items():
        print(f"\n🔹 {canal}:")
        print(f"   Metodología: {info['nombre']}")
        print(f"   Enfoque: {info['enfoque']}")
        print(f"   KPIs: {', '.join(info['kpis'])}")
        print(f"   Costos específicos: {', '.join(info['costos_especificos'])}")

def main():
    """Función principal de testing"""
    
    print("🧪" * 25)
    print("   TEST COMPLETO - ANÁLISIS DE RENTABILIDAD")
    print("🧪" * 25 + "\n")
    
    # Mostrar metodologías
    mostrar_metodologias()
    
    # Test 1: Rentabilidad específica
    resultado1 = test_rentabilidad_sector()
    
    # Test 2: Show completo
    resultado2 = test_show_completo_con_rentabilidad()
    
    # Resumen
    print(f"\n📋 RESUMEN DE TESTS:")
    print(f"   Análisis de rentabilidad: {'✅ OK' if resultado1 else '❌ FALLO'}")
    print(f"   Show completo: {'✅ OK' if resultado2 else '❌ FALLO'}")
    
    if resultado1 and resultado2:
        print(f"\n🎉 TODOS LOS TESTS DE RENTABILIDAD PASARON")
        print(f"🎯 El sistema ahora analiza rentabilidad por metodologías del sector")
        print(f"💡 Características implementadas:")
        print(f"   📊 Separación clara por canales (Mayorista/Minorista/Distribuidor)")
        print(f"   🎯 Metodologías específicas del sector baterías")
        print(f"   💰 Cálculo de markup real y rentabilidad")
        print(f"   📈 Proyecciones financieras precisas")
        print(f"   🔍 Evaluación automática de productos")
    else:
        print(f"\n❌ HAY TESTS FALLIDOS - REVISAR IMPLEMENTACIÓN")

if __name__ == "__main__":
    main()