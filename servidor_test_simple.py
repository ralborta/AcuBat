#!/usr/bin/env python3
"""
🚀 SERVIDOR TEST SIMPLE
Servidor HTTP básico para probar la funcionalidad sin FastAPI
"""
import http.server
import socketserver
import json
import urllib.parse
import cgi
import os
import tempfile
from pathlib import Path

class TestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personalizado para el test"""
    
    def do_GET(self):
        """Maneja peticiones GET"""
        
        if self.path == '/show' or self.path == '/':
            # Servir la página del show
            try:
                with open('templates/pricing_show.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
                return
                
            except FileNotFoundError:
                self.send_error(404, "No se encontró templates/pricing_show.html")
                return
        
        elif self.path == '/api/pricing-show-status':
            # Endpoint de status
            response = {
                "status": "ready", 
                "mensaje": "🎭 Sistema Test Listo",
                "modo": "test_simple",
                "timestamp": "2024-01-01T00:00:00"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # Para otros paths, usar el handler por defecto
        super().do_GET()
    
    def do_POST(self):
        """Maneja peticiones POST"""
        
        if self.path == '/api/pricing-show-upload':
            try:
                # Headers CORS
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                # Simular procesamiento del archivo
                response = {
                    "status": "success_simulated",
                    "mensaje": "🎭 Test completado exitosamente (modo simulación)",
                    "archivo_procesado": "test_file.xlsx",
                    "resultado": {
                        "productos_finales": [
                            {
                                "codigo": "TEST-001",
                                "nombre": "Batería Test 1",
                                "marca": "Moura",
                                "precio_base": 45000,
                                "precio_final": 83250,
                                "markup_aplicado": 85.0,
                                "analisis_rentabilidad": {
                                    "metodologia": "test_mode",
                                    "rentabilidad_consolidada": {
                                        "margen_promedio_canales": 42.5,
                                        "evaluacion_general": "PRODUCTO_RENTABLE"
                                    },
                                    "analisis_por_canal": {
                                        "minorista": {
                                            "margen_neto_pct": 45.2,
                                            "metodologia": "Rentabilidad Integral"
                                        },
                                        "mayorista": {
                                            "margen_contribucion_pct": 28.3,
                                            "metodologia": "Margen de Contribución"
                                        }
                                    }
                                }
                            },
                            {
                                "codigo": "TEST-002", 
                                "nombre": "Batería Test 2",
                                "marca": "AcuBat",
                                "precio_base": 38000,
                                "precio_final": 70300,
                                "markup_aplicado": 85.0,
                                "analisis_rentabilidad": {
                                    "metodologia": "test_mode",
                                    "rentabilidad_consolidada": {
                                        "margen_promedio_canales": 38.1,
                                        "evaluacion_general": "PRODUCTO_RENTABLE"
                                    },
                                    "analisis_por_canal": {
                                        "minorista": {
                                            "margen_neto_pct": 41.0,
                                            "metodologia": "Rentabilidad Integral"
                                        },
                                        "mayorista": {
                                            "margen_contribucion_pct": 25.2,
                                            "metodologia": "Margen de Contribución"
                                        }
                                    }
                                }
                            }
                        ],
                        "metricas_impacto": {
                            "resumen_general": {
                                "productos_generados": 2,
                                "revenue_anual_proyectado": 1840200,
                                "rentabilidad_promedio_sector": 40.3,
                                "beneficio_anual_proyectado": 741600
                            },
                            "distribucion_marcas": {
                                "moura": {
                                    "productos": 1,
                                    "revenue_promedio": 83250,
                                    "rentabilidad_promedio": 42.5
                                },
                                "acubat": {
                                    "productos": 1,
                                    "revenue_promedio": 70300,
                                    "rentabilidad_promedio": 38.1
                                }
                            },
                            "analisis_por_canal": {
                                "minorista": {
                                    "revenue": 153550,
                                    "rentabilidad_promedio": 43.1,
                                    "metodologia": "Rentabilidad Integral"
                                },
                                "mayorista": {
                                    "revenue": 120800,
                                    "rentabilidad_promedio": 26.8,
                                    "metodologia": "Margen de Contribución"
                                }
                            },
                            "rentabilidad_global": {
                                "productos_estrella": 0,
                                "productos_rentables": 2,
                                "productos_marginales": 0,
                                "productos_problematicos": 0
                            },
                            "oportunidades_detectadas": {
                                "productos_alto_potencial": 2,
                                "canal_mas_rentable": "minorista"
                            }
                        }
                    },
                    "show_completo": True,
                    "nota": "Datos generados para test de funcionalidad"
                }
                
                print(f"📁 Upload simulado procesado exitosamente")
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            except Exception as e:
                print(f"❌ Error en upload: {e}")
                error_response = {
                    "status": "error",
                    "mensaje": f"Error en test: {str(e)}"
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
        
        # Otros POSTs
        self.send_error(404, "Endpoint no encontrado")
    
    def do_OPTIONS(self):
        """Maneja peticiones OPTIONS para CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def iniciar_servidor_test(puerto=8000):
    """Inicia el servidor test"""
    
    print("🚀 INICIANDO SERVIDOR TEST SIMPLE")
    print("=" * 35)
    print(f"Puerto: {puerto}")
    print(f"URLs disponibles:")
    print(f"   🎭 Show: http://localhost:{puerto}/show")
    print(f"   🏠 Index: http://localhost:{puerto}/")
    print(f"   📊 Status: http://localhost:{puerto}/api/pricing-show-status")
    print(f"   📁 Upload: http://localhost:{puerto}/api/pricing-show-upload (POST)")
    print()
    
    # Verificar archivos necesarios
    if not os.path.exists('templates/pricing_show.html'):
        print("⚠️ ADVERTENCIA: No se encontró templates/pricing_show.html")
        print("   El servidor funcionará pero no podrá servir la página del show")
    else:
        print("✅ Archivo templates/pricing_show.html encontrado")
    
    print()
    print("🎯 PROPÓSITO: Probar si el problema está en el servidor o frontend")
    print("💡 Si funciona con este servidor → El problema estaba en FastAPI/dependencias")
    print("❌ Si NO funciona → El problema está en el frontend/JavaScript")
    print()
    print("📍 Para detener el servidor: Ctrl+C")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", puerto), TestHandler) as httpd:
            print(f"🟢 Servidor iniciado en http://localhost:{puerto}")
            print("Esperando conexiones...")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n🛑 Servidor detenido por el usuario")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Error: Puerto {puerto} ya está en uso")
            print(f"💡 Prueba con otro puerto: python3 servidor_test_simple.py 8001")
        else:
            print(f"❌ Error iniciando servidor: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    import sys
    
    # Permitir especificar puerto como argumento
    puerto = 8000
    if len(sys.argv) > 1:
        try:
            puerto = int(sys.argv[1])
        except ValueError:
            print("❌ Puerto debe ser un número")
            sys.exit(1)
    
    iniciar_servidor_test(puerto)