# FIX CONFLICTO: Eliminar functions del vercel.json - Solo usar builds - Commit f5f7a2a
# FORZAR DEPLOY: Importaciones absolutas para Vercel - Commit ed5b97a
# FORZAR DEPLOY: Cambio de rewrites a routes en vercel.json - Commit 7dbe87f
# FORZAR DEPLOY FINAL: JSON simplificado - Commit 6728e77 - Vercel debe reconocer este código
# ULTIMO COMMIT: cf76ece - PRUEBA: Deploy automático - Verificar que Vercel funciona correctamente
# PRUEBA DEPLOY AUTOMÁTICO - Commit de prueba para verificar que Vercel funciona
# FORZAR REBUILD - Vercel necesita detectar cambios en main.py para incluir rentabilidad_analyzer.py
# ROLLBACK EXITOSO - Volvimos a la versión estable 334126c - FORZAR DEPLOY
# VERIFICAR DEPLOY - Forzar detección de cambios en Vercel
# ROLLBACK EXITOSO - Volvimos a la versión funcional con descarga de reportes
# FORZAR DEPLOY VERCEL - Asegurar que detecte el rollback
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import logging
import io
import os
import json
from dotenv import load_dotenv
import pandas as pd
import traceback
import io
from datetime import datetime
from fastapi.responses import StreamingResponse

# Cargar variables de entorno
load_dotenv()

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detectar si estamos en Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1'

# Crear aplicación FastAPI
app = FastAPI(
    title="Backend Acubat",
    description="Sistema de gestión de productos con procesamiento de Excel y alertas inteligentes",
    version="1.0.0"
)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Variables globales para almacenar productos procesados
productos_actuales = []

# Variables globales para almacenar datos
rentabilidades_data = None
rentabilidades_filename = None
precios_data = None
precios_filename = None

# Importar módulos de forma segura con importaciones absolutas
try:
    from api.logic import PricingLogic
    from api.openai_helper import OpenAIHelper
    from api.parser import ExcelParser, detect_and_parse_file, is_moura_file
    from api.models import Producto, Marca, Canal
    from api.rentabilidad_analyzer import RentabilidadAnalyzer, analizar_rentabilidades_2_canales
    from api.moura_rentabilidad import analizar_rentabilidades_moura
    
    pricing_logic = PricingLogic()
    openai_helper = OpenAIHelper()
    excel_parser = ExcelParser()
    rentabilidad_analyzer = RentabilidadAnalyzer()
    
    MODULES_AVAILABLE = True
    logger.info("✅ Módulos completos cargados exitosamente")
except ImportError as e:
    logger.warning(f"⚠️ Algunos módulos no están disponibles: {e}")
    MODULES_AVAILABLE = False

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con panel de productos"""
    try:
        if not MODULES_AVAILABLE:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Acubat - Sistema de Pricing</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-md-3 bg-light p-4 min-vh-100">
                            <h4 class="mb-4">
                                <i class="fas fa-chart-line text-primary"></i>
                                Rating: Calificación
                            </h4>
                            
                            <div class="card bg-primary text-white p-3 mb-3">
                                <h2 class="display-4 text-center">0</h2>
                                <p class="text-center mb-0">Productos Cargados</p>
                            </div>

                            <div class="card bg-warning text-white p-3 mb-3">
                                <h2 class="display-4 text-center">0</h2>
                                <p class="text-center mb-0">Con Alertas</p>
                            </div>

                            <div class="mt-4">
                                <h5><i class="fas fa-filter text-info"></i> Filtros</h5>
                                <select class="form-select mb-2">
                                    <option value="">Todos los canales</option>
                                </select>
                                
                                <select class="form-select mb-2">
                                    <option value="">Todas las marcas</option>
                                </select>
                                
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="filtroAlertas">
                                    <label class="form-check-label" for="filtroAlertas">
                                        Solo con alertas
                                    </label>
                                </div>
                            </div>

                            <div class="mt-4">
                                <button class="btn btn-success w-100 mb-2" onclick="exportarCSV()">
                                    <i class="fas fa-download"></i> Exportar CSV
                                </button>
                                
                                <div class="alert alert-warning alert-sm">
                                    <i class="fas fa-exclamation-triangle"></i>
                                    Sistema en modo básico
                                </div>
                            </div>
                        </div>

                        <div class="col-md-9 p-4">
                            <h1 class="mb-4">
                                <i class="fas fa-rocket text-primary"></i>
                                AcuBat - Sistema de Pricing Inteligente
                            </h1>

                            <div class="alert alert-info">
                                <h4>🚀 Sistema Funcionando</h4>
                                <p>El sistema está funcionando en modo optimizado. Sube archivos Excel/CSV para comenzar.</p>
                            </div>

                            <div class="card shadow-sm">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <i class="fas fa-cloud-upload-alt text-primary"></i>
                                        Cargar Lista de Precios
                                    </h5>
                                    
                                    <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                                        <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                                        <h5>Arrastra tu archivo aquí</h5>
                                        <p class="text-muted">Soporta Excel (.xlsx, .xls) y CSV (.csv)</p>
                                        <button class="btn btn-primary">
                                            <i class="fas fa-file-upload"></i>
                                            Seleccionar Archivo
                                        </button>
                                    </div>

                                    <input type="file" id="fileInput" accept=".xlsx,.xls,.csv" style="display: none;">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                <script>
                    const uploadArea = document.getElementById('uploadArea');
                    const fileInput = document.getElementById('fileInput');

                    uploadArea.addEventListener('dragover', (e) => {
                        e.preventDefault();
                        uploadArea.classList.add('dragover');
                    });

                    uploadArea.addEventListener('dragleave', () => {
                        uploadArea.classList.remove('dragover');
                    });

                    uploadArea.addEventListener('drop', (e) => {
                        e.preventDefault();
                        uploadArea.classList.remove('dragover');
                        const files = e.dataTransfer.files;
                        if (files.length > 0) {
                            subirArchivo(files[0]);
                        }
                    });

                    fileInput.addEventListener('change', (e) => {
                        if (e.target.files.length > 0) {
                            subirArchivo(e.target.files[0]);
                        }
                    });

                    function subirArchivo(file) {
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        fetch('/upload', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.mensaje) {
                                alert('✅ ' + data.mensaje);
                                location.reload();
                            } else {
                                alert('❌ Error: ' + (data.detail || 'Error desconocido'));
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('❌ Error al subir archivo');
                        });
                    }

                    function exportarCSV() {
                        window.location.href = '/export/csv';
                    }
                </script>
            </body>
            </html>
            """)
        
        # Generar resúmenes si los módulos están disponibles
        resumen_marcas = pricing_logic.obtener_resumen_marcas(productos_actuales) if productos_actuales and MODULES_AVAILABLE else {}
        resumen_canales = pricing_logic.obtener_resumen_canales(productos_actuales) if productos_actuales and MODULES_AVAILABLE else {}
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "productos": productos_actuales if productos_actuales else [],
            "total_productos": len(productos_actuales) if productos_actuales else 0,
            "productos_con_alertas": len([p for p in productos_actuales if p.get('alertas')]) if productos_actuales else 0,
            "openai_disponible": openai_helper.esta_disponible() if MODULES_AVAILABLE else False,
            "resumen_marcas": resumen_marcas,
            "resumen_canales": resumen_canales,
            "is_vercel": IS_VERCEL
        })
    except Exception as e:
        logger.error(f"Error en página principal: {e}")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Acubat - Error</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1>🚀 Backend Acubat</h1>
                <div class="alert alert-danger">
                    <h4>❌ Error cargando la página</h4>
                    <p>{str(e)}</p>
                </div>
                <p>Productos cargados: {len(productos_actuales) if productos_actuales else 0}</p>
                <a href="/health" class="btn btn-primary">Health Check</a>
            </div>
        </body>
        </html>
        """)

@app.get("/test")
async def test_endpoint():
    """Endpoint de prueba para verificar que la aplicación funciona"""
    return {
        "mensaje": "✅ API funcionando correctamente",
        "timestamp": "2024-01-01T00:00:00Z",
        "status": "ok"
    }

@app.get("/test-simple")
async def test_simple():
    """Endpoint de test simple para verificar que el servidor funciona"""
    return {
        "status": "ok",
        "mensaje": "Servidor funcionando correctamente",
        "timestamp": "2024-12-19"
    }

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Endpoint de test para subir archivos"""
    try:
        logger.info(f"=== TEST UPLOAD ===")
        logger.info(f"Archivo: {file.filename}")
        logger.info(f"Content-Type: {file.content_type}")
        
        # Leer archivo
        contenido = file.file.read()
        logger.info(f"Tamaño: {len(contenido)} bytes")
        
        return {
            "status": "ok",
            "archivo": file.filename,
            "tamaño": len(contenido),
            "content_type": file.content_type,
            "mensaje": "Archivo recibido correctamente"
        }
        
    except Exception as e:
        logger.error(f"Error en test upload: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check para verificar que la aplicación funciona"""
    return {
        "status": "healthy", 
        "message": "Backend Acubat funcionando",
        "modules_available": MODULES_AVAILABLE,
        "is_vercel": IS_VERCEL,
        "productos_cargados": len(productos_actuales) if productos_actuales else 0
    }

@app.get("/api/status")
async def get_status():
    """Obtiene el estado del sistema"""
    return {
        "status": "ok",
        "mensaje": "Aplicación funcionando correctamente",
        "productos_cargados": len(productos_actuales) if productos_actuales else 0,
        "modules_available": MODULES_AVAILABLE,
        "is_vercel": IS_VERCEL
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para subir archivo de productos"""
    try:
        logger.info(f"=== INICIO UPLOAD ===")
        logger.info(f"Archivo recibido: {file.filename}")
        logger.info(f"Content-Type: {file.content_type}")
        
        # Verificación básica
        if not file.filename:
            raise HTTPException(status_code=400, detail="No se proporcionó nombre de archivo")
        
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail=f"Tipo de archivo no soportado: {file.filename}")
        
        # Leer contenido del archivo
        contenido = file.file.read()
        logger.info(f"Contenido leído: {len(contenido)} bytes")
        
        if not contenido:
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        
        # Por ahora, solo devolver información básica
        logger.info(f"=== UPLOAD BÁSICO EXITOSO ===")
        
        return {
            "mensaje": f"✅ Archivo recibido correctamente: {file.filename} ({len(contenido)} bytes)",
            "archivo": file.filename,
            "tamaño": len(contenido),
            "tipo": file.content_type,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en upload: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")

@app.post("/cargar-rentabilidades")
async def upload_rentabilidades(file: UploadFile = File(...)):
    """Endpoint SIMPLE para subir archivo de rentabilidades"""
    global rentabilidades_data, rentabilidades_filename
    
    try:
        logger.info(f"=== CARGA SIMPLE DE RENTABILIDADES ===")
        logger.info(f"Archivo: {file.filename}")
        
        # Verificar que sea Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            return {
                "status": "error",
                "mensaje": "Solo archivos Excel (.xlsx, .xls)"
            }
        
        # Leer archivo
        contenido = file.file.read()
        logger.info(f"Tamaño: {len(contenido)} bytes")
        
        if len(contenido) == 0:
            return {
                "status": "error", 
                "mensaje": "Archivo vacío"
            }
        
        # Guardar temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Leer y guardar en memoria
            import pandas as pd
            excel_file = pd.ExcelFile(temp_file_path)
            
            # Guardar datos en memoria
            rentabilidades_data = {}
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                rentabilidades_data[sheet_name] = df.to_dict('records')
            
            rentabilidades_filename = file.filename
            
            logger.info(f"✅ Archivo guardado en memoria: {file.filename} con {len(excel_file.sheet_names)} hojas")
            
            return {
                "status": "success",
                "mensaje": f"Archivo de rentabilidades cargado exitosamente: {file.filename}",
                "hojas": excel_file.sheet_names,
                "total_hojas": len(excel_file.sheet_names),
                "tamaño": len(contenido),
                "archivo_guardado": file.filename
            }
            
        except Exception as e:
            logger.error(f"Error leyendo Excel: {str(e)}")
            return {
                "status": "error",
                "mensaje": f"Error al leer archivo Excel: {str(e)}"
            }
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        return {
            "status": "error",
            "mensaje": f"Error: {str(e)}"
        }

@app.post("/cargar-precios")
async def upload_precios(file: UploadFile = File(...)):
    """Endpoint para subir archivo de precios"""
    global precios_data, precios_filename
    
    try:
        logger.info(f"=== CARGA SIMPLE DE PRECIOS ===")
        logger.info(f"Archivo: {file.filename}")
        
        # Verificar que sea Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            return {
                "status": "error",
                "mensaje": "Solo archivos Excel (.xlsx, .xls)"
            }
        
        # Leer archivo
        contenido = file.file.read()
        logger.info(f"Tamaño: {len(contenido)} bytes")
        
        if len(contenido) == 0:
            return {
                "status": "error", 
                "mensaje": "Archivo vacío"
            }
        
        # Guardar temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Leer y guardar en memoria
            import pandas as pd
            excel_file = pd.ExcelFile(temp_file_path)
            
            # Guardar datos en memoria
            precios_data = {}
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                precios_data[sheet_name] = df.to_dict('records')
            
            precios_filename = file.filename
            
            logger.info(f"✅ Archivo guardado en memoria: {file.filename} con {len(excel_file.sheet_names)} hojas")
            
            return {
                "status": "success",
                "mensaje": f"Archivo de precios cargado exitosamente: {file.filename}",
                "hojas": excel_file.sheet_names,
                "total_hojas": len(excel_file.sheet_names),
                "tamaño": len(contenido),
                "archivo_guardado": file.filename
            }
            
        except Exception as e:
            logger.error(f"Error leyendo Excel: {str(e)}")
            return {
                "status": "error",
                "mensaje": f"Error al leer archivo Excel: {str(e)}"
            }
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        return {
            "status": "error",
            "mensaje": f"Error: {str(e)}"
        }

@app.post("/diagnostico-excel")
async def diagnostico_excel(file: UploadFile = File(...)):
    """Endpoint para diagnóstico completo de archivos Excel"""
    try:
        logger.info(f"=== DIAGNÓSTICO COMPLETO EXCEL ===")
        logger.info(f"Archivo: {file.filename}")
        logger.info(f"Content-Type: {file.content_type}")
        
        # Leer archivo
        contenido = file.file.read()
        logger.info(f"Tamaño: {len(contenido)} bytes")
        
        if not contenido:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        
        # Guardar temporalmente
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            import pandas as pd
            
            # Leer Excel
            excel_file = pd.ExcelFile(temp_file_path)
            logger.info(f"Excel con {len(excel_file.sheet_names)} hojas")
            
            diagnostico_completo = {
                "archivo": file.filename,
                "tamaño_bytes": len(contenido),
                "total_hojas": len(excel_file.sheet_names),
                "hojas": []
            }
            
            # Analizar cada hoja
            for i, sheet_name in enumerate(excel_file.sheet_names):
                logger.info(f"=== ANALIZANDO HOJA {i+1}: {sheet_name} ===")
                
                # Leer hoja
                df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                
                # Información básica
                info_hoja = {
                    "nombre": sheet_name,
                    "filas": len(df),
                    "columnas": len(df.columns),
                    "nombres_columnas": list(df.columns),
                    "tipos_columnas": df.dtypes.to_dict(),
                    "es_hoja_moura": 'moura' in sheet_name.lower(),
                    "primeras_filas": df.head(3).to_dict('records')
                }
                
                # Buscar columnas requeridas
                columnas_requeridas = {
                    "canal": False,
                    "línea": False, 
                    "margen_minimo": False,
                    "margen_optimo": False
                }
                
                for col in df.columns:
                    col_str = str(col).lower().strip()
                    if any(palabra in col_str for palabra in ['canal', 'channel']):
                        columnas_requeridas["canal"] = True
                    if any(palabra in col_str for palabra in ['línea', 'linea', 'line']):
                        columnas_requeridas["línea"] = True
                    if any(palabra in col_str for palabra in ['margen mínimo', 'margen_minimo', 'minimo']):
                        columnas_requeridas["margen_minimo"] = True
                    if any(palabra in col_str for palabra in ['margen óptimo', 'margen_optimo', 'optimo']):
                        columnas_requeridas["margen_optimo"] = True
                
                info_hoja["columnas_requeridas_encontradas"] = columnas_requeridas
                info_hoja["tiene_todas_las_columnas"] = all(columnas_requeridas.values())
                
                diagnostico_completo["hojas"].append(info_hoja)
                
                logger.info(f"Hoja '{sheet_name}': {len(df)} filas, {len(df.columns)} columnas")
                logger.info(f"Columnas: {list(df.columns)}")
                logger.info(f"Es Moura: {info_hoja['es_hoja_moura']}")
                logger.info(f"Tiene todas las columnas: {info_hoja['tiene_todas_las_columnas']}")
            
            # Resumen
            hojas_moura = [h for h in diagnostico_completo["hojas"] if h["es_hoja_moura"]]
            hojas_validas = [h for h in diagnostico_completo["hojas"] if h["tiene_todas_las_columnas"]]
            
            diagnostico_completo["resumen"] = {
                "hojas_moura_encontradas": len(hojas_moura),
                "hojas_con_todas_las_columnas": len(hojas_validas),
                "puede_procesarse": len(hojas_moura) > 0 and len(hojas_validas) > 0
            }
            
            logger.info(f"=== DIAGNÓSTICO COMPLETO ===")
            logger.info(f"Resumen: {diagnostico_completo['resumen']}")
            
            return diagnostico_completo
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error en diagnóstico: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico: {str(e)}")

@app.get("/api/diagnostico-archivos")
async def diagnostico_archivos():
    """Diagnosticar qué archivos y hojas están cargados"""
    global precios_data, rentabilidades_data, precios_filename, rentabilidades_filename
    
    try:
        resultado = {
            "precios": {
                "cargado": precios_data is not None,
                "archivo": precios_filename,
                "hojas": list(precios_data.keys()) if precios_data else []
            },
            "rentabilidades": {
                "cargado": rentabilidades_data is not None,
                "archivo": rentabilidades_filename,
                "hojas": list(rentabilidades_data.keys()) if rentabilidades_data else []
            }
        }
        
        # Agregar información de columnas si hay datos
        if precios_data and len(precios_data) > 0:
            primera_hoja = list(precios_data.keys())[0]
            if len(precios_data[primera_hoja]) > 0:
                resultado["precios"]["columnas"] = list(precios_data[primera_hoja][0].keys())
        
        if rentabilidades_data and len(rentabilidades_data) > 0:
            primera_hoja = list(rentabilidades_data.keys())[0]
            if len(rentabilidades_data[primera_hoja]) > 0:
                resultado["rentabilidades"]["columnas"] = list(rentabilidades_data[primera_hoja][0].keys())
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en diagnóstico: {str(e)}")
        return {
            "error": str(e),
            "precios": {"cargado": False},
            "rentabilidades": {"cargado": False}
        }

@app.get("/api/diagnostico-detallado")
async def diagnostico_detallado():
    """Diagnóstico detallado de los datos cargados"""
    global precios_data, rentabilidades_data
    
    try:
        resultado = {
            "precios": {
                "cargado": precios_data is not None,
                "hojas": list(precios_data.keys()) if precios_data else [],
                "datos_ejemplo": [],
                "total_productos": 0
            },
            "rentabilidades": {
                "cargado": rentabilidades_data is not None,
                "hojas": list(rentabilidades_data.keys()) if rentabilidades_data else [],
                "datos_ejemplo": [],
                "total_reglas": 0
            }
        }
        
        # Mostrar primeros 3 productos como ejemplo
        if precios_data and len(precios_data) > 0:
            primera_hoja = list(precios_data.keys())[0]
            productos = precios_data[primera_hoja]
            resultado["precios"]["total_productos"] = len(productos)
            
            # Mostrar hasta 3 productos con manejo de errores
            for i in range(min(3, len(productos))):
                try:
                    producto = productos[i]
                    # Limpiar datos para evitar errores de serialización
                    producto_limpio = {}
                    for key, value in producto.items():
                        if isinstance(value, (str, int, float, bool)):
                            producto_limpio[str(key)] = str(value)
                        else:
                            producto_limpio[str(key)] = str(value) if value is not None else ""
                    resultado["precios"]["datos_ejemplo"].append(producto_limpio)
                except Exception as e:
                    logger.error(f"Error procesando producto {i}: {e}")
                    resultado["precios"]["datos_ejemplo"].append({"error": f"Error en producto {i}: {str(e)}"})
        
        # Mostrar primeras 3 reglas como ejemplo
        if rentabilidades_data and len(rentabilidades_data) > 0:
            primera_hoja = list(rentabilidades_data.keys())[0]
            reglas = rentabilidades_data[primera_hoja]
            resultado["rentabilidades"]["total_reglas"] = len(reglas)
            
            # Mostrar hasta 3 reglas con manejo de errores
            for i in range(min(3, len(reglas))):
                try:
                    regla = reglas[i]
                    # Limpiar datos para evitar errores de serialización
                    regla_limpia = {}
                    for key, value in regla.items():
                        if isinstance(value, (str, int, float, bool)):
                            regla_limpia[str(key)] = str(value)
                        else:
                            regla_limpia[str(key)] = str(value) if value is not None else ""
                    resultado["rentabilidades"]["datos_ejemplo"].append(regla_limpia)
                except Exception as e:
                    logger.error(f"Error procesando regla {i}: {e}")
                    resultado["rentabilidades"]["datos_ejemplo"].append({"error": f"Error en regla {i}: {str(e)}"})
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en diagnóstico detallado: {str(e)}")
        return {
            "error": str(e),
            "precios": {"cargado": False, "datos_ejemplo": []},
            "rentabilidades": {"cargado": False, "datos_ejemplo": []}
        }

@app.post("/api/analizar-planilla-compleja")
async def analizar_planilla_compleja(file: UploadFile = File(...)):
    """Endpoint para analizar planillas de rentabilidad complejas"""
    try:
        logger.info(f"🔍 Analizando planilla compleja: {file.filename}")
        
        # Guardar archivo temporalmente
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Analizar la planilla
        diagnostico = rentabilidad_analyzer.analizar_planilla_compleja(temp_path)
        
        # Limpiar archivo temporal
        os.remove(temp_path)
        
        logger.info(f"✅ Análisis completado: {diagnostico.get('reglas_encontradas', 0)} reglas encontradas")
        
        return {
            'status': 'success',
            'diagnostico': diagnostico,
            'reglas_extraidas': rentabilidad_analyzer.obtener_reglas_extraidas()
        }
        
    except Exception as e:
        logger.error(f"Error analizando planilla compleja: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

@app.get("/api/estado-rentabilidad")
async def obtener_estado_rentabilidad():
    """Obtiene el estado de las rentabilidades cargadas"""
    try:
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Módulo de rentabilidad no disponible")
        
        archivo_cargado = rentabilidades_filename
        resumen = {} # No hay un resumen directo en memoria, solo el archivo
        
        return {
            "archivo_cargado": archivo_cargado,
            "total_reglas": 0, # No hay reglas en memoria
            "resumen": resumen
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado de rentabilidad: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

@app.get("/api/verificar-rentabilidades")
async def verificar_rentabilidades():
    """Endpoint para verificar si hay rentabilidades cargadas"""
    global rentabilidades_data, rentabilidades_filename
    
    if rentabilidades_data is None:
        return {
            "status": "no_cargado",
            "mensaje": "No hay archivo de rentabilidades cargado",
            "archivo": None,
            "hojas": []
        }
    
    return {
        "status": "cargado",
        "mensaje": f"Archivo de rentabilidades cargado: {rentabilidades_filename}",
        "archivo": rentabilidades_filename,
        "hojas": list(rentabilidades_data.keys()),
        "total_hojas": len(rentabilidades_data)
    }

@app.get("/api/estado-archivos")
async def obtener_estado_archivos():
    """Obtiene el estado actual de los archivos cargados"""
    global precios_data, rentabilidades_data
    
    try:
        logger.info(f"🔍 Verificando estado de archivos:")
        logger.info(f"  - precios_data: {precios_data is not None} ({type(precios_data)})")
        logger.info(f"  - rentabilidades_data: {rentabilidades_data is not None} ({type(rentabilidades_data)})")
        
        estado = {
            "precios_cargados": precios_data is not None,
            "rentabilidades_cargadas": rentabilidades_data is not None,
            "listo_para_procesar": precios_data is not None and rentabilidades_data is not None
        }
        
        logger.info(f"✅ Estado retornado: {estado}")
        return estado
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de archivos: {e}")
        return {
            "precios_cargados": False,
            "rentabilidades_cargadas": False,
            "listo_para_procesar": False
        }

@app.get("/export/csv")
async def export_csv():
    """Exportar productos a CSV"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos para exportar")
        
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Módulo de exportación no disponible")
        
        # Crear CSV
        csv_content = pricing_logic.exportar_a_csv(productos_actuales)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=productos_pricing.csv"}
        )
    except Exception as e:
        logger.error(f"Error al exportar CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.get("/api/analisis-openai")
async def obtener_analisis_openai():
    """Obtener análisis de OpenAI de productos actuales"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos para analizar")
        
        if not MODULES_AVAILABLE or not openai_helper.esta_disponible():
            raise HTTPException(status_code=503, detail="Análisis OpenAI no disponible")
        
        # Analizar productos con OpenAI
        productos_analizados = openai_helper.analizar_lote_productos(productos_actuales)
        
        return {
            "mensaje": "Análisis OpenAI completado",
            "productos_analizados": len(productos_analizados),
            "sugerencias_generadas": len([p for p in productos_analizados if p.sugerencias_openai])
        }
    except Exception as e:
        logger.error(f"Error en análisis OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@app.get("/api/filtrar")
async def filtrar_productos(
    canal: str = None,
    marca: str = None,
    con_alertas: bool = None
):
    """Filtrar productos por criterios"""
    try:
        if not productos_actuales:
            return {"productos": [], "total": 0}
        
        productos_filtrados = productos_actuales.copy()
        
        if canal:
            productos_filtrados = [p for p in productos_filtrados if p.canal == canal]
        
        if marca:
            productos_filtrados = [p for p in productos_filtrados if p.get('marca') == marca]
        
        if con_alertas is not None:
            if con_alertas:
                productos_filtrados = [p for p in productos_filtrados if p.get('alertas')]
            else:
                productos_filtrados = [p for p in productos_filtrados if not p.get('alertas')]
        
        return {
            "productos": productos_filtrados,
            "total": len(productos_filtrados),
            "filtros_aplicados": {
                "canal": canal,
                "marca": marca,
                "con_alertas": con_alertas
            }
        }
    except Exception as e:
        logger.error(f"Error al filtrar productos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al filtrar: {str(e)}")

@app.get("/api/reporte-pricing")
async def obtener_reporte_pricing():
    """Obtener reporte completo de pricing"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos para analizar")
        
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Módulo de reportes no disponible")
        
        # Generar reporte completo
        reporte = pricing_logic.generar_reporte_pricing(productos_actuales)
        
        return {
            "mensaje": "Reporte de pricing generado exitosamente",
            "reporte": reporte,
            "fecha_generacion": "2024-01-01"
        }
    except Exception as e:
        logger.error(f"Error generando reporte de pricing: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

@app.get("/api/sugerencias-precio/{codigo_producto}")
async def obtener_sugerencias_precio(codigo_producto: str):
    """Obtener sugerencias de precio para un producto específico"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos cargados")
        
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Módulo de sugerencias no disponible")
        
        # Buscar producto por código
        producto = next((p for p in productos_actuales if p.get('codigo') == codigo_producto), None)
        
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {codigo_producto} no encontrado")
        
        # Generar sugerencias
        sugerencias = pricing_logic.generar_sugerencias_precio(producto)
        
        return {
            "producto": {
                "codigo": producto.get('codigo'),
                "nombre": producto.get('nombre'),
                "precio_actual": producto.get('precio_final'),
                "margen_actual": producto.get('margen')
            },
            "sugerencias": sugerencias
        }
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias para {codigo_producto}: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo sugerencias: {str(e)}") 

@app.post("/calcular-precios-con-rentabilidad")
async def calcular_precios_con_rentabilidad():
    """
    Calcula precios usando la nueva estructura de 2 canales (Minorista y Mayorista)
    con markups variables para cada canal.
    """
    try:
        logger.info("🚀 Iniciando cálculo de precios con estructura de 2 canales")
        
        # Verificar que tenemos el archivo de precios cargado
        if not precios_data:
            logger.error("❌ No hay archivo de precios cargado")
            return {
                "status": "error",
                "mensaje": "No hay archivo de precios cargado. Sube primero el archivo de precios.",
                "productos": 0,
                "productos_detalle": [],
                "pasos_completados": [],
                "resumen": {}
            }
        
        logger.info(f"📊 Archivo de precios disponible: {precios_filename}")
        
        # Usar directamente el archivo de rentabilidades de la raíz
        archivo_rentabilidades = "Rentalibilidades-2.xlsx"
        
        if not os.path.exists(archivo_rentabilidades):
            logger.error(f"❌ No se encontró el archivo de rentabilidades: {archivo_rentabilidades}")
            return {
                "status": "error",
                "mensaje": f"No se encontró el archivo de rentabilidades: {archivo_rentabilidades}",
                "productos": 0,
                "productos_detalle": [],
                "pasos_completados": [],
                "resumen": {}
            }
        
        logger.info(f"✅ Usando archivo de rentabilidades: {archivo_rentabilidades}")
        
        # Analizar rentabilidades con el parser específico de Moura
        try:
            analisis_rentabilidades = analizar_rentabilidades_moura(archivo_rentabilidades)
            logger.info(f"📊 Análisis de rentabilidades Moura: {analisis_rentabilidades['resumen']}")
        except Exception as e:
            logger.error(f"❌ Error analizando rentabilidades Moura: {e}")
            return {
                "status": "error",
                "mensaje": f"Error analizando archivo de rentabilidades Moura: {str(e)}",
                "productos": 0,
                "productos_detalle": [],
                "pasos_completados": [],
                "resumen": {}
            }
        
        if not analisis_rentabilidades['reglas_minorista'] and not analisis_rentabilidades['reglas_mayorista']:
            logger.error("❌ No se encontraron reglas de rentabilidad")
            return {
                "status": "error",
                "mensaje": "No se encontraron reglas de rentabilidad en el archivo. Verifica la estructura del archivo.",
                "productos": 0,
                "productos_detalle": [],
                "pasos_completados": [],
                "resumen": {}
            }
        
        # Procesar productos de precios
        logger.info("🔄 Procesando productos de precios")
        productos_procesados = []
        
        # Seleccionar la hoja de precios (buscar "Moura" primero)
        precios_hoja = None
        if isinstance(precios_data, dict):
            # Si es un diccionario con hojas
            logger.info(f"📋 Hojas disponibles en precios: {list(precios_data.keys())}")
            for hoja_nombre, datos in precios_data.items():
                if 'moura' in hoja_nombre.lower():
                    precios_hoja = datos
                    logger.info(f"✅ Usando hoja Moura: {hoja_nombre}")
                    break
            if not precios_hoja and precios_data:
                primera_hoja = list(precios_data.keys())[0]
                precios_hoja = precios_data[primera_hoja]
                logger.info(f"✅ Usando primera hoja disponible: {primera_hoja}")
        else:
            # Si es una lista directa
            precios_hoja = precios_data
            logger.info("✅ Usando datos de precios como lista directa")
        
        if not precios_hoja:
            logger.error("❌ No se encontró hoja de precios válida")
            return {
                "status": "error",
                "mensaje": "No se encontró hoja de precios válida.",
                "productos": 0,
                "productos_detalle": [],
                "pasos_completados": [],
                "resumen": {}
            }
        
        logger.info(f"📋 Procesando {len(precios_hoja)} productos de precios")
        
        # Convertir productos de precios
        productos_precios = []
        for i, item in enumerate(precios_hoja):
            try:
                # Extraer datos del producto
                codigo = str(item.get('CODIGO BATERIAS', item.get('CODIGO', ''))).strip()
                nombre = str(item.get('DENOMINACION COMERCIAL / ALGUNAS APLICACIONES (4)', 
                                    item.get('NOMBRE', item.get('DENOMINACION', '')))).strip()
                precio_lista = item.get('Precio de Lista', item.get('PRECIO', 0))
                
                # Solo procesar productos válidos
                if codigo and codigo != 'nan' and precio_lista and precio_lista != 'nan':
                    productos_precios.append({
                        'codigo': codigo,
                        'nombre': nombre if nombre != 'nan' else f'Producto {codigo}',
                        'precio_base': float(precio_lista)
                    })
                    logger.info(f"  ✅ Producto {i+1}: {codigo} - ${precio_lista}")
                else:
                    logger.info(f"  ⚠️ Producto {i+1} saltado: código='{codigo}', precio='{precio_lista}'")
                    
            except Exception as e:
                logger.error(f"Error procesando producto {i+1}: {e}")
                continue
        
        logger.info(f"✅ Total productos de precios válidos: {len(productos_precios)}")
        
        # Procesar cada producto con ambos canales
        for producto_precio in productos_precios:
            try:
                codigo = producto_precio['codigo']
                nombre = producto_precio['nombre']
                precio_base = producto_precio['precio_base']
                
                # Buscar reglas específicas por código de producto
                regla_minorista = None
                regla_mayorista = None
                
                # Buscar regla minorista específica por código
                for regla in analisis_rentabilidades['reglas_minorista']:
                    if regla['codigo'] == codigo:
                        regla_minorista = regla
                        logger.info(f"✅ Regla Minorista encontrada para {codigo}: {regla['markup']}%")
                        break
                
                # Si no se encuentra regla específica, buscar por similitud de código
                if not regla_minorista and analisis_rentabilidades['reglas_minorista']:
                    # Buscar regla con código similar (mismo prefijo)
                    for regla in analisis_rentabilidades['reglas_minorista']:
                        if codigo.startswith(regla['codigo'][:3]) or regla['codigo'].startswith(codigo[:3]):
                            regla_minorista = regla
                            logger.info(f"⚠️ Usando regla Minorista similar para {codigo}: {regla['markup']}% (código: {regla['codigo']})")
                            break
                
                # Si aún no se encuentra, usar la primera disponible
                if not regla_minorista and analisis_rentabilidades['reglas_minorista']:
                    regla_minorista = analisis_rentabilidades['reglas_minorista'][0]
                    logger.info(f"⚠️ Usando regla Minorista default para {codigo}: {regla_minorista['markup']}%")
                
                # Buscar regla mayorista específica por código
                for regla in analisis_rentabilidades['reglas_mayorista']:
                    if regla['codigo'] == codigo:
                        regla_mayorista = regla
                        logger.info(f"✅ Regla Mayorista encontrada para {codigo}: {regla['markup']}%")
                        break
                
                # Si no se encuentra regla específica, buscar por similitud de código
                if not regla_mayorista and analisis_rentabilidades['reglas_mayorista']:
                    # Buscar regla con código similar (mismo prefijo)
                    for regla in analisis_rentabilidades['reglas_mayorista']:
                        if codigo.startswith(regla['codigo'][:3]) or regla['codigo'].startswith(codigo[:3]):
                            regla_mayorista = regla
                            logger.info(f"⚠️ Usando regla Mayorista similar para {codigo}: {regla['markup']}% (código: {regla['codigo']})")
                            break
                
                # Si aún no se encuentra, usar la primera disponible
                if not regla_mayorista and analisis_rentabilidades['reglas_mayorista']:
                    regla_mayorista = analisis_rentabilidades['reglas_mayorista'][0]
                    logger.info(f"⚠️ Usando regla Mayorista default para {codigo}: {regla_mayorista['markup']}%")
                
                # Calcular precios para ambos canales
                producto_resultado = {
                    'codigo': codigo,
                    'nombre': nombre,
                    'precio_base': precio_base,
                    'canales': {}
                }
                
                # Canal Minorista
                if regla_minorista:
                    markup_minorista = regla_minorista['markup']
                    precio_minorista = precio_base * (1 + markup_minorista / 100)
                    # Redondear a múltiplos de 100
                    precio_minorista = round(precio_minorista / 100) * 100
                    margen_minorista = ((precio_minorista - precio_base) / precio_minorista) * 100
                    
                    producto_resultado['canales']['minorista'] = {
                        'precio_final': precio_minorista,
                        'markup_aplicado': markup_minorista,
                        'margen': margen_minorista,
                        'rentabilidad': regla_minorista.get('rentabilidad', 0),
                        'estado': 'ÓPTIMO' if margen_minorista >= 20 else 'ADVERTENCIA' if margen_minorista >= 10 else 'CRÍTICO'
                    }
                else:
                    logger.warning(f"⚠️ No hay regla Minorista para {codigo}")
                
                # Canal Mayorista
                if regla_mayorista:
                    markup_mayorista = regla_mayorista['markup']
                    precio_mayorista = precio_base * (1 + markup_mayorista / 100)
                    # Redondear a múltiplos de 100
                    precio_mayorista = round(precio_mayorista / 100) * 100
                    margen_mayorista = ((precio_mayorista - precio_base) / precio_mayorista) * 100
                    
                    producto_resultado['canales']['mayorista'] = {
                        'precio_final': precio_mayorista,
                        'markup_aplicado': markup_mayorista,
                        'margen': margen_mayorista,
                        'rentabilidad': regla_mayorista.get('rentabilidad', 0),
                        'estado': 'ÓPTIMO' if margen_mayorista >= 20 else 'ADVERTENCIA' if margen_mayorista >= 10 else 'CRÍTICO'
                    }
                else:
                    logger.warning(f"⚠️ No hay regla Mayorista para {codigo}")
                
                productos_procesados.append(producto_resultado)
                logger.info(f"✅ Producto {codigo} procesado: Minorista=${producto_resultado['canales'].get('minorista', {}).get('precio_final', 0)}, Mayorista=${producto_resultado['canales'].get('mayorista', {}).get('precio_final', 0)}")
                
            except Exception as e:
                logger.error(f"Error procesando producto {codigo}: {e}")
                continue
        
        # Actualizar datos globales
        global productos_actuales
        productos_actuales = productos_procesados
        
        pasos_completados = [
            "✅ Archivo de precios cargado",
            "✅ Reglas de rentabilidad cargadas desde archivo local",
            "✅ Productos convertidos",
            "✅ Reglas de rentabilidad aplicadas por canal",
            "✅ Precios calculados para Minorista y Mayorista",
            "✅ Validación completada"
        ]
        
        logger.info(f"✅ Proceso completado exitosamente - {len(productos_procesados)} productos")
        
        # Generar resumen
        total_minorista = len([p for p in productos_procesados if 'minorista' in p['canales']])
        total_mayorista = len([p for p in productos_procesados if 'mayorista' in p['canales']])
        
        margen_promedio_minorista = sum([p['canales']['minorista']['margen'] for p in productos_procesados if 'minorista' in p['canales']]) / total_minorista if total_minorista > 0 else 0
        margen_promedio_mayorista = sum([p['canales']['mayorista']['margen'] for p in productos_procesados if 'mayorista' in p['canales']]) / total_mayorista if total_mayorista > 0 else 0
        
        resumen = {
            'total_productos': len(productos_procesados),
            'total_minorista': total_minorista,
            'total_mayorista': total_mayorista,
            'margen_promedio_minorista': round(margen_promedio_minorista, 2),
            'margen_promedio_mayorista': round(margen_promedio_mayorista, 2),
            'archivo_precios': precios_filename,
            'archivo_rentabilidades': archivo_rentabilidades,
            'reglas_cargadas': len(analisis_rentabilidades['reglas_minorista']) + len(analisis_rentabilidades['reglas_mayorista'])
        }
        
        return {
            "status": "success",
            "mensaje": f"✅ Proceso completado exitosamente - {len(productos_procesados)} productos procesados",
            "productos": len(productos_procesados),
            "productos_detalle": productos_procesados,  # TODOS los productos procesados
            "pasos_completados": pasos_completados,
            "resumen": resumen
        }
        
    except Exception as e:
        logger.error(f"❌ Error en cálculo de precios: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "mensaje": f"Error en el cálculo: {str(e)}",
            "productos": 0,
            "productos_detalle": [],
            "pasos_completados": [],
            "resumen": {}
        }

@app.post("/api/analizar-rentabilidades-2-canales")
async def analizar_rentabilidades_2_canales_endpoint():
    """
    Analiza específicamente el archivo Rentalibilidades-2.xlsx con estructura de 2 canales.
    """
    try:
        logger.info("🔍 Iniciando análisis de rentabilidades con 2 canales")
        
        # Buscar el archivo
        archivo_path = None
        posibles_paths = [
            "Rentalibilidades-2.xlsx",
            "Rentalibilidades-2.xls",
            "data/Rentalibilidades-2.xlsx",
            "data/Rentalibilidades-2.xls"
        ]
        
        for path in posibles_paths:
            if os.path.exists(path):
                archivo_path = path
                break
        
        if not archivo_path:
            return {
                "status": "error",
                "mensaje": "No se encontró el archivo Rentalibilidades-2.xlsx en el proyecto",
                "analisis": None
            }
        
        # Analizar el archivo
        analisis = analizar_rentabilidades_2_canales(archivo_path)
        
        return {
            "status": "success",
            "mensaje": f"Análisis completado para {archivo_path}",
            "analisis": analisis
        }
        
    except Exception as e:
        logger.error(f"❌ Error analizando rentabilidades: {e}")
        return {
            "status": "error",
            "mensaje": f"Error en el análisis: {str(e)}",
            "analisis": None
        }

@app.get("/api/logs")
async def obtener_logs():
    """Endpoint para obtener logs del servidor"""
    try:
        # Capturar logs recientes
        logs = []
        
        # Verificar estado de archivos
        logs.append(f"📁 Estado de archivos:")
        logs.append(f"  - precios_data: {'✅ Cargado' if precios_data else '❌ No cargado'}")
        logs.append(f"  - rentabilidades_data: {'✅ Cargado' if rentabilidades_data else '❌ No cargado'}")
        
        if precios_data:
            logs.append(f"  - Hojas de precios: {list(precios_data.keys())}")
            for hoja, datos in precios_data.items():
                logs.append(f"    - {hoja}: {len(datos)} productos")
                if datos:
                    logs.append(f"      Primer producto: {datos[0]}")
        
        if rentabilidades_data:
            logs.append(f"  - Hojas de rentabilidad: {list(rentabilidades_data.keys())}")
            for hoja, datos in rentabilidades_data.items():
                logs.append(f"    - {hoja}: {len(datos)} reglas")
                if datos:
                    logs.append(f"      Primera regla: {datos[0]}")
        
        logs.append(f"📊 Productos actuales: {len(productos_actuales)}")
        
        return {
            "status": "success",
            "logs": logs
        }
        
    except Exception as e:
        return {
            "status": "error",
            "mensaje": f"Error obteniendo logs: {str(e)}"
        } 

@app.get("/api/listar-archivos")
async def listar_archivos():
    """Lista todos los archivos disponibles en el directorio de trabajo"""
    try:
        # Obtener directorio actual
        current_dir = os.getcwd()
        
        # Listar todos los archivos
        archivos = []
        for root, dirs, files in os.walk(current_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, current_dir)
                
                # Obtener información del archivo
                try:
                    file_size = os.path.getsize(file_path)
                    archivos.append({
                        "nombre": file,
                        "ruta": relative_path,
                        "tamaño": file_size,
                        "tamaño_mb": round(file_size / (1024 * 1024), 2)
                    })
                except:
                    archivos.append({
                        "nombre": file,
                        "ruta": relative_path,
                        "tamaño": "error",
                        "tamaño_mb": "error"
                    })
        
        # Filtrar solo archivos Excel
        archivos_excel = [f for f in archivos if f["nombre"].lower().endswith('.xlsx')]
        
        return {
            "directorio_actual": current_dir,
            "total_archivos": len(archivos),
            "archivos_excel": archivos_excel,
            "todos_los_archivos": archivos[:20]  # Solo los primeros 20 para no saturar
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "directorio_actual": os.getcwd() if os.getcwd() else "No disponible"
        }

@app.post("/descargar-excel")
async def descargar_excel(data: dict):
    """
    Genera y descarga un archivo Excel con los resultados de precios
    """
    try:
        logger.info("📊 Generando archivo Excel...")
        
        # Crear un DataFrame con los resultados
        productos = []
        
        for producto in data.get('productos', []):
            codigo = producto.get('codigo', '')
            descripcion = producto.get('descripcion', '')
            precio_base = producto.get('precio_base', 0)
            
            # Datos Minorista
            minorista = producto.get('canales', {}).get('minorista', {})
            precio_minorista = minorista.get('precio_final', 0)
            markup_minorista = minorista.get('markup_aplicado', 0)
            rentabilidad_minorista = minorista.get('rentabilidad', 0)
            estado_minorista = minorista.get('estado', '')
            
            # Datos Mayorista
            mayorista = producto.get('canales', {}).get('mayorista', {})
            precio_mayorista = mayorista.get('precio_final', 0)
            markup_mayorista = mayorista.get('markup_aplicado', 0)
            rentabilidad_mayorista = mayorista.get('rentabilidad', 0)
            estado_mayorista = mayorista.get('estado', '')
            
            productos.append({
                'Código': codigo,
                'Descripción': descripcion,
                'Precio Base': precio_base,
                'Precio Minorista': precio_minorista,
                'Markup Minorista (%)': markup_minorista,
                'Rentabilidad Minorista (%)': rentabilidad_minorista,
                'Estado Minorista': estado_minorista,
                'Precio Mayorista': precio_mayorista,
                'Markup Mayorista (%)': markup_mayorista,
                'Rentabilidad Mayorista (%)': rentabilidad_mayorista,
                'Estado Mayorista': estado_mayorista
            })
        
        # Crear DataFrame
        df = pd.DataFrame(productos)
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Precios Calculados', index=False)
            
            # Obtener el workbook para formatear
            workbook = writer.book
            worksheet = writer.sheets['Precios Calculados']
            
            # Formatear columnas de precios
            for col in ['C', 'D', 'H']:  # Precio Base, Precio Minorista, Precio Mayorista
                for row in range(2, len(productos) + 2):
                    cell = worksheet[f'{col}{row}']
                    cell.number_format = '#,##0.00'  # Formato con punto millar y dos decimales
            
            # Formatear columnas de porcentajes (sin símbolo %)
            for col in ['E', 'F', 'I', 'J']:  # Markups y Rentabilidades
                for row in range(2, len(productos) + 2):
                    cell = worksheet[f'{col}{row}']
                    cell.number_format = '0.00'  # Solo números con coma decimal, sin símbolo %
            
            # Ajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"precios_calculados_{timestamp}.xlsx"
        
        logger.info(f"✅ Archivo Excel generado: {filename}")
        
        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"❌ Error generando Excel: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando Excel: {str(e)}")

@app.post("/api/analisis-ia-inteligente")
async def analisis_ia_inteligente():
    """
    Análisis IA inteligente de productos críticos y con advertencias
    """
    try:
        logger.info("🤖 Iniciando análisis IA inteligente...")
        
        # Verificar que tenemos datos
        if not productos_actuales:
            return {
                "status": "error",
                "mensaje": "No hay productos calculados. Primero debes calcular los precios."
            }
        
        # Filtrar productos críticos y con advertencias
        productos_criticos = []
        productos_advertencia = []
        
        for producto in productos_actuales:
            canales = producto.get('canales', {})
            
            # Verificar canal minorista
            minorista = canales.get('minorista', {})
            if minorista.get('estado') == 'CRÍTICO':
                productos_criticos.append(producto)
            elif minorista.get('estado') == 'ADVERTENCIA':
                productos_advertencia.append(producto)
            
            # Verificar canal mayorista
            mayorista = canales.get('mayorista', {})
            if mayorista.get('estado') == 'CRÍTICO':
                productos_criticos.append(producto)
            elif mayorista.get('estado') == 'ADVERTENCIA':
                productos_advertencia.append(producto)
        
        # Eliminar duplicados
        productos_criticos = list({p['codigo']: p for p in productos_criticos}.values())
        productos_advertencia = list({p['codigo']: p for p in productos_advertencia}.values())
        
        # Generar sugerencias para productos críticos y con advertencias
        sugerencias = []
        
        for producto in productos_criticos + productos_advertencia:
            codigo = producto['codigo']
            nombre = producto.get('nombre', '')
            precio_base = producto['precio_base']
            
            # Obtener información de ambos canales
            canales = producto.get('canales', {})
            minorista = canales.get('minorista', {})
            mayorista = canales.get('mayorista', {})
            
            estado_minorista = minorista.get('estado', 'ÓPTIMO')
            estado_mayorista = mayorista.get('estado', 'ÓPTIMO')
            margen_minorista = minorista.get('margen', 0)
            margen_mayorista = mayorista.get('margen', 0)
            
            # Determinar el estado más crítico y canal correspondiente
            if estado_minorista == 'CRÍTICO' or estado_mayorista == 'CRÍTICO':
                estado = 'CRÍTICO'
                if estado_minorista == 'CRÍTICO':
                    canal_problema = 'Minorista'
                    margen_problema = margen_minorista
                else:
                    canal_problema = 'Mayorista'
                    margen_problema = margen_mayorista
            elif estado_minorista == 'ADVERTENCIA' or estado_mayorista == 'ADVERTENCIA':
                estado = 'ADVERTENCIA'
                if estado_minorista == 'ADVERTENCIA':
                    canal_problema = 'Minorista'
                    margen_problema = margen_minorista
                else:
                    canal_problema = 'Mayorista'
                    margen_problema = margen_mayorista
            else:
                estado = 'ÓPTIMO'
                canal_problema = 'N/A'
                margen_problema = 0
            
            # Generar sugerencias de precio para el canal con problema
            sugerencias_precio = generar_sugerencias_precio(precio_base, margen_problema)
            
            sugerencias.append({
                'codigo': codigo,
                'nombre': nombre,
                'estado': estado,
                'canal_problema': canal_problema,
                'margen_actual': round(margen_problema, 2),
                'margen_minorista': round(margen_minorista, 2),
                'margen_mayorista': round(margen_mayorista, 2),
                'sugerencias_precio': sugerencias_precio
            })
        
        # Ordenar por estado (críticos primero)
        sugerencias.sort(key=lambda x: {'CRÍTICO': 0, 'ADVERTENCIA': 1, 'ÓPTIMO': 2}[x['estado']])
        
        logger.info(f"🤖 Análisis IA completado: {len(productos_criticos)} críticos, {len(productos_advertencia)} con advertencias")
        
        return {
            "status": "success",
            "mensaje": f"Análisis IA completado. {len(productos_criticos)} productos críticos, {len(productos_advertencia)} con advertencias.",
            "total_productos": len(productos_actuales),
            "productos_criticos": len(productos_criticos),
            "productos_advertencia": len(productos_advertencia),
            "sugerencias": sugerencias
        }
        
    except Exception as e:
        logger.error(f"❌ Error en análisis IA: {e}")
        return {
            "status": "error",
            "mensaje": f"Error en análisis IA: {str(e)}"
        }

def generar_sugerencias_precio(precio_base: float, margen_actual: float) -> list:
    """
    Genera sugerencias de precio para mejorar el margen
    """
    sugerencias = []
    
    # Sugerencia conservadora: mejorar margen en 5%
    margen_objetivo_conservador = min(margen_actual + 5, 25)
    precio_conservador = precio_base / (1 - margen_objetivo_conservador / 100)
    precio_conservador = round(precio_conservador / 100) * 100  # Redondear a múltiplos de 100
    
    sugerencias.append({
        'tipo': 'Conservadora',
        'precio_sugerido': precio_conservador,
        'mejora_margen': round(margen_objetivo_conservador - margen_actual, 2)
    })
    
    # Sugerencia moderada: mejorar margen en 10%
    margen_objetivo_moderado = min(margen_actual + 10, 30)
    precio_moderado = precio_base / (1 - margen_objetivo_moderado / 100)
    precio_moderado = round(precio_moderado / 100) * 100
    
    sugerencias.append({
        'tipo': 'Moderada',
        'precio_sugerido': precio_moderado,
        'mejora_margen': round(margen_objetivo_moderado - margen_actual, 2)
    })
    
    # Sugerencia agresiva: mejorar margen en 15%
    margen_objetivo_agresivo = min(margen_actual + 15, 35)
    precio_agresivo = precio_base / (1 - margen_objetivo_agresivo / 100)
    precio_agresivo = round(precio_agresivo / 100) * 100
    
    sugerencias.append({
        'tipo': 'Agresiva',
        'precio_sugerido': precio_agresivo,
        'mejora_margen': round(margen_objetivo_agresivo - margen_actual, 2)
    })
    
    return sugerencias

@app.post("/api/descargar-reporte-ia")
async def descargar_reporte_ia(data: dict):
    """
    Genera y descarga un reporte Word con el análisis IA
    """
    try:
        logger.info("📄 Generando reporte IA...")
        
        # Crear contenido del reporte
        contenido = f"""
# Reporte de Análisis IA Inteligente - AcuBat

**Fecha de generación:** {datetime.now().strftime("%d/%m/%Y %H:%M")}
**Total de productos analizados:** {data.get('total_productos', 0)}

## Resumen Ejecutivo

- **Productos críticos:** {data.get('productos_criticos', 0)}
- **Productos con advertencias:** {data.get('productos_advertencia', 0)}
- **Productos óptimos:** {data.get('total_productos', 0) - data.get('productos_criticos', 0) - data.get('productos_advertencia', 0)}

## Análisis Detallado por Producto

"""
        
        # Agregar análisis por producto
        for sugerencia in data.get('sugerencias', []):
            contenido += f"""
### {sugerencia['codigo']} - {sugerencia['nombre']}

**Estado:** {sugerencia['estado']}
**Canal con problema:** {sugerencia['canal_problema']}
**Margen actual:** {sugerencia['margen_actual']}%
**Margen Minorista:** {sugerencia['margen_minorista']}%
**Margen Mayorista:** {sugerencia['margen_mayorista']}%

#### Sugerencias de Precio:

"""
            
            for sug in sugerencia.get('sugerencias_precio', []):
                contenido += f"""
**{sug['tipo']}:**
- Precio sugerido: ${sug['precio_sugerido']:,.0f}
- Mejora de margen: +{sug['mejora_margen']}%

"""
        
        contenido += f"""
## Recomendaciones Generales

1. **Productos Críticos:** Priorizar la revisión de precios para productos con margen menor al 10%
2. **Productos con Advertencias:** Considerar ajustes moderados para productos con margen entre 10-20%
3. **Optimización Continua:** Monitorear regularmente los márgenes y ajustar precios según sea necesario

---
*Reporte generado automáticamente por el Sistema de Pricing Inteligente AcuBat*
"""
        
        # Crear archivo de texto (simulado como Word)
        output = io.BytesIO()
        output.write(contenido.encode('utf-8'))
        output.seek(0)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analisis_ia_{timestamp}.txt"
        
        logger.info(f"✅ Reporte IA generado: {filename}")
        
        return StreamingResponse(
            output,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"❌ Error generando reporte IA: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")